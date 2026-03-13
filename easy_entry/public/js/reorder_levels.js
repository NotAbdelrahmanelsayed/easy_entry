frappe.ui.form.on("Stock Settings", {
    refresh(frm) {
        frm.add_custom_button(__("Set Missing Reorder Levels"), function () {
            frappe.confirm(
                __("This will calculate and set reorder levels for all items that have none, based on the last 90 days of stock movement. Continue?"),
                function () {
                    frappe.show_progress(__("Setting Reorder Levels"), 0, 100, __("Please wait..."));
                    frappe.call({
                        method: "easy_entry.easy_entry.reorder_levels.set_missing_reorder_levels",
                        freeze: true,
                        freeze_message: __("Calculating reorder levels..."),
                        callback(r) {
                            frappe.hide_progress();
                            if (!r.exc && r.message) {
                                const s = r.message;
                                let msg = `
                                    <b>${__("Items updated")}:</b> ${s.processed}<br>
                                    <b>${__("Warehouse rows created")}:</b> ${s.warehouses_set}<br>
                                    <b>${__("Skipped (no movement)")}:</b> ${s.skipped_no_movement}<br>
                                    <b>${__("Errors")}:</b> ${s.skipped_error}
                                `;
                                if (s.errors && s.errors.length) {
                                    msg += "<br><br><b>Error details:</b><br>";
                                    s.errors.forEach(e => {
                                        msg += `${e.item}: ${e.error}<br>`;
                                    });
                                }
                                frappe.msgprint({
                                    title: __("Reorder Levels Set"),
                                    indicator: s.skipped_error ? "orange" : "green",
                                    message: msg,
                                });
                            }
                        },
                    });
                }
            );
        }, __("Stock"));

        frm.add_custom_button(__("Update All Reorder Levels"), function () {
            frappe.confirm(
                __("This will REPLACE existing reorder rows for ALL items based on last 90 days of movement. Manually set values will be overwritten. Continue?"),
                function () {
                    frappe.show_progress(__("Updating Reorder Levels"), 0, 100, __("Please wait..."));
                    frappe.call({
                        method: "easy_entry.easy_entry.reorder_levels.update_all_reorder_levels",
                        freeze: true,
                        freeze_message: __("Recalculating all reorder levels..."),
                        callback(r) {
                            frappe.hide_progress();
                            if (!r.exc && r.message) {
                                const s = r.message;
                                let msg = `
                                    <b>${__("Items updated")}:</b> ${s.processed}<br>
                                    <b>${__("Warehouse rows set")}:</b> ${s.warehouses_set}<br>
                                    <b>${__("Skipped (no movement)")}:</b> ${s.skipped_no_movement}<br>
                                    <b>${__("Errors")}:</b> ${s.skipped_error}
                                `;
                                if (s.errors && s.errors.length) {
                                    msg += "<br><br><b>Error details:</b><br>";
                                    s.errors.forEach(e => {
                                        msg += `${e.item}: ${e.error}<br>`;
                                    });
                                }
                                frappe.msgprint({
                                    title: __("Reorder Levels Updated"),
                                    indicator: s.skipped_error ? "orange" : "green",
                                    message: msg,
                                });
                            }
                        },
                    });
                }
            );
        }, __("Stock"));
    },
});
