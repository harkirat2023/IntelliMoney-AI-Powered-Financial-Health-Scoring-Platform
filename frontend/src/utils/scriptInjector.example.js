/**
 * EXAMPLE USAGE - Script Injection Utility
 * 
 * This file demonstrates proper usage of the injectScript utility.
 */

import { injectScript, createAndInjectScript, injectInlineScript } from './scriptInjector.js';

// ============================================================================
// EXAMPLE 1: Proper Script Element Creation and Injection
// ============================================================================

// CORRECT: Create a script DOM node programmatically
const loadExternalScript = () => {
  // Step 1: Create the script element using document.createElement
  const scriptElement = document.createElement('script');
  
  // Step 2: Configure the script element
  scriptElement.src = 'https://example.com/analytics.js';
  scriptElement.async = true;
  scriptElement.defer = false;
  
  // Step 3: Inject the script using the utility
  injectScript(scriptElement);
};

// ============================================================================
// EXAMPLE 2: Using the Helper Function (Recommended)
// ============================================================================

const loadScriptWithHelper = () => {
  // The createAndInjectScript function handles all validation internally
  const script = createAndInjectScript('https://example.com/widget.js', {
    id: 'external-widget',
    async: true
  });
  
  if (script) {
    console.log('Script injected successfully:', script);
  }
};

// ============================================================================
// EXAMPLE 3: Inline Script Injection
// ============================================================================

const injectInlineCode = () => {
  const inlineCode = `
    (function() {
      console.log('Inline script executed');
      window.myCustomVar = 'Hello World';
    })();
  `;
  
  const script = injectInlineScript(inlineCode, {
    id: 'inline-config'
  });
};

// ============================================================================
// EXAMPLE 4: Common Anti-Patterns to AVOID
// ============================================================================

// ❌ WRONG: Passing a string instead of a DOM node
// injectScript('https://example.com/script.js'); // TypeError!

// ❌ WRONG: Passing null or undefined
// injectScript(null); // TypeError!
// injectScript(undefined); // TypeError!

// ❌ WRONG: Passing a plain object
// injectScript({ src: 'https://example.com/script.js' }); // TypeError!

// ❌ WRONG: Forgetting to check SSR context
// if (typeof window !== 'undefined') {
//   injectScript(scriptElement); // Still might fail if document.head is undefined
// }

// ============================================================================
// EXAMPLE 5: React Integration (Safe for SSR)
// ============================================================================

// In a React component or useEffect hook:
// import { useEffect } from 'react';
// 
// useEffect(() => {
//   // This is safe - runs only on client-side after mount
//   const script = createAndInjectScript('https://example.com/react-widget.js');
//   
//   return () => {
//     // Cleanup: remove script on unmount
//     if (script && script.parentNode) {
//       script.parentNode.removeChild(script);
//     }
//   };
// }, []);

// ============================================================================
// EXAMPLE 6: Dynamic Script Loading with Error Handling
// ============================================================================

const loadScriptWithErrorHandling = async (src) => {
  try {
    const script = createAndInjectScript(src, { async: true });
    
    if (!script) {
      console.warn('Script not loaded - likely SSR environment');
      return null;
    }
    
    // Return a promise that resolves when script loads
    return new Promise((resolve, reject) => {
      script.onload = () => resolve(script);
      script.onerror = () => reject(new Error(`Failed to load script: ${src}`));
    });
  } catch (error) {
    console.error('Script injection failed:', error);
    return null;
  }
};

export { 
  loadExternalScript, 
  loadScriptWithHelper, 
  injectInlineCode, 
  loadScriptWithErrorHandling 
};