/**
 * Keep the custom header navigation active state synchronised with
 * MkDocs Material instant navigation.
 */

(() => {
  "use strict";

  const { onDocumentReady, onInstantNavigation } =
    window.LupaxaPageLifecycle;

  const normalisePath = (value) => {
    const url = new URL(value, window.location.origin);

    const path = url.pathname
      .replace(/\/index\.html$/, "/")
      .replace(/\/+$/, "");

    return path || "/";
  };

  const updateActiveNavigation = () => {
    const currentPath = normalisePath(window.location.href);

    document
      .querySelectorAll(".lupaxa-header__nav-item")
      .forEach((item) => {
        const link = item.querySelector(
          ".lupaxa-header__nav-link",
        );

        if (!link) {
          return;
        }

        const linkPath = normalisePath(link.href);

        const isActive =
          linkPath === "/"
            ? currentPath === "/"
            : currentPath === linkPath ||
              currentPath.startsWith(`${linkPath}/`);

        item.classList.toggle(
          "lupaxa-header__nav-item--active",
          isActive,
        );

        if (isActive) {
          link.setAttribute("aria-current", "page");
        } else {
          link.removeAttribute("aria-current");
        }
      });
  };

  const scheduleUpdate = () => {
    requestAnimationFrame(updateActiveNavigation);
  };

  onDocumentReady(updateActiveNavigation);
  onInstantNavigation(updateActiveNavigation);

  window.addEventListener("popstate", scheduleUpdate);
})();
