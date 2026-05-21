# Easy Entry — Frontend Design System

A design contract every page under `/easy/<feature>` must follow. The Easy Entry
SPA is a single Vue 3 + Vite + frappe-ui app served at the `/easy` www route. New
feature pages should look and behave like the existing ones — this document is the
reference.

## Stack constraints

- **Vue 3** `<script setup>` single-file components only.
- **frappe-ui** is the component library. Prefer its components (e.g. `Button`)
  over hand-rolled equivalents where one exists.
- **Tailwind CSS** for styling, configured via the `frappe-ui/tailwind` preset
  (`tailwind.config.js`). Use utility classes — no separate CSS files per page.
- **No raw jQuery / vanilla DOM manipulation.** Render through Vue.
- **All server calls go through `frappeRequest`** — use `createResource` / `call`
  from `frappe-ui` (CSRF is wired in `main.js`). Never `fetch()` Frappe directly.
- Wrap user-facing strings in `__()` (the translation shim from `translation.js`).

## Design tokens

Extracted from `ItemManager.vue` — the doc matches the built UI.

### Colors

| Role | Class |
|------|-------|
| Page background | `bg-gray-50` |
| Surface / card / header | `bg-white` |
| Border | `border-gray-200` (dividers `divide-gray-100`) |
| Primary action | `bg-blue-600` → hover `bg-blue-700`, text white |
| Primary accent (links, focus ring) | `text-blue-600`, `focus:ring-blue-500` |
| Dirty / unsaved | border `border-amber-400`, fill `bg-amber-50`, text `text-amber-600` |
| Success | `text-green-600` / toast `bg-green-600` |
| Error | `text-red-600` / toast `bg-red-600` |
| Info toast | `bg-gray-800` |
| Primary text | `text-gray-900` · secondary `text-gray-500` · muted `text-gray-400` |

### Typography

| Use | Class |
|-----|-------|
| Page title | `text-lg` / `text-xl` `font-semibold text-gray-900` |
| Section / card heading | `font-semibold text-gray-900` |
| Body | `text-sm` |
| Caption / helper | `text-xs text-gray-500` |
| Table header | `text-xs uppercase tracking-wider text-gray-500` |

### Spacing & shape

- Page padding: `px-6` horizontally; headers `py-4`, toolbars `py-3`.
- Gaps between controls: `gap-3` / `gap-4`.
- Radius: inputs/buttons `rounded-lg` (`rounded-md` for compact table inputs),
  cards/modals `rounded-xl`.
- Shadow: cards on hover `hover:shadow-md`; modals `shadow-xl`.

## Layout

- **AppShell** (`components/AppShell.vue`) wraps every route — it renders the
  global app bar (brand + back-to-dashboard link on non-home routes) and a
  `<slot />` for page content. It is mounted once in `App.vue`; pages do not
  render it themselves.
- A page is a full-height `flex flex-col` column: optional page header
  (`bg-white border-b`), optional toolbar (`bg-white border-b`), a scrollable
  content region (`flex-1 overflow-auto`), and optional pagination footer
  (`bg-white border-t`).
- Content max-width: lightweight pages (e.g. Dashboard) center at `max-w-5xl`;
  data tables run full width.
- **Table pattern** — `w-full text-sm`, sticky `thead` (`sticky top-0 z-10`),
  zebra-free rows with `hover:bg-gray-50`.
- **Dirty-cell highlighting** — when an editable field differs from its saved
  value, mark the input with `border-amber-400 bg-amber-50` and the row with
  `bg-amber-50`; show a per-row Save button plus a header "Save All".
- **States** — every data view handles loading (skeleton/spinner), error (with
  Retry), and empty (icon + message).

## Feature-card convention

Dashboard cards (`pages/Dashboard.vue`) are `<router-link>`s. Card anatomy:
icon badge (`w-10 h-10 rounded-lg bg-blue-50 text-blue-600`), title
(`font-semibold`), one-sentence description (`text-sm text-gray-500`). Cards sit
in a responsive grid (`grid gap-4 sm:grid-cols-2 lg:grid-cols-3`).

## Route naming

- The router base is `/easy` (`createWebHistory("/easy")`).
- Dashboard is the home route `/`.
- Each feature gets a kebab-case path, e.g. `/item-manager`, with exactly one
  page component per feature under `src/pages/`.

## Registering a new feature

1. Add `src/pages/<Feature>.vue` — the page, following the layout above.
2. Add a route in `src/router.js` with a unique `name` and kebab-case `path`.
3. Add an entry to `src/features.js` (`key`, `title`, `description`, `icon`,
   `route`). The dashboard card appears automatically.

A feature shows on the dashboard only once it has a working page — there are no
"coming soon" placeholders.

## Feedback

- Use the shared toast store `useToast` (`composables/useToast.js`):
  `showSuccess` / `showError` / `showInfo`. Toasts render once via `App.vue`.
- Never use `alert()` / `confirm()` / `prompt()`.
- For destructive or review-worthy actions, prefer a modal (see the rename and
  quantity modals in `ItemManager.vue`) over a blocking browser dialog.
