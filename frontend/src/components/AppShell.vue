<template>
	<div class="min-h-screen flex flex-col bg-gray-50">
		<!-- Global app bar — persists across every Easy Entry page. -->
		<div
			class="bg-white border-b border-gray-200 px-6 py-2.5 flex items-center gap-4"
		>
			<router-link
				:to="{ name: 'Dashboard' }"
				class="flex items-center gap-2 text-gray-900 font-semibold"
			>
				<span
					class="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-blue-600 text-white text-sm"
				>
					E
				</span>
				{{ __("Easy Entry") }}
			</router-link>

			<router-link
				v-if="!isHome"
				:to="{ name: 'Dashboard' }"
				class="ml-2 flex items-center gap-1 text-sm text-gray-500 hover:text-blue-600"
				data-testid="back-to-dashboard"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M15 19l-7-7 7-7"
					/>
				</svg>
				{{ __("Dashboard") }}
			</router-link>

			<!-- Shortcuts help — available on every page. -->
			<button
				class="ml-auto inline-flex items-center justify-center w-7 h-7 rounded-lg border border-gray-300 text-gray-500 hover:text-blue-600 hover:border-blue-400 text-sm font-semibold"
				:aria-label="__('Keyboard shortcuts')"
				:title="__('Keyboard shortcuts (?)')"
				data-testid="shortcuts-button"
				@click="shortcutsOpen = true"
			>
				?
			</button>
		</div>

		<!-- Page content -->
		<div class="flex-1 flex flex-col min-h-0">
			<slot />
		</div>

		<ShortcutsModal :open="shortcutsOpen" @close="shortcutsOpen = false" />
	</div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRoute } from "vue-router";
import ShortcutsModal from "@/components/ShortcutsModal.vue";

const route = useRoute();
const isHome = computed(() => route.name === "Dashboard");

const shortcutsOpen = ref(false);

// True when the user is typing somewhere — don't hijack "?" then.
function isTyping(target) {
	if (!target) return false;
	const tag = target.tagName;
	return tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || target.isContentEditable;
}

function handleKeydown(event) {
	if (event.key === "Escape" && shortcutsOpen.value) {
		shortcutsOpen.value = false;
		return;
	}
	// "?" is Shift+/ — open the cheat-sheet unless focus is in a field.
	if (event.key === "?" && !isTyping(event.target)) {
		event.preventDefault();
		shortcutsOpen.value = true;
	}
}

onMounted(() => window.addEventListener("keydown", handleKeydown));
onUnmounted(() => window.removeEventListener("keydown", handleKeydown));
</script>
