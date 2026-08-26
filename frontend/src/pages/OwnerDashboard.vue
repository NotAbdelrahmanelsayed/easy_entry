<template>
	<div class="flex-1 min-h-0 bg-gray-50 overflow-auto">
		<!-- Permission lock — full page, no retry -->
		<div
			v-if="isPermissionError"
			class="flex flex-col items-center justify-center py-24 text-gray-500 px-6"
			data-testid="owner-dashboard-lock"
		>
			<svg class="w-14 h-14 mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="1.5"
					d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
				/>
			</svg>
			<p class="text-sm font-medium text-gray-700">
				{{ __("You need the Store Owner role to view this dashboard.") }}
			</p>
			<router-link :to="{ name: 'Dashboard' }" class="mt-3 text-sm text-blue-600 hover:underline">
				{{ __("Back to Dashboard") }}
			</router-link>
		</div>

		<div v-else class="px-4 py-6 sm:px-6 sm:py-8 max-w-5xl mx-auto w-full">
			<!-- Header + period selector -->
			<div class="mb-6 flex items-start justify-between flex-wrap gap-3">
				<div>
					<h1 class="text-xl font-semibold text-gray-900">{{ __("Owner Dashboard") }}</h1>
					<p class="text-sm text-gray-500 mt-1">
						{{ __("Sales, profit, receivables and low-stock alerts at a glance.") }}
					</p>
				</div>
				<div class="flex flex-col items-end gap-2">
					<div class="flex items-center gap-2">
						<div class="inline-flex rounded-lg border border-gray-200 bg-white p-1" data-testid="period-selector">
							<button
								v-for="opt in PERIODS"
								:key="opt.value"
								class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
								:class="
									period === opt.value
										? 'bg-blue-600 text-white'
										: 'text-gray-600 hover:bg-gray-50'
								"
								:data-testid="`period-${opt.value}`"
								@click="selectPeriod(opt.value)"
							>
								{{ opt.label }}
							</button>
						</div>
						<button
							class="px-3 py-2 rounded-lg text-sm font-medium border border-gray-300 text-gray-700 hover:bg-gray-50 hover:border-blue-400 hover:text-blue-600 active:scale-95 transition flex items-center gap-1.5 disabled:opacity-50"
							:disabled="isRefreshing"
							:title="__('Refresh dashboard')"
							data-testid="refresh-dashboard-btn"
							@click="refreshDashboard"
						>
							<svg
								class="w-4 h-4"
								:class="{ 'animate-spin': isRefreshing }"
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
							<span class="hidden sm:inline">
								{{ isRefreshing ? __("Refreshing...") : __("Refresh") }}
							</span>
						</button>
					</div>
					<div v-if="period === 'custom'" class="flex items-center gap-2" data-testid="custom-range">
						<input
							v-model="customFrom"
							type="date"
							:max="customTo || undefined"
							class="border border-gray-300 rounded-lg px-2.5 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
							data-testid="custom-from"
						/>
						<span class="text-gray-400 text-sm">{{ __("to") }}</span>
						<input
							v-model="customTo"
							type="date"
							:min="customFrom || undefined"
							:max="todayStr"
							class="border border-gray-300 rounded-lg px-2.5 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
							data-testid="custom-to"
						/>
					</div>
				</div>
			</div>

			<!-- KPI row -->
			<div class="grid grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4">
				<template v-if="dashboard.loading && !dashboard.data">
					<div v-for="n in 5" :key="n" class="bg-white rounded-xl border border-gray-200 p-4">
						<div class="h-3 w-20 bg-gray-100 rounded animate-pulse"></div>
						<div class="h-6 w-28 bg-gray-100 rounded animate-pulse mt-3"></div>
					</div>
				</template>
				<template v-else-if="dashboard.data">
					<div class="bg-white rounded-xl border border-gray-200 p-4">
						<p class="text-xs text-gray-500">{{ __("Total Sales") }}</p>
						<p class="text-lg font-semibold text-gray-900 mt-1 tabular-nums">
							{{ formatCurrency(dashboard.data.kpis.total_sales, currency) }}
						</p>
					</div>
					<div class="bg-white rounded-xl border border-gray-200 p-4">
						<p class="text-xs text-gray-500">{{ __("Gross Profit") }}</p>
						<p
							class="text-lg font-semibold mt-1 tabular-nums"
							:class="dashboard.data.kpis.gross_profit > 0 ? 'text-green-600' : 'text-gray-900'"
						>
							{{ formatCurrency(dashboard.data.kpis.gross_profit, currency) }}
						</p>
					</div>
					<div class="bg-white rounded-xl border border-gray-200 p-4">
						<p class="text-xs text-gray-500">{{ __("Invoices") }}</p>
						<p class="text-lg font-semibold text-gray-900 mt-1 tabular-nums">
							{{ dashboard.data.kpis.invoice_count.toLocaleString() }}
						</p>
					</div>
					<div class="bg-white rounded-xl border border-gray-200 p-4">
						<p class="text-xs text-gray-500">{{ __("Collected") }}</p>
						<p class="text-lg font-semibold text-gray-900 mt-1 tabular-nums">
							{{ formatCurrency(dashboard.data.kpis.total_collected, currency) }}
						</p>
					</div>
					<div class="bg-white rounded-xl border border-gray-200 p-4">
						<p class="text-xs text-gray-500">{{ __("Credit") }}</p>
						<p
							class="text-lg font-semibold mt-1 tabular-nums"
							:class="dashboard.data.kpis.total_credit > 0 ? 'text-red-600' : 'text-gray-900'"
						>
							{{ formatCurrency(dashboard.data.kpis.total_credit, currency) }}
						</p>
					</div>
				</template>
				<div v-else-if="dashboard.error" class="col-span-2 lg:col-span-5">
					<ErrorCard :message="__('Failed to load KPIs')" @retry="dashboard.reload()" />
				</div>
			</div>

			<!-- Trend chart -->
			<div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5 mt-4 sm:mt-6">
				<h2 class="font-semibold text-gray-900 text-sm">{{ __("Last 30 days") }}</h2>
				<div class="h-72 mt-2">
					<div v-if="staticData.loading && !staticData.data" class="h-full bg-gray-50 rounded-lg animate-pulse"></div>
					<ErrorCard
						v-else-if="staticData.error"
						:message="__('Failed to load trend')"
						@retry="staticData.reload()"
					/>
					<AxisChart v-else-if="trendConfig" :config="trendConfig" />
				</div>
			</div>

			<!-- Weekday performance -->
			<div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5 mt-4 sm:mt-6">
				<h2 class="font-semibold text-gray-900 text-sm">{{ __("Performance by weekday") }}</h2>
				<p class="text-xs text-gray-500 mt-0.5">
					{{ __("Average sales & profit per day, last {0} days", [90]) }}
				</p>
				<div class="h-64 mt-2">
					<div v-if="staticData.loading && !staticData.data" class="h-full bg-gray-50 rounded-lg animate-pulse"></div>
					<ErrorCard
						v-else-if="staticData.error"
						:message="__('Failed to load weekday trend')"
						@retry="staticData.reload()"
					/>
					<AxisChart v-else-if="weekdayConfig" :config="weekdayConfig" />
				</div>
			</div>

			<!-- Best sellers + Receivables -->
			<div class="grid lg:grid-cols-2 gap-4 sm:gap-6 mt-4 sm:mt-6">
				<!-- Best sellers -->
				<div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5">
					<div class="flex items-center justify-between mb-3 gap-2 flex-wrap">
						<h2 class="font-semibold text-gray-900 text-sm">{{ __("Best sellers") }}</h2>
						<div class="inline-flex rounded-lg border border-gray-200 p-0.5">
							<button
								class="px-2.5 py-1 rounded-md text-xs font-medium"
								:class="sortBy === 'gross_profit' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'"
								data-testid="sort-by-profit"
								@click="sortBy = 'gross_profit'"
							>
								{{ __("By profit") }}
							</button>
							<button
								class="px-2.5 py-1 rounded-md text-xs font-medium"
								:class="sortBy === 'qty' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'"
								data-testid="sort-by-qty"
								@click="sortBy = 'qty'"
							>
								{{ __("By qty") }}
							</button>
						</div>
					</div>

					<!-- Item / item-group filters -->
					<div class="flex items-center gap-2 mb-3">
						<select
							v-model="itemGroupFilter"
							class="flex-1 min-w-0 border border-gray-300 rounded-lg px-2.5 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
							data-testid="item-group-filter"
						>
							<option value="">{{ __("All item groups") }}</option>
							<option v-for="g in itemGroups.data || []" :key="g.name" :value="g.name">
								{{ g.name }}
							</option>
						</select>
						<input
							v-model="itemSearch"
							type="text"
							:placeholder="__('Search item...')"
							class="flex-1 min-w-0 border border-gray-300 rounded-lg px-2.5 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
							data-testid="item-search-filter"
						/>
						<button
							v-if="itemGroupFilter || itemSearch"
							class="text-xs text-blue-600 hover:underline whitespace-nowrap"
							data-testid="clear-item-filters"
							@click="clearItemFilters"
						>
							{{ __("Clear") }}
						</button>
					</div>

					<div v-if="dashboard.loading && !dashboard.data" class="space-y-2">
						<div v-for="n in 5" :key="n" class="h-8 bg-gray-50 rounded animate-pulse"></div>
					</div>
					<ErrorCard
						v-else-if="dashboard.error"
						:message="__('Failed to load best sellers')"
						@retry="dashboard.reload()"
					/>
					<p v-else-if="!bestItems.length" class="text-sm text-gray-400 py-8 text-center">
						{{ itemGroupFilter || itemSearch ? __("No matching items in this period") : __("No sales in this period") }}
					</p>
					<table v-else class="w-full text-sm">
						<thead>
							<tr class="text-left text-gray-400 text-xs uppercase tracking-wider">
								<th class="py-1.5 font-medium">{{ __("Item") }}</th>
								<th class="py-1.5 font-medium text-right">{{ __("Qty") }}</th>
								<th class="py-1.5 font-medium text-right">{{ __("Profit") }}</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-100">
							<tr v-for="row in bestItems" :key="row.item_code">
								<td class="py-2 text-gray-800 truncate max-w-[10rem]">{{ row.item_name }}</td>
								<td class="py-2 text-right tabular-nums text-gray-600">{{ Number(row.qty_sold).toLocaleString() }}</td>
								<td class="py-2 text-right tabular-nums font-medium text-gray-900">
									{{ formatCurrency(row.gross_profit, currency, 2) }}
								</td>
							</tr>
						</tbody>
					</table>
				</div>

				<!-- Receivables -->
				<div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5">
					<h2 class="font-semibold text-gray-900 text-sm mb-3">{{ __("Receivables") }}</h2>
					<div v-if="staticData.loading && !staticData.data" class="space-y-2">
						<div class="h-8 bg-gray-50 rounded animate-pulse w-1/2"></div>
						<div v-for="n in 4" :key="n" class="h-7 bg-gray-50 rounded animate-pulse"></div>
					</div>
					<ErrorCard
						v-else-if="staticData.error"
						:message="__('Failed to load receivables')"
						@retry="staticData.reload()"
					/>
					<template v-else-if="staticData.data">
						<template v-if="staticData.data.receivables.customer_count">
							<p class="text-2xl font-semibold text-red-600 tabular-nums">
								{{ formatCurrency(staticData.data.receivables.total_outstanding, currency) }}
							</p>
							<p class="text-xs text-gray-500 mt-1">
								{{ __("{0} customers owe you", [staticData.data.receivables.customer_count]) }}
							</p>
							<ul class="mt-3 divide-y divide-gray-100">
								<li
									v-for="row in staticData.data.receivables.top_debtors"
									:key="row.customer"
									class="flex items-center justify-between py-1.5 text-sm"
								>
									<span class="text-gray-700 truncate max-w-[10rem]">{{ row.customer_name }}</span>
									<span class="tabular-nums font-medium text-gray-900">
										{{ formatCurrency(row.total_outstanding, currency, 2) }}
									</span>
								</li>
							</ul>
						</template>
						<p v-else class="text-sm text-green-600 py-8 text-center">
							{{ __("No outstanding receivables") }}
						</p>
					</template>
				</div>
			</div>

			<!-- Low stock -->
			<div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5 mt-4 sm:mt-6 mb-6">
				<div class="flex items-center justify-between mb-3">
					<h2 class="font-semibold text-gray-900 text-sm">{{ __("Low stock") }}</h2>
					<span
						v-if="staticData.data?.low_stock?.count"
						class="text-xs font-medium bg-red-50 text-red-600 rounded-full px-2 py-0.5"
					>
						{{ staticData.data.low_stock.count }}
					</span>
				</div>

				<div v-if="staticData.loading && !staticData.data" class="space-y-2">
					<div v-for="n in 5" :key="n" class="h-8 bg-gray-50 rounded animate-pulse"></div>
				</div>
				<ErrorCard
					v-else-if="staticData.error"
					:message="__('Failed to load low stock items')"
					@retry="staticData.reload()"
				/>
				<template v-else-if="staticData.data">
					<p v-if="!staticData.data.low_stock.items.length" class="text-sm text-green-600 py-8 text-center">
						{{ __("All items above reorder level") }}
					</p>
					<template v-else>
						<div class="overflow-x-auto">
							<table class="w-full text-sm">
								<thead>
									<tr class="text-left text-gray-400 text-xs uppercase tracking-wider">
										<th class="py-1.5 font-medium">{{ __("Item") }}</th>
										<th class="py-1.5 font-medium">{{ __("Warehouse") }}</th>
										<th class="py-1.5 font-medium text-right">{{ __("On hand") }}</th>
										<th class="py-1.5 font-medium text-right">{{ __("Reorder level") }}</th>
										<th class="py-1.5 font-medium text-right">{{ __("Suggested qty") }}</th>
									</tr>
								</thead>
								<tbody class="divide-y divide-gray-100">
									<tr v-for="row in staticData.data.low_stock.items" :key="`${row.item_code}-${row.warehouse}`">
										<td class="py-2 text-gray-800 truncate max-w-[12rem]">{{ row.item_name }}</td>
										<td class="py-2 text-gray-500 truncate max-w-[8rem]">{{ row.warehouse }}</td>
										<td class="py-2 text-right tabular-nums text-red-600 font-medium">
											{{ Number(row.actual_qty).toLocaleString() }}
										</td>
										<td class="py-2 text-right tabular-nums text-gray-600">
											{{ Number(row.reorder_level).toLocaleString() }}
										</td>
										<td class="py-2 text-right tabular-nums text-gray-600">
											{{ Number(row.reorder_qty).toLocaleString() }}
										</td>
									</tr>
								</tbody>
							</table>
						</div>
						<p
							v-if="staticData.data.low_stock.count > staticData.data.low_stock.items.length"
							class="text-xs text-gray-400 mt-3"
						>
							{{
								__("Showing {0} of {1}", [
									staticData.data.low_stock.items.length,
									staticData.data.low_stock.count,
								])
							}}
						</p>
					</template>
				</template>
			</div>
		</div>
	</div>
