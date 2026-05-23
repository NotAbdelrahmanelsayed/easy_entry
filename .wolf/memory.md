# Memory

> Chronological action log. Hooks and AI append to this file automatically.
> Old sessions are consolidated by the daemon weekly.
| 17:56 | Created ../../../.claude/plans/there-is-a-report-bright-castle.md | — | ~2015 |

## Session: 2026-05-18 17:56

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 18:03 | Created easy_entry/api/item_manager.py | — | ~2208 |
| 18:08 | Edited easy_entry/api/item_manager.py | expanded (+11 lines) | ~314 |
| 18:09 | Edited easy_entry/api/item_manager.py | 4→4 lines | ~37 |
| 18:11 | Created frontend/package.json | — | ~143 |
| 18:11 | Created frontend/vite.config.js | — | ~214 |
| 18:11 | Created frontend/tailwind.config.js | — | ~94 |
| 18:11 | Created frontend/postcss.config.js | — | ~22 |
| 18:11 | Created frontend/index.html | — | ~88 |
| 18:11 | Created frontend/src/index.css | — | ~35 |
| 18:11 | Created frontend/src/translation.js | — | ~146 |
| 18:11 | Created frontend/src/composables/useToast.js | — | ~222 |
| 18:12 | Created frontend/src/main.js | — | ~145 |
| 18:12 | Created frontend/src/router.js | — | ~133 |
| 18:12 | Created frontend/src/App.vue | — | ~267 |
| 18:12 | Edited frontend/src/pages/ItemPriceEditor.vue | 4→4 lines | ~40 |
| 18:14 | Created frontend/src/pages/ItemManager.vue | — | ~5758 |
| 18:14 | Edited easy_entry/hooks.py | 2→7 lines | ~78 |
| 18:18 | Edited frontend/src/pages/ItemManager.vue | 3→4 lines | ~34 |
| 18:23 | Created ../../../../../tmp/ee-shot/shot.mjs | — | ~304 |
| 18:24 | Created easy_entry/api/test_item_manager.py | — | ~1699 |
| 18:25 | Created ../../../.claude/projects/-home-frappe-frappe-bench-16-apps-easy-entry/memory/item-manager-spa.md | — | ~298 |
| 18:25 | Created ../../../.claude/projects/-home-frappe-frappe-bench-16-apps-easy-entry/memory/stock-reconciliation-expense-account.md | — | ~169 |
| 18:25 | Created ../../../.claude/projects/-home-frappe-frappe-bench-16-apps-easy-entry/memory/MEMORY.md | — | ~67 |
| 18:26 | Session end: 23 writes across 20 files (item_manager.py, package.json, vite.config.js, tailwind.config.js, postcss.config.js) | 10 reads | ~28026 tok |
| 18:29 | Created ../../../../../tmp/ee-shot/shot.mjs | — | ~295 |
| 18:29 | Edited frontend/src/pages/ItemManager.vue | 14→19 lines | ~131 |
| 18:30 | Created ../../../../../tmp/ee-shot/interact.mjs | — | ~448 |
| 18:31 | Created ../../../../../tmp/ee-shot/save-test.mjs | — | ~285 |
| 18:32 | Edited easy_entry/api/test_item_manager.py | modified tearDownClass() | ~314 |
| 18:33 | Edited easy_entry/api/test_item_manager.py | modified _purge_test_data() | ~440 |

## Session 2026-05-18 — Item Manager SPA
Built the first page of easy_entry's second interface: backend API (`item_manager.py`,
6 endpoints, 17 passing tests), Vue 3 + Vite + frappe-ui build infra under `frontend/`,
and `ItemManager.vue`. Served at `/item-manager`. Tested on the `capital` site (port 8002).
Verified end-to-end via headless Chromium screenshots; fixed the Save-column dash noise.
| 18:34 | Session end: 29 writes across 22 files (item_manager.py, package.json, vite.config.js, tailwind.config.js, postcss.config.js) | 17 reads | ~31987 tok |
| 18:36 | Edited CLAUDE.md | 3→3 lines | ~80 |
| 18:36 | Edited CLAUDE.md | modified assets() | ~103 |
| 18:37 | Edited CLAUDE.md | expanded (+10 lines) | ~343 |
| 18:37 | Edited CLAUDE.md | 1→2 lines | ~73 |
| 18:37 | Edited CLAUDE.md | expanded (+6 lines) | ~441 |
| 18:37 | Edited CLAUDE.md | 1→2 lines | ~128 |
| 18:37 | Session end: 35 writes across 23 files (item_manager.py, package.json, vite.config.js, tailwind.config.js, postcss.config.js) | 18 reads | ~34629 tok |

