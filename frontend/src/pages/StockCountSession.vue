<template>
	<div class="flex-1 min-h-0 bg-gray-50 flex flex-col">
		<!-- Sticky scan bar -->
		<div class="bg-white border-b border-gray-200 px-4 py-3 flex flex-col gap-2">
			<div class="flex items-center gap-2">
				<button
					class="flex items-center gap-1 text-sm text-gray-500 hover:text-blue-600"
					@click="$router.push({ name: 'StockCount' })"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M15 19l-7-7 7-7"
						/>
					</svg>
				</button>
				<span class="text-sm font-medium text-gray-900 truncate">{{ session }}</span>
				<span v-if="warehouse" class="text-xs text-gray-400 truncate">· {{ warehouse }}</span>
			</div>

			<div v-if="!isFinished" class="flex items-center gap-2">
				<input
					ref="scanInputEl"
					v-model="scanInput"
					type="text"
					:placeholder="__('Scan a barcode or type a code/name...')"
					class="flex-1 min-w-0 border border-gray-300 rounded-lg px-3 py-3 text-base focus:outline-none focus:ring-2 focus:ring-blue-500"
					data-testid="scan-input"
					autocomplete="off"
					autocapitalize="off"
					@keydown.enter.prevent="submitScan"
				/>
				<button
					class="flex-shrink-0 px-3 py-3 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
					data-testid="open-scanner"
					:aria-label="__('Scan with camera')"
					@click="showScanner = true"
				>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="1.8"
							d="M3 9V7a2 2 0 012-2h2M17 5h2a2 2 0 012 2v2M21 15v2a2 2 0 01-2 2h-2M7 19H5a2 2 0 01-2-2v-2M7 12h10"
						/>
					</svg>
				</button>
			</div>
			<p v-if="!isFinished" class="text-xs text-gray-400">
				{{ __("Enter to search · ? for shortcuts") }}
			</p>
		</div>

		<!-- Finished banner -->
		<div
			v-if="isFinished"
			class="bg-gray-100 border-b border-gray-200 px-4 py-2 text-xs text-gray-600"
		>
			{{ __("This session is finished.") }}
			<span v-if="stockReconciliation">
				{{ __("Stock Reconciliation {0} created.", [stockReconciliation]) }}
			</span>
		</div>

		<!-- Resolve → count panel -->
		<div
			v-if="pending.item"
			class="bg-blue-50 border-b border-blue-200 px-4 py-3 flex items-center gap-3"
			data-testid="count-panel"
		>
			<div class="min-w-0 flex-1">
				<p class="font-medium text-gray-900 truncate">{{ pending.item.item_name }}</p>
				<p class="text-xs text-gray-500 truncate">
					{{ pending.item.item_code }} ·
					{{ __("system {0}", [formatQty(pending.item.system_qty)]) }}
				</p>
			</div>
			<input
				ref="qtyInputEl"
				v-model="pending.qty"
				type="number"
				min="0"
				step="any"
				inputmode="decimal"
				:placeholder="__('Qty')"
				class="w-24 border border-gray-300 rounded-lg px-2 py-2 text-base text-right focus:outline-none focus:ring-2 focus:ring-blue-500"
				data-testid="count-qty"
				@keydown.enter.prevent="saveCount"
			/>
			<button
				class="px-3 py-2 rounded-lg text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
				:disabled="savingPending"
				data-testid="count-save"
				@click="saveCount"
			>
				{{ savingPending ? __("Saving...") : __("Add") }}
			</button>
			<button
				class="px-2 py-2 text-gray-400 hover:text-gray-700"
				:aria-label="__('Cancel')"
				@click="pending.item = null"
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

		<!-- Counted list -->
		<div class="flex-1 overflow-auto">
			<!-- Loading -->
			<div v-if="data.loading && !lines.length" class="p-4 flex flex-col gap-2">
				<div
					v-for="n in 5"
					:key="n"
					class="h-16 bg-white border border-gray-200 rounded-xl animate-pulse"
				></div>
			</div>

			<!-- Error -->
			<div
				v-else-if="data.error"
				class="flex flex-col items-center justify-center py-24 text-red-400 px-6 text-center"
			>
				<p class="text-sm">
					{{
						isAuthError(data.error)
							? __("Please log in to view this session")
							: __("Failed to load the session")
					}}
				</p>
				<button
					class="mt-2 text-sm text-blue-600 hover:underline"
					@click="isAuthError(data.error) ? redirectToLogin() : data.reload()"
				>
					{{ isAuthError(data.error) ? __("Log in") : __("Retry") }}
				</button>
			</div>

			<!-- Empty -->
			<div
				v-else-if="!lines.length"
				class="flex flex-col items-center justify-center py-24 text-gray-400 px-6 text-center"
			>
				<svg class="w-14 h-14 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="1.5"
						d="M12 4v16m8-8H4"
					/>
				</svg>
				<p class="text-sm">{{ __("Scan your first item to start counting.") }}</p>
			</div>

			<!-- Lines -->
			<ul v-else class="divide-y divide-gray-100 bg-white" data-testid="count-lines">
				<li
					v-for="(line, idx) in lines"
					:key="line.item_code"
					class="px-4 py-3 flex items-center gap-3"
					:data-testid="`count-line-${idx}`"
				>
					<div class="min-w-0 flex-1">
						<p class="font-medium text-gray-900 truncate">{{ line.item_name }}</p>
						<p class="text-xs text-gray-500 truncate">
							{{ line.item_code }} ·
							{{ __("system {0}", [formatQty(line.system_qty)]) }}
						</p>
						<p
							v-if="lineState[line.item_code]?.error"
							class="text-xs text-red-600 mt-1 flex items-center gap-1"
						>
							{{ lineState[line.item_code].error }}
							<button class="underline" @click="commitLine(line)">
								{{ __("Retry") }}
							</button>
						</p>
					</div>

					<input
						v-model="line.counted_qty"
						type="number"
						min="0"
						step="any"
						inputmode="decimal"
						:disabled="isFinished || lineState[line.item_code]?.saving"
						class="w-20 border border-gray-300 rounded-md px-2 py-2 text-base text-right focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-50"
						:data-testid="`line-qty-${idx}`"
						@keydown.enter.prevent="commitLine(line)"
						@blur="commitLine(line)"
					/>

					<span
						class="w-14 text-right text-sm font-medium tabular-nums"
						:class="diffClass(lineDiff(line))"
						:data-testid="`line-diff-${idx}`"
					>
						{{ formatDiff(lineDiff(line)) }}
					</span>

					<button
						v-if="!isFinished"
						class="px-1.5 py-2 text-gray-300 hover:text-red-500 disabled:opacity-40"
						:disabled="lineState[line.item_code]?.saving"
						:aria-label="__('Remove')"
						:data-testid="`line-remove-${idx}`"
						@click="deleteLine(line)"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
							/>
						</svg>
					</button>
				</li>
			</ul>
		</div>

		<!-- Footer -->
		<div
			v-if="!isFinished"
			class="bg-white border-t border-gray-200 px-4 py-3 flex items-center justify-between"
		>
			<span class="text-sm text-gray-500">
				{{ __("{0} item(s) counted", [lines.length]) }}
			</span>
			<button
				class="px-4 py-2.5 rounded-lg text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
				:disabled="!lines.length"
				data-testid="finish-count"
				@click="finishModal.open = true"
			>
				{{ __("Finish count") }}
			</button>
		</div>

		<!-- Camera scanner -->
		<BarcodeScanner
			v-if="showScanner"
			@scanned="onScanned"
			@close="showScanner = false"
		/>

		<!-- Finish confirmation -->
		<div
			v-if="finishModal.open"
			class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
			@click.self="finishModal.open = false"
		>
			<div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6" data-testid="finish-modal">
				<h2 class="text-base font-semibold text-gray-900">{{ __("Finish this count?") }}</h2>
				<p class="text-sm text-gray-500 mt-1">
					{{
						__(
							"A DRAFT Stock Reconciliation is created for items whose count differs from system stock. Stock changes only after someone reviews and submits it in the desk.",
						)
					}}
				</p>
				<div class="flex justify-end gap-2 mt-5">
					<button
						class="px-3 py-2 rounded-lg text-sm border border-gray-300 hover:bg-gray-50"
						@click="finishModal.open = false"
					>
						{{ __("Cancel") }}
					</button>
					<button
						class="px-3 py-2 rounded-lg text-sm bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
						:disabled="finishModal.busy"
						data-testid="finish-confirm"
						@click="confirmFinish"
					>
						{{ finishModal.busy ? __("Finishing...") : __("Finish count") }}
					</button>
				</div>
			</div>
		</div>

		<!-- Item picker — shown when a typed query matched several items -->
		<div
			v-if="pickerModal.open"
			class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
			@click.self="pickerModal.open = false"
		>
			<div
				class="bg-white rounded-xl shadow-xl w-full max-w-md p-6 flex flex-col max-h-[80vh]"
				data-testid="picker-modal"
			>
				<div class="flex items-start justify-between">
					<h2 class="text-base font-semibold text-gray-900">
						{{ __("Which item did you mean?") }}
					</h2>
					<button
						class="text-gray-400 hover:text-gray-700"
						:aria-label="__('Cancel')"
						@click="pickerModal.open = false"
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
				<ul class="mt-3 -mx-2 overflow-auto divide-y divide-gray-100">
					<li
						v-for="(match, idx) in pickerModal.matches"
						:key="match.item_code"
					>
						<button
							class="w-full text-left px-2 py-2.5 rounded-lg hover:bg-blue-50 flex items-center justify-between gap-3"
							:data-testid="`picker-option-${idx}`"
							@click="selectPickerItem(match)"
						>
							<span class="min-w-0">
								<span class="block font-medium text-gray-900 truncate">
									{{ match.item_name }}
								</span>
								<span class="block text-xs text-gray-500 truncate">
									{{ match.item_code }}
								</span>
							</span>
							<span class="text-xs text-gray-400 whitespace-nowrap">
								{{ __("system {0}", [formatQty(match.system_qty)]) }}
							</span>
						</button>
					</li>
				</ul>
				<p class="text-xs text-gray-400 mt-3">{{ __("Esc to cancel") }}</p>
			</div>
		</div>
	</div>
