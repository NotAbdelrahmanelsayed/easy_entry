import "./index.css";

import { createApp } from "vue";
import { FrappeUI, Button, setConfig, frappeRequest } from "frappe-ui";

import App from "./App.vue";
import router from "./router";
import translationPlugin from "./translation";

// Route all frappe-ui resources through Frappe's request layer (handles CSRF).
setConfig("resourceFetcher", frappeRequest);

const app = createApp(App);
app.use(FrappeUI);
app.use(router);
app.use(translationPlugin);
app.component("Button", Button);
app.mount("#app");