## Session: 2026-05-19 09:10

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-19 09:12

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 09:16 | seeded school demo data (18 items, 4 groups, 4 suppliers) on `capital` | /tmp/school_demo.py | 26 items total, prices+stock verified via get_items | ~2k |
| 09:18 | Created ../../../.claude/projects/-home-frappe-frappe-bench-16-apps-easy-entry/memory/ui-work-screenshot-verify.md | — | ~219 |
| 09:21 | Edited ../../../.claude/projects/-home-frappe-frappe-bench-16-apps-easy-entry/memory/MEMORY.md | 1→2 lines | ~72 |
| 09:21 | Session end: 2 writes across 2 files (ui-work-screenshot-verify.md, MEMORY.md) | 1 reads | ~312 tok |
| 09:22 | Edited frontend/src/pages/ItemManager.vue | added 1 condition(s) | ~107 |
| 09:22 | Edited frontend/src/pages/ItemManager.vue | added 2 condition(s) | ~227 |
| 09:22 | Edited frontend/src/pages/ItemManager.vue | modified __() | ~125 |
| 09:24 | Created ../../../../../tmp/ee-shot/shot.mjs | — | ~364 |
| 09:25 | fixed "Failed to load items" — guest 403 now redirects to login | ItemManager.vue | verified via screenshots: guest->login, auth->20 rows | ~6k |
| 09:26 | Session end: 6 writes across 4 files (ui-work-screenshot-verify.md, MEMORY.md, ItemManager.vue, shot.mjs) | 4 reads | ~6987 tok |
| 09:27 | Created ../../../../../tmp/ee-shot/diag.mjs | — | ~312 |
| 09:28 | Session end: 7 writes across 5 files (ui-work-screenshot-verify.md, MEMORY.md, ItemManager.vue, shot.mjs, diag.mjs) | 4 reads | ~7321 tok |
| 09:31 | Session end: 7 writes across 5 files (ui-work-screenshot-verify.md, MEMORY.md, ItemManager.vue, shot.mjs, diag.mjs) | 4 reads | ~7321 tok |

## Session: 2026-05-19 09:33

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 09:37 | Created docs/superpowers/specs/2026-05-19-item-manager-filters-design.md | — | ~555 |
| 09:38 | Created easy_entry/api/item_manager.py | — | ~2947 |
| 09:38 | Edited easy_entry/api/test_item_manager.py | added 1 import(s) | ~55 |
| 09:39 | Edited easy_entry/api/test_item_manager.py | modified _give_stock() | ~360 |
| 09:39 | Edited easy_entry/api/test_item_manager.py | expanded (+7 lines) | ~152 |
| 09:39 | Edited easy_entry/api/test_item_manager.py | modified _codes() | ~603 |
| 09:40 | Session end: 6 writes across 3 files (2026-05-19-item-manager-filters-design.md, item_manager.py, test_item_manager.py) | 3 reads | ~15132 tok |

## Session: 2026-05-19 09:45

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 09:53 | Created ../../../.claude/plans/failed-to-load-items-warm-puddle.md | — | ~1076 |

## Session: 2026-05-19 09:54

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 09:54 | Created easy_entry/www/item-manager.py | — | ~161 |
| 09:58 | Fix CSRF: add www controller item_manager.py | easy_entry/www/item_manager.py | guest 301->/login verified | ~600 |
| 09:58 | Session end: 1 writes across 1 files (item-manager.py) | 1 reads | ~161 tok |

