import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{
			"fieldname": "item_code",
			"label": "Item Code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 160,
		},
		{"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 220},
		{"fieldname": "buying_price", "label": "Buying Price", "fieldtype": "Currency", "width": 130},
		{"fieldname": "selling_price", "label": "Selling Price", "fieldtype": "Currency", "width": 130},
		{"fieldname": "missing", "label": "Missing", "fieldtype": "Data", "hidden": 1, "width": 220},
		{"fieldname": "actions", "label": "Actions", "fieldtype": "HTML", "width": 360},
	]


def get_data(filters):
	missing_type = filters.get("missing_type", "Any Missing")

	rows = frappe.db.sql(
		"""
        SELECT
            i.name              AS item_code,
            i.item_name,
            i.valuation_rate,
            bp.price_list_rate  AS buying_price,
            sp.price_list_rate  AS selling_price
        FROM `tabItem` i
        LEFT JOIN `tabItem Price` bp
            ON  bp.item_code  = i.name
            AND bp.price_list = 'Standard Buying'
        LEFT JOIN `tabItem Price` sp
            ON  sp.item_code  = i.name
            AND sp.price_list = 'Standard Selling'
        WHERE i.disabled = 0
          AND (bp.name IS NULL OR sp.name IS NULL)
        ORDER BY i.name
    """,
		as_dict=True,
	)

	data = []
	for row in rows:
		has_buying = 1 if row.buying_price is not None else 0
		has_selling = 1 if row.selling_price is not None else 0

		if missing_type == "Missing Buying Only" and not (not has_buying and has_selling):
			continue
		if missing_type == "Missing Selling Only" and not (has_buying and not has_selling):
			continue
		if missing_type == "Missing Both" and not (not has_buying and not has_selling):
			continue

		if not has_buying and not has_selling:
			missing_text = _("No Buying Price & No Selling Price")
		elif not has_buying:
			missing_text = _("No Buying Price")
		else:
			missing_text = _("No Selling Price")

		data.append(
			{
				"item_code": row.item_code,
				"item_name": row.item_name,
				"valuation_rate": flt(row.valuation_rate),
				"buying_price": flt(row.buying_price) if has_buying else None,
				"selling_price": flt(row.selling_price) if has_selling else None,
				"missing": missing_text,
				"actions": "",  # rendered client-side by JS formatter
				"has_buying": has_buying,  # hidden flag for JS — no column definition
				"has_selling": has_selling,
			}
		)

	return data


@frappe.whitelist()
def add_item_price(item_code, price_list, price):
	price = flt(price)
	if not price or price <= 0:
		frappe.throw(_("Price must be a positive number."))
	if price_list not in ("Standard Buying", "Standard Selling"):
		frappe.throw(_("Invalid price list."))

	existing = frappe.db.get_value("Item Price", {"item_code": item_code, "price_list": price_list}, "name")
	if existing:
		frappe.db.set_value("Item Price", existing, "price_list_rate", price)
	else:
		frappe.get_doc(
			{
				"doctype": "Item Price",
				"item_code": item_code,
				"price_list": price_list,
				"price_list_rate": price,
			}
		).insert(ignore_permissions=True)

	frappe.db.commit()
	return {"ok": True}
