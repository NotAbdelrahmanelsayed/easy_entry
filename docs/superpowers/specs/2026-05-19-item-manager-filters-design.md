# Item Manager — More Filters + Searchable Supplier Filter

**Date:** 2026-05-19
**Status:** Approved

## Goal

Add three filters to the Item Manager SPA toolbar (supplier, stock status,
price status) and make the supplier filter searchable.

## Backend — `easy_entry/api/item_manager.py`

`_items_query()` currently returns a WHERE clause referencing only `tabItem i`,
and the COUNT query runs without joins. The new filters sit on joined data
(supplier, on-hand qty, prices), so the FROM + JOIN block becomes shared
between the list query and the COUNT query — keeping `total` correct under
filtering.

`get_items()` and `export_items_xlsx()` gain three optional params:

| Param          | Values                                                        | SQL condition |
|----------------|---------------------------------------------------------------|---------------|
| `supplier`     | a Supplier name                                               | `sup.supplier = %(supplier)s` |
| `stock_status` | `in_stock` / `out_of_stock` / `negative`                      | `COALESCE(b.qty,0)` `> 0` / `= 0` / `< 0` |
| `price_status` | `missing_buying` / `missing_selling` / `missing_any` / `has_both` | `bp/sp.price_list_rate IS [NOT] NULL` |

Unknown / empty values are ignored (no condition added).

## Frontend — `frontend/src/pages/ItemManager.vue`

Toolbar gains three controls beside the item-group filter:

- **Supplier** — searchable dropdown (frappe-ui `Autocomplete`) over the
  already-loaded supplier list. The per-row supplier `<select>` is unchanged.
- **Stock status** — plain `<select>`, 4 options incl. "All".
- **Price status** — plain `<select>`, 5 options incl. "All".

All three call `reloadFirstPage()` on change and feed `items.makeParams()` and
`exportSheet()`.

## Tests — `easy_entry/api/test_item_manager.py`

New cases per filter plus a combined-filter case, asserting both `rows` and
`total`. Self-cleaning, matching the existing suite's conventions.

## Out of scope

- Price-range filter (deferred).
- Making the per-row supplier picker searchable.
