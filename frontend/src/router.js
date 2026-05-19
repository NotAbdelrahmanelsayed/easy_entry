import { createRouter, createWebHistory } from "vue-router";

const routes = [
	{
		name: "ItemManager",
		path: "/",
		component: () => import("@/pages/ItemManager.vue"),
	},
	{
		name: "ItemPriceEditor",
		path: "/price-editor",
		component: () => import("@/pages/ItemPriceEditor.vue"),
	},
];

const router = createRouter({
	// The SPA is mounted at the /item-manager www route.
	history: createWebHistory("/item-manager"),
	routes,
});

export default router;
