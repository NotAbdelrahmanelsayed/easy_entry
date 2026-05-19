import { reactive } from "vue";

// A tiny self-contained toast store. Shared module state means every caller of
// useToast() sees the same queue, and <ToastHost> renders it once in App.vue.
const toasts = reactive([]);
let seq = 0;

function remove(id) {
	const index = toasts.findIndex((t) => t.id === id);
	if (index !== -1) toasts.splice(index, 1);
}

function push(type, message, timeout) {
	const id = ++seq;
	toasts.push({ id, type, message });
	if (timeout) {
		setTimeout(() => remove(id), timeout);
	}
	return id;
}

export function useToast() {
	return {
		toasts,
		removeToast: remove,
		showSuccess: (message) => push("success", message, 3000),
		showError: (message) => push("error", message, 6000),
		showInfo: (message) => push("info", message, 4000),
	};
}
