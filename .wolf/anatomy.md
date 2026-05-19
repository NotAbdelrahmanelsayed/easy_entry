# anatomy.md

> Auto-maintained by OpenWolf. Last scanned: 2026-05-19T07:05:41.111Z
> Files: 90 tracked | Anatomy hits: 0 | Misses: 0

## ../../../../../tmp/ee-shot/

- `diag.mjs` — Declares EXE (~312 tok)
- `interact.mjs` — API routes: POST (1 endpoints) (~448 tok)
- `save-test.mjs` — API routes: POST (1 endpoints) (~285 tok)
- `shot.mjs` — API routes: POST (1 endpoints) (~364 tok)
- `verify-filters.mjs` — API routes: POST (1 endpoints) (~367 tok)

## ../../../.claude/plans/

- `failed-to-load-items-warm-puddle.md` — Fix: "Failed to load items" on /item-manager/ for logged-in users (~1009 tok)
- `there-is-a-report-bright-castle.md` — Plan: Item Manager SPA — first page of the easy_entry second interface (~1889 tok)

## ../../../.claude/projects/-home-frappe-frappe-bench-16-apps-easy-entry/memory/

- `item-manager-spa.md` (~299 tok)
- `MEMORY.md` — Memory Index (~97 tok)
- `stock-reconciliation-expense-account.md` (~177 tok)
- `ui-work-screenshot-verify.md` (~225 tok)

## ./

- `.editorconfig` — Editor configuration (~109 tok)
- `.eslintrc` (~671 tok)
- `.gitignore` — Git ignore rules (~17 tok)
- `.pre-commit-config.yaml` (~506 tok)
- `CLAUDE.md` — OpenWolf (~2058 tok)
- `license.txt` (~268 tok)
- `pyproject.toml` — Python project configuration (~437 tok)
- `README.md` — Project documentation (~172 tok)

## .claude/

- `settings.json` (~441 tok)

## .claude/rules/

- `openwolf.md` (~313 tok)

## docs/superpowers/specs/

- `2026-05-19-item-manager-filters-design.md` — Item Manager — More Filters + Searchable Supplier Filter (~520 tok)

## easy_entry/

- `__init__.py` (~63 tok)
- `hooks.py` — Declares views (~1787 tok)
- `modules.txt` (~3 tok)
- `patches.txt` (~84 tok)
- `rename_itemcode_with_names.py` — bench console (~760 tok)

## easy_entry/api/

- `__init__.py` (~0 tok)
- `item_manager.py` — Whitelisted endpoints for the Item Manager SPA. (~3037 tok)
- `item_prices.py` — get_price_lists, get_item_prices, update_item_price (~467 tok)
- `test_item_manager.py` — Integration tests for the Item Manager API. (~2946 tok)

## easy_entry/config/

- `__init__.py` (~0 tok)

## easy_entry/easy_entry/

- `__init__.py` (~0 tok)
- `price_warnings.py` — warn_missing_prices (~316 tok)
- `reorder_levels.py` — set_missing_reorder_levels, update_all_reorder_levels (~2161 tok)

## easy_entry/easy_entry/doctype/

- `__init__.py` (~0 tok)

## easy_entry/easy_entry/doctype/barcode_generator/

- `__init__.py` (~16 tok)
- `barcode_generator.js` — For license information, please see license.txt (~52 tok)
- `barcode_generator.json` (~331 tok)
- `barcode_generator.py` — For license information, please see license.txt (~398 tok)
- `test_barcode_generator.py` — See license.txt (~53 tok)

## easy_entry/easy_entry/doctype/product/

- `__init__.py` (~0 tok)
- `product.js` — For license information, please see license.txt (~50 tok)
- `product.json` (~841 tok)
- `product.py` — For license information, please see license.txt (~1528 tok)
- `test_product.py` — See license.txt (~50 tok)

## easy_entry/easy_entry/print_format/easy_entry_purchase_invoice/

- `easy_entry_purchase_invoice.json` (~4637 tok)

## easy_entry/easy_entry/print_format/easy_entry_sales_invoice/

- `easy_entry_sales_invoice.json` (~4618 tok)

## easy_entry/easy_entry/report/

- `__init__.py` (~0 tok)

## easy_entry/easy_entry/report/customer_account_statement/

- `__init__.py` (~0 tok)
- `customer_account_statement.html` (~1421 tok)
- `customer_account_statement.js` (~190 tok)
- `customer_account_statement.json` (~116 tok)
- `customer_account_statement.py` — execute, validate_filters, get_columns, get_data + 5 more (~2708 tok)

## easy_entry/easy_entry/report/items_missing_prices/

- `__init__.py` (~0 tok)
- `items_missing_prices.js` (~908 tok)
- `items_missing_prices.json` (~107 tok)
- `items_missing_prices.py` — execute, get_columns, get_data, add_item_price (~958 tok)

## easy_entry/easy_entry/workspace/easy_entry/

- `easy_entry.json` (~759 tok)

## easy_entry/fixtures/

- `role.json` (~26 tok)

## easy_entry/overrides/

- `__init__.py` (~0 tok)
- `reorder_item.py` — send_email_notification (~154 tok)

## easy_entry/patches/

- `__init__.py` (~0 tok)
- `set_default_print_formats.py` — execute (~74 tok)

## easy_entry/public/

- `.gitkeep` (~0 tok)

## easy_entry/public/js/

- `barcode_generator.js` (~82 tok)
- `pos_guard.js` — pos_guard.js — idle refocus for item search (robust across POS variants) (~1019 tok)
- `pos_shortcuts.js` (~32 tok)
- `reorder_levels.js` — Declares s (~928 tok)

## easy_entry/tasks/

- `__init__.py` (~0 tok)
- `daily_owner_report.py` — send_daily_owner_report (~455 tok)

## easy_entry/templates/

- `__init__.py` (~0 tok)

## easy_entry/templates/emails/

- `daily_owner_report_ar.html` (~1052 tok)
- `reorder_item_ar.html` (~926 tok)

## easy_entry/templates/pages/

- `__init__.py` (~0 tok)

## easy_entry/translations/

- `ar.csv` (~266 tok)

## easy_entry/www/

- `item_manager.py` — www controller: injects csrf_token into boot, redirects Guest to /login (~150 tok)

## frontend/

- `index.html` — Item Manager (~88 tok)
- `package.json` — Node.js package manifest (~143 tok)
- `postcss.config.js` (~22 tok)
- `tailwind.config.js` — /*.{vue,js,ts,jsx,tsx}", (~94 tok)
- `vite.config.js` — Builds to ../easy_entry/public/frontend and writes the SPA host page to (~214 tok)

## frontend/src/

- `App.vue` — Vue: setup (~267 tok)
- `index.css` — Styles: 4 rules (~35 tok)
- `main.js` — Route all frappe-ui resources through Frappe's request layer (handles CSRF). (~145 tok)
- `router.js` — Declares routes (~133 tok)
- `translation.js` — Minimal translation shim. Frappe's desk exposes a full `__()`; the SPA only (~146 tok)

## frontend/src/composables/

- `useToast.js` — A tiny self-contained toast store. Shared module state means every caller of (~222 tok)

## frontend/src/pages/

- `ItemManager.vue` — Vue component (~6738 tok)
- `ItemPriceEditor.vue` — Vue: ItemManager, setup (~3075 tok)
