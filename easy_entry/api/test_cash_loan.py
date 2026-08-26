"""Integration tests for the Cash Loan API.

Run with:
	bench --site <site> run-tests --module easy_entry.api.test_cash_loan
"""

import frappe
from frappe.tests import IntegrationTestCase

from easy_entry.api import cash_loan

TEST_CUSTOMER = "_TEST-CL-Borrower"


class TestCashLoan(IntegrationTestCase):
	def setUp(self):
		self._loans = []
		self._journal_entries = []
		if not frappe.db.exists("Customer", TEST_CUSTOMER):
			frappe.get_doc(
				{
					"doctype": "Customer",
					"customer_name": TEST_CUSTOMER,
					"customer_type": "Individual",
					"customer_group": "Individual",
					"territory": "Egypt",
				}
			).insert(ignore_permissions=True)

	def tearDown(self):
		for loan_name in self._loans:
			if frappe.db.exists("Cash Loan", loan_name):
				frappe.delete_doc("Cash Loan", loan_name, force=True, ignore_permissions=True)
		for je_name in self._journal_entries:
			if frappe.db.exists("Journal Entry", je_name):
				je = frappe.get_doc("Journal Entry", je_name)
				if je.docstatus == 1:
					je.cancel()
		if frappe.db.exists("Customer", TEST_CUSTOMER):
			frappe.delete_doc("Customer", TEST_CUSTOMER, force=True, ignore_permissions=True)
		# Cleanup must be committed: give_loan/repay_loan commit internally (see
		# CLAUDE.md), which already breaks IntegrationTestCase's rollback-based
		# isolation for this site (no separate test DB). Without this commit,
		# cancel()/delete_doc() above land in a new transaction that the test
		# framework's final rollback silently discards, leaving real orphaned
		# Journal Entries / Cash Loan docs in the live database.
		frappe.db.commit()

	def _mode_of_payment(self):
		company = cash_loan._default_company()
		row = frappe.db.get_value(
			"Mode of Payment Account", {"company": company}, "parent"
		)
		self.assertTrue(row, "Test site needs at least one Mode of Payment configured for its company.")
		return row

	def test_give_and_repay_loan_full_cycle(self):
		mop = self._mode_of_payment()

		res = cash_loan.give_loan(borrower=TEST_CUSTOMER, amount=500, mode_of_payment=mop)
		self._loans.append(res["name"])
		self._journal_entries.append(res["journal_entry"])

		loan = frappe.get_doc("Cash Loan", res["name"])
		self.assertEqual(loan.status, "Open")
		self.assertEqual(loan.amount, 500)
		self.assertEqual(loan.borrower, TEST_CUSTOMER)

		je = frappe.get_doc("Journal Entry", res["journal_entry"])
		self.assertEqual(je.docstatus, 1)
		accounts = {r.account: (r.debit_in_account_currency, r.credit_in_account_currency) for r in je.accounts}
		self.assertEqual(accounts[loan.receivable_account], (500, 0))
		self.assertEqual(accounts[loan.loan_account], (0, 500))

		repay_res = cash_loan.repay_loan(name=loan.name, mode_of_payment=mop)
		self._journal_entries.append(repay_res["journal_entry"])

		loan.reload()
		self.assertEqual(loan.status, "Repaid")
		self.assertIsNotNone(loan.repaid_date)

		# Net effect of THIS loan's two vouchers only -- the receivable account
		# is shared with every other (possibly real, open) Cash Loan, so the
		# account-wide balance is not zero in general.
		bal = frappe.db.sql(
			"""
			select sum(debit)-sum(credit) from `tabGL Entry`
			where account=%s and is_cancelled=0
				and voucher_no in (%s, %s)
			""",
			(loan.receivable_account, res["journal_entry"], repay_res["journal_entry"]),
		)[0][0]
		self.assertEqual(bal, 0)

	def test_give_loan_requires_existing_customer(self):
		mop = self._mode_of_payment()
		with self.assertRaises(frappe.ValidationError):
			cash_loan.give_loan(borrower="_TEST-CL-No-Such-Customer", amount=100, mode_of_payment=mop)

	def test_repay_loan_twice_is_rejected(self):
		mop = self._mode_of_payment()
		res = cash_loan.give_loan(borrower=TEST_CUSTOMER, amount=100, mode_of_payment=mop)
		self._loans.append(res["name"])
		self._journal_entries.append(res["journal_entry"])

		repay_res = cash_loan.repay_loan(name=res["name"], mode_of_payment=mop)
		self._journal_entries.append(repay_res["journal_entry"])

		with self.assertRaises(frappe.ValidationError):
			cash_loan.repay_loan(name=res["name"], mode_of_payment=mop)

	def test_give_loan_requires_positive_amount(self):
		mop = self._mode_of_payment()
		with self.assertRaises(frappe.ValidationError):
			cash_loan.give_loan(borrower=TEST_CUSTOMER, amount=0, mode_of_payment=mop)

	def test_list_loans_filters_by_status(self):
		mop = self._mode_of_payment()
		res = cash_loan.give_loan(borrower=TEST_CUSTOMER, amount=75, mode_of_payment=mop)
		self._loans.append(res["name"])
		self._journal_entries.append(res["journal_entry"])

		open_listing = cash_loan.list_loans(search=TEST_CUSTOMER, status="Open")
		self.assertTrue(any(r["name"] == res["name"] for r in open_listing["rows"]))

		repaid_listing = cash_loan.list_loans(search=TEST_CUSTOMER, status="Repaid")
		self.assertFalse(any(r["name"] == res["name"] for r in repaid_listing["rows"]))
