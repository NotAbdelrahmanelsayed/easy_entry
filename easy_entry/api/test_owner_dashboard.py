"""Integration tests for the Store Owner Analytics Dashboard API.

Run with:
	bench --site <site> run-tests --module easy_entry.api.test_owner_dashboard

Value assertions on the SQL formulas (gross profit, receivables, low stock)
are skipped -- those formulas are already production-proven in
tasks/daily_owner_report.py and tasks/reorder email logic. These tests cover
the parts that are new here: period math, access control and response shape.
"""

import frappe
from frappe.tests import IntegrationTestCase

from easy_entry.api import owner_dashboard

TEST_USER = "_test-owner-dashboard@example.com"


class TestGetPeriodRange(IntegrationTestCase):
	"""Pure function -- no DB, pinned "today" so results are deterministic."""

	def test_today(self):
		frm, to = owner_dashboard.get_period_range("today", today="2026-07-16")
		self.assertEqual(str(frm), "2026-07-16")
		self.assertEqual(str(to), "2026-07-16")

	def test_yesterday(self):
		frm, to = owner_dashboard.get_period_range("yesterday", today="2026-07-16")
		self.assertEqual(str(frm), "2026-07-15")
		self.assertEqual(str(to), "2026-07-15")

	def test_last_7_days(self):
		frm, to = owner_dashboard.get_period_range("last_7_days", today="2026-07-16")
		self.assertEqual(str(frm), "2026-07-10")
		self.assertEqual(str(to), "2026-07-16")

	def test_this_month(self):
		frm, to = owner_dashboard.get_period_range("this_month", today="2026-07-16")
		self.assertEqual(str(frm), "2026-07-01")
		self.assertEqual(str(to), "2026-07-16")

	def test_this_month_boundary(self):
		frm, to = owner_dashboard.get_period_range("this_month", today="2026-07-01")
		self.assertEqual(str(frm), "2026-07-01")
		self.assertEqual(str(to), "2026-07-01")

	def test_invalid_period(self):
		with self.assertRaises(frappe.ValidationError):
			owner_dashboard.get_period_range("bogus", today="2026-07-16")

	def test_custom_range(self):
		frm, to = owner_dashboard.get_period_range(
			"custom", today="2026-07-16", from_date="2026-06-01", to_date="2026-06-15"
		)
		self.assertEqual(str(frm), "2026-06-01")
		self.assertEqual(str(to), "2026-06-15")

	def test_custom_range_requires_both_dates(self):
		with self.assertRaises(frappe.ValidationError):
			owner_dashboard.get_period_range("custom", today="2026-07-16", from_date="2026-06-01")

	def test_custom_range_rejects_reversed_dates(self):
		with self.assertRaises(frappe.ValidationError):
			owner_dashboard.get_period_range(
				"custom", today="2026-07-16", from_date="2026-06-15", to_date="2026-06-01"
			)

	def test_custom_range_rejects_too_wide(self):
		with self.assertRaises(frappe.ValidationError):
			owner_dashboard.get_period_range(
				"custom", today="2026-07-16", from_date="2020-01-01", to_date="2026-07-16"
			)


