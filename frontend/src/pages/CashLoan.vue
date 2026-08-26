<template>
	<div class="flex-1 min-h-0 bg-gray-50 flex flex-col">
		<!-- Header -->
		<header
			class="bg-white border-b border-gray-200 px-4 py-3 sm:px-6 sm:py-4 flex items-center justify-between flex-wrap gap-2 sm:gap-3"
		>
			<div>
				<h1 class="text-lg font-semibold text-gray-900">{{ __("Cash Loans") }}</h1>
				<p class="text-xs text-gray-500 hidden sm:block">
					{{ __("Track informal cash advances — no interest, no schedule, full repayment only.") }}
				</p>
			</div>
			<div class="flex items-center gap-2 sm:gap-3">
				<span v-if="loans.data" class="text-sm text-gray-500 whitespace-nowrap">
					{{ __("Open: {0}", [formatCurrency(loans.data.open_total)]) }}
				</span>
				<button
					class="px-3 py-2 rounded-lg text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 flex items-center gap-1.5"
					data-testid="give-loan-btn"
					@click="openGive"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
					</svg>
					{{ __("Give Loan") }}
				</button>
			</div>
		</header>

		<!-- Toolbar -->
		<div class="bg-white border-b border-gray-200 px-4 sm:px-6 py-3 flex items-center gap-2 sm:gap-3 flex-wrap">
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
					:placeholder="__('Search by borrower or loan ID...')"
					class="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
					data-testid="search-input"
					@input="onSearchInput()"
				/>
			</div>

			<select
				v-model="statusFilter"
				class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
				data-testid="status-filter"
				@change="reloadFirstPage"
			>
				<option value="">{{ __("All statuses") }}</option>
				<option value="Open">{{ __("Open") }}</option>
				<option value="Repaid">{{ __("Repaid") }}</option>
			</select>

			<span class="text-xs text-gray-400 whitespace-nowrap hidden sm:inline ml-auto">
				{{ __("Shortcuts: N give loan · F4 search") }}
			</span>
		</div>

		<!-- Table -->
		<div class="flex-1 overflow-auto">
			<table v-if="loans.loading" class="w-full text-sm">
				<tbody>
					<tr v-for="n in pageSize" :key="n" class="border-b border-gray-100">
						<td v-for="c in 6" :key="c" class="px-6 py-4">
							<div class="h-4 bg-gray-100 rounded animate-pulse"></div>
						</td>
					</tr>
				</tbody>
			</table>

			<div
				v-else-if="loans.error"
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
				<p class="text-sm">{{ __("Failed to load loans") }}</p>
				<button class="mt-2 text-sm text-blue-600 hover:underline" @click="loans.reload()">
					{{ __("Retry") }}
				</button>
			</div>

			<div
				v-else-if="!rows.length"
				class="flex flex-col items-center justify-center py-24 text-gray-400"
			>
				<svg class="w-14 h-14 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="1.5"
						d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V6m0 10v2m9-8a9 9 0 11-18 0 9 9 0 0118 0z"
					/>
				</svg>
				<p class="text-sm">
					{{ searchQuery ? __("No loans match your search") : __("No cash loans yet") }}
				</p>
			</div>

			<table v-else class="w-full text-sm" data-testid="loan-table">
				<thead class="bg-gray-50 border-b border-gray-200 sticky top-0 z-10">
					<tr class="text-left text-gray-500 uppercase tracking-wider text-xs">
						<th class="px-4 py-3">{{ __("Borrower") }}</th>
						<th class="px-4 py-3 w-32 text-right">{{ __("Amount") }}</th>
						<th class="px-4 py-3 w-28">{{ __("Status") }}</th>
						<th class="px-4 py-3 w-32">{{ __("Loan Date") }}</th>
						<th class="px-4 py-3 w-32">{{ __("Repaid Date") }}</th>
						<th class="px-4 py-3 w-32 text-center">{{ __("Action") }}</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-100 bg-white">
					<tr
						v-for="(row, idx) in rows"
						:key="row.name"
						class="hover:bg-gray-50 transition-colors"
						:data-testid="`loan-row-${idx}`"
					>
						<td class="px-4 py-3">
							<div class="font-medium text-gray-900">{{ row.customer_name || row.borrower }}</div>
							<div class="text-xs text-gray-400">{{ row.name }} · {{ row.borrower }}</div>
						</td>
						<td class="px-4 py-3 text-right tabular-nums">{{ formatCurrency(row.amount) }}</td>
						<td class="px-4 py-3">
							<span
								class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
								:class="row.status === 'Open' ? 'bg-amber-50 text-amber-600' : 'bg-green-50 text-green-600'"
							>
								{{ row.status === "Open" ? __("Open") : __("Repaid") }}
							</span>
						</td>
						<td class="px-4 py-3 text-gray-500">{{ row.loan_date }}</td>
						<td class="px-4 py-3 text-gray-500">{{ row.repaid_date || "—" }}</td>
						<td class="px-4 py-3 text-center">
							<button
								v-if="row.status === 'Open'"
								class="text-xs px-2.5 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
								:data-testid="`repay-btn-${idx}`"
								@click="openRepay(row)"
							>
								{{ __("Repay") }}
							</button>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Pagination -->
		<div
			v-if="(loans.data?.total ?? 0) > pageSize"
			class="bg-white border-t border-gray-200 px-4 sm:px-6 py-3 flex items-center justify-between"
		>
			<span class="text-sm text-gray-500">
				{{
					__("Showing {0}–{1} of {2}", [
						offset + 1,
						Math.min(offset + pageSize, loans.data.total),
						loans.data.total,
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
					:disabled="offset + pageSize >= loans.data.total"
					@click="goToPage(currentPage + 1)"
				>
					{{ __("Next") }}
				</button>
			</div>
		</div>

		<!-- Give loan modal -->
		<div
			v-if="giveModal.open"
			class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
			@click.self="giveModal.open = false"
		>
			<div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6" data-testid="give-modal">
				<h2 class="text-base font-semibold text-gray-900">{{ __("Give a cash loan") }}</h2>
				<p class="text-sm text-gray-500 mt-1">
					{{ __("Records the cash leaving the register as a receivable — never a sale.") }}
				</p>

				<label class="block text-xs font-medium text-gray-500 mt-4 mb-1">
					{{ __("Borrower") }}
				</label>
				<select
					ref="giveBorrowerEl"
					v-model="giveModal.borrower"
					class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
					data-testid="give-borrower-select"
				>
					<option value="" disabled>{{ __("Select a customer...") }}</option>
					<option v-for="c in customers.data || []" :key="c.name" :value="c.name">
						{{ c.customer_name }}
					</option>
				</select>

				<label class="block text-xs font-medium text-gray-500 mt-4 mb-1">{{ __("Amount") }}</label>
				<input
					v-model.number="giveModal.amount"
					type="number"
					min="0"
					step="0.01"
					class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
					data-testid="give-amount-input"
				/>

				<label class="block text-xs font-medium text-gray-500 mt-4 mb-1">
					{{ __("Mode of payment (given from)") }}
				</label>
				<select
					v-model="giveModal.modeOfPayment"
					class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
					data-testid="give-mop-select"
				>
					<option v-for="m in modesOfPayment.data || []" :key="m.name" :value="m.name">
						{{ m.name }}
					</option>
				</select>

				<label class="block text-xs font-medium text-gray-500 mt-4 mb-1">
					{{ __("Remarks (optional)") }}
				</label>
				<textarea
					v-model="giveModal.remarks"
					rows="2"
					class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
					data-testid="give-remarks-input"
				></textarea>

				<div class="flex items-center justify-between gap-2 mt-5">
					<span class="text-xs text-gray-400">{{ __("Ctrl+S to save · Esc to cancel") }}</span>
					<div class="flex gap-2">
						<button
							class="px-3 py-2 rounded-lg text-sm border border-gray-300 hover:bg-gray-50"
							@click="giveModal.open = false"
						>
							{{ __("Cancel") }}
						</button>
						<button
							class="px-3 py-2 rounded-lg text-sm bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
							:disabled="giveModal.busy || !canConfirmGive"
							data-testid="give-confirm"
							@click="confirmGive"
						>
							{{ giveModal.busy ? __("Saving...") : __("Give loan") }}
						</button>
					</div>
				</div>
			</div>
		</div>

		<!-- Repay modal -->
		<div
			v-if="repayModal.row"
			class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
			@click.self="repayModal.row = null"
		>
			<div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6" data-testid="repay-modal">
				<h2 class="text-base font-semibold text-gray-900">{{ __("Repay loan") }}</h2>
				<p class="text-sm text-gray-500 mt-1">
					{{
						__("{0} repays {1} in full. This closes the loan — partial repayment is not supported.", [
							repayModal.row.customer_name || repayModal.row.borrower,
							formatCurrency(repayModal.row.amount),
						])
					}}
				</p>

				<label class="block text-xs font-medium text-gray-500 mt-4 mb-1">
					{{ __("Mode of payment (repaid into)") }}
				</label>
				<select
					v-model="repayModal.modeOfPayment"
					class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
					data-testid="repay-mop-select"
				>
					<option v-for="m in modesOfPayment.data || []" :key="m.name" :value="m.name">
						{{ m.name }}
					</option>
				</select>

				<div class="flex items-center justify-between gap-2 mt-5">
					<span class="text-xs text-gray-400">{{ __("Ctrl+S to save · Esc to cancel") }}</span>
					<div class="flex gap-2">
						<button
							class="px-3 py-2 rounded-lg text-sm border border-gray-300 hover:bg-gray-50"
							@click="repayModal.row = null"
						>
							{{ __("Cancel") }}
						</button>
						<button
							class="px-3 py-2 rounded-lg text-sm bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
							:disabled="repayModal.busy || !repayModal.modeOfPayment"
							data-testid="repay-confirm"
							@click="confirmRepay"
						>
							{{ repayModal.busy ? __("Saving...") : __("Mark repaid") }}
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { call, createResource } from "frappe-ui";
import { computed, nextTick, onMounted, onUnmounted, reactive, ref } from "vue";
import { useToast } from "@/composables/useToast";
import { useModalShortcuts } from "@/composables/useModalShortcuts";

const { showSuccess, showError, showInfo } = useToast();

const API = "easy_entry.api.cash_loan";
const pageSize = 20;

const searchQuery = ref("");
const statusFilter = ref("");
const currentPage = ref(0);
const searchInputEl = ref(null);
let searchTimer = null;

const offset = computed(() => currentPage.value * pageSize);

const modesOfPayment = createResource({
	url: `${API}.get_modes_of_payment`,
	auto: true,
});

const customers = createResource({
	url: "frappe.client.get_list",
	params: {
		doctype: "Customer",
		fields: ["name", "customer_name"],
		limit_page_length: 0,
		order_by: "customer_name asc",
	},
	auto: true,
});

const loans = createResource({
	url: `${API}.list_loans`,
	makeParams() {
		return {
			search: searchQuery.value,
			status: statusFilter.value,
			limit: pageSize,
			offset: offset.value,
		};
	},
	auto: true,
});

const rows = computed(() => loans.data?.rows ?? []);

function formatCurrency(value) {
	return Number(value || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function onSearchInput() {
	clearTimeout(searchTimer);
	searchTimer = setTimeout(reloadFirstPage, 300);
}

function reloadFirstPage() {
	currentPage.value = 0;
	loans.reload();
}

function goToPage(page) {
	currentPage.value = page;
	loans.reload();
}

// --- Give loan -------------------------------------------------------------

const giveModal = reactive({
	open: false,
	borrower: "",
	amount: null,
	modeOfPayment: "",
	remarks: "",
	busy: false,
});
const giveBorrowerEl = ref(null);

const canConfirmGive = computed(
	() => giveModal.borrower && Number(giveModal.amount) > 0 && giveModal.modeOfPayment,
);

function openGive() {
	giveModal.open = true;
	giveModal.borrower = "";
	giveModal.amount = null;
	giveModal.modeOfPayment = modesOfPayment.data?.[0]?.name || "";
	giveModal.remarks = "";
	giveModal.busy = false;
	nextTick(() => giveBorrowerEl.value?.focus());
}

async function confirmGive() {
	if (!canConfirmGive.value || giveModal.busy) return;
	giveModal.busy = true;
	try {
		const res = await call(`${API}.give_loan`, {
			borrower: giveModal.borrower,
			amount: giveModal.amount,
			mode_of_payment: giveModal.modeOfPayment,
			remarks: giveModal.remarks || null,
		});
		const customerName =
			customers.data?.find((c) => c.name === giveModal.borrower)?.customer_name || giveModal.borrower;
		showSuccess(__("Loan {0} given to {1}", [res.name, customerName]));
		giveModal.open = false;
		reloadFirstPage();
	} catch (e) {
		showError(errorMessage(e) || __("Could not give loan"));
		giveModal.busy = false;
	}
}

// --- Repay -------------------------------------------------------------

const repayModal = reactive({ row: null, modeOfPayment: "", busy: false });

function openRepay(row) {
	repayModal.row = row;
	repayModal.modeOfPayment = modesOfPayment.data?.[0]?.name || "";
	repayModal.busy = false;
}

async function confirmRepay() {
	const row = repayModal.row;
	if (!row || !repayModal.modeOfPayment || repayModal.busy) return;
	repayModal.busy = true;
	try {
		await call(`${API}.repay_loan`, { name: row.name, mode_of_payment: repayModal.modeOfPayment });
		showInfo(__("Loan {0} closed — repaid in full.", [row.name]));
		repayModal.row = null;
		loans.reload();
	} catch (e) {
		showError(errorMessage(e) || __("Could not repay loan"));
		repayModal.busy = false;
	}
}

// --- Shortcuts ---------------------------------------------------------

useModalShortcuts(() => giveModal.open, {
	onSave: confirmGive,
	onCancel: () => (giveModal.open = false),
});
useModalShortcuts(() => !!repayModal.row, {
	onSave: confirmRepay,
	onCancel: () => (repayModal.row = null),
});

function isTyping(target) {
	if (!target) return false;
	const tag = target.tagName;
	return tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || target.isContentEditable;
}

function handlePageKeydown(event) {
	if (giveModal.open || repayModal.row) return;

	if (event.key === "/" && !isTyping(event.target)) {
		event.preventDefault();
		searchInputEl.value?.focus();
		return;
	}
	if (event.key === "F4") {
		event.preventDefault();
		searchInputEl.value?.focus();
		return;
	}
	if (event.key.toLowerCase() === "n" && !isTyping(event.target)) {
		event.preventDefault();
		openGive();
	}
}

onMounted(() => window.addEventListener("keydown", handlePageKeydown));
onUnmounted(() => window.removeEventListener("keydown", handlePageKeydown));

// --- Errors --------------------------------------------------------------

function errorMessage(e) {
	if (!e) return "";
	if (Array.isArray(e.messages) && e.messages.length) return e.messages.join(", ");
	return e.message || String(e);
}
</script>
