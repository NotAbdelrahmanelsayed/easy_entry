// Feature registry — the single source of truth for the Easy Entry dashboard.
//
// To add a new feature: create a page under src/pages/, register its route in
// router.js, then add an entry here. The dashboard renders one card per entry.
// Only list features that have a working page — there are no "coming soon" cards.
//
// Each entry:
//   key         unique kebab-case id
//   title       card heading
//   description one short sentence shown under the title
//   icon        an SVG path `d` string (stroke style, 24x24 viewBox)
//   route       vue-router route name (see router.js)

export const features = [
	{
		key: "item-manager",
		title: "Item Manager",
		description: "Edit every item's name, prices, stock and supplier in one place.",
		icon: "M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4",
		route: "ItemManager",
	},
	{
		key: "stock-count",
		title: "Stock Count",
		description: "Walk the warehouse with your phone — scan, count and reconcile stock.",
		icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7l-3 3-1.5-1.5",
		route: "StockCount",
	},
];
