import random

import frappe

# Letters only, excluding I and O (easily confused with 1 and 0 on small labels)
CHARSET = "ABCDEFGHJKLMNPQRSTUVWXYZ"
CODE_LEN = 3


def generate_unique_supplier_code():
    for _ in range(1000):
        code = "".join(random.choices(CHARSET, k=CODE_LEN))
        if not frappe.db.exists("Supplier", {"ee_supplier_code": code}):
            return code
    frappe.throw("Could not generate a unique supplier code after 1000 attempts")


def assign_supplier_code(doc, method=None):
    if not doc.ee_supplier_code:
        doc.db_set("ee_supplier_code", generate_unique_supplier_code(), update_modified=False)


@frappe.whitelist()
def backfill_all_supplier_codes(force=False):
    filters = {} if force else {"ee_supplier_code": ["in", [None, ""]]}
    suppliers = frappe.get_all("Supplier", filters=filters, pluck="name")
    if force:
        # Clear first so uniqueness checks run against a clean slate
        frappe.db.sql("UPDATE `tabSupplier` SET ee_supplier_code = ''")
    for name in suppliers:
        frappe.db.set_value(
            "Supplier",
            name,
            "ee_supplier_code",
            generate_unique_supplier_code(),
            update_modified=False,
        )
    frappe.db.commit()
    return len(suppliers)


def item_supplier_code(item_code):
    """Jinja helper: supplier code of the item's default (first) Item Supplier row.

    Used by the label print formats as a fallback when no supplier_code is
    passed in the print URL. Must never raise — a label should still print
    without a code rather than fail.
    """
    try:
        if not item_code:
            return ""
        supplier = frappe.db.get_value(
            "Item Supplier", {"parent": item_code, "parenttype": "Item"}, "supplier", order_by="idx asc"
        )
        if not supplier:
            return ""
        return frappe.db.get_value("Supplier", supplier, "ee_supplier_code") or ""
    except Exception:
        return ""