## Session: 2026-05-19 09:58

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 09:59 | Edited easy_entry/api/item_manager.py | expanded (+14 lines) | ~245 |
| 10:00 | Edited frontend/src/pages/ItemManager.vue | CSS: filter, hover | ~635 |
| 10:00 | Edited frontend/src/pages/ItemManager.vue | 3→6 lines | ~48 |
| 10:00 | Edited frontend/src/pages/ItemManager.vue | CSS: supplier, stock_status, price_status | ~68 |
| 10:00 | Edited frontend/src/pages/ItemManager.vue | modified reloadFirstPage() | ~98 |
| 10:01 | Edited frontend/src/pages/ItemManager.vue | CSS: supplier, stock_status, price_status | ~65 |
| 10:05 | Created ../../../../../tmp/ee-shot/verify-filters.mjs | — | ~367 |

## Session: 2026-05-19 14:58

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-19 15:00

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 15:12 | Created ../../../.claude/plans/good-work-so-far-noble-lightning.md | — | ~1476 |

## Session: 2026-05-19 15:12

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 15:14 | Edited easy_entry/www/easy.py | "/login?redirect-to=/item-" → "/login?redirect-to=/easy" | ~20 |
| 15:14 | Edited easy_entry/hooks.py | 4→4 lines | ~44 |
| 15:14 | Edited frontend/vite.config.js | 2→2 lines | ~44 |
| 15:14 | Edited frontend/vite.config.js | "../easy_entry/www/item-ma" → "../easy_entry/www/easy.ht" | ~14 |
| 15:14 | Created frontend/src/router.js | — | ~158 |
| 15:15 | Created frontend/src/features.js | — | ~337 |
| 15:15 | Created frontend/src/components/AppShell.vue | — | ~342 |
| 15:15 | Created frontend/src/pages/Dashboard.vue | — | ~356 |
| 15:15 | Edited frontend/src/App.vue | 3→5 lines | ~19 |
| 15:15 | Edited frontend/src/App.vue | added 1 import(s) | ~27 |
| 15:15 | Edited frontend/src/pages/ItemManager.vue | "min-h-screen bg-gray-50 f" → "flex-1 min-h-0 bg-gray-50" | ~15 |
| 15:15 | Edited frontend/src/pages/ItemPriceEditor.vue | "min-h-screen bg-gray-50 f" → "flex-1 min-h-0 bg-gray-50" | ~15 |
| 15:16 | Created frontend/design.md | — | ~1281 |
| 15:16 | Edited CLAUDE.md | inline fix | ~58 |
| 15:16 | Edited CLAUDE.md | inline fix | ~20 |
| 15:17 | Edited CLAUDE.md | inline fix | ~34 |
| 15:17 | Edited CLAUDE.md | 5→9 lines | ~341 |
| 15:17 | Edited CLAUDE.md | inline fix | ~50 |
| 15:19 | Created ../../../.claude/projects/-home-frappe-frappe-bench-16-apps-easy-entry/memory/local-dev-site.md | — | ~155 |
| 15:20 | Edited ../../../.claude/projects/-home-frappe-frappe-bench-16-apps-easy-entry/memory/MEMORY.md | 1→2 lines | ~68 |
| 15:22 | Edited frontend/index.html | inline fix | ~8 |
| 15:26 | Created ../../../.claude/projects/-home-frappe-frappe-bench-16-apps-easy-entry/memory/local-dev-credentials.md | — | ~80 |
| 15:26 | Edited ../../../.claude/projects/-home-frappe-frappe-bench-16-apps-easy-entry/memory/MEMORY.md | 1→2 lines | ~59 |
| 15:27 | Created ../../../../../tmp/ee-verify/verify.mjs | — | ~493 |
| 15:28 | Edited ../../../../../tmp/ee-verify/verify.mjs | inline fix | ~11 |
| 15:30 | Created ../../../../../tmp/ee-verify/verify.mjs | — | ~488 |
| 15:32 | Session end: 26 writes across 17 files (easy.py, hooks.py, vite.config.js, router.js, features.js) | 15 reads | ~19468 tok |

## Session: 2026-05-19 15:34

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 15:37 | Created ../../../.claude/plans/item-price-editor-is-unified-pixel.md | — | ~765 |