</template>

<script setup>
import { AxisChart, createResource } from "frappe-ui";
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import ErrorCard from "@/components/ErrorCard.vue";

const API = "easy_entry.api.owner_dashboard";

const PERIODS = [
	{ value: "today", label: __("Today") },
	{ value: "yesterday", label: __("Yesterday") },
	{ value: "last_7_days", label: __("Last 7 days") },
	{ value: "this_month", label: __("This month") },
	{ value: "custom", label: __("Custom") },
];

const todayStr = new Date().toISOString().slice(0, 10);

function toDateStr(d) {
	return d.toISOString().slice(0, 10);
}

const period = ref("today");
const sortBy = ref("gross_profit");
// Default custom range to the last 7 days so the first custom request is valid immediately.
const customFrom = ref(toDateStr(new Date(Date.now() - 6 * 86400000)));
const customTo = ref(todayStr);
const itemGroupFilter = ref("");
const itemSearch = ref("");
let itemSearchTimer = null;

function selectPeriod(value) {
	period.value = value;
}

function clearItemFilters() {
	itemGroupFilter.value = "";
	itemSearch.value = "";
}

// True once a custom range has both ends filled in and from <= to.
const customRangeValid = computed(
	() => !!customFrom.value && !!customTo.value && customFrom.value <= customTo.value,
);

