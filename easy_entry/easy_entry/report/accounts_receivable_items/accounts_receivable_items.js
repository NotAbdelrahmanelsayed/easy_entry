frappe.query_reports["Accounts Receivable Items"] = {
	filters: [
		{
			fieldname: "company",
			label: __("الشركة / Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_default("company"),
		},
		{
			fieldname: "customer",
			label: __("العميل / Customer"),
			fieldtype: "Link",
			options: "Customer",
		},
		{
			fieldname: "as_of_date",
			label: __("حتى تاريخ / As of Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
	],

	onload: function (report) {
		// Inject mobile-friendly styles
		if (!document.getElementById("ar-report-styles")) {
			const style = document.createElement("style");
			style.id = "ar-report-styles";
			style.textContent = `
				/* Make the report area scrollable on mobile */
				.page-content-wrapper .datatable {
					overflow-x: auto !important;
					-webkit-overflow-scrolling: touch;
				}

				/* Compact cells on mobile */
				@media (max-width: 768px) {
					.dt-cell__content {
						font-size: 12px !important;
						padding: 4px 6px !important;
					}
					.dt-cell__resize-handle { display: none !important; }
					.report-summary {
						flex-direction: column !important;
						gap: 8px !important;
					}
					.report-summary-item {
						padding: 10px 14px !important;
						border-radius: 8px !important;
					}
					.report-summary-value {
						font-size: 20px !important;
					}
					/* Customer header rows — bigger touch targets on mobile */
					.dt-row[data-is-group="1"] .dt-cell__content,
					.dt-row .dt-cell__content[data-is-group="1"] {
						padding: 6px 8px !important;
					}
				}

				/* Summary cards — always look good */
				.report-summary {
					display: flex;
					gap: 12px;
					flex-wrap: wrap;
					margin-bottom: 16px;
				}
				.report-summary-item {
					flex: 1 1 180px;
				}
				.report-summary-value.text-blue {
					color: #2563eb !important;
				}
				.report-summary-value.text-orange {
					color: #b45309 !important;
				}

				/* Tighten the filter bar on mobile */
				@media (max-width: 576px) {
					.filter-field { width: 100% !important; margin-bottom: 6px; }
					.page-actions { flex-wrap: wrap; gap: 6px; }
				}
			`;
			document.head.appendChild(style);
		}
	},

	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (!data) return value;

		if (data.is_group) {
			let inner = "";

			if (column.fieldname === "customer") {
				inner = value
					? `<span style="font-weight:700;color:#92400e;font-size:0.88em;letter-spacing:0.04em;">${value}</span>`
					: "";
			} else if (column.fieldname === "customer_name") {
				inner = value
					? `<span style="font-weight:700;color:#1c1917;font-size:0.97em;">${value}</span>`
					: "";
			} else if (column.fieldname === "outstanding_amount") {
				inner = value
					? `<span style="display:inline-block;background:#fef3c7;color:#92400e;border:1.5px solid #f59e0b;border-radius:5px;padding:1px 10px;font-weight:800;font-size:0.93em;white-space:nowrap;">${value}</span>`
					: "";
			} else {
				inner = value || "";
			}

			return `<div style="background:#fef3c7;margin:-3px -8px;padding:3px 8px;min-height:22px;border-top:1.5px solid #fde68a;border-bottom:1.5px solid #fde68a;">${inner}</div>`;
		} else {
			if (column.fieldname === "outstanding_amount" && value) {
				return `<span style="color:#b45309;font-weight:600;">${value}</span>`;
			}
			if (column.fieldname === "invoice" && value) {
				return `<span style="color:#2563eb;">${value}</span>`;
			}
			return value;
		}
	},
};
