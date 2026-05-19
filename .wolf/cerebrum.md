# Cerebrum

> OpenWolf's learning memory. Updated automatically as the AI learns from interactions.
> Do not edit manually unless correcting an error.
> Last updated: 2026-05-18

## User Preferences

<!-- How the user likes things done. Code style, tools, patterns, communication. -->

## Key Learnings

- **Project:** easy_entry
- **Description:** Add Items, Prices, Stock and Purchase invoices with ease in a single DocType
- The app is NOT installed on a dedicated site; local testing uses the `capital` site (has ERPNext). Dev web server runs on port 8002 — `http://capital:8002`.
- The Item Manager SPA lives in `frontend/` (Vue 3 + Vite + frappe-ui). Build with `cd frontend && npm run build`; it writes `easy_entry/www/item-manager.html` and assets to `public/frontend/`. Served at `/item-manager`.
- Stock Reconciliation's "Difference Account" field is named `expense_account` (not `difference_account`). For opening-stock items it must be an Asset/Liability account — use the company's "Temporary Opening" account.
- The Barcode Generator singleton needs `prefix` configured, otherwise every new Item insert fails with "Prefix is required" (the `Item.after_insert` hook calls it).

## Do-Not-Repeat

<!-- Mistakes made and corrected. Each entry prevents the same mistake recurring. -->
<!-- Format: [YYYY-MM-DD] Description of what went wrong and what to do instead. -->
- [2026-05-18] Stock Reconciliation difference account: set `sr.expense_account`, NOT `sr.difference_account` (that field does not exist).
- [2026-05-18] In a `.vue` file, always close `<script setup>` with `</script>` — a missing close fails the Vite build with a misleading "Element is missing end tag".

## Decision Log

- [2026-05-18] Item Manager qty edits create a DRAFT Stock Reconciliation (unsubmitted) so a human reviews before stock ledger entries are posted. Supplier is read/written as the first `supplier_items` (Item Supplier) row — no schema change. Export is XLSX-only via `frappe.utils.xlsxutils.make_xlsx`.

<!-- Significant technical decisions with rationale. Why X was chosen over Y. -->
