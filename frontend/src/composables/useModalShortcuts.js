import { onMounted, onUnmounted } from "vue";

// Keyboard behaviour shared by every Easy Entry popup.
//
// While `isOpen()` returns true:
//   - Esc           -> onCancel()
//   - Ctrl+S / Cmd+S -> preventDefault() + onSave()
//
// Enter is intentionally NOT handled here: it stays on the individual inputs
// (`@keydown.enter`) so it only fires when focus is in the form, avoiding
// surprise saves while focus sits on a button or the backdrop.
//
// Usage:
//   useModalShortcuts(() => !!qtyModal.row, { onSave: confirmQty, onCancel: closeQty });
export function useModalShortcuts(isOpen, { onSave, onCancel } = {}) {
	function handleKeydown(event) {
		if (!isOpen()) return;

		if (event.key === "Escape") {
			event.preventDefault();
			onCancel?.();
			return;
		}

		// Ctrl+S (Windows/Linux) or Cmd+S (macOS).
		if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
			event.preventDefault();
			onSave?.();
		}
	}

	onMounted(() => window.addEventListener("keydown", handleKeydown));
	onUnmounted(() => window.removeEventListener("keydown", handleKeydown));
}
