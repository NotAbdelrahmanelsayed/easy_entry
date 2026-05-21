<template>
	<div
		class="fixed inset-0 bg-black/70 z-50 flex flex-col"
		@click.self="$emit('close')"
	>
		<div
			class="bg-white mt-auto sm:m-auto w-full sm:max-w-md rounded-t-xl sm:rounded-xl p-4 shadow-xl"
		>
			<div class="flex items-center justify-between mb-3">
				<h2 class="font-semibold text-gray-900">{{ __("Scan a barcode") }}</h2>
				<button
					class="text-gray-400 hover:text-gray-700 p-1 -m-1"
					aria-label="Close"
					@click="$emit('close')"
				>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						/>
					</svg>
				</button>
			</div>

			<!-- Camera failed — the typed scan bar is always the fallback. -->
			<div
				v-if="error"
				class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-4 text-center"
				data-testid="scanner-error"
			>
				{{ error }}
			</div>

			<video
				v-show="!error"
				ref="video"
				class="w-full rounded-lg bg-black aspect-[4/3] object-cover"
				muted
				playsinline
			></video>

			<p v-if="!error" class="text-xs text-gray-500 mt-2 text-center">
				{{ __("Point the camera at the item barcode.") }}
			</p>
		</div>
	</div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";

const emit = defineEmits(["scanned", "close"]);

const video = ref(null);
const error = ref("");
let controls = null;

onMounted(async () => {
	try {
		// Dynamic import keeps the ~200KB decoder out of the main SPA bundle —
		// it loads only when someone actually opens the camera scanner.
		const { BrowserMultiFormatReader } = await import("@zxing/browser");
		const reader = new BrowserMultiFormatReader();
		controls = await reader.decodeFromVideoDevice(undefined, video.value, (result) => {
			if (result) emit("scanned", result.getText());
		});
	} catch (e) {
		error.value = __(
			"Could not access the camera. Check permissions, or type the code into the scan bar instead.",
		);
	}
});

onBeforeUnmount(() => {
	// Release the camera when the modal closes.
	try {
		controls?.stop();
	} catch (e) {
		/* camera already released */
	}
});
</script>
