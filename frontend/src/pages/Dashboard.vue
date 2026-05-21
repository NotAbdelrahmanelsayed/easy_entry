<template>
	<div class="px-6 py-8 max-w-5xl mx-auto w-full">
		<div class="mb-6">
			<h1 class="text-xl font-semibold text-gray-900">{{ __("Easy Entry") }}</h1>
			<p class="text-sm text-gray-500 mt-1">
				{{ __("Pick a tool to get started.") }}
			</p>
		</div>

		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3" data-testid="feature-grid">
			<router-link
				v-for="feature in features"
				:key="feature.key"
				:to="{ name: feature.route }"
				class="group flex flex-col rounded-xl border border-gray-200 bg-white p-5 transition-shadow hover:shadow-md hover:border-blue-300"
				:data-testid="`feature-card-${feature.key}`"
			>
				<span
					class="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-blue-50 text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							:d="feature.icon"
						/>
					</svg>
				</span>
				<h2 class="mt-3 font-semibold text-gray-900">{{ __(feature.title) }}</h2>
				<p class="mt-1 text-sm text-gray-500 flex-1">{{ __(feature.description) }}</p>
			</router-link>
		</div>
	</div>
</template>

<script setup>
import { features } from "@/features";
</script>
