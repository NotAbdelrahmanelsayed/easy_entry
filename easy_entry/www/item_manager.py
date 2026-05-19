import frappe

no_cache = 1


def get_context(context):
	# Gate the SPA server-side: guests never see the app shell.
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/item-manager"
		raise frappe.Redirect

	# get_csrf_token() generates + stores the token in the session if absent;
	# the commit persists it. jinjaBootData injects each boot key as window[key].
	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()
	context.boot = frappe._dict(
		csrf_token=csrf_token,
		sitename=frappe.local.site,
	)
