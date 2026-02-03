frappe.ui.form.on("Item", {
	refresh(frm) {
		frm.add_custom_button("<b>Generate Barcode<b>", () => {
			frappe.call({
				method: "easy_entry.easy_entry.doctype.barcode_generator.barcode_generator.generate_barcode_to_item",
				args: { doc_name: frm.doc.name },
			});
		});
	},
});
