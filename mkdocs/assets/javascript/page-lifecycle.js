/**
 * Shared page-load and MkDocs Material instant-navigation helpers.
 */

(() => {
  "use strict";

  /**
   * Run once the document is ready.
   *
   * @param {() => void} fn
   */
  const onDocumentReady = (fn) => {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn, {
        once: true,
      });
    } else {
      fn();
    }
  };

  /**
   * Subscribe to MkDocs Material instant navigation when available.
   *
   * @param {() => void} fn
   */
  const onInstantNavigation = (fn) => {
    if (typeof document$ !== "undefined") {
      document$.subscribe(() => {
        requestAnimationFrame(fn);
      });
    }
  };

  window.LupaxaPageLifecycle = {
    onDocumentReady,
    onInstantNavigation,
  };
})();
