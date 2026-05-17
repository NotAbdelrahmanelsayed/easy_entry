// Add this route to your vue-router routes array:
//
// {
//   name: "ItemPriceEditor",
//   path: "/price-editor",
//   component: () => import("@/pages/ItemPriceEditor.vue"),
// },
//
// Example full router setup (adjust base path to match your SPA mount point):

import { createRouter, createWebHistory } from "vue-router";

const routes = [
	{
		name: "ItemPriceEditor",
		path: "/price-editor",
		component: () => import("@/pages/ItemPriceEditor.vue"),
	},
	// add your other routes here
];

const router = createRouter({
	history: createWebHistory("/"), // update base path to match your app's mount point
	routes,
});

export default router;
