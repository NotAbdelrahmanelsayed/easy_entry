// pos_guard.js — idle refocus for item search (robust across POS variants)
(() => {
	const IDLE_TIME = 3000; // ms of inactivity before focusing back
	let idleTimer = null;
	let wiredEl = null;

	const onPOS = () => {
		const p = location.pathname.toLowerCase();
		return (
			p.includes("/desk/point-of-sale") ||
			p.includes("/desk/pos") ||
			p.includes("/app/point-of-sale") ||
			p.includes("/app/pos") ||
			p.includes("/pos") ||
			p.includes("pos")
		);
	};

	const isVisible = (el) => {
		if (!el) return false;
		const rect = el.getBoundingClientRect();
		return (
			!!(rect.width || rect.height) && window.getComputedStyle(el).visibility !== "hidden"
		);
	};

	function findPOSContainer() {
		return (
			document.querySelector(".point-of-sale-app") ||
			document.querySelector("#page-point-of-sale") ||
			document.querySelector('[data-page-route="point-of-sale"]') ||
			document
		);
	}

	function candidatesWithin(root) {
		// Prefer inputs inside typical POS areas
		const specific = [
			"div.search-field input.input-with-feedback.form-control",
			"section.items-selector input.input-with-feedback.form-control",
		];
		for (const sel of specific) {
			const els = Array.from(root.querySelectorAll(sel));
			if (els.length) return els;
		}
		// Generic fallbacks in container
		return Array.from(root.querySelectorAll("input.input-with-feedback.form-control"));
	}

	function looksLikeSearch(el) {
		const ph = (el.getAttribute("placeholder") || "").toLowerCase();
		// Match common English strings; add more if you localize later
		return (
			ph.includes("search") ||
			ph.includes("barcode") ||
			ph.includes("item code") ||
			ph.includes("serial number")
		);
	}

	function pickBestInput() {
		// 1) Hard-coded fallback using your known selector path
		const hard = document.querySelector("#item-search");
		if (hard && isVisible(hard)) {
			return hard;
		}

		// 2) Generic logic
		const container = findPOSContainer();
		const allVisible = candidatesWithin(container).filter(isVisible);
		if (!allVisible.length) return null;

		// First: those that *look like* search (if placeholder helps)
		const matched = allVisible.filter(looksLikeSearch);
		const pool = matched.length ? matched : allVisible;

		// Prefer ones under .search-field first
		const preferred = pool.find((el) => el.closest(".search-field")) || pool[0];

		return preferred || null;
	}

	function userIsBusy(input) {
		const ae = document.activeElement;
		// Never steal focus from another text field (e.g. customer search,
		// quantity edit) — only reclaim it from buttons/body after idle.
		if (
			ae &&
			ae !== input &&
			(ae.tagName === "INPUT" ||
				ae.tagName === "TEXTAREA" ||
				ae.tagName === "SELECT" ||
				ae.isContentEditable)
		) {
			return true;
		}
		// Don't fight open dialogs (frappe-ui renders [data-dialog] only while open)
		if (document.querySelector('[data-dialog], .modal.show, [role="dialog"]')) {
			return true;
		}
		return false;
	}

	function resetIdle(input) {
		clearTimeout(idleTimer);
		idleTimer = setTimeout(() => {
			if (userIsBusy(input)) {
				// Check again later instead of grabbing focus mid-task
				resetIdle(input);
				return;
			}
			if (document.activeElement !== input && isVisible(input)) {
				input.focus({ preventScroll: true });
			}
		}, IDLE_TIME);
	}

	function wire(input) {
		if (!input || wiredEl === input) return;
		wiredEl = input;

		// Any activity resets the idle timer
		["keydown", "mousedown", "touchstart", "pointerdown", "input"].forEach((evt) =>
			document.addEventListener(evt, () => resetIdle(input), true)
		);
		resetIdle(input);
		console.log("[POS] idle-refocus wired →", input);
	}

	function tryWire() {
		if (!onPOS()) return;
		const input = pickBestInput();
		if (input) {
			wire(input);
		} else {
			console.debug("[POS] search input not found yet; will retry…");
		}
	}

	// Re-run when DOM changes (POS re-renders often)
	const mo = new MutationObserver(() => tryWire());

	function boot() {
		if (!document.body || !onPOS()) return;
		tryWire();
		mo.observe(document.body, { childList: true, subtree: true });
	}

	const start = () => boot();

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", start);
	} else {
		start();
	}
})();
