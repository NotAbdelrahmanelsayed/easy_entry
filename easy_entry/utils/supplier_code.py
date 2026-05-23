import random
import string

import frappe

CHARSET = string.ascii_uppercase + string.digits
CODE_LEN = 6


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
def backfill_all_supplier_codes():
    suppliers = frappe.get_all(
        "Supplier",
        filters={"ee_supplier_code": ["in", [None, ""]]},
        pluck="name",
    )
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
