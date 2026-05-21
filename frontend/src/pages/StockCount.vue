<template>
	<div class="flex-1 min-h-0 bg-gray-50 flex flex-col">
		<!-- Header -->
		<header class="bg-white border-b border-gray-200 px-6 py-4">
			<h1 class="text-lg font-semibold text-gray-900">{{ __("Stock Count") }}</h1>
			<p class="text-xs text-gray-500">
				{{ __("Scan and count items, then reconcile stock in one session.") }}
			</p>
		</header>

		<!-- Content -->
		<div class="flex-1 overflow-auto px-6 py-6">
			<div class="mx-auto w-full max-w-md flex flex-col gap-6">
				<!-- Start a new count -->
				<section class="bg-white border border-gray-200 rounded-xl p-5">
					<h2 class="font-semibold text-gray-900">{{ __("Start a new count") }}</h2>
					<label class="block text-xs font-medium text-gray-500 mt-4 mb-1">
						{{ __("Warehouse") }}
					</label>
					<select
						v-model="selectedWarehouse"
						class="w-full border border-gray-300 rounded-lg px-3 py-3 text-base focus:outline-none focus:ring-2 focus:ring-blue-500"
						data-testid="warehouse-select"
					>
						<option value="" disabled>{{ __("Select a warehouse") }}</option>
						<option v-for="w in warehouses.data || []" :key="w.name" :value="w.name">
							{{ w.name }}
						</option>
					</select>
					<button
						class="mt-4 w-full py-3 rounded-lg text-base font-medium bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
						:disabled="!selectedWarehouse || starting"
						data-testid="start-count"
						@click="startCount"
					>
						{{ starting ? __("Starting...") : __("Start new count") }}
					</button>
				</section>

				<!-- Resume an open session -->
				<section>
					<h2 class="font-semibold text-gray-900 mb-2">{{ __("Open sessions") }}</h2>

					<div v-if="sessions.loading" class="flex flex-col gap-2">
						<div
							v-for="n in 3"
							:key="n"
							class="h-16 bg-white border border-gray-200 rounded-xl animate-pulse"
						></div>
					</div>

					<div
						v-else-if="sessions.error"
						class="bg-white border border-gray-200 rounded-xl p-6 text-center"
					>
						<p class="text-sm text-red-500">
							{{
								isAuthError(sessions.error)
									? __("Please log in to view sessions")
									: __("Failed to load sessions")
							}}
						</p>
						<button
							class="mt-2 text-sm text-blue-600 hover:underline"
							@click="isAuthError(sessions.error) ? redirectToLogin() : sessions.reload()"
						>
							{{ isAuthError(sessions.error) ? __("Log in") : __("Retry") }}
						</button>
					</div>

					<p
						v-else-if="!(sessions.data || []).length"
						class="text-sm text-gray-400 bg-white border border-gray-200 rounded-xl p-6 text-center"
					>
						{{ __("No open sessions — start one above.") }}
					</p>

					<div v-else class="flex flex-col gap-2" data-testid="session-list">
						<router-link
							v-for="s in sessions.data"
							:key="s.name"
							:to="{ name: 'StockCountSession', params: { session: s.name } }"
							class="flex items-center justify-between bg-white border border-gray-200 rounded-xl px-4 py-3 hover:border-blue-300 hover:shadow-sm transition"
						>
							<div class="min-w-0">
								<p class="font-medium text-gray-900 truncate">{{ s.name }}</p>
								<p class="text-xs text-gray-500 truncate">
									{{ s.warehouse }} ·
									{{ __("{0} item(s) counted", [s.line_count]) }}
								</p>
							</div>
							<svg
								class="w-5 h-5 text-gray-400 flex-shrink-0"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M9 5l7 7-7 7"
								/>
							</svg>
						</router-link>
					</div>
				</section>
			</div>
		</div>
	</div>
</template>

<script setup>
import { call, createResource } from "frappe-ui";
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "@/composables/useToast";

const API = "easy_entry.api.stock_count";
const router = useRouter();
const { showError } = useToast();

const selectedWarehouse = ref("");
const starting = ref(false);

const warehouses = createResource({
	url: "frappe.client.get_list",
	params: {
		doctype: "Warehouse",
		filters: { is_group: 0 },
		fields: ["name"],
		limit_page_length: 0,
		order_by: "name asc",
	},
	auto: true,
});

// Pre-select the Stock Settings default warehouse — most counts use it.
createResource({
	url: "frappe.client.get_single_value",
	params: { doctype: "Stock Settings", field: "default_warehouse" },
	auto: true,
	onSuccess(value) {
		if (value && !selectedWarehouse.value) selectedWarehouse.value = value;
	},
});

const sessions = createResource({
	url: `${API}.list_open_sessions`,
	auto: true,
	onError(err) {
		if (isAuthError(err)) redirectToLogin();
	},
});

async function startCount() {
	if (!selectedWarehouse.value || starting.value) return;
	starting.value = true;
	try {
		const res = await call(`${API}.start_session`, {
			warehouse: selectedWarehouse.value,
		});
		router.push({ name: "StockCountSession", params: { session: res.session } });
	} catch (e) {
		showError(errorMessage(e) || __("Could not start the count"));
		starting.value = false;
	}
}

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