## Session: 2026-05-19 15:37

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 15:38 | Edited frontend/src/router.js | 11→6 lines | ~32 |
| 15:38 | Edited frontend/src/features.js | removed 10 lines | ~9 |
| 15:38 | Edited easy_entry/api/item_manager.py | 5→5 lines | ~41 |
| 15:38 | Edited frontend/design.md | 2→1 lines | ~18 |
| 15:38 | Edited frontend/design.md | 2→2 lines | ~34 |
| 15:39 | Edited CLAUDE.md | 7→2 lines | ~32 |
| 15:39 | Edited CLAUDE.md | inline fix | ~18 |
| 15:39 | Edited CLAUDE.md | — | ~0 |

## Session: 2026-05-19 15:39

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 15:40 | Removed Item Price Editor feature (redundant with Item Manager) | ItemPriceEditor.vue, item_prices.py, router.js, features.js, CLAUDE.md, design.md | done, rebuilt | ~3k |
| 15:46 | Created ../../../.claude/plans/we-need-to-create-tingly-scott.md | — | ~2261 |

## Session: 2026-05-19 15:46

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 15:49 | Created easy_entry/api/_stock.py | — | ~708 |
| 15:49 | Edited easy_entry/api/item_manager.py | added 1 import(s) | ~48 |
| 15:49 | Edited easy_entry/api/item_manager.py | reduced (-19 lines) | ~112 |
| 15:55 | Created easy_entry/easy_entry/doctype/ee_stock_count_line/ee_stock_count_line.json | — | ~416 |
| 15:55 | Created easy_entry/easy_entry/doctype/ee_stock_count/ee_stock_count.json | — | ~690 |
| 15:55 | Created easy_entry/easy_entry/doctype/ee_stock_count_line/ee_stock_count_line.py | — | ~98 |
| 15:56 | Created easy_entry/easy_entry/doctype/ee_stock_count/ee_stock_count.py | — | ~933 |
| 15:57 | Created easy_entry/api/stock_count.py | — | ~1448 |
| 15:58 | Created easy_entry/api/test_stock_count.py | — | ~2434 |
| 15:59 | Edited frontend/src/router.js | expanded (+11 lines) | ~104 |
| 15:59 | Edited frontend/src/features.js | expanded (+7 lines) | ~160 |
| 15:59 | Edited frontend/package.json | 5→6 lines | ~38 |
| 16:00 | Created frontend/src/components/BarcodeScanner.vue | — | ~595 |
| 16:00 | Created frontend/src/pages/StockCount.vue | — | ~1573 |

## Session: 2026-05-19 16:02

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 16:02 | Created frontend/src/pages/StockCountSession.vue | — | ~4113 |
| 16:02 | Session end: 1 writes across 1 files (StockCountSession.vue) | 0 reads | ~4406 tok |

## Session: 2026-05-19 17:34

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-19 17:36

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 17:52 | Built SPA, migrated capital, ran Stock Count tests, screenshot-verified mobile flow | frontend, EE Stock Count doctypes | build OK; 19/19 tests pass; scan→count→difference flow verified | ~9k |

## Session: 2026-05-19 19:24

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-19 19:31

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-19 19:31

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 19:36 | Created ../../../.claude/plans/plan-for-better-experience-wild-orbit.md | — | ~2364 |

