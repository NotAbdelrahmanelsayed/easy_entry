import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def get_price_lists():
	return frappe.get_all(
		"Price List",
		filters={"enabled": 1},
		fields=["name", "currency", "buying", "selling"],
		order_by="name asc",
	)


@frappe.whitelist()
def get_item_prices(search="", price_list="Standard Selling", limit=50, offset=0):
	limit = min(int(limit), 200)
	offset = int(offset)

	search_cond = ""
	values = {"price_list": price_list, "limit": limit, "offset": offset}

	if search:
		search_cond = "AND (ip.item_code LIKE %(search)s OR ip.item_name LIKE %(search)s)"
		values["search"] = f"%{search}%"

	rows = frappe.db.sql(
		f"""
		SELECT
			ip.name,
			ip.item_code,
			ip.item_name,
			ip.uom,
			ip.currency,
			ip.price_list_rate,
			ip.price_list,
			i.image
		FROM `tabItem Price` ip
		LEFT JOIN `tabItem` i ON i.name = ip.item_code
		WHERE ip.price_list = %(price_list)s
			AND (ip.valid_upto IS NULL OR ip.valid_upto >= CURDATE())
			{search_cond}
		ORDER BY ip.item_name ASC
		LIMIT %(limit)s OFFSET %(offset)s
		""",
		values,
		as_dict=True,
	)

	total = frappe.db.sql(
		f"""
		SELECT COUNT(*) as cnt
		FROM `tabItem Price` ip
		WHERE ip.price_list = %(price_list)s
			AND (ip.valid_upto IS NULL OR ip.valid_upto >= CURDATE())
			{search_cond}
		""",
		values,
	)[0][0]

	return {"rows": rows, "total": total}


@frappe.whitelist()
def update_item_price(name, price_list_rate):
	doc = frappe.get_doc("Item Price", name)
	doc.price_list_rate = flt(price_list_rate)
	doc.save(ignore_permissions=False)
	frappe.db.commit()
	return {"name": doc.name, "price_list_rate": doc.price_list_rate}
