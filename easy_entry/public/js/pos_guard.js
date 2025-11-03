// pos_guard.js — simple idle refocus for POS search input
(() => {
  // Your exact selector (kept as-is)
  const SELECTOR = "#page-point-of-sale > div.container.page-body > div.page-wrapper > div > div.row.layout-main > div > div.layout-main-section > div.point-of-sale-app > section.items-selector > div.filter-section > div.search-field > div > div > div.control-input-wrapper > div.control-input > input";

  const IDLE_TIME = 3000; // ms of inactivity before focusing back
  let idleTimer = null;
  let wired = false;

  // Wait for an element to exist, then resolve
  function waitForElement(selector, timeoutMs = 15000) {
    return new Promise((resolve, reject) => {
      const start = performance.now();

      function tryFind() {
        const el = document.querySelector(selector);
        if (el) return resolve(el);

        if (performance.now() - start > timeoutMs) {
          return reject(new Error("timeout waiting for " + selector));
        }
        requestAnimationFrame(tryFind);
      }
      tryFind();
    });
  }

  function resetIdle(input) {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(() => {
      if (document.activeElement !== input) {
        input.focus({ preventScroll: true });
      }
    }, IDLE_TIME);
  }

  function wireOnce(input) {
    if (!input || wired) return;
    // Listen high in the capture phase so any interaction resets the timer
    ["keydown", "mousedown", "touchstart", "input", "pointerdown"].forEach(evt =>
      document.addEventListener(evt, () => resetIdle(input), true)
    );
    resetIdle(input);
    wired = true;
    console.log("[POS] auto-focus guard attached to:", input);
  }

  // (Re)wire whenever POS DOM changes (the POS app re-renders a lot)
  const mo = new MutationObserver(async () => {
    try {
      const input = document.querySelector(SELECTOR);
      if (input) {
        wireOnce(input);
      }
    } catch (_) {}
  });

  async function boot() {
    try {
      const input = await waitForElement(SELECTOR, 20000);
      wireOnce(input);
      mo.observe(document.body, { childList: true, subtree: true });
    } catch (err) {
      console.warn("[POS] search input not found:", err.message);
    }
  }

  // Defer until DOM ready; also re-run on route changes
  const start = () => {
    // Ensure we’re on the POS page
    const onPOS = location.pathname.includes("/app/point-of-sale");
    if (!onPOS) return;
    boot();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }

  if (window.frappe?.router?.on) {
    frappe.router.on("change", () => {
      // reset state between navigations
      wired = false;
      clearTimeout(idleTimer);
      mo.disconnect();
      start();
    });
  }
})();
