"""Shared stock helpers for the Easy Entry APIs.

Both ``item_manager.set_item_qty`` (single-item correction) and the Stock
Count feature (``stock_count``) need the same answers: what valuation rate
to stamp on a Stock Reconciliation line, which difference account a draft
reconciliation should use, and the current on-hand quantity of an item.
Keeping that logic here gives the two features one source of truth.

This module is internal (``_`` prefix) -- it exposes no whitelisted endpoints.
"""

import frappe
from frappe.utils import flt

BUYING_PRICE_LIST = "Standard Buying"


def resolve_valuation_rate(item_code, warehouse):
	"""Best-effort valuation rate for a Stock Reconciliation line.

	``valuation_rate`` is required on every SR line. Lookup order, most
	specific first: the existing Bin value for this item+warehouse, then the
	item's buying price, then the Item master's valuation rate. Returns a
	float (``0.0`` when nothing is known -- the SR still validates).
	"""
	rate = frappe.db.get_value(
		"Bin", {"item_code": item_code, "warehouse": warehouse}, "valuation_rate"
	)
	if not rate:
		rate = frappe.db.get_value(
			"Item Price",
			{"item_code": item_code, "price_list": BUYING_PRICE_LIST},
			"price_list_rate",
		)
	if not rate:
		rate = frappe.db.get_value("Item", item_code, "valuation_rate")
	return flt(rate)


def resolve_difference_account(company):
	"""The account a draft Stock Reconciliation should post differences to.

	An opening entry (a brand-new item with no prior ledger entry) requires
	an Asset/Liability account, so prefer the company's "Temporary Opening"
	account; fall back to its configured ``stock_adjustment_account``.
	"""
	return frappe.db.get_value(
		"Account",
		{"company": company, "account_name": "Temporary Opening", "is_group": 0},
		"name",
	) or frappe.db.get_value("Company", company, "stock_adjustment_account")


def get_system_qty(item_code, warehouse):
	"""Current system on-hand quantity for an item in a warehouse (float)."""
	return flt(
		frappe.db.get_value(
			"Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty"
		)
	)


def resolve_warehouse(warehouse=None):
	"""Return the given warehouse, or the Stock Settings default; throw if neither."""
	if not warehouse:
		warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
	if not warehouse:
		frappe.throw(
			frappe._("No warehouse provided and no default warehouse set in Stock Settings.")
		)
	return warehouse
