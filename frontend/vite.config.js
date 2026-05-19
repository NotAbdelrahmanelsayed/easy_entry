import path from "path";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import frappeui from "frappe-ui/vite";

// Builds to ../easy_entry/public/frontend and writes the SPA host page to
// ../easy_entry/www/item-manager.html (with the CSRF token injected by jinjaBootData).
export default defineConfig({
	plugins: [
		frappeui({
			frappeProxy: true,
			lucideIcons: true,
			jinjaBootData: true,
			buildConfig: {
				indexHtmlPath: "../easy_entry/www/item-manager.html",
				emptyOutDir: true,
			},
		}),
		vue(),
	],
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "src"),
		},
	},
	server: {
		fs: {
			allow: [".."],
		},
	},
	build: {
		outDir: "../easy_entry/public/frontend",
		target: "es2015",
	},
});
