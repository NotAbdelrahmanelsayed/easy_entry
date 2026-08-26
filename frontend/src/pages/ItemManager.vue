<template>
	<div class="flex-1 min-h-0 bg-gray-50 flex flex-col">
		<!-- Header -->
		<header
			class="bg-white border-b border-gray-200 px-4 py-3 sm:px-6 sm:py-4 flex items-center justify-between flex-wrap gap-2 sm:gap-3"
		>
			<div>
				<h1 class="text-lg font-semibold text-gray-900">{{ __("Item Manager") }}</h1>
				<p class="text-xs text-gray-500 hidden sm:block">
					{{ __("Edit every item's name, prices, stock and supplier in one place.") }}
				</p>
			</div>
			<div class="flex items-center gap-2 sm:gap-3">
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
					class="px-3 py-2 rounded-lg text-sm font-medium border border-gray-300 text-gray-700 hover:bg-gray-50 hover:border-blue-400 hover:text-blue-600 active:scale-95 transition flex items-center gap-1.5 disabled:opacity-50"
					:disabled="items.loading"
					:title="__('Refresh items')"
					data-testid="refresh-btn"
					@click="refreshItems"
				>
					<svg
						class="w-4 h-4"
						:class="{ 'animate-spin': items.loading }"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
						/>
					</svg>
					<span class="hidden sm:inline">{{ items.loading ? __("Refreshing...") : __("Refresh") }}</span>
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
					<span class="hidden sm:inline">{{ __("Export sheet") }}</span>
				</button>
				<button
					class="px-3 py-2 rounded-lg text-sm font-medium border border-gray-300 text-gray-700 hover:bg-gray-50 flex items-center gap-1"
					:title="__('Label print settings')"
					data-testid="settings-btn"
					@click="openSettings"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
					</svg>
					<span class="hidden sm:inline">{{ __("Settings") }}</span>
				</button>
			</div>
		</header>

		<!-- Toolbar -->
		<div class="bg-white border-b border-gray-200 px-4 sm:px-6 py-3 flex flex-col gap-2">
			<!-- Search row (always visible) -->
			<div class="flex items-center gap-2">
				<div class="relative flex-1 min-w-0 sm:max-w-sm">
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
						ref="searchInputEl"
						v-model="searchQuery"
						type="text"
						:placeholder="__('Search or scan barcode...')"
						class="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						data-testid="search-input"
						@input="onSearchInput()"
						@keydown.enter.prevent="onBarcodeScan()"
					/>
				</div>

				<!-- Camera scan button -->
				<button
					class="flex-shrink-0 px-3 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
					:aria-label="__('Scan with camera')"
					data-testid="open-scanner"
					@click="showScanner = true"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="1.8"
							d="M3 9V7a2 2 0 012-2h2M17 5h2a2 2 0 012 2v2M21 15v2a2 2 0 01-2 2h-2M7 19H5a2 2 0 01-2-2v-2M7 12h10"
						/>
					</svg>
				</button>

				<!-- Mobile: filter toggle button -->
				<button
					class="sm:hidden flex items-center gap-1.5 px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 flex-shrink-0 relative"
					@click="showFilters = !showFilters"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2a1 1 0 01-.293.707L13 13.414V19a1 1 0 01-.553.894l-4 2A1 1 0 017 21v-7.586L3.293 6.707A1 1 0 013 6V4z" />
					</svg>
					{{ __("Filters") }}
					<span
						v-if="activeFilterCount"
						class="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-blue-600 text-white text-[10px] flex items-center justify-center font-medium"
					>{{ activeFilterCount }}</span>
				</button>

				<!-- Desktop: items count -->
				<span class="hidden sm:inline text-sm text-gray-500 whitespace-nowrap ml-auto">
					{{ __("{0} items", [items.data?.total ?? 0]) }}
				</span>
			</div>

			<!-- Desktop filter row -->
			<div class="hidden sm:flex items-center gap-3 flex-wrap">
				<span class="text-xs text-gray-400 whitespace-nowrap">
					{{ __("Shortcuts: F4 search · F5 refresh · Ctrl+S save all") }}
				</span>

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

				<select
					v-model="supplierFilter"
					class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
					data-testid="supplier-filter"
					@change="reloadFirstPage"
				>
					<option value="">{{ __("All suppliers") }}</option>
					<option v-for="s in suppliers.data || []" :key="s.name" :value="s.name">
						{{ s.name }}
					</option>
				</select>

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

			<!-- Mobile filter panel (collapsible) -->
			<div v-if="showFilters" class="sm:hidden grid grid-cols-2 gap-2 pt-1">
				<select
					v-model="itemGroupFilter"
					class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
					data-testid="group-filter-mobile"
					@change="reloadFirstPage"
				>
					<option value="">{{ __("All item groups") }}</option>
					<option v-for="g in itemGroups.data || []" :key="g.name" :value="g.name">
						{{ g.name }}
					</option>
				</select>

				<select
					v-model="supplierFilter"
					class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
					data-testid="supplier-filter-mobile"
					@change="reloadFirstPage"
				>
					<option value="">{{ __("All suppliers") }}</option>
					<option v-for="s in suppliers.data || []" :key="s.name" :value="s.name">
						{{ s.name }}
					</option>
				</select>

				<select
					v-model="stockFilter"
					class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
					data-testid="stock-filter-mobile"
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
					data-testid="price-filter-mobile"
					@change="reloadFirstPage"
				>
					<option value="">{{ __("All prices") }}</option>
					<option value="missing_buying">{{ __("Missing buying price") }}</option>
					<option value="missing_selling">{{ __("Missing selling price") }}</option>
					<option value="missing_any">{{ __("Missing any price") }}</option>
					<option value="has_both">{{ __("Has both prices") }}</option>
				</select>

				<div class="col-span-2 flex items-center justify-between">
					<span class="text-sm text-gray-500">{{ __("{0} items", [items.data?.total ?? 0]) }}</span>
					<button
						v-if="hasActiveFilters"
						class="text-sm text-blue-600 hover:underline"
						data-testid="clear-filters-mobile"
						@click="clearFilters"
					>
						{{ __("Clear filters") }}
					</button>
				</div>
			</div>
		</div>
