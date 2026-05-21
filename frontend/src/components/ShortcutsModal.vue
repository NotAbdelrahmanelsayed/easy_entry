<template>
	<div
		v-if="open"
		class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
		data-testid="shortcuts-modal"
		@click.self="$emit('close')"
	>
		<div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
			<div class="flex items-start justify-between">
				<h2 class="text-base font-semibold text-gray-900">
					{{ __("Keyboard shortcuts") }}
				</h2>
				<button
					class="text-gray-400 hover:text-gray-700"
					:aria-label="__('Close')"
					@click="$emit('close')"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						/>
					</svg>
				</button>
			</div>

			<div v-for="group in groups" :key="group.title" class="mt-4">
				<h3 class="text-xs font-semibold uppercase tracking-wider text-gray-400">
					{{ __(group.title) }}
				</h3>
				<ul class="mt-2 divide-y divide-gray-100">
					<li
						v-for="item in group.items"
						:key="item.label"
						class="flex items-center justify-between py-1.5"
					>
						<span class="text-sm text-gray-600">{{ __(item.label) }}</span>
						<kbd
							class="text-xs font-medium bg-gray-100 border border-gray-300 rounded px-1.5 py-0.5 text-gray-700"
						>
							{{ item.keys }}
						</kbd>
					</li>
				</ul>
			</div>
		</div>
	</div>
</template>

<script setup>
defineProps({ open: { type: Boolean, default: false } });
defineEmits(["close"]);

// Static cheat-sheet, grouped by where each shortcut applies.
const groups = [
	{
		title: "Global",
		items: [
			{ label: "Show this help", keys: "?" },
			{ label: "Close a popup", keys: "Esc" },
			{ label: "Save inside a popup", keys: "Ctrl+S" },
		],
	},
	{
		title: "Item Manager",
		items: [
			{ label: "Focus the search box", keys: "/" },
			{ label: "Save all unsaved rows", keys: "Ctrl+S" },
			{ label: "Save the open popup", keys: "Enter" },
		],
	},
	{
		title: "Stock Count",
		items: [
			{ label: "Search / resolve the scan box", keys: "Enter" },
			{ label: "Save a counted quantity", keys: "Enter" },
		],
	},
];
</script>
