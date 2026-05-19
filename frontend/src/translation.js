// Minimal translation shim. Frappe's desk exposes a full `__()`; the SPA only
// needs printf-style `{0}` substitution so the same call sites work everywhere.
function translate(message, replace) {
	let text = message;
	if (replace && /{\d+}/.test(text)) {
		text = text.replace(/{(\d+)}/g, (match, i) => replace[i] ?? match);
	}
	return text;
}

export default function translationPlugin(app) {
	app.config.globalProperties.__ = translate;
	if (typeof window !== "undefined") {
		window.__ = translate;
	}
}
