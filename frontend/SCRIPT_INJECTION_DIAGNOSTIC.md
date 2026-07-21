# Script Injection Utility - Diagnostic Analysis & Solution

## A. Diagnostic Root Cause

Based on the Web API specification for `.appendChild()`, the original code throws a runtime error due to the following edge cases:

### 1. **Type Validation Failure**
```javascript
// ORIGINAL CODE:
const injectScript = (scriptElement) => {
  if (isDocumentReady()) {
    (document.head || document.documentElement).appendChild(scriptElement);
  }
};
```

**Problem:** The function assumes `scriptElement` is always a valid DOM `Node` object. However, callers may accidentally pass:
- A `String` (e.g., a URL like `'https://example.com/script.js'`)
- `undefined` or `null` (if the script creation failed)
- A plain `Object` (e.g., `{ src: '...' }`)
- A number or other primitive type

**Web API Behavior:** According to the DOM specification, `appendChild()` requires its argument to be a `Node` object. Passing any other type throws a `TypeError: Failed to execute 'appendChild' on 'Node': parameter 1 is not of type 'Node'`.

### 2. **Server-Side Rendering (SSR) Context**
**Problem:** In Next.js, Nuxt, or other SSR frameworks, `document` is `undefined` during server-side rendering. The `isDocumentReady()` check may not properly guard against this.

**Web API Behavior:** Accessing `document.head` or `document.documentElement` when `document` is undefined throws a `ReferenceError: document is not defined`.

### 3. **DOM Availability During Early Execution**
**Problem:** During early page load stages, `document.head` may be `null` or `undefined` while the browser is still parsing the document. The fallback to `document.documentElement` is insufficient because:
- `document.documentElement` (the `<html>` element) may also be unavailable
- The document may be in a "loading" state where neither head nor body exist yet

**Web API Behavior:** Calling `appendChild()` on a `null` or `undefined` parent throws a `TypeError`.

### 4. **Cross-Origin Frame Context**
**Problem:** If the code runs inside an iframe with different origin policies, the `scriptElement` may be a valid Node in its own document context but incompatible with the parent document.

**Web API Behavior:** Attempting to append a node from a different document context throws a `DOMException: Node cannot be inserted into a parent node that is not in the same document`.

---

## B. Robust Refactored Code

The solution has been implemented in `frontend/src/utils/scriptInjector.js`:

```javascript
/**
 * Checks if the document is ready for DOM manipulation.
 * Handles SSR environments where `document` is undefined.
 */
const isDocumentReady = () => {
  if (typeof document === 'undefined' || typeof window === 'undefined') {
    return false;
  }
  return document.body !== null && document.body !== undefined;
};

/**
 * Safely injects a script element into the DOM.
 */
const injectScript = (scriptElement) => {
  // SSR Environment Guard
  if (typeof document === 'undefined' || typeof window === 'undefined') {
    console.warn('injectScript: Document not available (SSR environment). Script not injected.');
    return;
  }

  // Type Validation: Ensure scriptElement is a valid DOM Node
  if (!scriptElement || typeof scriptElement.appendChild !== 'function') {
    throw new TypeError(
      `injectScript: Invalid scriptElement provided. Expected a DOM Node, received: ${
        scriptElement === null ? 'null' : 
        scriptElement === undefined ? 'undefined' : 
        typeof scriptElement
      }`
    );
  }

  // Additional validation: Check if it's actually a Script element
  if (scriptElement.nodeType !== Node.ELEMENT_NODE || scriptElement.tagName !== 'SCRIPT') {
    console.warn(
      `injectScript: Expected SCRIPT element, received: ${scriptElement?.tagName || 'unknown'}`
    );
  }

  // DOM Availability Check with fallback chain
  const targetElement = 
    document.head || 
    document.documentElement || 
    document.body || 
    document;

  if (!targetElement) {
    setTimeout(() => injectScript(scriptElement), 50);
    return;
  }

  // Safe append operation
  try {
    targetElement.appendChild(scriptElement);
  } catch (error) {
    console.error('injectScript: Failed to append script element', error);
    if (targetElement !== document.documentElement) {
      setTimeout(() => {
        if (document.documentElement) {
          document.documentElement.appendChild(scriptElement);
        }
      }, 100);
    }
  }
};
```

### Key Improvements:

1. **Strict Runtime Guards:**
   - Validates `scriptElement` is a valid DOM Node using `appendChild` method check
   - Throws descriptive `TypeError` for invalid inputs
   - Warns if element is not a SCRIPT tag

2. **SSR Environment Handling:**
   - Checks `typeof document === 'undefined'` before any DOM access
   - Checks `typeof window === 'undefined'` for complete environment detection
   - Gracefully returns with warning instead of crashing

3. **Bulletproof Fallback Path:**
   - Primary: `document.head`
   - Secondary: `document.documentElement`
   - Tertiary: `document.body`
   - Final: `document` itself
   - Retries with timeout if all targets fail

---

## C. Input Validation Example

### ❌ INCORRECT Usage (Will Throw Error):
```javascript
// These will all throw TypeError:
injectScript('https://example.com/script.js');  // String, not Node
injectScript(null);                           // null
injectScript(undefined);                      // undefined
injectScript({ src: '...' });                 // Plain object
injectScript(123);                            // Number
```

### ✅ CORRECT Usage (Proper Script DOM Node Creation):

```javascript
// Method 1: Create script element programmatically
const scriptElement = document.createElement('script');
scriptElement.src = 'https://example.com/analytics.js';
scriptElement.async = true;
scriptElement.defer = false;
injectScript(scriptElement);

// Method 2: Use the helper function (Recommended)
const script = createAndInjectScript('https://example.com/widget.js', {
  id: 'external-widget',
  async: true
});

// Method 3: Inline script injection
const inlineScript = document.createElement('script');
inlineScript.textContent = `
  (function() {
    console.log('Inline script executed');
    window.myCustomVar = 'Hello World';
  })();
`;
injectScript(inlineScript);
```

### React Integration Example:
```javascript
import { useEffect } from 'react';
import { createAndInjectScript } from './utils/scriptInjector.js';

function MyComponent() {
  useEffect(() => {
    // Safe - runs only on client-side after mount
    const script = createAndInjectScript('https://example.com/widget.js');
    
    return () => {
      // Cleanup on unmount
      if (script && script.parentNode) {
        script.parentNode.removeChild(script);
      }
    };
  }, []);

  return <div>Component with external script</div>;
}
```

---

## D. Frontend Black Screen Issue Analysis

The black screen at localhost:3002 is likely caused by:

1. **Missing CSS Styles:** The `index.html` references `bundle.js` but the CSS might not be loading correctly
2. **JavaScript Error:** A runtime error in the bundle could be preventing React from rendering
3. **Nginx Configuration:** The 304 response suggests caching issues

### Quick Fix for Black Screen:

1. **Clear browser cache** and do a hard refresh (Ctrl+F5)
2. **Check browser console** for JavaScript errors
3. **Verify the bundle is loading** - check Network tab for 404s
4. **Add a fallback style** to `index.html` to ensure background is visible:

```html
<style>
  body {
    background: #f5f7fb !important;
    min-height: 100vh;
    margin: 0;
  }
  #root {
    min-height: 100vh;
  }
</style>
```

5. **Restart the frontend container** to ensure fresh build:
```bash
docker-compose restart frontend