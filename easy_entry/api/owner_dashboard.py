"""Whitelisted, read-only endpoints for the Store Owner Analytics Dashboard.

Restricted to Store Owner / System Manager (frappe.only_for auto-passes
Administrator). No writes -- no frappe.db.commit() calls in this module.

The gross-profit formula and the AR-per-customer query are duplicated from
``tasks/daily_owner_report.py`` and ``tasks/ar_summary_email.py`` on purpose
(see the plan's decision log) -- keep the SQL in sync if either changes.
"""

import frappe
from frappe import _
from frappe.utils import add_days, cint, flt, get_first_day, getdate, nowdate

VALID_PERIODS = ("today", "yesterday", "last_7_days", "this_month", "custom")
MAX_CUSTOM_RANGE_DAYS = 366
TREND_DAYS = 30
BEST_ITEMS_LIMIT = 10
# A filtered item/item-group view is meant for closer analysis -- show more rows.
BEST_ITEMS_FILTERED_LIMIT = 50
TOP_DEBTORS_LIMIT = 8
LOW_STOCK_LIMIT = 15
# Lookback window for the weekday-performance breakdown (same convention as
# reorder_levels.py's 90-day consumption window).
WEEKDAY_LOOKBACK_DAYS = 90
WEEKDAY_LABELS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

# sort_by -> ORDER BY column expression. Never interpolate user input directly.
_BEST_ITEMS_SORT_COLUMNS = {
	"gross_profit": "gross_profit",
	"qty": "qty_sold",
}


def _check_owner_access():
	frappe.only_for(("Store Owner", "System Manager"))


def _get_currency():
	return frappe.defaults.get_global_default("currency") or "EGP"


def get_period_range(period, today=None, from_date=None, to_date=None):
	"""Pure function: (period, pinned "today", optional custom range) -> (from_date, to_date)."""
	if period not in VALID_PERIODS:
		frappe.throw(_("Invalid period: {0}").format(period))

	ref_today = getdate(today) if today else getdate(nowdate())

	if period == "today":
		return ref_today, ref_today
	if period == "yesterday":
		yesterday = add_days(ref_today, -1)
		return yesterday, yesterday
	if period == "last_7_days":
		return add_days(ref_today, -6), ref_today
	if period == "this_month":
		return get_first_day(ref_today), ref_today

	# custom
	if not from_date or not to_date:
		frappe.throw(_("from_date and to_date are required for a custom period."))
	custom_from, custom_to = getdate(from_date), getdate(to_date)
	if custom_from > custom_to:
		frappe.throw(_("from_date cannot be after to_date."))
	if (custom_to - custom_from).days > MAX_CUSTOM_RANGE_DAYS:
		frappe.throw(_("Custom date range cannot exceed {0} days.").format(MAX_CUSTOM_RANGE_DAYS))
	return custom_from, custom_to


