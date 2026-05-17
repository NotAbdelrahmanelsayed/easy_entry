<template>
	<div class="min-h-screen bg-gray-50 flex flex-col">
		<!-- Header -->
		<header
			class="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between"
		>
			<div class="flex items-center gap-4">
				<button
					class="text-gray-500 hover:text-gray-700 flex items-center gap-1 text-sm"
					@click="router.push({ name: 'POSSale' })"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M15 19l-7-7 7-7"
						/>
					</svg>
					{{ __("Back to POS") }}
				</button>
				<h1 class="text-lg font-semibold text-gray-900">{{ __("Item Price Editor") }}</h1>
			</div>
			<div class="flex items-center gap-3">
				<span v-if="pendingCount > 0" class="text-sm text-amber-600 font-medium">
					{{ __("{0} unsaved", [pendingCount]) }}
				</span>
				<Button
					v-if="pendingCount > 0"
					variant="solid"
					:loading="savingAll"
					@click="saveAll"
				>
					{{ __("Save All") }}
				</Button>
			</div>
		</header>

		<!-- Toolbar -->
		<div class="bg-white border-b border-gray-200 px-6 py-3 flex items-center gap-4">
			<!-- Search -->
			<div class="relative flex-1 max-w-sm">
				<svg
					class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0"
					/>
				</svg>
				<input
					v-model="searchQuery"
					type="text"
					:placeholder="__('Search items...')"
					class="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
					data-testid="search-input"
					@input="onSearchInput"
				/>
			</div>

			<!-- Price List Selector -->
			<select
				v-model="selectedPriceList"
				class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
				data-testid="price-list-select"
				@change="loadPrices"
			>
				<option v-for="pl in priceLists.data" :key="pl.name" :value="pl.name">
					{{ pl.name }}
				</option>
			</select>

			<!-- Item count -->
			<span class="text-sm text-gray-500 whitespace-nowrap">
				{{ __("{0} items", [prices.data?.total ?? 0]) }}
			</span>
		</div>

		<!-- Table -->
		<div class="flex-1 overflow-auto">
			<div v-if="prices.loading" class="flex items-center justify-center py-24">
				<div
					class="animate-spin h-8 w-8 border-2 border-blue-500 border-t-transparent rounded-full"
				></div>
			</div>

			<div
				v-else-if="prices.error"
				class="flex flex-col items-center justify-center py-24 text-red-400"
			>
				<svg class="w-12 h-12 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="1.5"
						d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
					/>
				</svg>
				<p class="text-sm">{{ __("Failed to load prices") }}</p>
				<button
					class="mt-2 text-sm text-blue-600 hover:underline"
					@click="prices.reload()"
				>
					{{ __("Retry") }}
				</button>
			</div>

			<div
				v-else-if="!prices.data?.rows?.length"
				class="flex flex-col items-center justify-center py-24 text-gray-400"
			>
				<svg class="w-12 h-12 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="1.5"
						d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
					/>
				</svg>
				<p class="text-sm">{{ __("No items found") }}</p>
			</div>

			<table v-else class="w-full text-sm" data-testid="price-table">
				<thead class="bg-gray-50 border-b border-gray-200 sticky top-0 z-10">
					<tr>
						<th
							class="px-6 py-3 text-left font-medium text-gray-500 uppercase tracking-wider w-12"
						>
							#
						</th>
						<th
							class="px-6 py-3 text-left font-medium text-gray-500 uppercase tracking-wider"
						>
							{{ __("Item") }}
						</th>
						<th
							class="px-6 py-3 text-left font-medium text-gray-500 uppercase tracking-wider w-32"
						>
							{{ __("UOM") }}
						</th>
						<th
							class="px-6 py-3 text-right font-medium text-gray-500 uppercase tracking-wider w-52"
						>
							{{ __("Price") }}
						</th>
						<th
							class="px-6 py-3 text-center font-medium text-gray-500 uppercase tracking-wider w-24"
						>
							{{ __("Status") }}
						</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-100 bg-white">
					<tr
						v-for="(row, idx) in rows"
						:key="row.name"
						class="hover:bg-gray-50 transition-colors"
						:class="{ 'bg-amber-50': isDirty(row.name) }"
						:data-testid="`price-row-${idx}`"
					>
						<td class="px-6 py-3 text-gray-400">{{ offset + idx + 1 }}</td>

						<!-- Item info -->
						<td class="px-6 py-3">
							<div class="flex items-center gap-3">
								<img
									v-if="row.image"
									:src="row.image"
									:alt="row.item_name"
									class="w-8 h-8 rounded object-cover flex-shrink-0"
								/>
								<div
									v-else
									class="w-8 h-8 rounded bg-gray-100 flex items-center justify-center flex-shrink-0"
								>
									<svg
										class="w-4 h-4 text-gray-400"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
										/>
									</svg>
								</div>
								<div>
									<div class="font-medium text-gray-900">
										{{ row.item_name }}
									</div>
									<div class="text-xs text-gray-400">{{ row.item_code }}</div>
								</div>
							</div>
						</td>

						<td class="px-6 py-3 text-gray-600">{{ row.uom }}</td>

						<!-- Editable price -->
						<td class="px-6 py-3">
							<div class="flex items-center justify-end gap-2">
								<span class="text-gray-400 text-xs">{{ row.currency }}</span>
								<input
									:value="editValues[row.name] ?? row.price_list_rate"
									type="number"
									min="0"
									step="0.01"
									class="w-32 text-right border border-gray-300 rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
									:class="{ 'border-amber-400 bg-amber-50': isDirty(row.name) }"
									:data-testid="`price-input-${idx}`"
									@input="onPriceInput(row.name, $event.target.value)"
									@keydown.enter="saveRowSingle(row)"
									@keydown.escape="cancelEdit(row.name)"
								/>
							</div>
						</td>

						<!-- Save/status -->
						<td class="px-6 py-3 text-center">
							<button
								v-if="isDirty(row.name)"
								class="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
								:disabled="saving[row.name]"
								:data-testid="`save-btn-${idx}`"
								@click="saveRowSingle(row)"
							>
								{{ saving[row.name] ? __("Saving...") : __("Save") }}
							</button>
							<span
								v-else-if="saved[row.name]"
								class="text-xs text-green-600 font-medium"
							>
								{{ __("Saved") }}
							</span>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Pagination -->
		<div
			v-if="prices.data?.total > pageSize"
			class="bg-white border-t border-gray-200 px-6 py-3 flex items-center justify-between"
		>
			<span class="text-sm text-gray-500">
				{{
					__("Showing {0}–{1} of {2}", [
						offset + 1,
						Math.min(offset + pageSize, prices.data.total),
						prices.data.total,
					])
				}}
			</span>
			<div class="flex gap-2">
				<button
					class="px-3 py-1 border rounded text-sm disabled:opacity-40 hover:bg-gray-50"
					:disabled="currentPage === 0"
					@click="goToPage(currentPage - 1)"
				>
					{{ __("Previous") }}
				</button>
				<button
					class="px-3 py-1 border rounded text-sm disabled:opacity-40 hover:bg-gray-50"
					:disabled="offset + pageSize >= prices.data.total"
					@click="goToPage(currentPage + 1)"
				>
					{{ __("Next") }}
				</button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { Button } from "frappe-ui";
