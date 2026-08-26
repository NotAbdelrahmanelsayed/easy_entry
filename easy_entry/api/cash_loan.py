"""Whitelisted endpoints for the Cash Loan SPA.

Cash Loan is a plain informal cash advance to a Customer -- no interest, no
schedule, no partial repayment. Giving a loan posts Dr "Cash Loans
Receivable" / Cr the cash-or-bank account for the chosen Mode of Payment;
repaying it posts the reverse and closes the loan. Nothing here touches
Sales Invoice or Item, so Gross Profit / sales reports never see these
amounts.

Convention: explicit ``frappe.db.commit()`` after writes and ``limit``
capped at 200 -- mirrors ``item_manager.py``.
"""

import frappe
from frappe import _
from frappe.utils import cint, flt, nowdate

RECEIVABLE_ACCOUNT_NAME = "Cash Loans Receivable"
MAX_LIMIT = 200


def _default_company():
	company = frappe.defaults.get_global_default("company")
	if company:
		return company
	companies = frappe.get_all("Company", pluck="name", limit=2)
	if len(companies) == 1:
		return companies[0]
	frappe.throw(_("Could not determine the default company. Please specify one."))


def _resolve_receivable_account(company):
	"""Find (and re-enable if needed) the company's Cash Loans Receivable account.

	Bilingual Chart of Accounts on this site means account names carry a
	" - <abbr>" suffix, so match by the base label rather than an exact name.
	Creates the account under Current Assets if it truly doesn't exist yet.
	"""
	account = frappe.db.get_value(
		"Account",
		{"company": company, "account_name": RECEIVABLE_ACCOUNT_NAME, "is_group": 0},
		["name", "disabled"],
		as_dict=True,
	)
	if account:
		if account.disabled:
			frappe.db.set_value("Account", account.name, "disabled", 0)
		return account.name

	parent = frappe.db.get_value(
		"Account",
		{"company": company, "account_name": ["like", "Current Assets%"], "is_group": 1, "root_type": "Asset"},
		"name",
	)
	if not parent:
		frappe.throw(_("Could not find a Current Assets group account for company {0}.").format(company))

	new_account = frappe.get_doc(
		{
			"doctype": "Account",
			"account_name": RECEIVABLE_ACCOUNT_NAME,
			"parent_account": parent,
			"company": company,
			"root_type": "Asset",
			"is_group": 0,
		}
	)
	new_account.insert(ignore_permissions=True)
	return new_account.name


def _resolve_mop_account(mode_of_payment, company):
	account = frappe.db.get_value(
		"Mode of Payment Account",
		{"parent": mode_of_payment, "company": company},
		"default_account",
	)
	if not account:
		frappe.throw(
			_("Mode of Payment {0} has no account configured for company {1}.").format(
				mode_of_payment, company
			)
		)
	return account


def _make_journal_entry(company, debit_account, credit_account, amount, remark, posting_date=None):
	je = frappe.new_doc("Journal Entry")
	je.voucher_type = "Journal Entry"
	je.company = company
	je.posting_date = posting_date or nowdate()
	je.user_remark = remark
	je.append("accounts", {"account": debit_account, "debit_in_account_currency": amount, "credit_in_account_currency": 0})
	je.append("accounts", {"account": credit_account, "debit_in_account_currency": 0, "credit_in_account_currency": amount})
	je.insert(ignore_permissions=True)
	je.submit()
	return je


@frappe.whitelist()
def get_modes_of_payment(company=None):
	"""Modes of Payment with a resolved account for the given company -- for the SPA's dropdowns."""
	company = company or _default_company()
	rows = frappe.db.sql(
		"""
		SELECT mop.name, mopa.default_account
		FROM `tabMode of Payment` mop
		JOIN `tabMode of Payment Account` mopa
			ON mopa.parent = mop.name AND mopa.company = %(company)s
		WHERE mop.enabled = 1
		ORDER BY mop.name
		""",
		{"company": company},
		as_dict=True,
	)
	return rows


