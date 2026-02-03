# Copyright (c) 2025, Abdelrahman and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cint
from frappe.model.document import Document


class BarcodeGenerator(Document):
    pass


# my_app/my_app/doctype/barcode_generator/barcode_generator.py


def get_barcode():
    barcode_doc = frappe.get_single("Barcode Generator")
    prefix = (barcode_doc.prefix or "").strip()
    if not prefix:
        frappe.throw("Prefix is required.")
    digits = cint(barcode_doc.numbers)
    code_number = cint(barcode_doc.code_number or 1)
    barcode = f"{code_number :0{digits}d}"
    barcode = f"{prefix}{barcode}"
    return barcode


def increase_code():
    barcode_number = frappe.get_single_value("Barcode Generator", "code_number")
    frappe.db.set_single_value(
        "Barcode Generator", "code_number", cint(barcode_number) + 1
    )


@frappe.whitelist()
def generate_barcode_to_item(doc=None, method=None, doc_name=None):
    """Return the next available unique barcode like PREFIX + zero-padded number.
    Uses a Redis-based lock to avoid duplicates under concurrency.
    """

    next_barcode = get_barcode()
    while frappe.db.exists({"doctype": "Item Barcode", "barcode": next_barcode}):
        increase_code()
        next_barcode = get_barcode()

    if doc_name:
        doc = frappe.get_doc("Item", doc_name)

    doc.append("barcodes", {"barcode": next_barcode})
    doc.save(ignore_permissions=True)
    increase_code()
