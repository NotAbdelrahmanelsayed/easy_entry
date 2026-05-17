# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## App Overview

`easy_entry` is a Frappe/ERPNext app that simplifies item, price, and stock management. It extends ERPNext with shortcuts for common operations: creating items with prices and initial stock in one form, managing item prices inline, detecting missing prices, and sending daily sales reports to store owners.

The app has two layers:
- **Python backend** — Frappe app under `easy_entry/` (standard double-directory layout: `easy_entry/easy_entry/`)
- **Vue SPA frontend** — source lives under `frontend/src/` (not yet built/served; intended for integration into a Vue app served at a custom route)

## Backend Commands

```bash
# After any Python or schema change:
bench --site erp.abderlahman-erp.store clear-cache

# After DocType JSON changes:
bench --site erp.abderlahman-erp.store migrate

# Build frontend assets (public/js files):
bench build --app easy_entry
```

## Architecture

### Custom DocType: `Product`
`easy_entry/easy_entry/doctype/product/product.py` — the core shortcut. On `validate`, it creates an ERPNext `Item`, sets buying/selling `Item Price` records, and creates a `Stock Reconciliation` to set initial quantity. Also generates an auto-incremented barcode (`P0001`, `P0002`, …) via the `BarcodeGenerator` singleton.

### API endpoints (`easy_entry/api/`)
`item_prices.py` — three `@frappe.whitelist()` functions for the Item Price Editor SPA:
- `get_price_lists()` — returns all enabled Price Lists
- `get_item_prices(search, price_list, limit, offset)` — paginated, searchable Item Price rows joined with Item image
- `update_item_price(name, price_list_rate)` — saves a single Item Price record

### Reports (`easy_entry/easy_entry/report/`)
All are Script Reports (Python + JS):
- **Item Price List** — shows buying/selling price per item side-by-side; supports inline editing of prices, supplier, item group, and item name directly from the report. The JS formatter renders edit controls in cells.
- **Items Missing Prices** — items with no buying or selling `Item Price`; supports filtering by which price is missing; inline "Add Price" action rendered via JS HTML column.
- **Customer Account Statement** — GL-based statement with HTML print template.

### Hooks and integrations (`hooks.py`)
- `doc_events["Item"]["after_insert"]` → `barcode_generator.generate_barcode_to_item` — auto-attaches a barcode on every new Item.
- `app_include_js` / `page_js["point-of-sale"]` → `pos_guard.js` — injected into the ERPNext desk and the legacy POS page.
- `doctype_js["Stock Settings"]` → `reorder_levels.js` — adds a button to the Stock Settings form that triggers `reorder_levels.set_missing_reorder_levels()`.
- `scheduler_events["daily"]` → `tasks/daily_owner_report.send_daily_owner_report` — emails Store Owner users a sold-items summary.

### Public JS (`easy_entry/public/js/`)
- `pos_guard.js` — idle-refocus helper injected into both the Frappe desk and the `pos_next` SPA (via manual injection in `pos_next/www/pos.html`). Must be re-injected after every `bench build` or `bench update` on pos_next.
- `reorder_levels.js` — Stock Settings form button that calls the whitelist API.
- `barcode_generator.js` — Item form customization for barcode generation.
- `pos_shortcuts.js` — keyboard shortcuts for POS.

### Utilities
- `price_warnings.py:warn_missing_prices(doc, method)` — fires on Purchase Invoice / Sales Invoice validate (wired in hooks) to show an orange warning when any line item lacks a buying or selling price.
- `reorder_levels.py` — calculates reorder level and qty from 90-day consumption (`LOOKBACK_DAYS = 90`, `SAFETY_STOCK_FACTOR = 2`); called from the Stock Settings button.
- `overrides/reorder_item.py` — overrides ERPNext's auto-reorder email to send Arabic HTML template.

### Frontend SPA (`frontend/src/`)
Not yet served. Intended to become a standalone Vue 3 SPA:
- `frontend/src/pages/ItemPriceEditor.vue` — full Item Price Editor: searchable paginated table with inline price editing, per-row save and batch Save All. Calls `easy_entry.api.item_prices.*` via `createResource` (frappe-ui pattern).
- `frontend/src/router.js` — router snippet; register the `/price-editor` route pointing to `ItemPriceEditor.vue`.

When setting up the Vue SPA, the entry point should use `createWebHistory` with whatever base path is configured in `www/`. The component uses `frappe-ui`'s `createResource` for API calls and `useToast` for notifications — both are standard frappe-ui composables.

## Key Domain Rules

- **Barcode format**: `P` prefix + zero-padded integer (e.g. `P0042`). Controlled by the `BarcodeGenerator` singleton doctype. The `Product` doctype uses its own incremental generator (`BARCODE_PREFIX = "P"`, `BARCODE_PAD = 4`) in `product.py`.
- **Price lists**: The app assumes `Standard Buying` and `Standard Selling` are the canonical price lists. Several places hardcode these names — `price_warnings.py`, `items_missing_prices.py`, `item_price_list.py`.
- **`frappe.db.commit()`**: All whitelist API functions that write data call `frappe.db.commit()` explicitly rather than relying on the request lifecycle.
- **Store Owner role**: Defined in `fixtures/role.json` and used by `daily_owner_report.py` to determine email recipients.