const itemGroups = createResource({
	url: "frappe.client.get_list",
	params: { doctype: "Item Group", fields: ["name"], limit_page_length: 0, order_by: "name asc" },
	auto: true,
});

const dashboard = createResource({
	url: `${API}.get_dashboard`,
	makeParams: () => ({
		period: period.value,
		sort_by: sortBy.value,
		item_group: itemGroupFilter.value,
		item_search: itemSearch.value,
		...(period.value === "custom" ? { from_date: customFrom.value, to_date: customTo.value } : {}),
	}),
	auto: true,
	onError(err) {
		if (isAuthError(err)) redirectToLogin();
	},
});

const staticData = createResource({
	url: `${API}.get_dashboard_static`,
	auto: true,
	onError(err) {
		if (isAuthError(err)) redirectToLogin();
	},
});

const isRefreshing = computed(() => dashboard.loading || staticData.loading);

function refreshDashboard() {
	if (isRefreshing.value) return;
	dashboard.reload();
	staticData.reload();
}

// Skip reloading while a custom range is only half-filled in.
watch([period, sortBy, customFrom, customTo, itemGroupFilter], () => {
	if (period.value === "custom" && !customRangeValid.value) return;
	dashboard.reload();
});

// Debounce the free-text item search so every keystroke doesn't fire a request.
watch(itemSearch, () => {
	clearTimeout(itemSearchTimer);
	itemSearchTimer = setTimeout(() => {
		if (period.value === "custom" && !customRangeValid.value) return;
		dashboard.reload();
	}, 300);
});

