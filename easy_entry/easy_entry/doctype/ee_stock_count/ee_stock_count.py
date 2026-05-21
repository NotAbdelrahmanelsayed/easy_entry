# For license information, please see license.txt

"""EE Stock Count -- a resumable, mobile-first stock-counting session.

One session holds many counted lines. Counting never touches the stock
ledger; finishing the session generates a *draft* Stock Reconciliation
(see ``build_reconciliation``) that a human reviews and submits on the desk.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate, nowtime

from easy_entry.api import _stock

STATUS_IN_PROGRESS = "In Progress"
STATUS_FINISHED = "Finished"


class EEStockCount(Document):
	def validate(self):
		# Keep every line's difference in sync with its counted/system qty.
		for line in self.count_lines:
			line.difference = flt(line.counted_qty) - flt(line.system_qty)

	def set_count(self, item_code, counted_qty):
		"""Add a counted line, or overwrite the count of an existing one.

		The first count of an item snapshots the system on-hand qty so the
		displayed difference stays stable as the owner walks the warehouse.
		Returns the affected child row.
		"""
		if self.status == STATUS_FINISHED:
			frappe.throw(_("This count session is already finished."))
		if not frappe.db.exists("Item", item_code):
			frappe.throw(_("Item {0} does not exist.").format(item_code))

		line = next((row for row in self.count_lines if row.item_code == item_code), None)
		if line:
			line.counted_qty = flt(counted_qty)
		else:
			line = self.append(
				"count_lines",
				{
					"item_code": item_code,
					"counted_qty": flt(counted_qty),
					"system_qty": _stock.get_system_qty(item_code, self.warehouse),
				},
			)
		return line

	def remove_count(self, item_code):
		"""Drop a counted line. No-op if the item was never counted."""
		if self.status == STATUS_FINISHED:
			frappe.throw(_("This count session is already finished."))
		self.count_lines = [row for row in self.count_lines if row.item_code != item_code]

	def build_reconciliation(self):
		"""Create a DRAFT Stock Reconciliation for lines that differ from stock.

		Lines whose counted qty already matches the system qty need no
		correction and are skipped. Returns the new SR name, or ``None`` when
		nothing needs reconciling (every count matched).
		"""
		from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import (
			EmptyStockReconciliationItemsError,
		)

		changed = [
			row for row in self.count_lines if flt(row.counted_qty) != flt(row.system_qty)
		]
		if not changed:
			return None

		company = frappe.db.get_value("Warehouse", self.warehouse, "company")
		sr = frappe.new_doc("Stock Reconciliation")
		sr.company = company
		sr.purpose = "Stock Reconciliation"
		sr.expense_account = _stock.resolve_difference_account(company)
		sr.posting_date = nowdate()
		sr.posting_time = nowtime()
		for row in changed:
			sr.append(
				"items",
				{
					"item_code": row.item_code,
					"warehouse": self.warehouse,
					"qty": flt(row.counted_qty),
					"valuation_rate": _stock.resolve_valuation_rate(
						row.item_code, self.warehouse
					),
				},
			)
		try:
			sr.insert(ignore_permissions=False)
		except EmptyStockReconciliationItemsError:
			# Live stock moved to match every count between scan and finish.
			return None
		return sr.name
