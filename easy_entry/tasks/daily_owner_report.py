import frappe

from easy_entry.tasks.recipients import get_report_recipients


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

	# Financial analysis: totals for the day (sales / credit / collected)
	totals = frappe.db.sql(
		"""
		SELECT
			COALESCE(SUM(si.grand_total), 0)                  AS total_sales,
			COALESCE(SUM(si.grand_total - si.paid_amount), 0) AS total_credit,
			COALESCE(SUM(si.paid_amount), 0)                  AS total_collected
		FROM `tabSales Invoice` si
		WHERE si.docstatus = 1
		  AND DATE(si.posting_date) = %(report_date)s
		""",
		{"report_date": report_date},
		as_dict=True,
	)[0]

	# Expected cash split by payment method (cash on hand, InstaPay, visa, …)
	payments = frappe.db.sql(
		"""
		SELECT sip.mode_of_payment          AS mode,
		       COALESCE(SUM(sip.amount), 0) AS amount
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON si.name = sip.parent
		WHERE si.docstatus = 1
		  AND DATE(si.posting_date) = %(report_date)s
		GROUP BY sip.mode_of_payment
		ORDER BY amount DESC
		""",
		{"report_date": report_date},
		as_dict=True,
	)

	recipients = get_report_recipients(["Store Owner"])

	if not recipients:
		return

	message = frappe.render_template(
		"easy_entry/templates/emails/daily_owner_report_ar.html",
		{
			"items": sold_items,
			"today": report_date,
			"total_sales": totals.total_sales,
			"total_credit": totals.total_credit,
			"total_collected": totals.total_collected,
			"payments": payments,
		},
	)

	frappe.sendmail(
		recipients=recipients,
		subject=f"تقرير مبيعات اليوم - {report_date}",
		message=message,
	)
