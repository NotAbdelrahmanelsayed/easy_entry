import frappe


def get_report_recipients(roles):
	"""Emails of enabled users holding any of `roles`, minus opted-out addresses.

	Opt-outs are read from site_config `easy_entry_report_optout` (a list of emails)
	so an address can be silenced without stripping the user's roles, which they may
	still need for permissions.
	"""
	optout = {e.lower() for e in (frappe.conf.get("easy_entry_report_optout") or [])}

	rows = frappe.db.sql(
		"""
		SELECT DISTINCT u.email
		FROM `tabUser` u
		JOIN `tabHas Role` hr ON hr.parent = u.name
		WHERE hr.role IN %(roles)s
		  AND u.enabled = 1
		  AND u.email != ''
		""",
		{"roles": tuple(roles)},
		as_dict=True,
	)

	return [r.email for r in rows if r.email.lower() not in optout]
