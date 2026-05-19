<template>
	<div class="min-h-screen bg-gray-50 flex flex-col">
		<!-- Header -->
		<header
			class="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between flex-wrap gap-3"
		>
			<div>
				<h1 class="text-lg font-semibold text-gray-900">{{ __("Item Manager") }}</h1>
				<p class="text-xs text-gray-500">
					{{ __("Edit every item's name, prices, stock and supplier in one place.") }}
				</p>
			</div>
			<div class="flex items-center gap-3">
				<span v-if="dirtyRows.length" class="text-sm text-amber-600 font-medium">
					{{ __("{0} unsaved", [dirtyRows.length]) }}
				</span>
				<button
					v-if="dirtyRows.length"
					class="px-3 py-2 rounded-lg text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
					:disabled="savingAll"
					@click="saveAll"
				>
					{{ savingAll ? __("Saving...") : __("Save All") }}
				</button>
				<button
					class="px-3 py-2 rounded-lg text-sm font-medium border border-gray-300 text-gray-700 hover:bg-gray-50 flex items-center gap-1"
					@click="exportSheet"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5 5-5M12 15V3"
						/>
					</svg>
					{{ __("Export sheet") }}
				</button>
			</div>
		</header>

		<!-- Toolbar -->
		<div
			class="bg-white border-b border-gray-200 px-6 py-3 flex items-center gap-3 flex-wrap"
		>
			<div class="relative flex-1 min-w-[200px] max-w-sm">
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
					:placeholder="__('Search by code or name...')"
					class="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
					data-testid="search-input"
					@input="onSearchInput"
				/>
			</div>

			<select
				v-model="itemGroupFilter"
				class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
				data-testid="group-filter"
				@change="reloadFirstPage"
			>
				<option value="">{{ __("All item groups") }}</option>
				<option v-for="g in itemGroups.data || []" :key="g.name" :value="g.name">
					{{ g.name }}
				</option>
			</select>

			<!-- Supplier filter: a native datalist makes the input type-to-search
			     without pulling in an extra component. -->
			<input
				v-model="supplierFilter"
				list="supplier-options"
				type="text"
				:placeholder="__('All suppliers')"
				class="border border-gray-300 rounded-lg px-3 py-2 text-sm min-w-[160px] focus:outline-none focus:ring-2 focus:ring-blue-500"
				data-testid="supplier-filter"
				@change="reloadFirstPage"
			/>
			<datalist id="supplier-options">
				<option v-for="s in suppliers.data || []" :key="s.name" :value="s.name" />
			</datalist>

			<select
				v-model="stockFilter"
				class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
				data-testid="stock-filter"
				@change="reloadFirstPage"
			>
				<option value="">{{ __("All stock") }}</option>
				<option value="in_stock">{{ __("In stock") }}</option>
				<option value="out_of_stock">{{ __("Out of stock") }}</option>
				<option value="negative">{{ __("Negative stock") }}</option>
			</select>

			<select
				v-model="priceFilter"
				class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
				data-testid="price-filter"
				@change="reloadFirstPage"
			>
				<option value="">{{ __("All prices") }}</option>
				<option value="missing_buying">{{ __("Missing buying price") }}</option>
				<option value="missing_selling">{{ __("Missing selling price") }}</option>
				<option value="missing_any">{{ __("Missing any price") }}</option>
				<option value="has_both">{{ __("Has both prices") }}</option>
			</select>

			<button
				v-if="hasActiveFilters"
				class="text-sm text-blue-600 hover:underline whitespace-nowrap"
				data-testid="clear-filters"
				@click="clearFilters"
			>
				{{ __("Clear filters") }}
			</button>

			<span class="text-sm text-gray-500 whitespace-nowrap ml-auto">
				{{ __("{0} items", [items.data?.total ?? 0]) }}
			</span>
		</div>

		<!-- Table -->
		<div class="flex-1 overflow-auto">
			<!-- Loading skeleton -->
			<table v-if="items.loading" class="w-full text-sm">
				<tbody>
					<tr v-for="n in pageSize" :key="n" class="border-b border-gray-100">
						<td v-for="c in 7" :key="c" class="px-6 py-4">
							<div class="h-4 bg-gray-100 rounded animate-pulse"></div>
						</td>
					</tr>
				</tbody>
			</table>

			<!-- Error state -->
			<div
				v-else-if="items.error"
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
				<p class="text-sm">
					{{ isAuthError(items.error) ? __("Please log in to view items") : __("Failed to load items") }}
				</p>
				<button
					v-if="isAuthError(items.error)"
					class="mt-2 text-sm text-blue-600 hover:underline"
					@click="redirectToLogin()"
				>
					{{ __("Log in") }}
				</button>
				<button
					v-else
					class="mt-2 text-sm text-blue-600 hover:underline"
					@click="items.reload()"
				>
					{{ __("Retry") }}
				</button>
			</div>

			<!-- Empty state -->
			<div
				v-else-if="!rows.length"
				class="flex flex-col items-center justify-center py-24 text-gray-400"
			>
				<svg class="w-14 h-14 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="1.5"
						d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
					/>
				</svg>
				<p class="text-sm">
					{{ searchQuery ? __("No items match your search") : __("No items yet") }}
				</p>
			</div>

			<!-- Data table -->
			<table v-else class="w-full text-sm" data-testid="item-table">
				<thead class="bg-gray-50 border-b border-gray-200 sticky top-0 z-10">
					<tr class="text-left text-gray-500 uppercase tracking-wider text-xs">
						<th class="px-4 py-3 w-12">#</th>
						<th class="px-4 py-3">{{ __("Item") }}</th>
						<th class="px-4 py-3 w-32 text-right">{{ __("Buying") }}</th>
						<th class="px-4 py-3 w-32 text-right">{{ __("Selling") }}</th>
						<th class="px-4 py-3 w-28 text-right">{{ __("On hand") }}</th>
						<th class="px-4 py-3 w-48">{{ __("Supplier") }}</th>
						<th class="px-4 py-3 w-28 text-center">{{ __("Save") }}</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-100 bg-white">
					<tr
						v-for="(row, idx) in rows"
						:key="row.item_code"
						class="hover:bg-gray-50 transition-colors"
						:class="{ 'bg-amber-50': isRowDirty(row) }"
						:data-testid="`item-row-${idx}`"
					>
						<td class="px-4 py-3 text-gray-400">{{ offset + idx + 1 }}</td>

						<!-- Item: image + code + name -->
						<td class="px-4 py-3">
							<div class="flex items-center gap-3">
								<img
									v-if="row.image"
									:src="row.image"
									:alt="row.item_name"
									class="w-9 h-9 rounded object-cover flex-shrink-0 border border-gray-200"
								/>
								<div
									v-else
									class="w-9 h-9 rounded bg-gray-100 flex items-center justify-center flex-shrink-0"
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
								<div class="min-w-0 flex-1">
									<input
										v-model="row.item_name"
										type="text"
										:placeholder="__('Item name')"
										class="w-full font-medium text-gray-900 bg-transparent border border-transparent rounded px-1.5 py-1 hover:border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white"
										:class="{ 'border-amber-400 bg-amber-50': isFieldDirty(row, 'item_name') }"
										:data-testid="`name-input-${idx}`"
									/>
									<button
										class="text-xs text-gray-400 hover:text-blue-600 flex items-center gap-1 px-1.5"
										:data-testid="`rename-btn-${idx}`"
										@click="openRename(row)"
									>
										{{ row.item_code }}
										<svg
											class="w-3 h-3"
											fill="none"
											stroke="currentColor"
											viewBox="0 0 24 24"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
											/>
										</svg>
									</button>
								</div>
							</div>
						</td>

						<!-- Buying price -->
						<td class="px-4 py-3">
							<input
								v-model="row.buying_price"
								type="number"
								min="0"
								step="0.01"
								:placeholder="__('—')"
								class="w-24 text-right border border-gray-300 rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
								:class="{ 'border-amber-400 bg-amber-50': isFieldDirty(row, 'buying_price') }"
								:data-testid="`buying-input-${idx}`"
							/>
						</td>

						<!-- Selling price -->
						<td class="px-4 py-3">
							<input
								v-model="row.selling_price"
								type="number"
								min="0"
								step="0.01"
								:placeholder="__('—')"
								class="w-24 text-right border border-gray-300 rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
								:class="{ 'border-amber-400 bg-amber-50': isFieldDirty(row, 'selling_price') }"
								:data-testid="`selling-input-${idx}`"
							/>
						</td>

						<!-- Quantity -->
						<td class="px-4 py-3 text-right">
							<button
								class="inline-flex items-center gap-1.5 px-2 py-1 rounded-md border border-gray-200 hover:border-blue-400 hover:bg-blue-50 text-gray-700"
								:data-testid="`qty-btn-${idx}`"
								@click="openQty(row)"
							>
								<span class="font-medium tabular-nums">{{ formatQty(row.qty) }}</span>
								<svg
									class="w-3.5 h-3.5 text-gray-400"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
									/>
								</svg>
							</button>
						</td>

						<!-- Supplier -->
						<td class="px-4 py-3">
							<select
								v-model="row.supplier"
								class="w-full border border-gray-300 rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
								:class="{ 'border-amber-400 bg-amber-50': isFieldDirty(row, 'supplier') }"
								:data-testid="`supplier-select-${idx}`"
							>
								<option :value="null">{{ __("— none —") }}</option>
								<option v-for="s in suppliers.data || []" :key="s.name" :value="s.name">
									{{ s.name }}
								</option>
							</select>
						</td>

						<!-- Save -->
						<td class="px-4 py-3 text-center">
							<button
								v-if="isRowDirty(row)"
								class="text-xs px-2.5 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
								:disabled="saving[row.item_code]"
								:data-testid="`save-btn-${idx}`"
								@click="saveRow(row)"
							>
								{{ saving[row.item_code] ? __("Saving...") : __("Save") }}
							</button>
							<span
								v-else-if="savedFlash[row.item_code]"
								class="inline-flex items-center gap-1 text-xs text-green-600 font-medium"
							>
								<svg
									class="w-3.5 h-3.5"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2.5"
										d="M5 13l4 4L19 7"
									/>
								</svg>
								{{ __("Saved") }}
							</span>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Pagination -->
		<div
			v-if="(items.data?.total ?? 0) > pageSize"
			class="bg-white border-t border-gray-200 px-6 py-3 flex items-center justify-between"
		>
			<span class="text-sm text-gray-500">
				{{
					__("Showing {0}–{1} of {2}", [
						offset + 1,
						Math.min(offset + pageSize, items.data.total),
						items.data.total,
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
					:disabled="offset + pageSize >= items.data.total"
					@click="goToPage(currentPage + 1)"
				>
					{{ __("Next") }}
				</button>
			</div>
		</div>

		<!-- Rename modal -->
		<div
			v-if="renameModal.row"
			class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
			@click.self="renameModal.row = null"
		>
			<div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6" data-testid="rename-modal">
				<h2 class="text-base font-semibold text-gray-900">{{ __("Rename item code") }}</h2>
				<p class="text-sm text-gray-500 mt-1">
					{{
						__(
							"Renaming the code updates it everywhere it is used (prices, stock, transactions).",
						)
					}}
				</p>
				<label class="block text-xs font-medium text-gray-500 mt-4 mb-1">
					{{ __("New item code") }}
				</label>
				<input
					v-model="renameModal.newCode"
					type="text"
					class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
					data-testid="rename-input"
					@keydown.enter="confirmRename"
				/>
				<div class="flex justify-end gap-2 mt-5">
					<button
						class="px-3 py-2 rounded-lg text-sm border border-gray-300 hover:bg-gray-50"
						@click="renameModal.row = null"
					>
						{{ __("Cancel") }}
					</button>
					<button
						class="px-3 py-2 rounded-lg text-sm bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
						:disabled="renameModal.busy || !renameModal.newCode.trim()"
						data-testid="rename-confirm"
						@click="confirmRename"
					>
						{{ renameModal.busy ? __("Renaming...") : __("Rename") }}
					</button>
				</div>
			</div>
		</div>

		<!-- Quantity modal -->
		<div
			v-if="qtyModal.row"
			class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
			@click.self="qtyModal.row = null"
		>
			<div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6" data-testid="qty-modal">
				<h2 class="text-base font-semibold text-gray-900">
					{{ __("Set on-hand quantity") }}
				</h2>
				<p class="text-sm text-gray-500 mt-1">
					{{ qtyModal.row.item_name }} ({{ qtyModal.row.item_code }})
				</p>
				<label class="block text-xs font-medium text-gray-500 mt-4 mb-1">
					{{ __("New quantity") }}
				</label>
				<input
					v-model.number="qtyModal.qty"
					type="number"
					min="0"
					step="1"
					class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
					data-testid="qty-input"
				/>
				<div
					class="mt-4 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2"
				>
					{{
						__(
							"This creates a DRAFT Stock Reconciliation. Stock changes only after someone reviews and submits it in the desk.",
						)
					}}
				</div>
				<div class="flex justify-end gap-2 mt-5">
					<button
						class="px-3 py-2 rounded-lg text-sm border border-gray-300 hover:bg-gray-50"
						@click="qtyModal.row = null"
					>
						{{ __("Cancel") }}
					</button>
					<button
						class="px-3 py-2 rounded-lg text-sm bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
						:disabled="qtyModal.busy"
						data-testid="qty-confirm"
						@click="confirmQty"
					>
						{{ qtyModal.busy ? __("Creating...") : __("Create draft") }}
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { call, createResource } from "frappe-ui";
import { computed, reactive, ref } from "vue";
import { useToast } from "@/composables/useToast";

const { showSuccess, showError, showInfo } = useToast();

const API = "easy_entry.api.item_manager";
const pageSize = 20;

const searchQuery = ref("");
const itemGroupFilter = ref("");
const supplierFilter = ref("");
const stockFilter = ref("");
const priceFilter = ref("");
const currentPage = ref(0);
let searchTimer = null;

const offset = computed(() => currentPage.value * pageSize);

// Per-item-code maps for save state.
const saving = reactive({});
const savedFlash = reactive({});
// Snapshot of the server values, keyed by item_code, to detect dirty fields.
const original = reactive({});

const itemGroups = createResource({
	url: "frappe.client.get_list",
	params: { doctype: "Item Group", fields: ["name"], limit_page_length: 0, order_by: "name asc" },
	auto: true,
});

const suppliers = createResource({
	url: "frappe.client.get_list",
	params: { doctype: "Supplier", fields: ["name"], limit_page_length: 0, order_by: "name asc" },
	auto: true,
});

const items = createResource({
	url: `${API}.get_items`,
	makeParams() {
		return {
			search: searchQuery.value,
			item_group: itemGroupFilter.value,
			supplier: supplierFilter.value,
			stock_status: stockFilter.value,
			price_status: priceFilter.value,
			limit: pageSize,
			offset: offset.value,
		};
	},
	auto: true,
	onSuccess(data) {
		// Refresh the dirty-tracking baseline for the rows now on screen.
		(data.rows || []).forEach((row) => {
			original[row.item_code] = snapshot(row);
		});
	},
	onError(err) {
		// A logged-out visitor can open this public page, but every API call
		// then 403s. Send them to login instead of a dead-end "Retry".
		if (isAuthError(err)) redirectToLogin();
	},
});

const rows = computed(() => items.data?.rows ?? []);

function snapshot(row) {
	return {
		item_name: row.item_name,
		supplier: row.supplier,
		buying_price: normalizePrice(row.buying_price),
		selling_price: normalizePrice(row.selling_price),
	};
}

function normalizePrice(value) {
	if (value === null || value === undefined || value === "") return null;
	return Number(value);
}

function formatQty(qty) {
	return Number(qty || 0).toLocaleString();
}

const EDITABLE_FIELDS = ["item_name", "supplier", "buying_price", "selling_price"];

function isFieldDirty(row, field) {
	const base = original[row.item_code];
	if (!base) return false;
	if (field === "buying_price" || field === "selling_price") {
		return normalizePrice(row[field]) !== base[field];
	}
	return (row[field] ?? null) !== (base[field] ?? null);
}

function isRowDirty(row) {
	return EDITABLE_FIELDS.some((f) => isFieldDirty(row, f));
}

const dirtyRows = computed(() => rows.value.filter(isRowDirty));

// --- Search / pagination -------------------------------------------------

function onSearchInput() {
	clearTimeout(searchTimer);
	searchTimer = setTimeout(reloadFirstPage, 300);
}

function reloadFirstPage() {
	currentPage.value = 0;
	items.reload();
}

const hasActiveFilters = computed(
	() => !!(itemGroupFilter.value || supplierFilter.value || stockFilter.value || priceFilter.value),
);

function clearFilters() {
	itemGroupFilter.value = "";
	supplierFilter.value = "";
	stockFilter.value = "";
	priceFilter.value = "";
	reloadFirstPage();
}

function goToPage(page) {
	currentPage.value = page;
	items.reload();
}

// --- Saving --------------------------------------------------------------

async function saveRow(row) {
	if (!isRowDirty(row) || saving[row.item_code]) return;
	saving[row.item_code] = true;
	try {
		const base = original[row.item_code];

		// 1. Name and/or supplier in a single update_item call.
		const fields = {};
		if (isFieldDirty(row, "item_name")) fields.item_name = row.item_name;
		if (isFieldDirty(row, "supplier")) fields.supplier = row.supplier;
		if (Object.keys(fields).length) {
			await call(`${API}.update_item`, { item_code: row.item_code, fields });
		}

		// 2. Prices — one call per changed price list.
		if (isFieldDirty(row, "buying_price")) {
			await savePrice(row, "Standard Buying", row.buying_price);
		}
		if (isFieldDirty(row, "selling_price")) {
			await savePrice(row, "Standard Selling", row.selling_price);
		}

		original[row.item_code] = snapshot(row);
		flashSaved(row.item_code);
		void base;
	} catch (e) {
		showError(errorMessage(e) || __("Failed to save {0}", [row.item_code]));
		throw e;
	} finally {
		saving[row.item_code] = false;
	}
}

async function savePrice(row, priceList, value) {
	const rate = normalizePrice(value);
	if (rate === null) {
		// Clearing a price is not supported by the API; tell the user.
		throw new Error(__("Price cannot be empty. Enter a positive number."));
	}
	await call(`${API}.update_item_price`, {
		item_code: row.item_code,
		price_list: priceList,
		rate,
	});
}

function flashSaved(itemCode) {
	savedFlash[itemCode] = true;
	setTimeout(() => delete savedFlash[itemCode], 2000);
}

const savingAll = ref(false);

async function saveAll() {
	savingAll.value = true;
	const targets = dirtyRows.value.slice();
	const results = await Promise.allSettled(targets.map((r) => saveRow(r)));
	const failed = results.filter((r) => r.status === "rejected").length;
	if (failed === 0) {
		showSuccess(__("All changes saved"));
	} else {
		showError(__("{0} item(s) failed to save", [failed]));
	}
	savingAll.value = false;
}

// --- Rename --------------------------------------------------------------

const renameModal = reactive({ row: null, newCode: "", busy: false });

function openRename(row) {
	renameModal.row = row;
	renameModal.newCode = row.item_code;
	renameModal.busy = false;
}

async function confirmRename() {
	const row = renameModal.row;
	const newCode = renameModal.newCode.trim();
	if (!row || !newCode || renameModal.busy) return;
	if (newCode === row.item_code) {
		renameModal.row = null;
		return;
	}
	renameModal.busy = true;
	try {
		await call(`${API}.rename_item`, { old_code: row.item_code, new_code: newCode });
		showSuccess(__("Renamed to {0}", [newCode]));
		renameModal.row = null;
		items.reload();
	} catch (e) {
		showError(errorMessage(e) || __("Rename failed"));
		renameModal.busy = false;
	}
}

// --- Quantity ------------------------------------------------------------

const qtyModal = reactive({ row: null, qty: 0, busy: false });

function openQty(row) {
	qtyModal.row = row;
	qtyModal.qty = Number(row.qty || 0);
	qtyModal.busy = false;
}

async function confirmQty() {
	const row = qtyModal.row;
	if (!row || qtyModal.busy) return;
	qtyModal.busy = true;
	try {
		const res = await call(`${API}.set_item_qty`, {
			item_code: row.item_code,
			qty: qtyModal.qty,
		});
		showInfo(
			__("Draft Stock Reconciliation {0} created — review it in the desk.", [
				res.stock_reconciliation,
			]),
		);
		qtyModal.row = null;
	} catch (e) {
		showError(errorMessage(e) || __("Could not set quantity"));
		qtyModal.busy = false;
	}
}

// --- Export --------------------------------------------------------------

function exportSheet() {
	const params = new URLSearchParams({
		search: searchQuery.value || "",
		item_group: itemGroupFilter.value || "",
		supplier: supplierFilter.value || "",
		stock_status: stockFilter.value || "",
		price_status: priceFilter.value || "",
	});
	window.open(`/api/method/${API}.export_items_xlsx?${params.toString()}`, "_blank");
}

// --- Errors --------------------------------------------------------------

function errorMessage(e) {
	if (!e) return "";
	// frappe-ui surfaces server messages on `messages` or `_server_messages`.
	if (Array.isArray(e.messages) && e.messages.length) return e.messages.join(", ");
	return e.message || String(e);
}

// True when the server rejected the call because there is no login session.
function isAuthError(e) {
	if (!e) return false;
	if (e.exc_type === "PermissionError" || e.exc_type === "AuthenticationError") return true;
	const text = `${e.exc_type || ""} ${errorMessage(e)}`.toLowerCase();
	return text.includes("not permitted") || text.includes("login to access");
}

// Send the visitor to the Frappe login page, returning here afterwards.
function redirectToLogin() {
	const here = window.location.pathname + window.location.search;
	window.location.href = `/login?redirect-to=${encodeURIComponent(here)}`;
}
</script>
