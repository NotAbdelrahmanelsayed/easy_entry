// Per-row and bulk item label printing for Stock Reconciliation,
// Purchase Invoice, Sales Invoice, and Stock Entry.

const DEFAULT_FORMAT = "50 * 25";
let _format = null;

async function getLabelFormat() {
	if (_format) return _format;
	const val = await frappe.db.get_single_value("Stock Settings", "ee_label_print_format");
	_format = val || DEFAULT_FORMAT;
	return _format;
}

// Guard: (itemCode, timestamp) — prevents multiple handlers from opening
// duplicate tabs for the same click event within a 400 ms window.
const _printGuard = new Map();

function openPrintview(itemCode, format) {
	const now = Date.now();
	if (now - (_printGuard.get(itemCode) || 0) < 400) return;
	_printGuard.set(itemCode, now);

	const params = new URLSearchParams({
		doctype: "Item",
		name: itemCode,
		trigger_print: "1",
		format: format,
		no_letterhead: "1",
		pdf_generator: "wkhtmltopdf",
	});
	window.open(`/printview?${params.toString()}`, "_blank");
}

function showBulkDialog(frm, format) {
	const items = (frm.doc.items || []).filter((r) => r.item_code);
	if (!items.length) {
		frappe.msgprint(__("No items to print."));
		return;
	}
	const links = items
		.map((r) => {
			const params = new URLSearchParams({
				doctype: "Item",
				name: r.item_code,
				trigger_print: "1",
				format: format,
				no_letterhead: "1",
				pdf_generator: "wkhtmltopdf",
			});
			return `<li><a href="/printview?${params.toString()}" target="_blank">${frappe.utils.escape_html(r.item_code)} — ${frappe.utils.escape_html(r.item_name || "")}</a></li>`;
		})
		.join("");
	frappe.msgprint({
		title: __("Item Label Print"),
		message: `<ul>${links}</ul>`,
		wide: true,
	});
}

function addBulkButton(frm) {
	if (!(frm.doc.items && frm.doc.items.length)) return;
	frm.add_custom_button(
		__("Item Label Print"),
		async () => showBulkDialog(frm, await getLabelFormat()),
		__("Print")
	);
}

// ── Per-row inline grid ───────────────────────────────────────────────────────
//
// Root causes fixed here:
//
// 1. Button static-area is empty in data rows — Frappe only puts the label in
//    the column header. We inject the emoji ourselves after every grid.refresh.
//
// 2. jQuery delegation from grid.wrapper fires AFTER Frappe's .grid-row popup
//    handler because delegation executes when the event reaches the attachment
//    point (wrapper), not the matched element. Fix: bind directly on each cell
//    so stopPropagation() cancels bubbling before it reaches .grid-row.
//
// 3. The heading row is also a .grid-row but has no data-name attribute. Using
//    .grid-row[data-name] as the selector excludes the header from injection
//    and ensures we always find a valid row when reading item_code.

function bindGridPrintClick(frm, fieldname, childDt) {
	const grid = frm.fields_dict[fieldname]?.grid;
	if (!grid || grid._ee_print_bound) return;
	grid._ee_print_bound = true;

	function injectIcons() {
		// .grid-row[data-name] excludes the heading row (which has no data-name)
		grid.wrapper
			.find(".grid-row[data-name] [data-fieldname='ee_print_label']")
			.each(function () {
				const $cell = $(this);
				const $staticArea = $cell.find(".static-area");

				if (!$staticArea.text().trim()) $staticArea.text("🖨️");
				$staticArea.css("cursor", "pointer");

				// Direct binding on the cell fires at cell level in the bubble chain,
				// before the event reaches Frappe's .grid-row open-popup handler.
				$cell.off("click.ee_print").on("click.ee_print", async function (e) {
					e.stopPropagation();
					e.preventDefault();
					const rowName = $(this).closest(".grid-row[data-name]").attr("data-name");
					const row = rowName && (locals[childDt] || {})[rowName];
					if (row?.item_code) openPrintview(row.item_code, await getLabelFormat());
				});
			});
	}

	// Patch grid.refresh so icons + handlers survive every re-render
	const _origRefresh = grid.refresh.bind(grid);
	grid.refresh = function (...args) {
		const r = _origRefresh(...args);
		injectIcons();
		return r;
	};

	injectIcons();

	// Alt+Ctrl+P on a focused/selected grid row prints that row's item
	$(document).off("keydown.ee_print_row").on("keydown.ee_print_row", async function (e) {
		if (!e.altKey || !e.ctrlKey || e.key !== "p") return;
		// Find which grid row is currently active/open
		const $activeRow = grid.wrapper.find(".grid-row.grid-row-open, .grid-row.editable-row").first();
		const rowName = $activeRow.attr("data-name");
		const row = rowName && (locals[childDt] || {})[rowName];
		if (row?.item_code) {
			e.preventDefault();
			openPrintview(row.item_code, await getLabelFormat());
		}
	});
}

