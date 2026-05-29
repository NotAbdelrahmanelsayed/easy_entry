"""Whitelisted endpoints for the Item Manager SPA.

Convention: explicit ``frappe.db.commit()`` after writes and ``limit``
capped at 200.
"""

import json

import frappe
from frappe import _
from frappe.utils import cint, flt, nowdate, nowtime
from frappe.utils.xlsxutils import make_xlsx

from easy_entry.api import _stock

BUYING_PRICE_LIST = "Standard Buying"
SELLING_PRICE_LIST = "Standard Selling"
MAX_LIMIT = 200

# The FROM + JOIN block shared by the list query, the COUNT query and the
# export. Aliases used by filter conditions: `i` (Item), `bp`/`sp` (buying/
# selling Item Price), `b` (summed on-hand qty from Bin), `sup` (first
# Item Supplier row).
_ITEMS_FROM = """
	FROM `tabItem` i
	LEFT JOIN `tabItem Price` bp
		ON bp.item_code = i.name AND bp.price_list = %(buying)s
	LEFT JOIN `tabItem Price` sp
		ON sp.item_code = i.name AND sp.price_list = %(selling)s
	LEFT JOIN (
		SELECT item_code, SUM(actual_qty) AS qty
		FROM `tabBin`
		GROUP BY item_code
	) b ON b.item_code = i.name
	LEFT JOIN `tabItem Supplier` sup ON sup.name = (
		SELECT name FROM `tabItem Supplier`
		WHERE parent = i.name ORDER BY idx ASC LIMIT 1
	)
"""


def _filter_conditions(supplier, stock_status, price_status, values):
	"""Translate the three toolbar filters into SQL WHERE conditions.

	Returns a list of SQL condition strings (joined later with ``AND``).
	Unknown or empty filter values must be ignored -- add no condition.
	Bind parameters are added by mutating the ``values`` dict in place.

	Available column expressions (see ``_ITEMS_FROM`` for the joins):
	  - supplier      -> ``sup.supplier``
	  - on-hand qty   -> ``COALESCE(b.qty, 0)``
	  - buying price  -> ``bp.price_list_rate`` (NULL when no Item Price)
	  - selling price -> ``sp.price_list_rate`` (NULL when no Item Price)

	Expected filter values:
	  supplier      -- a Supplier name, or "" for all
	  stock_status  -- "in_stock" / "out_of_stock" / "negative" / ""
	  price_status  -- "missing_buying" / "missing_selling" /
	                   "missing_any" / "has_both" / ""

	Semantics: "out_of_stock" means exactly qty == 0; negative stock is its
	own "negative" bucket. "missing_any" is an OR of the two NULL checks.
	"""
	conditions = []

	if supplier:
		conditions.append("sup.supplier = %(supplier)s")
		values["supplier"] = supplier

	stock_clause = {
		"in_stock": "COALESCE(b.qty, 0) > 0",
		"out_of_stock": "COALESCE(b.qty, 0) = 0",
		"negative": "COALESCE(b.qty, 0) < 0",
	}.get(stock_status)
	if stock_clause:
		conditions.append(stock_clause)

	price_clause = {
		"missing_buying": "bp.price_list_rate IS NULL",
		"missing_selling": "sp.price_list_rate IS NULL",
		"missing_any": "(bp.price_list_rate IS NULL OR sp.price_list_rate IS NULL)",
		"has_both": "(bp.price_list_rate IS NOT NULL AND sp.price_list_rate IS NOT NULL)",
	}.get(price_status)
	if price_clause:
		conditions.append(price_clause)

	return conditions


def _items_from_where(search="", item_group="", supplier="", stock_status="", price_status=""):
	"""Build the shared FROM/JOIN block, the WHERE clause and bind values."""
	conditions = ["i.disabled = 0"]
	values = {"buying": BUYING_PRICE_LIST, "selling": SELLING_PRICE_LIST}

	if search:
		conditions.append("(i.name LIKE %(search)s OR i.item_name LIKE %(search)s)")
		values["search"] = f"%{search}%"

	if item_group:
		conditions.append("i.item_group = %(item_group)s")
		values["item_group"] = item_group

	conditions.extend(_filter_conditions(supplier, stock_status, price_status, values))

	return _ITEMS_FROM, " AND ".join(conditions), values


