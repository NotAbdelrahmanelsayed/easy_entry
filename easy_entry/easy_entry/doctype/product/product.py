# Copyright (c) 2025, Abdelrahman and contributors
# For license information, please see license.txt

import re
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, nowtime, cint

BARCODE_PREFIX = "P"
BARCODE_PAD = 4
# P + 10 digits => e.g., P0305


class Product(Document):
    def validate(self):
        item = self.create_item()
        self.create_prices(item)
        self.create_stock_reconciliation(item)

    # ---------------------------
    # Item
    # ---------------------------
    def create_item(self):
        item = frappe.new_doc("Item")
        # Use a stable code; fall back to Item name later if not provided
        item.item_code = self.item_name
        item.item_group = self.item_group
        item.stock_uom = self.default_unit_of_measure

        # Generate/pick barcode, persist it on Product and attach to Item
        barcode = self.generate_barcode()
        if barcode:
            item.append(
                "barcodes", {"barcode": barcode, "uom": self.default_unit_of_measure}
            )

        item.insert()
        # Save link back to Product for later references
        self.db_set("item_code", item.name, commit=True)
        if barcode:
            self.db_set("item_barcode", barcode, commit=True)
        return item

    # ---------------------------
    # Barcode helpers
    # ---------------------------
    def generate_barcode(self):
        """
        Generate a unique incremental barcode with prefix `P` and zero-padded digits.
        If `self.item_barcode` already set, re-use it (but verify uniqueness).
        """
        # If a barcode already exists on the Product, keep it (validate uniqueness).
        if getattr(self, "item_barcode", None):
            if self._barcode_exists(self.item_barcode):
                frappe.throw(
                    f"Barcode {self.item_barcode} already exists on another Item."
                )
            return self.item_barcode

        # Fetch the latest highest barcode starting with the prefix.
        # We store numeric part after the first char; e.g., P0000000123
        last = frappe.db.sql(
            """
            SELECT ib.barcode
            FROM `tabItem Barcode` ib
            WHERE ib.barcode LIKE %s
            ORDER BY ib.barcode DESC
            LIMIT 1
        """,
            (f"{BARCODE_PREFIX}%",),
            as_dict=True,
        )

        if last:
            last_code = last[0]["barcode"]
            # Extract numeric tail; if malformed, reset to 0
            m = re.match(rf"^{BARCODE_PREFIX}(\d+)$", last_code or "")
            last_num = cint(m.group(1)) if m else 0
        else:
            last_num = 0

        # Propose next and ensure uniqueness (defensive loop)
        attempts = 0
        while attempts < 1000:
            last_num += 1
            candidate = f"{BARCODE_PREFIX}{str(last_num).zfill(BARCODE_PAD)}"
            if not self._barcode_exists(candidate):
                return candidate
            attempts += 1

        frappe.throw(
            "Could not generate a unique barcode after many attempts. Please check data integrity."
        )

    def _barcode_exists(self, barcode: str) -> bool:
        return bool(frappe.db.exists("Item Barcode", {"barcode": barcode}))

    # ---------------------------
    # Prices
    # ---------------------------
    def create_prices(self, item):
        """
        Create Item Price rows for buying/selling if provided on Product.
        """
        # Buying Price
        if getattr(self, "buying_price", None):
            buying_price = frappe.new_doc("Item Price")
            buying_price.item_code = item.name
            buying_price.uom = self.default_unit_of_measure
            buying_price.price_list = "Standard Buying"
            buying_price.price_list_rate = self.buying_price
            buying_price.insert()

        # Selling Price
        if getattr(self, "selling_price", None):
            selling_price = frappe.new_doc("Item Price")
            selling_price.item_code = item.name
            selling_price.uom = self.default_unit_of_measure
            selling_price.price_list = "Standard Selling"
            selling_price.price_list_rate = self.selling_price
            selling_price.insert()

    # ---------------------------
    # Stock
    # ---------------------------
    def create_stock_reconciliation(self, item):
        """
        Create an opening Stock Reconciliation (or a reconciliation on submit).
        Requires a valid warehouse and valuation_rate.
        """
        # If quantity not provided, do nothing
        qty = getattr(self, "quantity", 0)
        if not qty:
            return

        # Warehouse: Product.warehouse > Stock Settings default_warehouse
        default_wh = None
        try:
            default_wh = frappe.get_cached_doc("Stock Settings").default_warehouse
        except Exception:
            pass

        warehouse = getattr(self, "warehouse", None) or default_wh
        if not warehouse:
            frappe.throw(
                "No warehouse provided and no default warehouse set in Stock Settings."
            )

        valuation_rate = getattr(self, "buying_price", None)
        if valuation_rate in (None, 0):
            frappe.throw(
                "Buying Price is required to set an initial valuation rate for Stock Reconciliation."
            )
            
        purpose = getattr(self, "purpose", None)
        if not purpose:
            frappe.throw(
                "Please define the purpose Stock Reconciliation or Stock Entry"
            )

        sr = frappe.new_doc("Stock Reconciliation")
        sr.purpose = purpose
        sr.posting_date = nowdate()
        sr.posting_time = nowtime()
        # In many setups you must set difference_account and cost_center; set them if you keep this path.
        # sr.company = frappe.defaults.get_global_default("company")
        # sr.set("difference_account", "Expenses Included In Valuation - {abbr}")
        # sr.set("cost_center", "Main - {abbr}")

        sr.append(
            "items",
            {
                "item_code": item.name,
                "warehouse": warehouse,
                "qty": qty,
                "valuation_rate": valuation_rate,
            },
        )
        sr.save()
        sr.insert()
        # Optionally submit immediately:
        # sr.submit()