<!-- Table / Cards -->
		<div class="flex-1 overflow-auto">
			<!-- Loading skeleton — desktop -->
			<table v-if="items.loading" class="hidden sm:table w-full text-sm">
				<tbody>
					<tr v-for="n in pageSize" :key="n" class="border-b border-gray-100">
						<td v-for="c in 7" :key="c" class="px-6 py-4">
							<div class="h-4 bg-gray-100 rounded animate-pulse"></div>
						</td>
					</tr>
				</tbody>
			</table>
			<!-- Loading skeleton — mobile -->
			<div v-if="items.loading" class="sm:hidden divide-y divide-gray-100 bg-white">
				<div v-for="n in 5" :key="n" class="p-4 space-y-3">
					<div class="flex items-center gap-3">
						<div class="w-10 h-10 rounded bg-gray-100 animate-pulse flex-shrink-0"></div>
						<div class="flex-1 space-y-2">
							<div class="h-4 bg-gray-100 rounded animate-pulse w-3/4"></div>
							<div class="h-3 bg-gray-100 rounded animate-pulse w-1/3"></div>
						</div>
					</div>
					<div class="grid grid-cols-2 gap-3">
						<div class="h-9 bg-gray-100 rounded animate-pulse"></div>
						<div class="h-9 bg-gray-100 rounded animate-pulse"></div>
					</div>
					<div class="grid grid-cols-2 gap-3">
						<div class="h-9 bg-gray-100 rounded animate-pulse"></div>
						<div class="h-9 bg-gray-100 rounded animate-pulse"></div>
					</div>
				</div>
			</div>

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

			<!-- Mobile card list -->
			<div
				v-else-if="rows.length"
				class="sm:hidden divide-y divide-gray-100 bg-white"
				data-testid="item-cards"
			>
				<div
					v-for="(row, idx) in rows"
					:key="row.item_code"
					class="p-4"
					:class="{ 'bg-amber-50': isRowDirty(row) }"
					:data-testid="`item-card-${idx}`"
				>
					<!-- Row 1: image + name + save -->
					<div class="flex items-start gap-3">
						<img
							v-if="row.image"
							:src="row.image"
							:alt="row.item_name"
							class="w-10 h-10 rounded object-cover flex-shrink-0 border border-gray-200 mt-0.5"
						/>
						<div
							v-else
							class="w-10 h-10 rounded bg-gray-100 flex items-center justify-center flex-shrink-0 mt-0.5"
						>
							<svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
							</svg>
						</div>
						<div class="min-w-0 flex-1">
							<input
								v-model="row.item_name"
								type="text"
								:placeholder="__('Item name')"
								class="w-full font-medium text-gray-900 bg-transparent border border-transparent rounded px-1.5 py-1 hover:border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white text-base"
								:class="{ 'border-amber-400 bg-amber-50': isFieldDirty(row, 'item_name') }"
								:data-testid="`name-input-${idx}`"
							/>
							<button
								class="text-xs text-gray-400 hover:text-blue-600 flex items-center gap-1 px-1.5 mt-0.5"
								:data-testid="`rename-btn-${idx}`"
								@click="openRename(row)"
							>
								{{ row.item_code }}
								<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
								</svg>
							</button>
						</div>
						<div class="flex-shrink-0 mt-0.5 flex items-center gap-1">
							<button
								v-if="isRowDirty(row)"
								class="px-3 py-1.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
								:disabled="saving[row.item_code]"
								:data-testid="`save-btn-${idx}`"
								@click="saveRow(row)"
							>
								{{ saving[row.item_code] ? __("Saving...") : __("Save") }}
							</button>
							<span
								v-else-if="savedFlash[row.item_code]"
								class="inline-flex items-center gap-1 text-sm text-green-600 font-medium px-1"
							>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
								</svg>
							</span>
							<button
								class="p-1.5 rounded-lg text-gray-400 hover:text-blue-600 hover:bg-blue-50 border border-transparent hover:border-blue-200"
								:title="__('Print label')"
								:data-testid="`print-label-mobile-${idx}`"
								@click.stop="printLabel(row)"
							>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
								</svg>
							</button>
						</div>
					</div>

					<!-- Item group -->
					<div class="mt-3">
						<label class="text-xs text-gray-500 mb-1 block">{{ __("Item Group") }}</label>
						<select
							v-model="row.item_group"
							class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
							:class="{ 'border-amber-400 bg-amber-50': isFieldDirty(row, 'item_group') }"
							:data-testid="`group-input-mobile-${idx}`"
						>
							<option v-for="g in itemGroups.data || []" :key="g.name" :value="g.name">{{ g.name }}</option>
						</select>
					</div>

					<!-- Row 2: buying + selling prices -->
					<div class="mt-3 grid grid-cols-2 gap-3">
						<div>
							<label class="text-xs text-gray-500 mb-1 block">{{ __("Buying price") }}</label>
							<input
								v-model="row.buying_price"
								type="number"
								min="0"
								step="0.01"
								:placeholder="__('—')"
								class="w-full text-right border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
								:class="{ 'border-amber-400 bg-amber-50': isFieldDirty(row, 'buying_price') }"
								:data-testid="`buying-input-${idx}`"
							/>
						</div>
						<div>
							<label class="text-xs text-gray-500 mb-1 block">{{ __("Selling price") }}</label>
							<input
								v-model="row.selling_price"
								type="number"
								min="0"
								step="0.01"
								:placeholder="__('—')"
								class="w-full text-right border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
								:class="{ 'border-amber-400 bg-amber-50': isFieldDirty(row, 'selling_price') }"
								:data-testid="`selling-input-${idx}`"
							/>
						</div>
					</div>

					<!-- Row 3: supplier + qty -->
					<div class="mt-3 grid grid-cols-2 gap-3">
						<div>
							<label class="text-xs text-gray-500 mb-1 block">{{ __("Supplier") }}</label>
							<select
								v-model="row.supplier"
								class="w-full border border-gray-300 rounded-md px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
								:class="{ 'border-amber-400 bg-amber-50': isFieldDirty(row, 'supplier') }"
								:data-testid="`supplier-select-${idx}`"
							>
								<option :value="null">{{ __("— none —") }}</option>
								<option v-for="s in suppliers.data || []" :key="s.name" :value="s.name">
									{{ s.name }}
								</option>
							</select>
						</div>
						<div>
							<label class="text-xs text-gray-500 mb-1 block">{{ __("On hand") }}</label>
							<button
								class="w-full flex items-center justify-between px-3 py-2 rounded-md border border-gray-200 hover:border-blue-400 hover:bg-blue-50 text-gray-700 text-sm"
								:data-testid="`qty-btn-${idx}`"
								@click="openQty(row)"
							>
								<span class="font-medium tabular-nums">{{ formatQty(row.qty) }}</span>
								<svg class="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
								</svg>
							</button>
						</div>
					</div>
				</div>
			</div>

			<!-- Data table (desktop) -->
			<div class="hidden sm:block">
				<table v-if="rows.length" class="w-full text-sm" data-testid="item-table">
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
										<select
											v-model="row.item_group"
											class="mt-0.5 w-full border border-transparent rounded px-1.5 py-0.5 text-xs text-gray-500 hover:border-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-transparent"
											:class="{ 'border-amber-400 bg-amber-50': isFieldDirty(row, 'item_group') }"
											:data-testid="`group-input-${idx}`"
										>
											<option v-for="g in itemGroups.data || []" :key="g.name" :value="g.name">{{ g.name }}</option>
										</select>
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

							<!-- Save + Print -->
							<td class="px-4 py-3 text-center">
								<div class="flex items-center justify-center gap-1">
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
										<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
										</svg>
										{{ __("Saved") }}
									</span>
									<button
										class="p-1 rounded text-gray-400 hover:text-blue-600 hover:bg-blue-50 border border-transparent hover:border-blue-200 flex-shrink-0"
										:title="__('Print label')"
										:data-testid="`print-label-${idx}`"
										@click.stop="printLabel(row)"
									>
										<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
										</svg>
									</button>
								</div>
							</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>

		<!-- Pagination -->
		<div
			v-if="(items.data?.total ?? 0) > pageSize"
			class="bg-white border-t border-gray-200 px-4 sm:px-6 py-3 flex items-center justify-between"
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
				<div class="flex items-center justify-between gap-2 mt-5">
					<span class="text-xs text-gray-400">
						{{ __("Enter or Ctrl+S to save · Esc to cancel") }}
					</span>
					<div class="flex gap-2">
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
					@keydown.enter="confirmQty"
				/>

				<!-- Submit toggle: OFF keeps the safe draft-for-review default. -->
				<label class="flex items-start gap-2 mt-4 cursor-pointer">
					<input
						v-model="qtyModal.submit"
						type="checkbox"
						class="mt-0.5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
						data-testid="qty-submit-toggle"
					/>
					<span class="text-xs text-gray-600">
						<span class="font-medium text-gray-800">{{ __("Submit immediately") }}</span>
						<br />
						{{
							qtyModal.submit
								? __("Posts the stock change now — no desk review.")
								: __("Leave unchecked to create a draft for review (recommended).")
						}}
					</span>
				</label>

				<div
					class="mt-4 text-xs rounded-lg px-3 py-2 border"
					:class="
						qtyModal.submit
							? 'text-red-700 bg-red-50 border-red-200'
							: 'text-amber-700 bg-amber-50 border-amber-200'
					"
				>
					{{
						qtyModal.submit
							? __(
								"This SUBMITS a Stock Reconciliation — the stock ledger updates right away.",
							)
							: __(
								"This creates a DRAFT Stock Reconciliation. Stock changes only after someone reviews and submits it in the desk.",
							)
					}}
				</div>
				<div class="flex items-center justify-between gap-2 mt-5">
					<span class="text-xs text-gray-400">
						{{ __("Enter or Ctrl+S to save · Esc to cancel") }}
					</span>
					<div class="flex gap-2">
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
							{{
								qtyModal.busy
									? __("Saving...")
									: qtyModal.submit
										? __("Submit now")
										: __("Create draft")
							}}
						</button>
					</div>
				</div>
			</div>
		</div>

		<!-- Settings modal -->
		<div
			v-if="settingsModal.open"
			class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
			@click.self="settingsModal.open = false"
		>
			<div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6" data-testid="settings-modal">
				<h2 class="text-base font-semibold text-gray-900">{{ __("Label print settings") }}</h2>
				<p class="text-sm text-gray-500 mt-1">
					{{ __("Choose the default print format used when printing barcode labels.") }}
				</p>
				<label class="block text-xs font-medium text-gray-500 mt-4 mb-1">
					{{ __("Print format") }}
				</label>
				<select
					v-model="settingsModal.selected"
					class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
					data-testid="format-select"
				>
					<option v-for="fmt in settingsModal.formats" :key="fmt" :value="fmt">{{ fmt }}</option>
				</select>
				<div class="flex items-center justify-between gap-2 mt-5">
					<span class="text-xs text-gray-400">
						{{ __("Enter or Ctrl+S to save · Esc to cancel") }}
					</span>
					<div class="flex gap-2">
						<button
							class="px-3 py-2 rounded-lg text-sm border border-gray-300 hover:bg-gray-50"
							@click="settingsModal.open = false"
						>
							{{ __("Cancel") }}
						</button>
						<button
							class="px-3 py-2 rounded-lg text-sm bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
							:disabled="settingsModal.busy"
							data-testid="settings-save"
							@click="saveSettings"
						>
							{{ settingsModal.busy ? __("Saving...") : __("Save") }}
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Camera barcode scanner modal -->
	<BarcodeScanner
		v-if="showScanner"
		@scanned="onCameraScanned"
		@close="showScanner = false"
	/>
