"""Whitelisted endpoints for the Stock Count SPA feature.

A counting session is an ``EE Stock Count`` document; each scan upserts a
child line. Finishing builds a *draft* Stock Reconciliation for the lines
that differ from system stock -- a human reviews and submits it on the desk.

Convention (shared with ``item_manager``): explicit ``frappe.db.commit()``
after writes, permission-respecting (``ignore_permissions=False``).
"""

import frappe
from frappe import _
from frappe.utils import cint, flt

from easy_entry.api import _stock
from easy_entry.easy_entry.doctype.ee_stock_count.ee_stock_count import (
	STATUS_FINISHED,
)

SESSION_DOCTYPE = "EE Stock Count"


def _line_payload(item_code, item_name, counted_qty, warehouse):
	"""Shape one counted line for the SPA, with a live system qty + difference."""
	system_qty = _stock.get_system_qty(item_code, warehouse)
	counted_qty = flt(counted_qty)
	return {
		"item_code": item_code,
		"item_name": item_name,
		"counted_qty": counted_qty,
		"system_qty": system_qty,
		"difference": counted_qty - system_qty,
	}


@frappe.whitelist()
def resolve_barcode(code, warehouse=None):
	"""Resolve a scanned/typed code to an item.

	Lookup order: an ``Item Barcode`` row whose ``barcode`` matches, then a
	direct ``Item`` code match. Throws if nothing resolves or the item is
	disabled.
	"""
	code = (code or "").strip()
	if not code:
		frappe.throw(_("Scan or enter a code."))

	warehouse = _stock.resolve_warehouse(warehouse)

	item_code = frappe.db.get_value("Item Barcode", {"barcode": code}, "parent")
	if not item_code and frappe.db.exists("Item", code):
		item_code = code
	if not item_code:
		frappe.throw(_("No item found for code {0}.").format(code))

	item = frappe.db.get_value(
		"Item", item_code, ["item_name", "image", "disabled"], as_dict=True
	)
	if item.disabled:
		frappe.throw(_("Item {0} is disabled.").format(item_code))

	return {
		"item_code": item_code,
		"item_name": item.item_name,
		"image": item.image,
		"system_qty": _stock.get_system_qty(item_code, warehouse),
	}


@frappe.whitelist()
def search_items(query, warehouse=None, limit=20):
	"""Fuzzy item lookup for the scan box: matches barcode, code, or name.

	Used as the fallback when an exact ``resolve_barcode`` fails. Read-only.
	"""
	query = (query or "").strip()
	if not query:
		return []

	warehouse = _stock.resolve_warehouse(warehouse)
	like = f"%{query}%"
	rows = frappe.db.sql(
		"""
		SELECT DISTINCT i.name AS item_code, i.item_name, i.image
		FROM `tabItem` i
		LEFT JOIN `tabItem Barcode` bc ON bc.parent = i.name
		WHERE i.disabled = 0
		  AND (i.name LIKE %(like)s OR i.item_name LIKE %(like)s OR bc.barcode LIKE %(like)s)
		ORDER BY i.item_name ASC
		LIMIT %(limit)s
		""",
		{"like": like, "limit": cint(limit) or 20},
		as_dict=True,
	)
	for r in rows:
		r["system_qty"] = _stock.get_system_qty(r["item_code"], warehouse)
	return rows


@frappe.whitelist()
def start_session(warehouse=None):
	"""Create a new In Progress count session for a warehouse."""
	warehouse = _stock.resolve_warehouse(warehouse)

	doc = frappe.new_doc(SESSION_DOCTYPE)
	doc.warehouse = warehouse
	doc.company = frappe.db.get_value("Warehouse", warehouse, "company")
	doc.insert(ignore_permissions=False)
	frappe.db.commit()
	return {"session": doc.name, "warehouse": warehouse}


@frappe.whitelist()
def list_open_sessions():
	"""In Progress sessions owned by the current user, newest first."""
	sessions = frappe.get_all(
		SESSION_DOCTYPE,
		filters={"status": "In Progress", "owner": frappe.session.user},
		fields=["name", "warehouse", "modified"],
		order_by="modified desc",
	)
	for session in sessions:
		session["line_count"] = frappe.db.count(
			"EE Stock Count Line", {"parent": session["name"]}
		)
	return sessions


@frappe.whitelist()
def get_session(name):
	"""Session header plus every counted line, each with a live difference."""
	doc = frappe.get_doc(SESSION_DOCTYPE, name)
	doc.check_permission("read")

	# Newest scan first -- the SPA prepends new lines, so reverse child order.
	lines = [
		_line_payload(row.item_code, row.item_name, row.counted_qty, doc.warehouse)
		for row in reversed(doc.count_lines)
	]
	return {
		"session": doc.name,
		"warehouse": doc.warehouse,
		"status": doc.status,
		"modified": str(doc.modified),
		"stock_reconciliation": doc.stock_reconciliation,
		"lines": lines,
	}


@frappe.whitelist()
def upsert_count_line(session, item_code, counted_qty):
	"""Add a counted line, or overwrite an existing item's counted qty."""
	doc = frappe.get_doc(SESSION_DOCTYPE, session)
	line = doc.set_count(item_code, counted_qty)
	doc.save(ignore_permissions=False)
	frappe.db.commit()

	item_name = line.item_name or frappe.db.get_value("Item", item_code, "item_name")
	return _line_payload(line.item_code, item_name, line.counted_qty, doc.warehouse)


@frappe.whitelist()
def remove_count_line(session, item_code):
	"""Remove a counted line from an In Progress session."""
	doc = frappe.get_doc(SESSION_DOCTYPE, session)
	doc.remove_count(item_code)
	doc.save(ignore_permissions=False)
	frappe.db.commit()
	return {"ok": True, "line_count": len(doc.count_lines)}


@frappe.whitelist()
def finish_session(session):
	"""Finish a session: build a draft Stock Reconciliation, mark it Finished.

	Requires at least one counted line. The Stock Reconciliation is left as a
	draft for desk review; it is ``None`` when every count matched stock.
	"""
	doc = frappe.get_doc(SESSION_DOCTYPE, session)
	if doc.status == STATUS_FINISHED:
		frappe.throw(_("This count session is already finished."))
	if not doc.count_lines:
		frappe.throw(_("Count at least one item before finishing."))

	sr_name = doc.build_reconciliation()
	doc.stock_reconciliation = sr_name
	doc.status = STATUS_FINISHED
	doc.save(ignore_permissions=False)
	frappe.db.commit()

	return {
		"session": doc.name,
		"line_count": len(doc.count_lines),
		"stock_reconciliation": sr_name,
	}
