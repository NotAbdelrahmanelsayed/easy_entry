import frappe

from easy_entry.utils.supplier_code import backfill_all_supplier_codes


def execute():
    # Custom field column may not exist yet on first migrate; add it so the backfill can run.
    if not frappe.db.has_column("Supplier", "ee_supplier_code"):
        frappe.db.sql("ALTER TABLE `tabSupplier` ADD COLUMN `ee_supplier_code` varchar(140) DEFAULT ''")
    backfill_all_supplier_codes()
