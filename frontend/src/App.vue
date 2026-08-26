<template>
	<div class="h-full">
		<AppShell>
			<router-view />
		</AppShell>

		<!-- Toast host -->
		<div class="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
			<transition-group name="toast">
				<div
					v-for="t in toasts"
					:key="t.id"
					class="flex items-start gap-3 rounded-lg px-4 py-3 shadow-lg text-sm max-w-sm cursor-pointer"
					:class="{
						'bg-green-600 text-white': t.type === 'success',
						'bg-red-600 text-white': t.type === 'error',
						'bg-gray-800 text-white': t.type === 'info',
					}"
					@click="removeToast(t.id)"
				>
					<span class="flex-1">
						{{ t.message }}
						<a
							v-if="t.link"
							:href="t.link.url"
							target="_blank"
							class="ml-2 underline font-semibold opacity-90 hover:opacity-100"
							@click.stop
						>{{ t.link.label }}</a>
					</span>
					<span class="opacity-70">&times;</span>
				</div>
			</transition-group>
		</div>
	</div>
</template>

<script setup>
import AppShell from "@/components/AppShell.vue";
import { useToast } from "@/composables/useToast";

const { toasts, removeToast } = useToast();
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
	transition: all 0.25s ease;
}
.toast-enter-from,
.toast-leave-to {
	opacity: 0;
	transform: translateY(8px);
}
</style>