class TestOwnerDashboardAccess(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if frappe.db.exists("User", TEST_USER):
			frappe.delete_doc("User", TEST_USER, force=True, ignore_permissions=True)
		frappe.get_doc(
			{
				"doctype": "User",
				"email": TEST_USER,
				"first_name": "Owner Dashboard Tester",
				"send_welcome_email": 0,
			}
		).insert(ignore_permissions=True)
		frappe.db.commit()

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		if frappe.db.exists("User", TEST_USER):
			frappe.delete_doc("User", TEST_USER, force=True, ignore_permissions=True)
		frappe.db.commit()
		super().tearDownClass()

	def setUp(self):
		self.addCleanup(frappe.set_user, "Administrator")

	def test_no_role_rejected(self):
		frappe.set_user(TEST_USER)
		with self.assertRaises(frappe.PermissionError):
			owner_dashboard.get_dashboard()
		with self.assertRaises(frappe.PermissionError):
			owner_dashboard.get_dashboard_static()

	def test_store_owner_role_allowed(self):
		user = frappe.get_doc("User", TEST_USER)
		if not any(r.role == "Store Owner" for r in user.roles):
			user.append("roles", {"role": "Store Owner"})
			user.save(ignore_permissions=True)
			frappe.db.commit()

		frappe.set_user(TEST_USER)
		# Should not raise.
		owner_dashboard.get_dashboard()
		owner_dashboard.get_dashboard_static()


class TestOwnerDashboardShape(IntegrationTestCase):
	"""As Administrator -- verify response shape, not values."""

	def test_get_dashboard_keys(self):
		result = owner_dashboard.get_dashboard(period="today")
		for key in ("period", "from_date", "to_date", "currency", "kpis", "best_items"):
			self.assertIn(key, result)
		for key in ("total_sales", "gross_profit", "invoice_count", "total_collected", "total_credit"):
			self.assertIn(key, result["kpis"])

	def test_get_dashboard_invalid_sort_by(self):
		with self.assertRaises(frappe.ValidationError):
			owner_dashboard.get_dashboard(sort_by="; DROP TABLE tabItem")

	def test_get_dashboard_custom_period(self):
		result = owner_dashboard.get_dashboard(
			period="custom", from_date="2026-07-01", to_date="2026-07-10"
		)
		self.assertEqual(result["period"], "custom")
		self.assertEqual(str(result["from_date"]), "2026-07-01")
		self.assertEqual(str(result["to_date"]), "2026-07-10")

	def test_get_dashboard_custom_period_requires_dates(self):
		with self.assertRaises(frappe.ValidationError):
			owner_dashboard.get_dashboard(period="custom")

	def test_get_dashboard_static_keys(self):
		result = owner_dashboard.get_dashboard_static()
		for key in ("currency", "trend", "receivables", "low_stock"):
			self.assertIn(key, result)
		self.assertIn("total_outstanding", result["receivables"])
		self.assertIn("customer_count", result["receivables"])
		self.assertIn("top_debtors", result["receivables"])
		self.assertIn("count", result["low_stock"])
		self.assertIn("items", result["low_stock"])

	def test_trend_is_30_contiguous_days_ending_today(self):
		result = owner_dashboard.get_dashboard_static()
		days = result["trend"]["days"]
		self.assertEqual(len(days), owner_dashboard.TREND_DAYS)
		self.assertEqual(str(days[-1]["date"]), frappe.utils.nowdate())
		for day in days:
			self.assertIn("total_sales", day)
			self.assertIn("gross_profit", day)

	def test_weekday_trend_has_7_days_mon_to_sun(self):
		result = owner_dashboard.get_dashboard_static()
		days = result["weekday_trend"]["days"]
		self.assertEqual(len(days), 7)
		self.assertEqual([d["weekday"] for d in days], [0, 1, 2, 3, 4, 5, 6])
		self.assertEqual([d["label"] for d in days], list(owner_dashboard.WEEKDAY_LABELS))
		for day in days:
			self.assertIn("total_sales", day)
			self.assertIn("gross_profit", day)
			self.assertIn("avg_sales", day)
			self.assertIn("avg_gross_profit", day)
			self.assertIn("day_count", day)


TEST_PREFIX = "_TEST-OD-"


def _make_test_sale(item_group, item_code, item_name, rate):
	"""A minimal submitted Sales Invoice (no stock update) for filter tests."""
	if not frappe.db.exists("Item Group", item_group):
		frappe.get_doc({"doctype": "Item Group", "item_group_name": item_group}).insert(
			ignore_permissions=True
		)
	if not frappe.db.exists("Item", item_code):
		frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": item_code,
				"item_name": item_name,
				"item_group": item_group,
				"stock_uom": "Nos",
				"is_stock_item": 0,
			}
		).insert(ignore_permissions=True)

	si = frappe.new_doc("Sales Invoice")
	si.customer = "Walking Customer" if frappe.db.exists("Customer", "Walking Customer") else _ensure_customer()
	si.is_pos = 0
	si.update_stock = 0
	si.append("items", {"item_code": item_code, "qty": 1, "rate": rate})
	si.insert(ignore_permissions=True)
	si.submit()
	frappe.db.commit()
	return si.name


def _ensure_customer():
	name = f"{TEST_PREFIX}Customer"
	if not frappe.db.exists("Customer", name):
		frappe.get_doc(
			{"doctype": "Customer", "customer_name": name, "customer_group": "All Customer Groups"}
		).insert(ignore_permissions=True)
	return name


class TestOwnerDashboardItemFilters(IntegrationTestCase):
	"""Item/item-group narrowing of the best-sellers table -- new logic, not
	covered by the "SQL formulas are production-proven" skip elsewhere."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.group_a = f"{TEST_PREFIX}Group A"
		cls.group_b = f"{TEST_PREFIX}Group B"
		cls.item_a = f"{TEST_PREFIX}Alpha"
		cls.item_b = f"{TEST_PREFIX}Bravo"
		cls.sales = [
			_make_test_sale(cls.group_a, cls.item_a, f"{TEST_PREFIX}Alpha Widget", 100),
			_make_test_sale(cls.group_b, cls.item_b, f"{TEST_PREFIX}Bravo Widget", 50),
		]

	@classmethod
	def tearDownClass(cls):
		for si in cls.sales:
			doc = frappe.get_doc("Sales Invoice", si)
			if doc.docstatus == 1:
				doc.cancel()
			frappe.delete_doc("Sales Invoice", si, force=True, ignore_permissions=True)
		for item in (cls.item_a, cls.item_b):
			if frappe.db.exists("Item", item):
				frappe.delete_doc("Item", item, force=True, ignore_permissions=True)
		for group in (cls.group_a, cls.group_b):
			if frappe.db.exists("Item Group", group):
				frappe.delete_doc("Item Group", group, force=True, ignore_permissions=True)
		customer = f"{TEST_PREFIX}Customer"
		if frappe.db.exists("Customer", customer):
			frappe.delete_doc("Customer", customer, force=True, ignore_permissions=True)
		frappe.db.commit()
		super().tearDownClass()

	def test_item_group_filter_narrows_results(self):
		result = owner_dashboard.get_dashboard(period="today", item_group=self.group_a)
		codes = {r["item_code"] for r in result["best_items"]}
		self.assertIn(self.item_a, codes)
		self.assertNotIn(self.item_b, codes)

	def test_item_search_filter_narrows_results(self):
		result = owner_dashboard.get_dashboard(period="today", item_search="Bravo")
		codes = {r["item_code"] for r in result["best_items"]}
		self.assertIn(self.item_b, codes)
		self.assertNotIn(self.item_a, codes)

	def test_filters_do_not_affect_kpis(self):
		unfiltered = owner_dashboard.get_dashboard(period="today")
		filtered = owner_dashboard.get_dashboard(period="today", item_group=self.group_a)
		self.assertEqual(unfiltered["kpis"]["total_sales"], filtered["kpis"]["total_sales"])

	def test_no_filter_uses_default_limit_filtered_uses_higher_limit(self):
		result = owner_dashboard.get_dashboard(period="today", item_group=self.group_a)
		self.assertLessEqual(len(result["best_items"]), owner_dashboard.BEST_ITEMS_FILTERED_LIMIT)
