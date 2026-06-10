import frappe
from frappe import _
from frappe.utils import flt, today


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.as_of_date:
		filters.as_of_date = today()

	columns = get_columns()
	data = get_data(filters)
	summary = get_summary(data)

	return columns, data, None, None, summary


def get_columns():
	return [
		{
			"fieldname": "customer",
			"label": _("العميل / Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150,
		},
		{
			"fieldname": "customer_name",
			"label": _("الاسم / Name"),
			"fieldtype": "Data",
			"width": 155,
		},
		{
			"fieldname": "outstanding_amount",
			"label": _("المستحق / Outstanding"),
			"fieldtype": "Currency",
			"width": 135,
		},
		{
			"fieldname": "invoice",
			"label": _("الفاتورة / Invoice"),
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 135,
		},
		{
			"fieldname": "posting_date",
			"label": _("التاريخ / Date"),
			"fieldtype": "Date",
			"width": 90,
		},
		{
			"fieldname": "item_code",
			"label": _("الصنف / Item"),
			"fieldtype": "Link",
			"options": "Item",
			"width": 105,
		},
		{
			"fieldname": "item_name",
			"label": _("اسم الصنف / Item Name"),
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"fieldname": "qty",
			"label": _("الكمية / Qty"),
			"fieldtype": "Float",
			"width": 60,
		},
		{
			"fieldname": "rate",
			"label": _("السعر / Rate"),
			"fieldtype": "Currency",
			"width": 95,
		},
		{
			"fieldname": "amount",
			"label": _("الإجمالي / Amount"),
			"fieldtype": "Currency",
			"width": 105,
		},
	]


def get_data(filters):
	conditions = [
		"si.docstatus = 1",
		"si.outstanding_amount > 0.009",
		"si.posting_date <= %(as_of_date)s",
	]
	params = {"as_of_date": filters.as_of_date}

	if filters.get("company"):
		conditions.append("si.company = %(company)s")
		params["company"] = filters.company

	if filters.get("customer"):
		conditions.append("si.customer = %(customer)s")
		params["customer"] = filters.customer

	where = " AND ".join(conditions)

	rows = frappe.db.sql(
		f"""
		SELECT
			si.customer,
			si.customer_name,
			si.name AS invoice,
			si.posting_date,
			si.grand_total,
			si.outstanding_amount,
			sii.item_code,
			sii.item_name,
			sii.qty,
			sii.rate,
			sii.amount
		FROM `tabSales Invoice` si
		JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
		WHERE {where}
		ORDER BY si.customer, si.posting_date, si.name, sii.idx
		""",
		params,
		as_dict=True,
	)

	if not rows:
		return []

	# Aggregate customer totals first (one pass)
	customer_totals = {}
	customer_names = {}
	for row in rows:
		key = row.customer
		grand_total = flt(row.grand_total)
		item_outstanding = (
			flt(row.outstanding_amount) * flt(row.amount) / grand_total
			if grand_total
			else flt(row.amount)
		)
		customer_totals[key] = customer_totals.get(key, 0.0) + item_outstanding
		customer_names[key] = row.customer_name or row.customer

	# Build output: group header per customer (with total), then detail rows
	data = []
	current_customer = None

	for row in rows:
		if row.customer != current_customer:
			current_customer = row.customer

			# Customer header row: shows ID, name, and total outstanding
			data.append(
				{
					"customer": row.customer,
					"customer_name": customer_names[row.customer],
					"invoice": None,
					"posting_date": None,
					"item_code": None,
					"item_name": None,
					"qty": None,
					"rate": None,
					"amount": None,
					"outstanding_amount": customer_totals[row.customer],
					"is_group": 1,
					"indent": 0,
				}
			)

		grand_total = flt(row.grand_total)
		item_outstanding = (
			flt(row.outstanding_amount) * flt(row.amount) / grand_total
			if grand_total
			else flt(row.amount)
		)

		data.append(
			{
				"customer": None,
				"customer_name": None,
				"invoice": row.invoice,
				"posting_date": row.posting_date,
				"item_code": row.item_code,
				"item_name": row.item_name,
				"qty": flt(row.qty),
				"rate": flt(row.rate),
				"amount": flt(row.amount),
				"outstanding_amount": item_outstanding,
				"is_group": 0,
				"indent": 1,
			}
		)

	return data


def get_summary(data):
	header_rows = [r for r in data if r.get("is_group")]
	total = sum(flt(r.get("outstanding_amount") or 0) for r in header_rows)
	customer_count = len(header_rows)

	return [
		{
			"label": _("عدد العملاء / Customers"),
			"value": customer_count,
			"datatype": "Int",
			"color": "blue",
		},
		{
			"label": _("إجمالي المستحق / Total Outstanding"),
			"value": total,
			"datatype": "Currency",
			"color": "orange",
		},
	]