// ── Popup mode (row open as dialog) ──────────────────────────────────────────
//
// frappe.ui.form.on fires for EVERY keyboard navigation event that passes
// through the button column (Tab/Enter moves between columns and activates
// each one).  Guard: only proceed when the row is actually open as a popup
// dialog (grid.open_grid_row is set).  Inline-grid clicks are fully handled
// by the click.ee_print handler in bindGridPrintClick above.

function isPopupOpen(frm) {
	return !!(frm.fields_dict.items?.grid?.open_grid_row);
}

frappe.ui.form.on("Stock Reconciliation Item", {
	ee_print_label: async (frm, cdt, cdn) => {
		if (!isPopupOpen(frm)) return;
		openPrintview(locals[cdt][cdn].item_code, await getLabelFormat());
	},
});

frappe.ui.form.on("Purchase Invoice Item", {
	ee_print_label: async (frm, cdt, cdn) => {
		if (!isPopupOpen(frm)) return;
		openPrintview(locals[cdt][cdn].item_code, await getLabelFormat());
	},
});

frappe.ui.form.on("Sales Invoice Item", {
	ee_print_label: async (frm, cdt, cdn) => {
		if (!isPopupOpen(frm)) return;
		openPrintview(locals[cdt][cdn].item_code, await getLabelFormat());
	},
});

frappe.ui.form.on("Stock Entry Detail", {
	ee_print_label: async (frm, cdt, cdn) => {
		if (!isPopupOpen(frm)) return;
		openPrintview(locals[cdt][cdn].item_code, await getLabelFormat());
	},
});

// ── Parent form refresh ───────────────────────────────────────────────────────

frappe.ui.form.on("Stock Reconciliation", {
	refresh(frm) {
		bindGridPrintClick(frm, "items", "Stock Reconciliation Item");
		addBulkButton(frm);
		frappe.ui.keys.add_shortcut({
			shortcut: "ctrl+shift+p",
			action: async () => showBulkDialog(frm, await getLabelFormat()),
			description: __("Item Label Print (bulk)"),
			ignore_inputs: false,
			page: frm.page,
		});
	},
});

frappe.ui.form.on("Purchase Invoice", {
	refresh(frm) {
		bindGridPrintClick(frm, "items", "Purchase Invoice Item");
		addBulkButton(frm);
		frappe.ui.keys.add_shortcut({
			shortcut: "ctrl+shift+p",
			action: async () => showBulkDialog(frm, await getLabelFormat()),
			description: __("Item Label Print (bulk)"),
			ignore_inputs: false,
			page: frm.page,
		});
	},
});

frappe.ui.form.on("Sales Invoice", {
	refresh(frm) {
		bindGridPrintClick(frm, "items", "Sales Invoice Item");
		addBulkButton(frm);
		frappe.ui.keys.add_shortcut({
			shortcut: "ctrl+shift+p",
			action: async () => showBulkDialog(frm, await getLabelFormat()),
			description: __("Item Label Print (bulk)"),
			ignore_inputs: false,
			page: frm.page,
		});
	},
});

frappe.ui.form.on("Stock Entry", {
	refresh(frm) {
		bindGridPrintClick(frm, "items", "Stock Entry Detail");
		addBulkButton(frm);
		frappe.ui.keys.add_shortcut({
			shortcut: "ctrl+shift+p",
			action: async () => showBulkDialog(frm, await getLabelFormat()),
			description: __("Item Label Print (bulk)"),
			ignore_inputs: false,
			page: frm.page,
		});
	},
});
