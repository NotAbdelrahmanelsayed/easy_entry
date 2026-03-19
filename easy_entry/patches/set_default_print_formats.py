import frappe


def execute():
	frappe.db.set_value("DocType", "Sales Invoice", "default_print_format", "Easy Entry Sales Invoice")
	frappe.db.set_value("DocType", "Purchase Invoice", "default_print_format", "Easy Entry Purchase Invoice")
	frappe.db.commit()