import { createResource } from "frappe-ui";
import { computed, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "@/composables/useToast";

const router = useRouter();
const { showSuccess, showError } = useToast();

const pageSize = 50;
const currentPage = ref(0);
const searchQuery = ref("");
const selectedPriceList = ref("");
let searchTimer = null;

// dirty tracking: name → edited value
const editValues = reactive({});
// saving state per row
const saving = reactive({});
// briefly show "Saved" badge
const saved = reactive({});

const offset = computed(() => currentPage.value * pageSize);

const priceLists = createResource({
	url: "easy_entry.api.item_prices.get_price_lists",
	auto: true,
	onSuccess(data) {
		if (data.length && !selectedPriceList.value) {
			const selling = data.find((pl) => pl.selling);
			selectedPriceList.value = selling ? selling.name : data[0].name;
			loadPrices();
		}
	},
});

const prices = createResource({
	url: "easy_entry.api.item_prices.get_item_prices",
	makeParams() {
		return {
			search: searchQuery.value,
			price_list: selectedPriceList.value,
			limit: pageSize,
			offset: offset.value,
		};
	},
	auto: false,
});

const rows = computed(() => prices.data?.rows ?? []);

const pendingCount = computed(() => Object.keys(editValues).length);

function isDirty(name) {
	return name in editValues;
}

function loadPrices() {
	if (!selectedPriceList.value) return;
	currentPage.value = 0;
	// clear dirty state when switching lists
	Object.keys(editValues).forEach((k) => delete editValues[k]);
	prices.reload();
}

function goToPage(page) {
	currentPage.value = page;
	prices.reload();
}

function onSearchInput() {
	clearTimeout(searchTimer);
	searchTimer = setTimeout(() => {
		currentPage.value = 0;
		prices.reload();
	}, 300);
}

function onPriceInput(name, value) {
	editValues[name] = value;
}

function cancelEdit(name) {
	delete editValues[name];
}

const saveRow = createResource({
	url: "easy_entry.api.item_prices.update_item_price",
	auto: false,
});

async function saveRowSingle(row) {
	if (!isDirty(row.name)) return;
	saving[row.name] = true;
	try {
		await saveRow.submit({ name: row.name, price_list_rate: editValues[row.name] });
		// update local row so it reflects saved value without full reload
		row.price_list_rate = parseFloat(editValues[row.name]);
		delete editValues[row.name];
		saved[row.name] = true;
		setTimeout(() => delete saved[row.name], 2000);
	} catch (e) {
		showError(e.message || __("Failed to save price"));
	} finally {
		saving[row.name] = false;
	}
}

const savingAll = ref(false);

async function saveAll() {
	savingAll.value = true;
	const dirtyRows = rows.value.filter((r) => isDirty(r.name));
	const results = await Promise.allSettled(dirtyRows.map((r) => saveRowSingle(r)));
	const failed = results.filter((r) => r.status === "rejected").length;
	if (failed === 0) {
		showSuccess(__("All prices saved"));
	} else {
		showError(__("{0} price(s) failed to save", [failed]));
	}
	savingAll.value = false;
}
</script>