</template>

<script setup>
import { call, createResource } from "frappe-ui";
import { computed, onMounted, onUnmounted, reactive, ref } from "vue";
import { useToast } from "@/composables/useToast";
import { useModalShortcuts } from "@/composables/useModalShortcuts";
import BarcodeScanner from "@/components/BarcodeScanner.vue";

const { showSuccess, showError, showInfo, showInfoLink } = useToast();

const API = "easy_entry.api.item_manager";
const pageSize = 20;

// --- Label print -----------------------------------------------------------

const labelFormat = ref("50 * 25");
const settingsModal = reactive({ open: false, busy: false, formats: [], selected: "" });

function printLabel(row) {
	const params = new URLSearchParams({
		doctype: "Item",
		name: row.item_code,
		trigger_print: "1",
		format: labelFormat.value,
		no_letterhead: "1",
		pdf_generator: "wkhtmltopdf",
	});
	window.open(`/printview?${params.toString()}`, "_blank");
}

function openSettings() {
	settingsModal.open = true;
	settingsModal.selected = labelFormat.value;
	settingsModal.busy = false;
}

async function saveSettings() {
	if (settingsModal.busy) return;
	settingsModal.busy = true;
	try {
		await call(`${API}.set_label_print_format`, { fmt: settingsModal.selected });
		labelFormat.value = settingsModal.selected;
		showSuccess(__("Default print format saved"));
		settingsModal.open = false;
	} catch (e) {
		showError(errorMessage(e) || __("Failed to save settings"));
		settingsModal.busy = false;
	}
}