@frappe.whitelist()
def get_dashboard(
	period="today", sort_by="gross_profit", from_date=None, to_date=None, item_group="", item_search=""
):
	"""Period-dependent KPIs and best-selling items.

	``from_date``/``to_date`` are only used (and required) when ``period`` is
	"custom" -- see ``get_period_range``. ``item_group``/``item_search`` narrow
	the best-sellers table for closer item-level analysis; KPIs stay
	unfiltered (they represent the whole period, not just matching items).
	"""
	_check_owner_access()

	sort_col = _BEST_ITEMS_SORT_COLUMNS.get(sort_by)
	if not sort_col:
		frappe.throw(_("Invalid sort_by: {0}").format(sort_by))

	from_date, to_date = get_period_range(period, from_date=from_date, to_date=to_date)
	date_filter = {"from_date": from_date, "to_date": to_date}

	item_group = (item_group or "").strip()
	item_search = (item_search or "").strip()
	item_conditions = []
	item_values = {}
	if item_group:
		item_conditions.append("sii.item_group = %(item_group)s")
		item_values["item_group"] = item_group
	if item_search:
		item_conditions.append("(sii.item_code LIKE %(item_search)s OR sii.item_name LIKE %(item_search)s)")
		item_values["item_search"] = f"%{item_search}%"
	item_where = ("AND " + " AND ".join(item_conditions)) if item_conditions else ""
	best_items_limit = BEST_ITEMS_FILTERED_LIMIT if item_conditions else BEST_ITEMS_LIMIT

	kpis = frappe.db.sql(
		"""
		SELECT
			COALESCE(SUM(si.grand_total), 0)                  AS total_sales,
			COALESCE(SUM(si.paid_amount), 0)                  AS total_collected,
			COALESCE(SUM(si.grand_total - si.paid_amount), 0) AS total_credit,
			COUNT(*)                                           AS invoice_count
		FROM `tabSales Invoice` si
		WHERE si.docstatus = 1
		  AND DATE(si.posting_date) BETWEEN %(from_date)s AND %(to_date)s
		""",
		date_filter,
		as_dict=True,
	)[0]

	gross_profit = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(sii.amount - sii.qty * COALESCE(sii.incoming_rate, 0)), 0) AS gross_profit
		FROM `tabSales Invoice Item` sii
		JOIN `tabSales Invoice` si ON si.name = sii.parent
		WHERE si.docstatus = 1
		  AND DATE(si.posting_date) BETWEEN %(from_date)s AND %(to_date)s
		""",
		date_filter,
		as_dict=True,
	)[0].gross_profit

	best_items = frappe.db.sql(
		f"""
		SELECT
			sii.item_code,
			sii.item_name,
			sii.item_group,
			SUM(sii.qty)                                                        AS qty_sold,
			SUM(sii.amount)                                                     AS revenue,
			SUM(sii.amount - sii.qty * COALESCE(sii.incoming_rate, 0))         AS gross_profit
		FROM `tabSales Invoice Item` sii
		JOIN `tabSales Invoice` si ON si.name = sii.parent
		WHERE si.docstatus = 1
		  AND DATE(si.posting_date) BETWEEN %(from_date)s AND %(to_date)s
		  {item_where}
		GROUP BY sii.item_code, sii.item_name, sii.item_group
		ORDER BY {sort_col} DESC
		LIMIT %(limit)s
		""",
		{**date_filter, **item_values, "limit": best_items_limit},
		as_dict=True,
	)

	return {
		"period": period,
		"from_date": from_date,
		"to_date": to_date,
		"currency": _get_currency(),
		"item_group": item_group,
		"item_search": item_search,
		"kpis": {
			"total_sales": flt(kpis.total_sales),
			"gross_profit": flt(gross_profit),
			"invoice_count": cint(kpis.invoice_count),
			"total_collected": flt(kpis.total_collected),
			"total_credit": flt(kpis.total_credit),
		},
		"best_items": best_items,
	}


@frappe.whitelist()
def get_dashboard_static():
	"""Static (period-independent) dashboard data: trend, receivables, low stock."""
	_check_owner_access()

	return {
		"currency": _get_currency(),
		"trend": _get_trend(),
		"weekday_trend": _get_weekday_trend(),
		"receivables": _get_receivables(),
		"low_stock": _get_low_stock(),
	}


def _get_trend():
	to_date = getdate(nowdate())
	from_date = add_days(to_date, -(TREND_DAYS - 1))
	date_filter = {"from_date": from_date, "to_date": to_date}

	sales_rows = frappe.db.sql(
		"""
		SELECT DATE(si.posting_date) AS day, SUM(si.grand_total) AS total_sales
		FROM `tabSales Invoice` si
		WHERE si.docstatus = 1
		  AND DATE(si.posting_date) BETWEEN %(from_date)s AND %(to_date)s
		GROUP BY DATE(si.posting_date)
		""",
		date_filter,
		as_dict=True,
	)
	profit_rows = frappe.db.sql(
		"""
		SELECT DATE(si.posting_date) AS day,
		       SUM(sii.amount - sii.qty * COALESCE(sii.incoming_rate, 0)) AS gross_profit
		FROM `tabSales Invoice Item` sii
		JOIN `tabSales Invoice` si ON si.name = sii.parent
		WHERE si.docstatus = 1
		  AND DATE(si.posting_date) BETWEEN %(from_date)s AND %(to_date)s
		GROUP BY DATE(si.posting_date)
		""",
		date_filter,
		as_dict=True,
	)

	sales_by_day = {getdate(r.day): flt(r.total_sales) for r in sales_rows}
	profit_by_day = {getdate(r.day): flt(r.gross_profit) for r in profit_rows}

	days = []
	for i in range(TREND_DAYS):
		day = add_days(from_date, i)
		days.append(
			{
				"date": day,
				"total_sales": sales_by_day.get(day, 0.0),
				"gross_profit": profit_by_day.get(day, 0.0),
			}
		)

	return {"from_date": from_date, "to_date": to_date, "days": days}


def _get_weekday_trend():
	"""Sales/profit performance grouped by day of week over the lookback window.

	Averages are per-occurrence (total / number of times that weekday actually
	occurred in the window), so a quiet Monday doesn't get diluted by having
	fewer -- or more -- Mondays than Fridays in the window.
	MySQL's WEEKDAY() returns 0=Monday .. 6=Sunday, matching WEEKDAY_LABELS.
	"""
	to_date = getdate(nowdate())
	from_date = add_days(to_date, -(WEEKDAY_LOOKBACK_DAYS - 1))
	date_filter = {"from_date": from_date, "to_date": to_date}

	sales_rows = frappe.db.sql(
		"""
		SELECT WEEKDAY(si.posting_date)         AS wd,
		       SUM(si.grand_total)               AS total_sales,
		       COUNT(DISTINCT si.posting_date)    AS day_count
		FROM `tabSales Invoice` si
		WHERE si.docstatus = 1
		  AND DATE(si.posting_date) BETWEEN %(from_date)s AND %(to_date)s
		GROUP BY WEEKDAY(si.posting_date)
		""",
		date_filter,
		as_dict=True,
	)
	profit_rows = frappe.db.sql(
		"""
		SELECT WEEKDAY(si.posting_date) AS wd,
		       SUM(sii.amount - sii.qty * COALESCE(sii.incoming_rate, 0)) AS gross_profit
		FROM `tabSales Invoice Item` sii
		JOIN `tabSales Invoice` si ON si.name = sii.parent
		WHERE si.docstatus = 1
		  AND DATE(si.posting_date) BETWEEN %(from_date)s AND %(to_date)s
		GROUP BY WEEKDAY(si.posting_date)
		""",
		date_filter,
		as_dict=True,
	)

	sales_by_wd = {cint(r.wd): (flt(r.total_sales), cint(r.day_count)) for r in sales_rows}
	profit_by_wd = {cint(r.wd): flt(r.gross_profit) for r in profit_rows}

	days = []
	for wd, label in enumerate(WEEKDAY_LABELS):
		total_sales, day_count = sales_by_wd.get(wd, (0.0, 0))
		gross_profit = profit_by_wd.get(wd, 0.0)
		days.append(
			{
				"weekday": wd,
				"label": label,
				"total_sales": total_sales,
				"gross_profit": gross_profit,
				"day_count": day_count,
				"avg_sales": total_sales / day_count if day_count else 0.0,
				"avg_gross_profit": gross_profit / day_count if day_count else 0.0,
			}
		)

	return {"from_date": from_date, "to_date": to_date, "days": days}


def _get_receivables():
	as_of = nowdate()
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

	total_outstanding = sum(flt(r.total_outstanding) for r in rows)

	return {
		"total_outstanding": total_outstanding,
		"customer_count": len(rows),
		"top_debtors": rows[:TOP_DEBTORS_LIMIT],
	}


def _get_low_stock():
	rows = frappe.db.sql(
		"""
		SELECT
			i.name                                        AS item_code,
			i.item_name,
			ir.warehouse,
			COALESCE(b.actual_qty, 0)                      AS actual_qty,
			ir.warehouse_reorder_level                     AS reorder_level,
			ir.warehouse_reorder_qty                       AS reorder_qty
		FROM `tabItem Reorder` ir
		JOIN `tabItem` i ON i.name = ir.parent AND i.disabled = 0 AND i.is_stock_item = 1
		LEFT JOIN `tabBin` b ON b.item_code = i.name AND b.warehouse = ir.warehouse
		WHERE COALESCE(b.actual_qty, 0) <= ir.warehouse_reorder_level
		ORDER BY (COALESCE(b.actual_qty, 0) - ir.warehouse_reorder_level) ASC
		LIMIT %(limit)s
		""",
		{"limit": LOW_STOCK_LIMIT},
		as_dict=True,
	)

	count = frappe.db.sql(
		"""
		SELECT COUNT(*)
		FROM `tabItem Reorder` ir
		JOIN `tabItem` i ON i.name = ir.parent AND i.disabled = 0 AND i.is_stock_item = 1
		LEFT JOIN `tabBin` b ON b.item_code = i.name AND b.warehouse = ir.warehouse
		WHERE COALESCE(b.actual_qty, 0) <= ir.warehouse_reorder_level
		"""
	)[0][0]

	return {"count": cint(count), "items": rows}
