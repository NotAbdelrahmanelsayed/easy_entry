# Copyright (c) 2026, Abdelrahman and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class CashLoan(Document):
	def validate(self):
		if self.is_new():
			return
		before = self.get_doc_before_save()
		if not before:
			return
		if self.journal_entry_give and self.amount != before.amount:
			frappe.throw(_("Amount cannot be changed after the loan has been given."))
		if before.status == "Repaid" and self.status != "Repaid":
			frappe.throw(_("A repaid loan cannot be reopened."))
