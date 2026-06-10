import math

import frappe
from frappe.utils import add_days, flt, today

LOOKBACK_DAYS = 90
DEFAULT_LEAD_TIME = 7
SAFETY_STOCK_FACTOR = 2

logger = frappe.logger("reorder_levels")


@frappe.whitelist()
def set_missing_reorder_levels():
	"""
	Called from Stock Settings form button.
	Finds all active stock items with no Item Reorder entries,
	calculates reorder_level and reorder_qty from 90-day consumption,
	and saves them to the Item.
	Returns a summary dict for the client.
	"""
	frappe.only_for("System Manager")

	from_date = add_days(today(), -LOOKBACK_DAYS)
	to_date = today()

	items = _get_items_without_reorder()
	if not items:
		return {
			"processed": 0,
			"warehouses_set": 0,
			"skipped_no_movement": 0,
			"skipped_error": 0,
			"errors": [],
		}

	logger.info(f"Starting reorder calculation — {len(items)} candidate items")

	consumption_map = _get_consumption_by_warehouse([r.item_code for r in items], from_date, to_date)
	item_meta = {r.item_code: r for r in items}
	stats = {"processed": 0, "skipped_no_movement": 0, "skipped_error": 0, "warehouses_set": 0, "errors": []}

	for item_code, wh_data in consumption_map.items():
		meta = item_meta.get(item_code)
		if not meta:
			continue

		lead_time = int(meta.lead_time_days) if meta.lead_time_days else DEFAULT_LEAD_TIME
		safety_stock = flt(meta.safety_stock)
		rows_to_add = []

		for warehouse, total_outgoing in wh_data.items():
			avg_daily = flt(total_outgoing) / LOOKBACK_DAYS
			if avg_daily <= 0:
				continue
			effective_safety = safety_stock if safety_stock else avg_daily * SAFETY_STOCK_FACTOR
			level = math.ceil((avg_daily * lead_time) + effective_safety)
			qty = max(math.ceil(avg_daily * lead_time), 1)
			rows_to_add.append(
				{
					"warehouse": warehouse,
					"warehouse_reorder_level": level,
					"warehouse_reorder_qty": qty,
					"material_request_type": _resolve_mr_type(meta.default_material_request_type),
				}
			)
			logger.info(f"  {item_code} | {warehouse} | level={level} qty={qty}")

		if not rows_to_add:
			stats["skipped_no_movement"] += 1
			continue

		try:
			_insert_reorder_rows(item_code, rows_to_add)
			frappe.db.commit()
			stats["processed"] += 1
			stats["warehouses_set"] += len(rows_to_add)
		except Exception as e:
			frappe.db.rollback()
			stats["skipped_error"] += 1
			stats["errors"].append({"item": item_code, "error": str(e)})

	logger.info(
		f"Done — processed={stats['processed']} wh_rows={stats['warehouses_set']} "
		f"skipped={stats['skipped_no_movement']} errors={stats['skipped_error']}"
	)
	return stats