const searchQuery = ref("");
const itemGroupFilter = ref("");
const supplierFilter = ref("");
const stockFilter = ref("");
const priceFilter = ref("");
const currentPage = ref(0);
const showFilters = ref(false);
const searchInputEl = ref(null);
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
		item_group: row.item_group,
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

const EDITABLE_FIELDS = ["item_name", "supplier", "item_group", "buying_price", "selling_price"];

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

// --- Camera scanner -------------------------------------------------------

const showScanner = ref(false);

function onCameraScanned(code) {
	showScanner.value = false;
	searchQuery.value = code;
	onBarcodeScan();
}

// --- Search / pagination -------------------------------------------------

function onSearchInput() {
	clearTimeout(searchTimer);
	searchTimer = setTimeout(reloadFirstPage, 300);
}

async function onBarcodeScan() {
	const code = searchQuery.value.trim();
	if (!code) return;
	try {
		const res = await call(`${API}.get_items`, {
			search: code,
			limit: 2,
			offset: 0,
		});
		const found = res?.rows ?? [];
		if (found.length === 0) {
			showError(__("No item found for: {0}", [code]));
		} else if (found.length > 1) {
			showInfo(__('Multiple items match "{0}" — be more specific.', [code]));
		} else {
			// Exactly one match → open qty modal.
			const row = found[0];
			// Merge into current rows or use the raw result directly.
			searchQuery.value = "";
			openQty(row);
		}
	} catch (e) {
		showError(errorMessage(e) || __("Barcode lookup failed"));
	}
}

