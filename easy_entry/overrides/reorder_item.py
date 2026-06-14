import frappe


def send_email_notification(company_wise_mr):
	"""Override: send a *cumulative* auto reorder notification email in Arabic.

	Lists every item that auto-reorder flagged AND is *still actually short* right now —
	i.e. has an open auto-reorder Material Request and on-hand stock is still at/below its
	warehouse reorder level. One row per item+warehouse (newest related MR on top).

	Note: this is gated on live stock (on-hand <= reorder level), NOT on the Material
	Request's received_qty. In this shop items are restocked via Stock Reconciliation /
	Stock Count, not Purchase Receipts, so auto-reorder MRs never get marked received and
	would otherwise linger forever even after the shelf is refilled.
	"""
	from erpnext.stock.reorder_item import get_email_list
	from frappe.utils.pdf import get_pdf

	for company in company_wise_mr:
		email_list = get_email_list(company)

		if not email_list:
			continue

		rows = frappe.db.sql(
			"""
			SELECT * FROM (
				SELECT
					mr.name              AS mr_name,
					mr.transaction_date  AS transaction_date,
					mr.status            AS status,
					mri.item_code, mri.item_name, mri.warehouse, mri.uom,
					COALESCE(b.actual_qty, 0)      AS on_hand,
					ir.warehouse_reorder_level     AS reorder_level,
					ir.warehouse_reorder_qty       AS reorder_qty,
					ROW_NUMBER() OVER (
						PARTITION BY mri.item_code, mri.warehouse
						ORDER BY mr.transaction_date DESC, mr.name DESC
					) AS rn
				FROM `tabMaterial Request Item` mri
				JOIN `tabMaterial Request` mr ON mr.name = mri.parent
				LEFT JOIN `tabBin` b
					ON b.item_code = mri.item_code AND b.warehouse = mri.warehouse
				JOIN `tabItem Reorder` ir
					ON ir.parent = mri.item_code AND ir.warehouse = mri.warehouse
				WHERE mr.docstatus = 1
				  AND mr.auto_created_via_reorder = 1
				  AND mr.company = %(company)s
				  AND mr.status NOT IN ('Stopped', 'Cancelled', 'Received', 'Issued', 'Transferred')
				  AND mri.received_qty < mri.qty
				  AND COALESCE(b.actual_qty, 0) <= ir.warehouse_reorder_level
			) t
			WHERE t.rn = 1
			ORDER BY t.transaction_date DESC, t.mr_name DESC
			""",
			{"company": company},
			as_dict=True,
		)

		if not rows:
			continue

		today = frappe.utils.nowdate()

		msg = frappe.render_template(
			"easy_entry/templates/emails/reorder_item_ar.html",
			{"rows": rows},
		)

		# Build a printable PDF of the same list and attach it to the email.
		pdf_filename = f"reorder_items_{today}.pdf"
		pdf_html = frappe.render_template(
			"easy_entry/templates/emails/reorder_item_pdf.html",
			{"rows": rows, "company": company, "today": today},
		)
		pdf_content = get_pdf(pdf_html)

		frappe.sendmail(
			recipients=email_list,
			subject=f"أصناف تحتاج إعادة طلب ({len(rows)})",
			message=msg,
			attachments=[{"fname": pdf_filename, "fcontent": pdf_content}],
		)