def _fetch_item_rows(from_block, where, values, limit=None, offset=0):
	limit_clause = ""
	if limit is not None:
		limit_clause = "LIMIT %(limit)s OFFSET %(offset)s"
		values = {**values, "limit": limit, "offset": offset}

	return frappe.db.sql(
		f"""
		SELECT
			i.name              AS item_code,
			i.item_name,
			i.image,
			i.item_group,
			bp.price_list_rate  AS buying_price,
			sp.price_list_rate  AS selling_price,
			COALESCE(b.qty, 0)  AS qty,
			sup.supplier
		{from_block}
		WHERE {where}
		ORDER BY i.item_name ASC
		{limit_clause}
		""",
		values,
		as_dict=True,
	)


@frappe.whitelist()
def get_items(
	search="", item_group="", supplier="", stock_status="", price_status="", limit=50, offset=0
):
	"""Paginated, searchable item list with prices, on-hand qty and supplier."""
	limit = min(cint(limit) or 50, MAX_LIMIT)
	offset = cint(offset)

	from_block, where, values = _items_from_where(
		search, item_group, supplier, stock_status, price_status
	)
	rows = _fetch_item_rows(from_block, where, values, limit=limit, offset=offset)

	total = frappe.db.sql(
		f"SELECT COUNT(*) {from_block} WHERE {where}", values
	)[0][0]

	return {"rows": rows, "total": total}


@frappe.whitelist()
def update_item(item_code, fields):
	"""Update an item's name and/or primary supplier.

	``fields`` is a JSON object that may contain ``item_name`` and ``supplier``.
	The supplier is written to the first row of the Item's ``supplier_items``
	child table (Item Supplier) -- no schema change.
	"""
	if isinstance(fields, str):
		fields = json.loads(fields)

	if not frappe.db.exists("Item", item_code):
		frappe.throw(_("Item {0} does not exist.").format(item_code))

	doc = frappe.get_doc("Item", item_code)
	changed = []

	if "item_name" in fields:
		new_name = (fields["item_name"] or "").strip()
		if not new_name:
			frappe.throw(_("Item name cannot be empty."))
		doc.item_name = new_name
		changed.append("item_name")

	if "supplier" in fields:
		supplier = (fields["supplier"] or "").strip()
		if supplier and not frappe.db.exists("Supplier", supplier):
			frappe.throw(_("Supplier {0} does not exist.").format(supplier))
		if doc.supplier_items:
			if supplier:
				doc.supplier_items[0].supplier = supplier
			else:
				doc.supplier_items = []
		elif supplier:
			doc.append("supplier_items", {"supplier": supplier})
		changed.append("supplier")

	if "item_group" in fields:
		item_group = (fields["item_group"] or "").strip()
		if not item_group:
			frappe.throw(_("Item Group cannot be empty."))
		if not frappe.db.exists("Item Group", item_group):
			frappe.throw(_("Item Group {0} does not exist.").format(item_group))
		doc.item_group = item_group
		changed.append("item_group")

	if not changed:
		return {"ok": True, "changed": []}

	doc.save(ignore_permissions=False)
	frappe.db.commit()
	return {"ok": True, "changed": changed}


@frappe.whitelist()
def rename_item(old_code, new_code):
	"""Rename an Item's code -- a true primary-key rename, not a field write."""
	old_code = (old_code or "").strip()
	new_code = (new_code or "").strip()

	if not new_code:
		frappe.throw(_("New item code cannot be empty."))
	if old_code == new_code:
		return {"ok": True, "item_code": old_code}
	if not frappe.db.exists("Item", old_code):
		frappe.throw(_("Item {0} does not exist.").format(old_code))
	if frappe.db.exists("Item", new_code):
		frappe.throw(_("Item {0} already exists.").format(new_code))

	frappe.rename_doc("Item", old_code, new_code, merge=False)
	frappe.db.commit()
	return {"ok": True, "item_code": new_code}