@frappe.whitelist()
def update_all_reorder_levels():
	"""
	Called from Stock Settings form button.
	Recalculates reorder_level and reorder_qty for ALL active stock items,
	replacing any existing Item Reorder rows with freshly calculated values.
	Returns a summary dict for the client.
	"""
	frappe.only_for("System Manager")

	from_date = add_days(today(), -LOOKBACK_DAYS)
	to_date = today()

	items = _get_all_items()
	if not items:
		return {
			"processed": 0,
			"warehouses_set": 0,
			"skipped_no_movement": 0,
			"skipped_error": 0,
			"errors": [],
		}

	logger.info(f"Starting full reorder update — {len(items)} candidate items")

	consumption_map = _get_consumption_by_warehouse([r.item_code for r in items], from_date, to_date)
	item_meta = {r.item_code: r for r in items}
	stats = {"processed": 0, "skipped_no_movement": 0, "skipped_error": 0, "warehouses_set": 0, "errors": []}

	for item_code, wh_data in consumption_map.items():
		meta = item_meta.get(item_code)
		if not meta:
			continue

		lead_time = int(meta.lead_time_days) if meta.lead_time_days else DEFAULT_LEAD_TIME
		safety_stock = flt(meta.safety_stock)
		rows_to_add = []

		for warehouse, total_outgoing in wh_data.items():
			avg_daily = flt(total_outgoing) / LOOKBACK_DAYS
			if avg_daily <= 0:
				continue
			effective_safety = safety_stock if safety_stock else avg_daily * SAFETY_STOCK_FACTOR
			level = math.ceil((avg_daily * lead_time) + effective_safety)
			qty = max(math.ceil(avg_daily * lead_time), 1)
			rows_to_add.append(
				{
					"warehouse": warehouse,
					"warehouse_reorder_level": level,
					"warehouse_reorder_qty": qty,
					"material_request_type": _resolve_mr_type(meta.default_material_request_type),
				}
			)
			logger.info(f"  {item_code} | {warehouse} | level={level} qty={qty}")

		if not rows_to_add:
			stats["skipped_no_movement"] += 1
			continue

		try:
			doc = frappe.get_doc("Item", item_code)
			doc.reorder_levels = []
			for row in rows_to_add:
				doc.append("reorder_levels", row)
			doc.flags.ignore_permissions = True
			doc.flags.ignore_mandatory = True
			doc.save()
			frappe.db.commit()
			stats["processed"] += 1
			stats["warehouses_set"] += len(rows_to_add)
		except Exception as e:
			frappe.db.rollback()
			stats["skipped_error"] += 1
			stats["errors"].append({"item": item_code, "error": str(e)})

	logger.info(
		f"Done — processed={stats['processed']} wh_rows={stats['warehouses_set']} "
		f"skipped={stats['skipped_no_movement']} errors={stats['skipped_error']}"
	)
	return stats


def _get_all_items():
	return frappe.db.sql(
		"""
        SELECT
            i.name                          AS item_code,
            i.lead_time_days,
            i.safety_stock,
            i.default_material_request_type
        FROM `tabItem` i
        WHERE i.disabled       = 0
          AND i.is_stock_item  = 1
          AND i.has_variants   = 0
          AND (i.end_of_life IS NULL
               OR i.end_of_life = '0000-00-00'
               OR i.end_of_life > %(today)s)
        ORDER BY i.name
    """,
		{"today": today()},
		as_dict=True,
	)


def _get_items_without_reorder():
	return frappe.db.sql(
		"""
        SELECT
            i.name                          AS item_code,
            i.lead_time_days,
            i.safety_stock,
            i.default_material_request_type
        FROM `tabItem` i
        WHERE i.disabled       = 0
          AND i.is_stock_item  = 1
          AND i.has_variants   = 0
          AND (i.end_of_life IS NULL
               OR i.end_of_life = '0000-00-00'
               OR i.end_of_life > %(today)s)
          AND NOT EXISTS (
              SELECT 1 FROM `tabItem Reorder` ir WHERE ir.parent = i.name
          )
        ORDER BY i.name
    """,
		{"today": today()},
		as_dict=True,
	)


def _get_consumption_by_warehouse(item_codes, from_date, to_date):
	if not item_codes:
		return {}
	placeholders = ", ".join(["%s"] * len(item_codes))
	rows = frappe.db.sql(
		f"""
        SELECT sle.item_code,
               sle.warehouse,
               ABS(SUM(sle.actual_qty)) AS total_out
        FROM `tabStock Ledger Entry` sle
        INNER JOIN `tabBin` b
            ON b.item_code = sle.item_code
           AND b.warehouse = sle.warehouse
        WHERE sle.item_code   IN ({placeholders})
          AND sle.actual_qty  < 0
          AND sle.is_cancelled = 0
          AND sle.posting_date BETWEEN %s AND %s
        GROUP BY sle.item_code, sle.warehouse
        HAVING ABS(SUM(sle.actual_qty)) > 0
    """,
		[*item_codes, from_date, to_date],
		as_dict=True,
	)

	result = {}
	for row in rows:
		result.setdefault(row.item_code, {})[row.warehouse] = flt(row.total_out)
	return result


def _resolve_mr_type(t):
	return {
		"Purchase": "Purchase",
		"Material Transfer": "Transfer",
		"Material Issue": "Material Issue",
		"Manufacture": "Manufacture",
	}.get(t, "Purchase")
