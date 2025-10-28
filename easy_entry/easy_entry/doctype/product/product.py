# Copyright (c) 2025, Abdelrahman and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Product(Document):
	def before_save(self):
		self.create_item()
		self.creat_prices()
		self.create_stock_entry()

	def create_item(self):
		item = frappe.new_doc("Item")
		item.item_code = self.item_name
		item.item_group = self.item_group
		item.stock_uom = self.default_unit_of_measure
		item.append("barcodes", {
                "barcode": self.item_barcode,
                "uom": self.default_unit_of_measure
            })
		item.insert()
		return item
	
	def generate_barcode(self):
		"""
		YOU MAY ADD THIS ON ERPNEXT'S ITEMS FUNCTION,
		BUT IT'S BETTER TO USE IT AS A CUSTOM-APP. 
		SEE THE TRADE-OFF
		
		"""
		last_barcode = frappe.db.sql("""
		SELECT barcode FROM `tabItem Barcode`
		WHERE barcode LIKE "P0%"  
		ORDER BY barcode DESC 
		LIMIT 1;
									""")[0][0]
		new_number = str(int(last_barcode[1:]) + 1).zfill(len(last_barcode)-1)
		new_barcode = "P" + new_number
			# SELECT barcode FROM `tabItem Barcode` WHERE barcode LIKE "P0%"   ORDER BY barcode DESC LIMIT 1;
			
	def creat_prices(self):
		# Buying Price
		if self.buying_price:
			buying_price = frappe.new_doc("Item Price")
			buying_price.item_code = self.item_code
			buying_price.uom = self.default_unit_of_measure
			buying_price.price_list = "Standard Buying"
			buying_price.rate = self.buying_price
			buying_price.insert()
		
		# selling Price
		if self.selling_price:
			selling_price = frappe.new_doc("Item Price")
			selling_price.item_code = self.item_code
			selling_price.uom = self.default_unit_of_measure
			selling_price.price_list = "Standard Selling"
			selling_price.rate = self.selling_price
			selling_price.insert()
	
	def create_stock_entry(self):
		stock_entry = frappe.new_doc("Stock Entry")
		stock_entry.stock_entry_type = self.stock_entry_type
		stock_entry.append("items", {
			"item_code": self.item_name,
			"qty": self.quantity
		})
		stock_entry.insert()