function reloadFirstPage() {
	currentPage.value = 0;
	items.reload();
}

const hasActiveFilters = computed(
	() => !!(itemGroupFilter.value || supplierFilter.value || stockFilter.value || priceFilter.value),
);

const activeFilterCount = computed(
	() =>
		[itemGroupFilter.value, supplierFilter.value, stockFilter.value, priceFilter.value].filter(Boolean)
			.length,
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

// Refresh the current page from the server. Reloading rewrites the dirty
// baseline, so warn before discarding any unsaved row edits.
function refreshItems() {
	if (dirtyRows.value.length) {
		const ok = window.confirm(
			__("You have {0} unsaved change(s). Discard them and refresh?", [
				dirtyRows.value.length,
			]),
		);
		if (!ok) return;
	}
	items.reload();
}

// --- Saving --------------------------------------------------------------

async function saveRow(row) {
	if (!isRowDirty(row) || saving[row.item_code]) return;
	saving[row.item_code] = true;
	try {
		const base = original[row.item_code];

		// 1. Name, supplier and/or item_group in a single update_item call.
		const fields = {};
		if (isFieldDirty(row, "item_name")) fields.item_name = row.item_name;
		if (isFieldDirty(row, "supplier")) fields.supplier = row.supplier;
		if (isFieldDirty(row, "item_group")) fields.item_group = row.item_group;
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

const qtyModal = reactive({ row: null, qty: 0, submit: false, busy: false });

function openQty(row) {
	qtyModal.row = row;
	qtyModal.qty = Number(row.qty || 0);
	qtyModal.submit = false; // draft is always the default starting point
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
			submit: qtyModal.submit ? 1 : 0,
		});
		// docstatus 1 means the SR was submitted; 0 means it stayed a draft.
		if (res.docstatus === 1) {
			showSuccess(
				__("Stock Reconciliation {0} submitted — stock updated.", [
					res.stock_reconciliation,
				]),
			);
		} else {
			showInfoLink(
				__("Draft Stock Reconciliation {0} created.", [res.stock_reconciliation]),
				{
					url: `/app/stock-reconciliation/${res.stock_reconciliation}`,
					label: __("Open in desk"),
				},
			);
		}
		qtyModal.row = null;
	} catch (e) {
		showError(errorMessage(e) || __("Could not set quantity"));
		qtyModal.busy = false;
	}
}

