import frappe
from frappe.utils import flt, today, get_url

from easy_entry.tasks.recipients import get_report_recipients


def send_ar_summary_email(for_date=None):
	"""Send daily Accounts Receivable summary (customer totals only) to Store Owners."""
	as_of = for_date or today()
	company = frappe.defaults.get_global_default("company")

	rows = frappe.db.sql(
		"""
		SELECT
			si.customer,
			si.customer_name,
			SUM(si.outstanding_amount) AS total_outstanding
		FROM `tabSales Invoice` si
		WHERE si.docstatus = 1
		  AND si.outstanding_amount > 0.009
		  AND si.posting_date <= %(as_of)s
		  AND si.company = %(company)s
		GROUP BY si.customer, si.customer_name
		ORDER BY total_outstanding DESC
		""",
		{"as_of": as_of, "company": company},
		as_dict=True,
	)

	if not rows:
		return

	recipients = get_report_recipients(["Store Owner", "Accounts Manager", "Accounts User"])

	if not recipients:
		return

	total = sum(flt(r.total_outstanding) for r in rows)
	report_url = f"{get_url()}/app/query-report/Accounts%20Receivable%20Items"

	message = frappe.render_template(
		"easy_entry/templates/emails/ar_summary_ar.html",
		{
			"customers": rows,
			"total": total,
			"as_of": as_of,
			"report_url": report_url,
			"customer_count": len(rows),
		},
	)

	frappe.sendmail(
		recipients=recipients,
		subject=f"الذمم المدينة — {as_of}",
		message=message,
	)