@frappe.whitelist()
def update_item_price(item_code, price_list, rate):
	"""Create-or-update an Item Price row for the given price list."""
	rate = flt(rate)
	if rate <= 0:
		frappe.throw(_("Price must be a positive number."))
	if price_list not in (BUYING_PRICE_LIST, SELLING_PRICE_LIST):
		frappe.throw(_("Invalid price list."))
	if not frappe.db.exists("Item", item_code):
		frappe.throw(_("Item {0} does not exist.").format(item_code))

	existing = frappe.db.get_value(
		"Item Price", {"item_code": item_code, "price_list": price_list}, "name"
	)
	if existing:
		frappe.db.set_value("Item Price", existing, "price_list_rate", rate)
	else:
		frappe.get_doc(
			{
				"doctype": "Item Price",
				"item_code": item_code,
				"price_list": price_list,
				"price_list_rate": rate,
			}
		).insert(ignore_permissions=True)

	frappe.db.commit()
	return {"ok": True, "item_code": item_code, "price_list": price_list, "rate": rate}


@frappe.whitelist()
def set_item_qty(item_code, qty, warehouse=None, submit=False):
	"""Create a Stock Reconciliation that sets an item's on-hand qty.

	By default the document is left as a DRAFT -- a human reviews and submits
	it from the desk, since submission posts stock ledger entries. When
	``submit`` is truthy the SR is submitted immediately (still subject to the
	user's submit permission).
	"""
	qty = flt(qty)
	if qty < 0:
		frappe.throw(_("Quantity cannot be negative."))
	if not frappe.db.exists("Item", item_code):
		frappe.throw(_("Item {0} does not exist.").format(item_code))

	warehouse = _stock.resolve_warehouse(warehouse)

	# Valuation rate and difference account are shared with the Stock Count
	# feature -- see easy_entry.api._stock for the resolution rules.
	valuation_rate = _stock.resolve_valuation_rate(item_code, warehouse)
	company = frappe.db.get_value("Warehouse", warehouse, "company")
	difference_account = _stock.resolve_difference_account(company)

	sr = frappe.new_doc("Stock Reconciliation")
	sr.company = company
	sr.purpose = "Stock Reconciliation"
	sr.expense_account = difference_account
	sr.posting_date = nowdate()
	sr.posting_time = nowtime()
	sr.append(
		"items",
		{
			"item_code": item_code,
			"warehouse": warehouse,
			"qty": qty,
			"valuation_rate": flt(valuation_rate),
		},
	)
	sr.insert(ignore_permissions=False)
	if cint(submit):
		sr.submit()  # raises if the user lacks submit permission
	frappe.db.commit()
	return {"ok": True, "stock_reconciliation": sr.name, "docstatus": sr.docstatus}


@frappe.whitelist()
def export_items_xlsx(search="", item_group="", supplier="", stock_status="", price_status=""):
	"""Build an XLSX sheet of items (for handing to a supplier) and stream it."""
	from_block, where, values = _items_from_where(
		search, item_group, supplier, stock_status, price_status
	)
	rows = _fetch_item_rows(from_block, where, values)

	header = [
		_("Item Code"),
		_("Item Name"),
		_("Buying Price"),
		_("Selling Price"),
		_("Quantity"),
		_("Supplier"),
	]
	data = [header]
	for row in rows:
		data.append(
			[
				row.item_code,
				row.item_name,
				flt(row.buying_price),
				flt(row.selling_price),
				flt(row.qty),
				row.supplier or "",
			]
		)

	xlsx_file = make_xlsx(data, "Items")
	frappe.response["filename"] = "items.xlsx"
	frappe.response["filecontent"] = xlsx_file.getvalue()
	frappe.response["type"] = "binary"