// Esc + Ctrl+S inside each popup. Enter is handled on the inputs themselves.
useModalShortcuts(() => !!renameModal.row, {
	onSave: confirmRename,
	onCancel: () => (renameModal.row = null),
});
useModalShortcuts(() => !!qtyModal.row, {
	onSave: confirmQty,
	onCancel: () => (qtyModal.row = null),
});
useModalShortcuts(() => settingsModal.open, {
	onSave: saveSettings,
	onCancel: () => (settingsModal.open = false),
});

// --- Page-level shortcuts ------------------------------------------------

function isTyping(target) {
	if (!target) return false;
	const tag = target.tagName;
	return tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || target.isContentEditable;
}

function handlePageKeydown(event) {
	// A popup owns the keyboard while open — let useModalShortcuts handle it.
	if (renameModal.row || qtyModal.row || settingsModal.open) return;

	// "/" jumps to the search box, unless the user is already typing.
	if (event.key === "/" && !isTyping(event.target)) {
		event.preventDefault();
		searchInputEl.value?.focus();
		return;
	}

	// F4 focuses the search box — works even while typing in another field,
	// since a function key can't be a literal text character.
	if (event.key === "F4") {
		event.preventDefault();
		searchInputEl.value?.focus();
		return;
	}

	// F5 refreshes the current page. preventDefault stops the browser's own
	// hard reload so the SPA reloads its data in place instead.
	if (event.key === "F5") {
		event.preventDefault();
		if (!items.loading) refreshItems();
		return;
	}

	// Ctrl+S saves every dirty row at once.
	if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
		event.preventDefault();
		if (dirtyRows.value.length && !savingAll.value) saveAll();
	}
}

onMounted(async () => {
	window.addEventListener("keydown", handlePageKeydown);
	try {
		const res = await call(`${API}.get_label_settings`);
		labelFormat.value = res.default_format || "50 * 25";
		settingsModal.formats = res.formats || [];
	} catch {
		settingsModal.formats = ["Standard", "50 * 25", "38 * 25"];
	}
});
onUnmounted(() => window.removeEventListener("keydown", handlePageKeydown));

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
