"""Integration tests for the Item Manager API.

Run with:
	bench --site <site> run-tests --module easy_entry.api.test_item_manager
"""

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import nowdate, nowtime

from easy_entry.api import item_manager

TEST_GROUP = "Products"
TEST_PREFIX = "_TEST-IM-"


def _make_item(code, name, buying=None, selling=None, supplier=None):
	item_code = f"{TEST_PREFIX}{code}"
	if not frappe.db.exists("Item", item_code):
		doc = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": item_code,
				"item_name": name,
				"item_group": TEST_GROUP,
				"stock_uom": "Nos",
				"is_stock_item": 1,
			}
		)
		if supplier:
			doc.append("supplier_items", {"supplier": supplier})
		doc.insert()
	for price_list, rate in (("Standard Buying", buying), ("Standard Selling", selling)):
		if rate and not frappe.db.exists(
			"Item Price", {"item_code": item_code, "price_list": price_list}
		):
			frappe.get_doc(
				{
					"doctype": "Item Price",
					"item_code": item_code,
					"price_list": price_list,
					"price_list_rate": rate,
				}
			).insert()
	return item_code


def _give_stock(item_code, qty):
	"""Post real on-hand stock via a SUBMITTED Stock Reconciliation."""
	warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
	company = frappe.db.get_value("Warehouse", warehouse, "company")
	expense = frappe.db.get_value(
		"Account",
		{"company": company, "account_name": "Temporary Opening", "is_group": 0},
		"name",
	) or frappe.db.get_value("Company", company, "stock_adjustment_account")
	sr = frappe.new_doc("Stock Reconciliation")
	sr.company = company
	sr.purpose = "Stock Reconciliation"
	sr.expense_account = expense
	sr.posting_date = nowdate()
	sr.posting_time = nowtime()
	sr.append(
		"items",
		{"item_code": item_code, "warehouse": warehouse, "qty": qty, "valuation_rate": 1},
	)
	sr.insert()
	sr.submit()
	frappe.db.commit()


def _purge_test_data(supplier):
	"""Delete every artefact this test class may have created, in link order."""
	for sr in frappe.get_all(
		"Stock Reconciliation Item",
		filters={"item_code": ["like", f"{TEST_PREFIX}%"]},
		fields=["parent"],
		distinct=True,
	):
		doc = frappe.get_doc("Stock Reconciliation", sr.parent)
		if doc.docstatus == 1:
			doc.cancel()
		frappe.delete_doc("Stock Reconciliation", sr.parent, force=True, ignore_permissions=True)
	for price in frappe.get_all(
		"Item Price", filters={"item_code": ["like", f"{TEST_PREFIX}%"]}, pluck="name"
	):
		frappe.delete_doc("Item Price", price, force=True, ignore_permissions=True)
	for item in frappe.get_all(
		"Item", filters={"item_code": ["like", f"{TEST_PREFIX}%"]}, pluck="name"
	):
		frappe.delete_doc("Item", item, force=True, ignore_permissions=True)
	if supplier and frappe.db.exists("Supplier", supplier):
		frappe.delete_doc("Supplier", supplier, force=True, ignore_permissions=True)
	frappe.db.commit()


