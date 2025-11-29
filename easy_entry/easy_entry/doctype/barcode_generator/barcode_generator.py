# Copyright (c) 2025, Abdelrahman and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class BarcodeGenerator(Document):
    pass


# my_app/my_app/doctype/barcode_generator/barcode_generator.py
import frappe
from frappe.utils import cint


@frappe.whitelist()
def generate(prefix: str, digits: int):
    """Return the next available unique barcode like PREFIX + zero-padded number.
    Uses a Redis-based lock to avoid duplicates under concurrency.
    """
    prefix = (prefix or "").strip()
    if not prefix:
        frappe.throw("Prefix is required.")
    digits = cint(digits) or 6

    # distributed lock per prefix – prevents two requests from issuing the same code
    lock_name = f"barcode-seq:{prefix}"
    cache = frappe.cache()  # RedisWrapper
    lock = cache.lock(lock_name, timeout=10)

    try:
        lock.acquire(blocking=True, timeout=10)

        # Find the max numeric tail that starts with prefix
        # SUBSTRING(barcode, %s+1): cut the prefix; CAST to integer; take MAX
        max_num = (
            frappe.db.sql(
                """
            SELECT MAX(CAST(SUBSTRING(barcode, %s + 1) AS UNSIGNED))
            FROM `tabItem Barcode`
            WHERE barcode LIKE %s
            """,
                (len(prefix), f"{prefix}%"),
            )[0][0]
            or 0
        )

        # Loop in case the exact next value already exists (rare, but safe)
        while True:
            max_num += 1
            code = f"{prefix}{str(max_num).zfill(digits)}"
            # `Item Barcode` is the child table of Item
            if not frappe.db.exists("Item Barcode", {"barcode": code}):
                return code
            # else continue and try the next number

    finally:
        try:
            lock.release()
        except Exception:
            pass
