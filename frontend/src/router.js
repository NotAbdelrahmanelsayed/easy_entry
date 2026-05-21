import { createRouter, createWebHistory } from "vue-router";

const routes = [
	{
		name: "Dashboard",
		path: "/",
		component: () => import("@/pages/Dashboard.vue"),
	},
	{
		name: "ItemManager",
		path: "/item-manager",
		component: () => import("@/pages/ItemManager.vue"),
	},
	{
		name: "StockCount",
		path: "/stock-count",
		component: () => import("@/pages/StockCount.vue"),
	},
	{
		name: "StockCountSession",
		path: "/stock-count/:session",
		component: () => import("@/pages/StockCountSession.vue"),
		props: true,
	},
];

const router = createRouter({
	// The SPA is mounted at the /easy www route.
	history: createWebHistory("/easy"),
	routes,
});

export default router;