class TestItemManager(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.supplier = "_Test IM Supplier"
		# Start from a clean slate even if a previous run leaked data.
		_purge_test_data(cls.supplier)
		frappe.get_doc(
			{
				"doctype": "Supplier",
				"supplier_name": cls.supplier,
				"supplier_group": "All Supplier Groups",
			}
		).insert()
		# item_a: supplier + both prices, zero stock
		cls.item_a = _make_item("A", "Test Apple", buying=10, selling=18, supplier=cls.supplier)
		# item_b: no supplier, buying only (missing selling), zero stock
		cls.item_b = _make_item("B", "Test Bread", buying=5)
		# item_c: both prices, positive on-hand stock
		cls.item_c = _make_item("C", "Test Cheese", buying=7, selling=12)
		# item_d: no prices at all (missing buying AND selling)
		cls.item_d = _make_item("D", "Test Dates")
		frappe.db.commit()
		_give_stock(cls.item_c, 30)

	@classmethod
	def tearDownClass(cls):
		_purge_test_data(cls.supplier)
		super().tearDownClass()

	# --- get_items ------------------------------------------------------

	def test_get_items_returns_rows_and_total(self):
		result = item_manager.get_items(limit=100)
		self.assertIn("rows", result)
		self.assertIn("total", result)
		self.assertGreaterEqual(result["total"], 2)
		codes = {r["item_code"] for r in result["rows"]}
		self.assertIn(self.item_a, codes)

	def test_get_items_search_filters(self):
		result = item_manager.get_items(search="Test Apple", limit=100)
		names = {r["item_name"] for r in result["rows"]}
		self.assertIn("Test Apple", names)
		self.assertNotIn("Test Bread", names)

	def test_get_items_includes_prices_and_supplier(self):
		row = next(
			r for r in item_manager.get_items(limit=100)["rows"] if r["item_code"] == self.item_a
		)
		self.assertEqual(row["buying_price"], 10)
		self.assertEqual(row["selling_price"], 18)
		self.assertEqual(row["supplier"], self.supplier)

	def test_get_items_limit_is_capped(self):
		# A huge limit must not exceed MAX_LIMIT (no error, just clamped).
		result = item_manager.get_items(limit=99999)
		self.assertLessEqual(len(result["rows"]), item_manager.MAX_LIMIT)

	# --- get_items filters ----------------------------------------------

	def _codes(self, **kwargs):
		return {r["item_code"] for r in item_manager.get_items(limit=200, **kwargs)["rows"]}

	def test_filter_by_supplier(self):
		result = item_manager.get_items(supplier=self.supplier, limit=200)
		codes = {r["item_code"] for r in result["rows"]}
		self.assertEqual(codes, {self.item_a})
		# total must track the filter, not the unfiltered table.
		self.assertEqual(result["total"], 1)

	def test_filter_stock_in_stock(self):
		codes = self._codes(stock_status="in_stock")
		self.assertIn(self.item_c, codes)
		self.assertNotIn(self.item_a, codes)

	def test_filter_stock_out_of_stock(self):
		codes = self._codes(stock_status="out_of_stock")
		self.assertIn(self.item_a, codes)
		self.assertNotIn(self.item_c, codes)

	def test_filter_price_missing_buying(self):
		codes = self._codes(price_status="missing_buying")
		self.assertIn(self.item_d, codes)
		self.assertNotIn(self.item_a, codes)

	def test_filter_price_missing_selling(self):
		codes = self._codes(price_status="missing_selling")
		self.assertIn(self.item_b, codes)
		self.assertIn(self.item_d, codes)
		self.assertNotIn(self.item_a, codes)

	def test_filter_price_missing_any(self):
		codes = self._codes(price_status="missing_any")
		self.assertIn(self.item_b, codes)
		self.assertIn(self.item_d, codes)
		self.assertNotIn(self.item_a, codes)
		self.assertNotIn(self.item_c, codes)

	def test_filter_price_has_both(self):
		codes = self._codes(price_status="has_both")
		self.assertIn(self.item_a, codes)
		self.assertIn(self.item_c, codes)
		self.assertNotIn(self.item_b, codes)
		self.assertNotIn(self.item_d, codes)

	def test_filters_combine(self):
		codes = self._codes(supplier=self.supplier, price_status="has_both")
		self.assertEqual(codes, {self.item_a})

	def test_unknown_filter_value_is_ignored(self):
		# A garbage filter value adds no condition -- behaves like no filter.
		self.assertGreaterEqual(item_manager.get_items(stock_status="banana")["total"], 4)

	# --- update_item ----------------------------------------------------

	def test_update_item_name(self):
		item_manager.update_item(self.item_b, {"item_name": "Renamed Bread"})
		self.assertEqual(frappe.db.get_value("Item", self.item_b, "item_name"), "Renamed Bread")

	def test_update_item_supplier(self):
		item_manager.update_item(self.item_b, {"supplier": self.supplier})
		doc = frappe.get_doc("Item", self.item_b)
		self.assertEqual(doc.supplier_items[0].supplier, self.supplier)

	def test_update_item_rejects_empty_name(self):
		with self.assertRaises(frappe.ValidationError):
			item_manager.update_item(self.item_a, {"item_name": "  "})

	def test_update_item_rejects_unknown_supplier(self):
		with self.assertRaises(frappe.ValidationError):
			item_manager.update_item(self.item_a, {"supplier": "No Such Supplier"})

	# --- update_item_price ---------------------------------------------

	def test_update_item_price_creates_row(self):
		item_manager.update_item_price(self.item_b, "Standard Selling", 25)
		rate = frappe.db.get_value(
			"Item Price",
			{"item_code": self.item_b, "price_list": "Standard Selling"},
			"price_list_rate",
		)
		self.assertEqual(rate, 25)

	def test_update_item_price_updates_existing(self):
		item_manager.update_item_price(self.item_a, "Standard Buying", 12)
		rate = frappe.db.get_value(
			"Item Price",
			{"item_code": self.item_a, "price_list": "Standard Buying"},
			"price_list_rate",
		)
		self.assertEqual(rate, 12)

	def test_update_item_price_rejects_non_positive(self):
		with self.assertRaises(frappe.ValidationError):
			item_manager.update_item_price(self.item_a, "Standard Buying", 0)

	def test_update_item_price_rejects_bad_price_list(self):
		with self.assertRaises(frappe.ValidationError):
			item_manager.update_item_price(self.item_a, "Nonexistent List", 5)

	# --- rename_item ----------------------------------------------------

	def test_rename_item(self):
		old = _make_item("RENAME", "Rename Me", buying=3)
		new = f"{TEST_PREFIX}RENAMED"
		item_manager.rename_item(old, new)
		self.assertTrue(frappe.db.exists("Item", new))
		self.assertFalse(frappe.db.exists("Item", old))

	def test_rename_item_rejects_duplicate(self):
		with self.assertRaises(frappe.ValidationError):
			item_manager.rename_item(self.item_a, self.item_b)

	# --- set_item_qty ---------------------------------------------------

	def test_set_item_qty_creates_draft(self):
		result = item_manager.set_item_qty(self.item_a, 42)
		sr = frappe.get_doc("Stock Reconciliation", result["stock_reconciliation"])
		self.assertEqual(sr.docstatus, 0)  # draft, not submitted
		self.assertEqual(sr.items[0].qty, 42)

	def test_set_item_qty_rejects_negative(self):
		with self.assertRaises(frappe.ValidationError):
			item_manager.set_item_qty(self.item_a, -1)

	# --- export ---------------------------------------------------------

	def test_export_items_xlsx(self):
		frappe.response.clear()
		item_manager.export_items_xlsx()
		self.assertEqual(frappe.response.get("type"), "binary")
		self.assertTrue(frappe.response.get("filename", "").endswith(".xlsx"))
		self.assertGreater(len(frappe.response.get("filecontent", b"")), 0)
		frappe.response.clear()