## Session: 2026-05-19 19:39

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-19 19:39

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-19 19:40

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-19 19:40

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-19 19:40

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-19 19:40

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-19 19:40

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-19 19:40

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-19 19:41

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-19 19:41

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-19 19:42

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 19:43 | Edited easy_entry/api/item_manager.py | modified set_item_qty() | ~116 |
| 19:43 | Edited easy_entry/api/item_manager.py | modified cint() | ~62 |
| 19:43 | Edited easy_entry/api/stock_count.py | inline fix | ~10 |
| 19:43 | Edited easy_entry/api/stock_count.py | modified search_items() | ~257 |
| 19:43 | Edited easy_entry/api/test_item_manager.py | modified test_set_item_qty_submitted() | ~131 |
| 19:45 | Edited easy_entry/api/test_stock_count.py | modified test_search_items_by_partial_name() | ~342 |
| 20:30 | Created frontend/src/composables/useModalShortcuts.js | — | ~312 |
| 20:30 | Created frontend/src/components/ShortcutsModal.vue | — | ~577 |
| 20:30 | Edited frontend/src/components/AppShell.vue | CSS: hover, hover, ShortcutsModal | ~448 |
| 20:31 | Edited frontend/src/pages/ItemManager.vue | CSS: toggle | ~608 |
| 20:31 | Edited frontend/src/pages/ItemManager.vue | modified __() | ~202 |
| 20:31 | Edited frontend/src/pages/ItemManager.vue | CSS: sm | ~65 |
| 20:31 | Edited frontend/src/pages/ItemManager.vue | 4→5 lines | ~35 |
| 20:31 | Edited frontend/src/pages/ItemManager.vue | added 1 import(s) | ~64 |
| 20:31 | Edited frontend/src/pages/ItemManager.vue | 2→3 lines | ~23 |
| 20:32 | Edited frontend/src/pages/ItemManager.vue | CSS: submit, submit, 1 | ~275 |
| 20:32 | Edited frontend/src/pages/ItemManager.vue | added optional chaining | ~361 |
| 20:32 | Edited frontend/src/pages/StockCountSession.vue | added 1 import(s) | ~88 |
| 20:32 | Edited frontend/src/pages/StockCountSession.vue | CSS: matches | ~52 |
| 20:32 | Edited frontend/src/pages/StockCountSession.vue | CSS: path, Fallback, query | ~405 |
| 20:32 | Edited frontend/src/pages/StockCountSession.vue | CSS: onSave, onCancel, onCancel | ~86 |
| 20:33 | Edited frontend/src/pages/StockCountSession.vue | 12→12 lines | ~123 |
| 20:33 | Edited frontend/src/pages/StockCountSession.vue | 5→8 lines | ~47 |
| 20:33 | Edited frontend/src/pages/StockCountSession.vue | CSS: hover, hover | ~528 |

| 20:05 | UX+shortcuts: submit toggle, useModalShortcuts, ShortcutsModal, scan name-search | item_manager.py, stock_count.py, AppShell.vue, ItemManager.vue, StockCountSession.vue, +2 new | 51 tests pass, build clean | ~9k |
| 20:35 | Session end: 24 writes across 9 files (item_manager.py, stock_count.py, test_item_manager.py, test_stock_count.py, useModalShortcuts.js) | 9 reads | ~26574 tok |

## Session: 2026-05-19 20:42

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-19 20:46

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 20:46 | Edited frontend/src/pages/ItemManager.vue | CSS: active, disabled | ~271 |
| 20:46 | Edited frontend/src/pages/ItemManager.vue | CSS: weigh | ~166 |
| 20:49 | Edited frontend/src/pages/ItemManager.vue | added 2 condition(s) | ~99 |
| 20:49 | Created ../../../.claude/plans/delegated-plotting-chipmunk.md | — | ~516 |
| 20:51 | Add Refresh button to Item Manager | frontend/src/pages/ItemManager.vue | built OK | ~3k |
| 20:51 | Session end: 4 writes across 2 files (ItemManager.vue, delegated-plotting-chipmunk.md) | 1 reads | ~8751 tok |

## Session: 2026-05-19 20:52

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 20:56 | Created ../../../.claude/plans/add-to-the-project-s-encapsulated-engelbart.md | — | ~831 |
| 20:57 | Edited frontend/src/pages/ItemManager.vue | CSS: Shortcuts | ~41 |
| 20:57 | Edited frontend/src/pages/ItemManager.vue | added 3 condition(s) | ~178 |
| 20:57 | Created ../../../.claude/projects/-home-frappe-frappe-bench-16-apps-easy-entry/memory/shortcut-on-new-features.md | — | ~231 |
| 20:57 | Edited ../../../.claude/projects/-home-frappe-frappe-bench-16-apps-easy-entry/memory/MEMORY.md | 1→2 lines | ~60 |
| 20:59 | Added F4 (focus search) + F5 (refresh) shortcuts to Item Manager; recorded "add shortcut on new features" preference | ItemManager.vue, cerebrum.md | built OK | ~3k |
| 20:59 | Session end: 5 writes across 4 files (add-to-the-project-s-encapsulated-engelbart.md, ItemManager.vue, shortcut-on-new-features.md, MEMORY.md) | 2 reads | ~9384 tok |

## Session: 2026-05-21 09:54

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 10:03 | Created ../../../.claude/plans/can-you-see-this-giggly-hanrahan.md | — | ~1589 |

