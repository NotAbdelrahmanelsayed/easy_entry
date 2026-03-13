import frappe


def send_email_notification(company_wise_mr):
	"""Override: send auto reorder notification email in Arabic"""
	from erpnext.stock.reorder_item import get_email_list

	for company, mr_list in company_wise_mr.items():
		email_list = get_email_list(company)

		if not email_list:
			continue

		msg = frappe.render_template(
			"easy_entry/templates/emails/reorder_item_ar.html",
			{"mr_list": mr_list},
		)

		frappe.sendmail(
			recipients=email_list,
			subject="طلبات الشراء التلقائية - تم الإنشاء",
			message=msg,
		)