const bestItems = computed(() => dashboard.data?.best_items ?? []);
const currency = computed(() => dashboard.data?.currency ?? staticData.data?.currency ?? "EGP");

const isPermissionError = computed(
	() => dashboard.error?.exc_type === "PermissionError" || staticData.error?.exc_type === "PermissionError",
);

// AxisChart's series[].name doubles as the data-row key, so each row needs
// keys matching the translated series names exactly.
const SALES_KEY = __("Sales");
const PROFIT_KEY = __("Gross profit");

const trendConfig = computed(() => {
	const days = staticData.data?.trend?.days;
	if (!days) return null;
	return {
		data: days.map((d) => ({
			date: d.date,
			[SALES_KEY]: d.total_sales,
			[PROFIT_KEY]: d.gross_profit,
		})),
		xAxis: { key: "date", type: "time", timeGrain: "day" },
		yAxis: { title: "" },
		series: [
			{ name: SALES_KEY, type: "area", color: "#2563eb" },
			{ name: PROFIT_KEY, type: "line", color: "#16a34a" },
		],
	};
});

const AVG_SALES_KEY = __("Avg. sales");
const AVG_PROFIT_KEY = __("Avg. profit");

// Translated weekday labels, in the same Monday-first order the API returns.
const WEEKDAY_DISPLAY_LABELS = [
	__("Mon"),
	__("Tue"),
	__("Wed"),
	__("Thu"),
	__("Fri"),
	__("Sat"),
	__("Sun"),
];

