import frappe


def send_daily_owner_report(for_date=None):
	"""Send daily sales report (sold items only) to all Store Owner users."""

	report_date = for_date or frappe.utils.add_days(frappe.utils.today(), -1)

	sold_items = frappe.db.sql(
		"""
		SELECT
			sii.item_code,
			sii.item_name,
			SUM(sii.qty)                                                AS qty_sold,
			MAX(sii.rate)                                               AS selling_price,
			MAX(COALESCE(sii.incoming_rate, 0))                         AS buying_price,
			COALESCE(SUM(b.actual_qty), 0)                              AS remaining_qty,
			SUM(sii.amount - sii.qty * COALESCE(sii.incoming_rate, 0)) AS gross_profit
		FROM `tabSales Invoice Item` sii
		JOIN `tabSales Invoice` si ON si.name = sii.parent
		LEFT JOIN `tabBin` b ON b.item_code = sii.item_code
		WHERE si.docstatus = 1
		  AND DATE(si.posting_date) = %(report_date)s
		GROUP BY sii.item_code, sii.item_name
		ORDER BY gross_profit DESC
		""",
		{"report_date": report_date},
		as_dict=True,
	)

	if not sold_items:
		return

	recipients = frappe.db.sql(
		"""
		SELECT u.email
		FROM `tabUser` u
		JOIN `tabHas Role` hr ON hr.parent = u.name
		WHERE hr.role = 'Store Owner'
		  AND u.enabled = 1
		  AND u.email != ''
		""",
		as_dict=True,
	)

	if not recipients:
		return

	message = frappe.render_template(
		"easy_entry/templates/emails/daily_owner_report_ar.html",
		{"items": sold_items, "today": report_date},
	)

	frappe.sendmail(
		recipients=[r.email for r in recipients],
		subject=f"تقرير مبيعات اليوم - {report_date}",
		message=message,
	)
