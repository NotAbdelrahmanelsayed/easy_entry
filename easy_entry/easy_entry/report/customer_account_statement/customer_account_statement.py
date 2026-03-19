import frappe
from frappe import _
from frappe.utils import get_first_day, getdate, nowdate, today


def execute(filters=None):
	filters = frappe._dict(filters or {})
	validate_filters(filters)

	columns = get_columns()

	if not filters.customer:
		return columns, [], None, None, []

	data = get_data(filters)
	summary = get_report_summary(filters, columns, data, None)

	return columns, data, None, None, summary


def validate_filters(filters):
	if not filters.from_date:
		filters.from_date = get_first_day(today())
	if not filters.to_date:
		filters.to_date = today()


def get_columns():
	return [
		{
			"fieldname": "date",
			"label": _("التاريخ / Date"),
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"fieldname": "voucher_type",
			"label": _("النوع / Type"),
			"fieldtype": "Data",
			"width": 110,
		},
		{
			"fieldname": "voucher_no",
			"label": _("المرجع / Ref #"),
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 160,
		},
		{
			"fieldname": "description",
			"label": _("الوصف / Description"),
			"fieldtype": "Data",
			"width": 220,
		},
		{
			"fieldname": "qty",
			"label": _("الكمية / Qty"),
			"fieldtype": "Float",
			"width": 80,
		},
		{
			"fieldname": "rate",
			"label": _("السعر / Rate"),
			"fieldtype": "Currency",
			"width": 110,
		},
		{
			"fieldname": "debit",
			"label": _("مدين / Debit"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "credit",
			"label": _("دائن / Credit"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "balance",
			"label": _("الرصيد / Balance"),
			"fieldtype": "Currency",
			"width": 130,
		},
	]


def get_data(filters):
	opening_balance = get_opening_balance(filters)
	invoice_rows = get_invoice_rows(filters)
	payment_rows = get_payment_rows(filters)
	gl_debit_rows = get_gl_debit_rows(filters)

	data = []
	running_balance = opening_balance

	# Opening balance row
	data.append(
		{
			"date": filters.from_date,
			"voucher_type": "",
			"voucher_no": "",
			"description": _("رصيد أول المدة / Opening Balance"),
			"qty": None,
			"rate": None,
			"debit": None,
			"credit": None,
			"balance": opening_balance,
			"bold": 1,
		}
	)

	# Merge invoices, payments, and GL debit entries chronologically
	all_events = []

	# Group invoice items by invoice
	invoice_groups = {}
	for row in invoice_rows:
		key = row["voucher_no"]
		invoice_groups.setdefault(key, []).append(row)

	for voucher_no, items in invoice_groups.items():
		posting_date = items[0]["date"]
		all_events.append(
			{
				"type": "invoice",
				"date": posting_date,
				"voucher_no": voucher_no,
				"items": items,
			}
		)

	for row in payment_rows:
		all_events.append(
			{
				"type": "payment",
				"date": row["date"],
				"voucher_no": row["voucher_no"],
				"voucher_type": row["voucher_type"],
				"row": row,
			}
		)

	for row in gl_debit_rows:
		all_events.append(
			{
				"type": "gl_debit",
				"date": row["date"],
				"voucher_no": row["voucher_no"],
				"voucher_type": row["voucher_type"],
				"row": row,
			}
		)

	# Sort by date, then voucher_no; invoices first, then debits/payments on same date
	all_events.sort(key=lambda e: (getdate(e["date"]), e["voucher_no"], 0 if e["type"] == "invoice" else 1))

	total_debit = 0.0
	total_credit = 0.0

	for event in all_events:
		if event["type"] == "invoice":
			items = event["items"]
			invoice_debit = sum(item["debit"] or 0 for item in items)
			running_balance += invoice_debit
			total_debit += invoice_debit

			for i, item in enumerate(items):
				is_last = i == len(items) - 1
				data.append(
					{
						"date": item["date"],
						"voucher_type": "Sales Invoice",
						"voucher_no": item["voucher_no"],
						"description": item["description"],
						"qty": item["qty"],
						"rate": item["rate"],
						"debit": item["debit"],
						"credit": None,
						"balance": running_balance if is_last else None,
					}
				)

		elif event["type"] == "payment":
			row = event["row"]
			credit = row["credit"] or 0
			running_balance -= credit
			total_credit += credit

			voucher_type = event["voucher_type"]
			# Cash sales record payment as a GL credit under the Sales Invoice itself
			if voucher_type == "Sales Invoice":
				description = _("دفع نقدي / Cash Payment")
			else:
				description = row.get("description") or ""

			data.append(
				{
					"date": row["date"],
					"voucher_type": voucher_type,
					"voucher_no": row["voucher_no"],
					"description": description,
					"qty": None,
					"rate": None,
					"debit": None,
					"credit": credit,
					"balance": running_balance,
				}
			)

		elif event["type"] == "gl_debit":
			row = event["row"]
			debit = row["debit"] or 0
			running_balance += debit
			total_debit += debit

			data.append(
				{
					"date": row["date"],
					"voucher_type": row["voucher_type"],
					"voucher_no": row["voucher_no"],
					"description": row.get("description") or "",
					"qty": None,
					"rate": None,
					"debit": debit,
					"credit": None,
					"balance": running_balance,
				}
			)

	# Closing/Totals row
	data.append(
		{
			"date": filters.to_date,
			"voucher_type": "",
			"voucher_no": "",
			"description": _("الإجمالي / Closing Balance"),
			"qty": None,
			"rate": None,
			"debit": total_debit,
			"credit": total_credit,
			"balance": running_balance,
			"bold": 1,
		}
	)

	return data


def get_opening_balance(filters):
	result = frappe.db.sql(
		"""
        SELECT COALESCE(SUM(debit) - SUM(credit), 0) AS opening
        FROM `tabGL Entry`
        WHERE party_type = 'Customer'
          AND party = %(customer)s
          AND posting_date < %(from_date)s
          AND is_cancelled = 0
        """,
		{"customer": filters.customer, "from_date": filters.from_date},
		as_dict=True,
	)
	return result[0].opening if result else 0.0


def get_invoice_rows(filters):
	conditions = "si.customer = %(customer)s AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s AND si.docstatus = 1"
	if filters.get("company"):
		conditions += " AND si.company = %(company)s"

	rows = frappe.db.sql(
		f"""
        SELECT
            si.posting_date AS date,
            si.name AS voucher_no,
            sii.item_name AS description,
            sii.qty,
            sii.rate,
            sii.amount AS debit,
            sii.idx
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE {conditions}
        ORDER BY si.posting_date, si.name, sii.idx
        """,
		{
			"customer": filters.customer,
			"from_date": filters.from_date,
			"to_date": filters.to_date,
			"company": filters.get("company"),
		},
		as_dict=True,
	)
	return rows


def get_payment_rows(filters):
	"""Query GL credit entries — captures Payment Entry, cash-at-invoice, and Journal Entry payments."""
	conditions = """
        party_type = 'Customer'
        AND party = %(customer)s
        AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND is_cancelled = 0
        AND credit > 0
    """
	if filters.get("company"):
		conditions += " AND company = %(company)s"

	rows = frappe.db.sql(
		f"""
        SELECT
            posting_date AS date,
            voucher_type,
            voucher_no,
            SUM(credit) AS credit,
            MAX(remarks) AS description
        FROM `tabGL Entry`
        WHERE {conditions}
        GROUP BY voucher_type, voucher_no, posting_date
        ORDER BY posting_date, voucher_no
        """,
		{
			"customer": filters.customer,
			"from_date": filters.from_date,
			"to_date": filters.to_date,
			"company": filters.get("company"),
		},
		as_dict=True,
	)
	return rows


def get_gl_debit_rows(filters):
	"""Query GL debit entries from non-Sales Invoice vouchers (e.g. Journal Entry charges)."""
	conditions = """
        party_type = 'Customer'
        AND party = %(customer)s
        AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND is_cancelled = 0
        AND debit > 0
        AND voucher_type != 'Sales Invoice'
    """
	if filters.get("company"):
		conditions += " AND company = %(company)s"

	rows = frappe.db.sql(
		f"""
        SELECT
            posting_date AS date,
            voucher_type,
            voucher_no,
            SUM(debit) AS debit,
            MAX(remarks) AS description
        FROM `tabGL Entry`
        WHERE {conditions}
        GROUP BY voucher_type, voucher_no, posting_date
        ORDER BY posting_date, voucher_no
        """,
		{
			"customer": filters.customer,
			"from_date": filters.from_date,
			"to_date": filters.to_date,
			"company": filters.get("company"),
		},
		as_dict=True,
	)
	return rows


def get_report_summary(filters, columns, data, report):
	if not data:
		return []

	total_debit = 0.0
	total_credit = 0.0
	closing_balance = 0.0

	# Read totals from the closing row (last row)
	for row in data:
		if isinstance(row, dict) and row.get("description") == _("الإجمالي / Closing Balance"):
			total_debit = row.get("debit") or 0.0
			total_credit = row.get("credit") or 0.0
			closing_balance = row.get("balance") or 0.0
			break

	return [
		{
			"label": _("إجمالي الفواتير / Total Invoiced"),
			"value": total_debit,
			"datatype": "Currency",
			"color": "red",
		},
		{
			"label": _("إجمالي المدفوعات / Total Paid"),
			"value": total_credit,
			"datatype": "Currency",
			"color": "green",
		},
		{
			"label": _("الرصيد المستحق / Balance Due"),
			"value": closing_balance,
			"datatype": "Currency",
			"color": "orange",
		},
	]