@frappe.whitelist()
def give_loan(borrower, amount, mode_of_payment, company=None, remarks=None):
	"""Give a cash loan: Dr Cash Loans Receivable, Cr the chosen cash/bank account."""
	amount = flt(amount)
	if not borrower:
		frappe.throw(_("Borrower is required."))
	if not frappe.db.exists("Customer", borrower):
		frappe.throw(_("Customer {0} does not exist.").format(borrower))
	if amount <= 0:
		frappe.throw(_("Amount must be a positive number."))
	if not mode_of_payment:
		frappe.throw(_("Mode of Payment is required."))

	company = company or _default_company()
	receivable_account = _resolve_receivable_account(company)
	loan_account = _resolve_mop_account(mode_of_payment, company)
	customer_name = frappe.db.get_value("Customer", borrower, "customer_name") or borrower

	je = _make_journal_entry(
		company,
		debit_account=receivable_account,
		credit_account=loan_account,
		amount=amount,
		remark=_("Cash loan given to {0}").format(customer_name),
	)

	loan = frappe.get_doc(
		{
			"doctype": "Cash Loan",
			"borrower": borrower,
			"amount": amount,
			"company": company,
			"loan_date": nowdate(),
			"loan_mode_of_payment": mode_of_payment,
			"loan_account": loan_account,
			"receivable_account": receivable_account,
			"journal_entry_give": je.name,
			"status": "Open",
			"remarks": remarks,
		}
	)
	loan.insert(ignore_permissions=False)
	frappe.db.commit()
	return {"ok": True, "name": loan.name, "journal_entry": je.name}


@frappe.whitelist()
def repay_loan(name, mode_of_payment):
	"""Repay a cash loan in full: Dr the chosen cash/bank account, Cr Cash Loans Receivable."""
	if not mode_of_payment:
		frappe.throw(_("Mode of Payment is required."))

	loan = frappe.get_doc("Cash Loan", name)
	if loan.status != "Open":
		frappe.throw(_("Loan {0} is already repaid.").format(name))

	repay_account = _resolve_mop_account(mode_of_payment, loan.company)
	customer_name = frappe.db.get_value("Customer", loan.borrower, "customer_name") or loan.borrower

	je = _make_journal_entry(
		loan.company,
		debit_account=repay_account,
		credit_account=loan.receivable_account,
		amount=loan.amount,
		remark=_("Cash loan repaid by {0}").format(customer_name),
	)

	loan.status = "Repaid"
	loan.repaid_date = nowdate()
	loan.repay_mode_of_payment = mode_of_payment
	loan.repay_account = repay_account
	loan.journal_entry_repay = je.name
	loan.save(ignore_permissions=False)
	frappe.db.commit()
	return {"ok": True, "name": loan.name, "journal_entry": je.name}


@frappe.whitelist()
def list_loans(search="", status="", limit=50, offset=0):
	"""Paginated, searchable Cash Loan list for the SPA."""
	limit = min(cint(limit) or 50, MAX_LIMIT)
	offset = cint(offset)

	conditions = ["1=1"]
	values = {}

	if search:
		conditions.append("(name LIKE %(search)s OR borrower LIKE %(search)s OR customer_name LIKE %(search)s)")
		values["search"] = f"%{search}%"

	if status in ("Open", "Repaid"):
		conditions.append("status = %(status)s")
		values["status"] = status

	where = " AND ".join(conditions)

	rows = frappe.db.sql(
		f"""
		SELECT name, borrower, customer_name, amount, status, loan_date, repaid_date,
			loan_mode_of_payment, repay_mode_of_payment, remarks
		FROM `tabCash Loan`
		WHERE {where}
		ORDER BY loan_date DESC, creation DESC
		LIMIT %(limit)s OFFSET %(offset)s
		""",
		{**values, "limit": limit, "offset": offset},
		as_dict=True,
	)
	total = frappe.db.sql(f"SELECT COUNT(*) FROM `tabCash Loan` WHERE {where}", values)[0][0]

	open_total = frappe.db.sql(
		"SELECT COALESCE(SUM(amount), 0) FROM `tabCash Loan` WHERE status = 'Open'"
	)[0][0]

	return {"rows": rows, "total": total, "open_total": flt(open_total)}
