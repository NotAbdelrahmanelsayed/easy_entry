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
	{
		key: "owner-dashboard",
		title: "Owner Dashboard",
		description: "Sales, profit, receivables and low-stock alerts at a glance.",
		icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
		route: "OwnerDashboard",
	},
	{
		key: "cash-loan",
		title: "Cash Loans",
		description: "Give and track informal cash advances without touching sales.",
		icon: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V6m0 10v2m9-8a9 9 0 11-18 0 9 9 0 0118 0z",
		route: "CashLoan",
	},
];
