/**
 * Robust Script Injection Utility
 * 
 * This module provides a safe, SSR-compatible script injection function
 * that handles all edge cases for DOM manipulation.
 */

/**
 * Checks if the document is ready for DOM manipulation.
 * Handles SSR environments where `document` is undefined.
 * 
 * @returns {boolean} True if document is available and ready
 */
const isDocumentReady = () => {
  // SSR guard: Check if we're in a browser environment
  if (typeof document === 'undefined' || typeof window === 'undefined') {
    return false;
  }
  
  // Check if document.body exists (indicates basic DOM readiness)
  return document.body !== null && document.body !== undefined;
};

/**
 * Safely injects a script element into the DOM.
 * 
 * This function includes:
 * 1. Strict runtime guards ensuring scriptElement is a valid DOM Node
 * 2. SSR environment handling (gracefully returns if no document)
 * 3. Bulletproof fallback targeting for document.head
 * 
 * @param {Node} scriptElement - A valid HTMLScriptElement DOM node
 * @throws {TypeError} If scriptElement is not a valid DOM Node
 * @returns {void}
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
    // If no target is available, retry after a short delay
    setTimeout(() => injectScript(scriptElement), 50);
    return;
  }

  // Safe append operation
  try {
    targetElement.appendChild(scriptElement);
  } catch (error) {
    console.error('injectScript: Failed to append script element', error);
    // Retry with document.documentElement as last resort
    if (targetElement !== document.documentElement) {
      setTimeout(() => {
        if (document.documentElement) {
          document.documentElement.appendChild(scriptElement);
        }
      }, 100);
    }
  }
};

/**
 * Creates and injects a script element with the given source URL.
 * This is the recommended way to use the injectScript utility.
 * 
 * @param {string} src - The URL of the script to load
 * @param {Object} options - Optional configuration
 * @param {string} [options.id] - Optional script ID
 * @param {string} [options.async] - Whether to load asynchronously
 * @param {string} [options.defer] - Whether to defer loading
 * @returns {HTMLScriptElement | null} The created script element, or null in SSR
 */
const createAndInjectScript = (src, options = {}) => {
  // SSR Environment Guard
  if (typeof document === 'undefined' || typeof window === 'undefined') {
    console.warn('createAndInjectScript: Document not available (SSR environment).');
    return null;
  }

  // Validate src parameter
  if (!src || typeof src !== 'string') {
    throw new TypeError(`createAndInjectScript: Invalid src provided. Expected string, received: ${typeof src}`);
  }

  // Create the script element
  const scriptElement = document.createElement('script');
  scriptElement.src = src;
  
  if (options.id) {
    scriptElement.id = options.id;
  }
  
  if (options.async) {
    scriptElement.async = true;
  }
  
  if (options.defer) {
    scriptElement.defer = true;
  }

  // Inject the script
  injectScript(scriptElement);
  
  return scriptElement;
};

/**
 * Injects inline script content into the DOM.
 * 
 * @param {string} content - The JavaScript code to inject
 * @param {Object} options - Optional configuration
 * @param {string} [options.id] - Optional script ID
 * @returns {HTMLScriptElement | null} The created script element, or null in SSR
 */
const injectInlineScript = (content, options = {}) => {
  // SSR Environment Guard
  if (typeof document === 'undefined' || typeof window === 'undefined') {
    console.warn('injectInlineScript: Document not available (SSR environment).');
    return null;
  }

  // Validate content parameter
  if (typeof content !== 'string') {
    throw new TypeError(`injectInlineScript: Invalid content provided. Expected string, received: ${typeof content}`);
  }

  // Create the script element
  const scriptElement = document.createElement('script');
  scriptElement.textContent = content;
  
  if (options.id) {
    scriptElement.id = options.id;
  }

  // Inject the script
  injectScript(scriptElement);
  
  return scriptElement;
};

export { injectScript, createAndInjectScript, injectInlineScript, isDocumentReady };