</template>

<script setup>
import { call, createResource } from "frappe-ui";
import { computed, nextTick, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import BarcodeScanner from "@/components/BarcodeScanner.vue";
import { useToast } from "@/composables/useToast";
import { useModalShortcuts } from "@/composables/useModalShortcuts";

const props = defineProps({ session: { type: String, required: true } });

const API = "easy_entry.api.stock_count";
const router = useRouter();
const { showSuccess, showError, showInfo } = useToast();

const lines = ref([]);
const warehouse = ref("");
const status = ref("In Progress");
const stockReconciliation = ref(null);

const scanInput = ref("");
const scanInputEl = ref(null);
const qtyInputEl = ref(null);
const resolving = ref(false);
const savingPending = ref(false);
const showScanner = ref(false);

// Resolve → count panel: the item awaiting a counted qty.
const pending = reactive({ item: null, qty: "" });
// Per-item-code inline-edit state: { saving, error }.
const lineState = reactive({});
const finishModal = reactive({ open: false, busy: false });
// Disambiguation picker shown when a typed query matches several items.
const pickerModal = reactive({ open: false, matches: [] });

const isFinished = computed(() => status.value === "Finished");

const data = createResource({
	url: `${API}.get_session`,
	makeParams() {
		return { name: props.session };
	},
	auto: true,
	onSuccess(payload) {
		lines.value = payload.lines || [];
		warehouse.value = payload.warehouse;
		status.value = payload.status;
		stockReconciliation.value = payload.stock_reconciliation;
	},
	onError(err) {
		if (isAuthError(err)) redirectToLogin();
	},
});

// --- Formatting ----------------------------------------------------------

function formatQty(qty) {
	return Number(qty || 0).toLocaleString();
}

function lineDiff(line) {
	return Number(line.counted_qty || 0) - Number(line.system_qty || 0);
}

function formatDiff(diff) {
	if (diff > 0) return `+${formatQty(diff)}`;
	return formatQty(diff);
}

function diffClass(diff) {
	if (diff > 0) return "text-green-600";
	if (diff < 0) return "text-red-600";
	return "text-gray-400";
}

// --- Scan → resolve ------------------------------------------------------

function onScanned(code) {
	showScanner.value = false;
	scanInput.value = code;
	submitScan();
}

async function submitScan() {
	const code = scanInput.value.trim();
	if (!code || resolving.value || isFinished.value) return;
	resolving.value = true;
	try {
		let item;
		try {
			// Fast path: an exact barcode/code match — the scanner stays instant.
			item = await call(`${API}.resolve_barcode`, {
				code,
				warehouse: warehouse.value,
			});
		} catch (resolveErr) {
			// Fallback: treat the input as a partial name/code/barcode query.
			const matches = await call(`${API}.search_items`, {
				query: code,
				warehouse: warehouse.value,
			});
			if (!matches.length) throw resolveErr; // keep the original "not found"
			if (matches.length === 1) {
				item = matches[0];
			} else {
				pickerModal.matches = matches;
				pickerModal.open = true;
				return; // the user picks one; usePendingItem runs from there
			}
		}
		usePendingItem(item);
	} catch (e) {
		showError(errorMessage(e) || __("Item not found"));
	} finally {
		resolving.value = false;
	}
}

// Move a resolved item into the count panel and focus its qty input.
function usePendingItem(item) {
	pending.item = item;
	// Re-scanning a counted item pre-fills its current count for correction.
	const existing = lines.value.find((l) => l.item_code === item.item_code);
	pending.qty = existing ? String(existing.counted_qty) : "";
	scanInput.value = "";
	nextTick(() => qtyInputEl.value?.focus());
}

// Picker → chosen item.
function selectPickerItem(item) {
	pickerModal.open = false;
	pickerModal.matches = [];
	usePendingItem(item);
}

// --- Save a counted line -------------------------------------------------

async function saveCount() {
	if (!pending.item || savingPending.value) return;
	const qty = Number(pending.qty);
	if (pending.qty === "" || Number.isNaN(qty) || qty < 0) {
		showError(__("Enter a counted quantity (0 or more)."));
		return;
	}
	savingPending.value = true;
	try {
		const line = await call(`${API}.upsert_count_line`, {
			session: props.session,
			item_code: pending.item.item_code,
			counted_qty: qty,
		});
		mergeLine(line);
		pending.item = null;
		pending.qty = "";
		await nextTick();
		scanInputEl.value?.focus();
	} catch (e) {
		showError(errorMessage(e) || __("Could not save the count"));
	} finally {
		savingPending.value = false;
	}
}

// Insert the line at the top, or replace the existing row in place.
function mergeLine(line) {
	const idx = lines.value.findIndex((l) => l.item_code === line.item_code);
	if (idx === -1) {
		lines.value.unshift(line);
	} else {
		lines.value.splice(idx, 1, line);
	}
}

// --- Inline edit of an existing line ------------------------------------

async function commitLine(line) {
	const qty = Number(line.counted_qty);
	if (isFinished.value || Number.isNaN(qty) || qty < 0) return;
	lineState[line.item_code] = { saving: true, error: "" };
	try {
		const updated = await call(`${API}.upsert_count_line`, {
			session: props.session,
			item_code: line.item_code,
			counted_qty: qty,
		});
		Object.assign(line, updated);
		lineState[line.item_code] = { saving: false, error: "" };
	} catch (e) {
		// Keep the typed value on screen; surface an inline retry chip.
		lineState[line.item_code] = {
			saving: false,
			error: errorMessage(e) || __("Save failed"),
		};
	}
}

async function deleteLine(line) {
	if (isFinished.value) return;
	lineState[line.item_code] = { saving: true, error: "" };
	try {
		await call(`${API}.remove_count_line`, {
			session: props.session,
			item_code: line.item_code,
		});
		lines.value = lines.value.filter((l) => l.item_code !== line.item_code);
		delete lineState[line.item_code];
	} catch (e) {
		lineState[line.item_code] = {
			saving: false,
			error: errorMessage(e) || __("Could not remove"),
		};
	}
}

// --- Finish --------------------------------------------------------------

async function confirmFinish() {
	if (finishModal.busy) return;
	finishModal.busy = true;
	try {
		const res = await call(`${API}.finish_session`, { session: props.session });
		if (res.stock_reconciliation) {
			showInfo(
				__("Draft Stock Reconciliation {0} created — review it in the desk.", [
					res.stock_reconciliation,
				]),
			);
		} else {
			showSuccess(__("Count finished — every item matched system stock."));
		}
		router.push({ name: "StockCount" });
	} catch (e) {
		showError(errorMessage(e) || __("Could not finish the count"));
		finishModal.busy = false;
		finishModal.open = false;
	}
}

// Esc + Ctrl+S inside the popups.
useModalShortcuts(() => finishModal.open, {
	onSave: confirmFinish,
	onCancel: () => (finishModal.open = false),
});
useModalShortcuts(() => pickerModal.open, {
	onCancel: () => (pickerModal.open = false),
});

// --- Errors / auth (same contract as ItemManager) ------------------------

function errorMessage(e) {
	if (!e) return "";
	if (Array.isArray(e.messages) && e.messages.length) return e.messages.join(", ");
	return e.message || String(e);
}

function isAuthError(e) {
	if (!e) return false;
	if (e.exc_type === "PermissionError" || e.exc_type === "AuthenticationError") return true;
	const text = `${e.exc_type || ""} ${errorMessage(e)}`.toLowerCase();
	return text.includes("not permitted") || text.includes("login to access");
}

function redirectToLogin() {
	const here = window.location.pathname + window.location.search;
	window.location.href = `/login?redirect-to=${encodeURIComponent(here)}`;
}
</script>