const weekdayConfig = computed(() => {
	const days = staticData.data?.weekday_trend?.days;
	if (!days) return null;
	return {
		data: days.map((d, i) => ({
			weekday: WEEKDAY_DISPLAY_LABELS[i],
			[AVG_SALES_KEY]: d.avg_sales,
			[AVG_PROFIT_KEY]: d.avg_gross_profit,
		})),
		xAxis: { key: "weekday", type: "category" },
		yAxis: { title: "" },
		series: [
			{ name: AVG_SALES_KEY, type: "bar", color: "#2563eb" },
			{ name: AVG_PROFIT_KEY, type: "bar", color: "#16a34a" },
		],
	};
});

function formatCurrency(value, curr, fractionDigits = 0) {
	try {
		return new Intl.NumberFormat(undefined, {
			style: "currency",
			currency: curr,
			minimumFractionDigits: fractionDigits,
			maximumFractionDigits: fractionDigits,
		}).format(Number(value || 0));
	} catch {
		return Number(value || 0).toLocaleString();
	}
}

function isAuthError(e) {
	return e?.exc_type === "AuthenticationError";
}

function redirectToLogin() {
	const here = window.location.pathname + window.location.search;
	window.location.href = `/login?redirect-to=${encodeURIComponent(here)}`;
}

// --- Page-level shortcuts: 1-4 switch period ------------------------------

function isTyping(target) {
	if (!target) return false;
	const tag = target.tagName;
	return tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || target.isContentEditable;
}

function handlePageKeydown(event) {
	if (isTyping(event.target)) return;
	// Only the four fixed periods are keyboard-reachable; Custom needs date inputs.
	const idx = ["1", "2", "3", "4"].indexOf(event.key);
	if (idx !== -1) {
		event.preventDefault();
		selectPeriod(PERIODS[idx].value);
	}
}

onMounted(() => window.addEventListener("keydown", handlePageKeydown));
onUnmounted(() => window.removeEventListener("keydown", handlePageKeydown));
</script>