## Session: 2026-05-21 10:04

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 10:06 | Created easy_entry/fixtures/custom_field.json | — | ~473 |
| 10:06 | Created easy_entry/public/js/label_printer.js | — | ~911 |
| 10:07 | Edited easy_entry/hooks.py | 4→8 lines | ~89 |
| 10:07 | Edited easy_entry/hooks.py | 1→4 lines | ~43 |
| 10:10 | Implemented per-row label print feature: custom_field.json (5 fields), label_printer.js, hooks.py doctype_js + fixtures | easy_entry/fixtures/custom_field.json, easy_entry/public/js/label_printer.js, easy_entry/hooks.py | success — all 5 custom fields confirmed in DB | ~1200 |
| 10:11 | Session end: 4 writes across 3 files (custom_field.json, label_printer.js, hooks.py) | 3 reads | ~3322 tok |
| 10:20 | Created easy_entry/public/js/label_printer.js | — | ~1235 |
| 10:21 | Session end: 5 writes across 3 files (custom_field.json, label_printer.js, hooks.py) | 4 reads | ~5468 tok |
| 10:24 | designqc: captured 2 screenshots (24KB, ~5000 tok) | /app/stock-reconciliation/MAT-RECO-2026-00002 | ready for eval | ~0 |
| 10:31 | Created easy_entry/public/js/label_printer.js | — | ~1464 |
| 10:34 | Created easy_entry/public/js/label_printer.js | — | ~1509 |
| 10:38 | Created easy_entry/public/js/label_printer.js | — | ~1896 |
| 19:52 | patched trigger_print_script in __init__.py + code128_svg Jinja global + updated 50*25 print format | __init__.py, hooks.py, utils/barcode.py, DB | committed 0fb49e1 | ~2800 |

## Session 2026-05-22 — Print Format Redesign

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 15:54 | Diagnosed `50 * 25` format — barcode invisible (SVG height:100% collapses), css field conflicts direction:rtl | print_format.json | Root cause found | ~800 |
| 15:54 | Rewrote `50 * 25` HTML: cleared css field, 9pt font, explicit height:11mm on SVG, name-wrap vertical centering | print_format.json | Barcode now renders | ~400 |
| 15:54 | Created `38 * 25` format: 38mm width, 8.5pt font, 36mm barcode | print_format.json | New format working | ~400 |
| 15:54 | Loaded both formats into site via frappe console db_set | erp.abderlahman-erp.store | Updated+Inserted | ~200 |
| 15:54 | Updated CLAUDE.md with Print Formats section (6 gotchas) | CLAUDE.md | Documented | ~300 |
| 15:54 | Updated .wolf/cerebrum.md Key Learnings and Do-Not-Repeat with css field + SVG height findings | cerebrum.md | Learned | ~200 |
| 15:54 | Updated .wolf/anatomy.md with print_format.json entry | anatomy.md | Documented | ~100 |

Session summary: Fixed `50 * 25` label (barcode was completely invisible due to SVG height:100% in flex container) and created new `38 * 25` label. Cleared the conflicting `css` field in both. Key lesson: old WebKit (wkhtmltopdf) doesn't resolve `height:100%` on SVG inside a flex item.

## Session: 2026-05-22

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| — | Created utils/supplier_code.py (generate + assign + backfill) | utils/supplier_code.py | Done | ~300 |
| — | Added Supplier after_insert hook in hooks.py | hooks.py | Done | ~100 |
| — | Added ee_supplier_code custom field to fixtures/custom_field.json | fixtures/custom_field.json | Done | ~200 |
| — | Added supplier code display to PI print format HTML | easy_entry_purchase_invoice.json | Done | ~150 |
| — | Created patches/v1/backfill_supplier_codes.py + registered in patches.txt | patches/v1/backfill_supplier_codes.py, patches.txt | Done | ~100 |
| — | Ran bench migrate — all existing suppliers backfilled with unique codes | DB | Done | ~50 |

Session summary: Implemented ee_supplier_code feature. Each supplier gets a unique 6-char alphanumeric code on create (after_insert hook). All existing suppliers backfilled via patch. Code shown in "Bill From" section of Easy Entry Purchase Invoice print format.
