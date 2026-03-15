frappe.query_reports["Items Missing Prices"] = {
	filters: [
		{
			fieldname: "missing_type",
			label: __("Show Items"),
			fieldtype: "Select",
			options: "Any Missing\nMissing Buying Only\nMissing Selling Only\nMissing Both",
			default: "Any Missing",
		},
	],

	formatter: function (value, row, column, data, default_formatter) {
		if (column.fieldname === "actions") {
			let buttons = "";
			if (!data.has_buying) {
				if (parseFloat(data.valuation_rate) > 0) {
					buttons += `<button class="btn btn-xs btn-primary ee-fill-valuation"
                        data-item="${frappe.utils.escape_html(data.item_code)}"
                        data-rate="${data.valuation_rate}"
                        style="margin-right:4px">${__("From Valuation")}</button>`;
				}
				buttons += `<button class="btn btn-xs btn-default ee-add-price"
                    data-item="${frappe.utils.escape_html(data.item_code)}"
                    data-pricelist="Standard Buying"
                    style="margin-right:4px">${__("Add Buying")}</button>`;
			}
			if (!data.has_selling) {
				buttons += `<button class="btn btn-xs btn-default ee-add-price"
                    data-item="${frappe.utils.escape_html(data.item_code)}"
                    data-pricelist="Standard Selling">${__("Add Selling")}</button>`;
			}
			return buttons;
		}
		// Blank instead of 0.00 for missing prices
		if (
			(column.fieldname === "buying_price" && !data.has_buying) ||
			(column.fieldname === "selling_price" && !data.has_selling)
		) {
			return "";
		}
		return default_formatter(value, row, column, data);
	},

	onload: function (report) {
		report.page.wrapper.on("click", ".ee-fill-valuation", function (e) {
			let $btn = $(e.currentTarget);
			let item_code = $btn.data("item");
			let rate = $btn.data("rate");
			frappe.call({
				method: "easy_entry.easy_entry.report.items_missing_prices.items_missing_prices.add_item_price",
				args: { item_code, price_list: "Standard Buying", price: rate },
				freeze: true,
				freeze_message: __("Saving price\u2026"),
				callback: function () {
					frappe.show_alert({
						message: __("Price added for {0}", [item_code]),
						indicator: "green",
					});
					report.refresh();
				},
			});
		});

		report.page.wrapper.on("click", ".ee-add-price", function (e) {
			let $btn = $(e.currentTarget);
			let item_code = $btn.data("item");
			let price_list = $btn.data("pricelist");
			let label =
				price_list === "Standard Buying" ? __("Buying Price") : __("Selling Price");

			frappe.prompt(
				[{ fieldname: "price", label: label, fieldtype: "Currency", reqd: 1 }],
				function (values) {
					frappe.call({
						method: "easy_entry.easy_entry.report.items_missing_prices.items_missing_prices.add_item_price",
						args: { item_code, price_list, price: values.price },
						freeze: true,
						freeze_message: __("Saving price\u2026"),
						callback: function () {
							frappe.show_alert({
								message: __("Price added for {0}", [item_code]),
								indicator: "green",
							});
							report.refresh();
						},
					});
				},
				__("Add {0} for {1}", [label, item_code]),
				__("Save")
			);
		});
	},
};
