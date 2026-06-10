# Cerebrum

> OpenWolf's learning memory. Updated automatically as the AI learns from interactions.
> Do not edit manually unless correcting an error.
> Last updated: 2026-05-18

## User Preferences

<!-- How the user likes things done. Code style, tools, patterns, communication. -->
- When adding any feature, also add a keyboard shortcut if it would improve UX — do this proactively as part of the feature, without being asked.

## Key Learnings

- **Per-row child-table actions** in easy_entry use a Custom Button field (`fieldtype: Button`, `in_list_view: 1`, `columns: 1`, `print_hide: 1`) handled via `frappe.ui.form.on("<Child Doctype>", "fieldname", fn)`. The handler receives `(frm, cdt, cdn)` and reads the row with `locals[cdt][cdn]`. Custom fields ship via `easy_entry/fixtures/custom_field.json`; the fixtures list in hooks.py uses `{"dt": "Custom Field", "filters": [["name", "like", "%-ee_%"]]}`.
- **Configurable settings** for the app are stored on existing ERPNext singletons (e.g., Stock Settings) via Custom Field fixtures — no new Singleton DocType needed. Reads use `frappe.db.get_single_value("Stock Settings", "fieldname")`.
- **Project:** easy_entry
- **Description:** Add Items, Prices, Stock and Purchase invoices with ease in a single DocType
- The app is NOT installed on a dedicated site; local testing uses the `capital` site (has ERPNext). Dev web server runs on port 8002 — `http://capital:8002`.
- The Item Manager SPA lives in `frontend/` (Vue 3 + Vite + frappe-ui). Build with `cd frontend && npm run build`; it writes `easy_entry/www/item-manager.html` and assets to `public/frontend/`. Served at `/item-manager`.
- Stock Reconciliation's "Difference Account" field is named `expense_account` (not `difference_account`). For opening-stock items it must be an Asset/Liability account — use the company's "Temporary Opening" account.
- The Barcode Generator singleton needs `prefix` configured, otherwise every new Item insert fails with "Prefix is required" (the `Item.after_insert` hook calls it).
- **Print Format `css` field** is injected as a separate `<style>` block after the inline HTML `<style>`. For label formats, leave `css: ""` and put ALL styles inside the `html` field only. The old `50 * 25` had `direction:rtl` in `css` which broke English items and `font-size:13px` that overrode the intended 8pt.
- **SVG `height: 100%` inside a flex item collapses to 0 in old WebKit** (wkhtmltopdf). The barcode was completely invisible in the old format for this reason. Always use explicit `height: NNmm` on `.barcode svg`.
- **wkhtmltoimage ≠ wkhtmltopdf** for label testing: `wkhtmltoimage` ignores `pdfkit-page-height` meta tags and renders natural content height. Screenshots show extra whitespace below the barcode. The real PDF (wkhtmltopdf) correctly clips to the declared page height. Verify label designs in Frappe's actual printview.
- **Extra query params on `/printview` are fragile transport**: the printview "Get PDF" button rebuilds the URL with only doctype/name/format/letterhead, dropping custom params like `supplier_code`. Never rely on a URL param as the ONLY source for data a print format needs — give the template a server-side fallback (jinja method hook). Pattern: `{%- set x = frappe.form_dict.get('param','') or my_jinja_helper(doc.name) %}`.
- **Thermal label printers are 1-bit**: mid-gray text (e.g. `color: #555`) at 6pt dithers to near-invisible dots on the physical label. Always use pure black (`#000`) for anything that must be legible on a printed label.
- **Supplier codes** (`ee_supplier_code`): 3 random uppercase letters from A-Z minus I/O (confusable with 1/0), generated on Supplier `after_insert`; labels fall back to the item's first Item Supplier row via the `item_supplier_code` jinja method when no `supplier_code` param is passed.
- **In `bench console` (piped input)**, top-level imports don't survive into later statements reliably; jinja env (`frappe.local.jenv`) caches the `form_dict` reference at first render — set `frappe.local.jenv = None` between renders when testing print formats with different `form_dict` values. Run multi-statement test scripts via `exec(open('/tmp/x.py').read(), {})`.

## Do-Not-Repeat

<!-- Mistakes made and corrected. Each entry prevents the same mistake recurring. -->
<!-- Format: [YYYY-MM-DD] Description of what went wrong and what to do instead. -->
- [2026-05-18] Stock Reconciliation difference account: set `sr.expense_account`, NOT `sr.difference_account` (that field does not exist).
- [2026-05-21] `frappe.ui.form.on(childDoctype, "buttonField", fn)` does NOT fire when the button is clicked in the **inline grid** (static row). It only fires when the row is open as a popup. For always-clickable per-row buttons use jQuery delegation on `grid.wrapper.on("click.ns", "[data-fieldname='fieldname']", fn)` instead — this fires at DOM level regardless of Frappe form state.
- [2026-05-18] In a `.vue` file, always close `<script setup>` with `</script>` — a missing close fails the Vite build with a misleading "Element is missing end tag".
- [2026-05-22] Print Format `css` field: NEVER put styles in `css` for label formats — it overrides inline styles with wrong `direction:rtl` and font-size. Set `css: ""` and style inside `html`.
- [2026-05-22] SVG `height: 100%` in flex container: collapses to 0 in wkhtmltopdf's old WebKit — use explicit `height: 11mm` on `.barcode svg`, never `100%`.
- [2026-05-22] When a patch depends on a custom field column that may not exist yet (fixtures run after patches in bench migrate), add the column explicitly: check with `frappe.db.has_column("Supplier", "fieldname")` and add with `frappe.db.sql("ALTER TABLE ... ADD COLUMN ...")`. Neither `frappe.db.column_exists` nor `frappe.db.add_column` exist in this Frappe version.
- [2026-05-22] Custom field fixture entries MUST include a `name` field (e.g., `"name": "Supplier-ee_supplier_code"`); omitting it causes `KeyError: 'name'` during `sync_fixtures`.

## Decision Log

- [2026-05-18] Item Manager qty edits create a DRAFT Stock Reconciliation (unsubmitted) so a human reviews before stock ledger entries are posted. Supplier is read/written as the first `supplier_items` (Item Supplier) row — no schema change. Export is XLSX-only via `frappe.utils.xlsxutils.make_xlsx`.
- [2026-05-19] Removed the Item Price Editor SPA page + `item_prices.py` API entirely — redundant with Item Manager's inline buying/selling price editing. The feature was fully isolated (no hooks, no tests, no cross-references), so removal was a clean delete.
- [2026-05-19] Stock Count feature uses a dedicated `EE Stock Count` / `EE Stock Count Line` DocType pair as the session store — NOT a draft Stock Reconciliation as the session. ERPNext's `Stock Reconciliation.validate()` unconditionally calls `remove_items_with_no_change()`, which prunes no-difference lines and raises `EmptyStockReconciliationItemsError` on an empty SR — that would silently drop counted-but-unchanged lines mid-session. The SR is built only at `finish_session`, from lines where `counted_qty != system_qty`; `build_reconciliation` catches `EmptyStockReconciliationItemsError` and returns `None`. Traceability via the `EE Stock Count.stock_reconciliation` link. The originally-planned `Stock Reconciliation` custom-field fixture was dropped.

<!-- Significant technical decisions with rationale. Why X was chosen over Y. -->
