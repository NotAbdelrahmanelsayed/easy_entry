<template>
	<div class="flex flex-col items-center justify-center py-8 text-red-400" data-testid="error-card">
		<svg class="w-8 h-8 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="1.5"
				d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
			/>
		</svg>
		<p class="text-sm">{{ message }}</p>
		<button class="mt-2 text-sm text-blue-600 hover:underline" @click="$emit('retry')">
			{{ __("Retry") }}
		</button>
	</div>
</template>

<script setup>
defineProps({ message: { type: String, required: true } });
defineEmits(["retry"]);
</script>
