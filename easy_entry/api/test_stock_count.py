"""Integration tests for the Stock Count API.

Run with:
	bench --site <site> run-tests --module easy_entry.api.test_stock_count
"""

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import nowdate, nowtime

from easy_entry.api import _stock, stock_count

TEST_GROUP = "Products"
TEST_PREFIX = "_TEST-SC-"
TEST_BARCODE = "_TEST-SC-BARCODE-1"


def _warehouse():
	return frappe.db.get_single_value("Stock Settings", "default_warehouse")


def _make_item(code, name, barcode=None):
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
		if barcode:
			doc.append("barcodes", {"barcode": barcode})
		doc.insert()
	return item_code


def _give_stock(item_code, qty):
	"""Post real on-hand stock via a SUBMITTED Stock Reconciliation."""
	warehouse = _warehouse()
	company = frappe.db.get_value("Warehouse", warehouse, "company")
	sr = frappe.new_doc("Stock Reconciliation")
	sr.company = company
	sr.purpose = "Stock Reconciliation"
	sr.expense_account = _stock.resolve_difference_account(company)
	sr.posting_date = nowdate()
	sr.posting_time = nowtime()
	sr.append(
		"items",
		{"item_code": item_code, "warehouse": warehouse, "qty": qty, "valuation_rate": 1},
	)
	sr.insert()
	sr.submit()
	frappe.db.commit()


def _purge():
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
	for sc in frappe.get_all(
		"EE Stock Count Line",
		filters={"item_code": ["like", f"{TEST_PREFIX}%"]},
		fields=["parent"],
		distinct=True,
	):
		frappe.delete_doc("EE Stock Count", sc.parent, force=True, ignore_permissions=True)
	for item in frappe.get_all(
		"Item", filters={"item_code": ["like", f"{TEST_PREFIX}%"]}, pluck="name"
	):
		frappe.delete_doc("Item", item, force=True, ignore_permissions=True)
	frappe.db.commit()


class TestStockCount(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		_purge()
		cls.warehouse = _warehouse()
		# item_a: has a barcode, zero stock
		cls.item_a = _make_item("A", "SC Apple", barcode=TEST_BARCODE)
		# item_b: no barcode, zero stock
		cls.item_b = _make_item("B", "SC Bread")
		# item_c: no barcode, 30 on hand
		cls.item_c = _make_item("C", "SC Cheese")
		frappe.db.commit()
		_give_stock(cls.item_c, 30)
		# Empty In Progress sessions started directly (no test items) are
		# tracked so tearDown can clean them too.
		cls.extra_sessions = []

	@classmethod
	def tearDownClass(cls):
		for name in cls.extra_sessions:
			if frappe.db.exists("EE Stock Count", name):
				frappe.delete_doc("EE Stock Count", name, force=True, ignore_permissions=True)
		_purge()
		super().tearDownClass()

	def _start(self):
		name = stock_count.start_session(self.warehouse)["session"]
		self.extra_sessions.append(name)
		return name

	# --- resolve_barcode ------------------------------------------------

	def test_resolve_barcode_by_barcode(self):
		result = stock_count.resolve_barcode(TEST_BARCODE, self.warehouse)
		self.assertEqual(result["item_code"], self.item_a)
		self.assertEqual(result["item_name"], "SC Apple")

	def test_resolve_barcode_falls_back_to_item_code(self):
		result = stock_count.resolve_barcode(self.item_b, self.warehouse)
		self.assertEqual(result["item_code"], self.item_b)

	def test_resolve_barcode_reports_system_qty(self):
		result = stock_count.resolve_barcode(self.item_c, self.warehouse)
		self.assertEqual(result["system_qty"], 30)

	def test_resolve_barcode_unknown_raises(self):
		with self.assertRaises(frappe.ValidationError):
			stock_count.resolve_barcode("_TEST-SC-NO-SUCH-CODE", self.warehouse)

	def test_resolve_barcode_blank_raises(self):
		with self.assertRaises(frappe.ValidationError):
			stock_count.resolve_barcode("  ", self.warehouse)

	# --- search_items ---------------------------------------------------

	def test_search_items_by_partial_name(self):
		rows = stock_count.search_items("Appl", self.warehouse)
		codes = {r["item_code"] for r in rows}
		self.assertIn(self.item_a, codes)

	def test_search_items_by_partial_barcode(self):
		rows = stock_count.search_items("SC-BARCODE", self.warehouse)
		codes = {r["item_code"] for r in rows}
		self.assertIn(self.item_a, codes)

	def test_search_items_reports_system_qty(self):
		rows = stock_count.search_items("SC Cheese", self.warehouse)
		match = next(r for r in rows if r["item_code"] == self.item_c)
		self.assertEqual(match["system_qty"], 30)

	def test_search_items_empty_query_returns_empty(self):
		self.assertEqual(stock_count.search_items("  ", self.warehouse), [])

	def test_search_items_excludes_disabled(self):
		frappe.db.set_value("Item", self.item_b, "disabled", 1)
		try:
			rows = stock_count.search_items("SC Bread", self.warehouse)
			codes = {r["item_code"] for r in rows}
			self.assertNotIn(self.item_b, codes)
		finally:
			frappe.db.set_value("Item", self.item_b, "disabled", 0)

	# --- session lifecycle ----------------------------------------------

	def test_start_session_creates_in_progress(self):
		name = self._start()
		doc = frappe.get_doc("EE Stock Count", name)
		self.assertEqual(doc.status, "In Progress")
		self.assertEqual(doc.warehouse, self.warehouse)

	def test_list_open_sessions_includes_new_session(self):
		name = self._start()
		names = {s["name"] for s in stock_count.list_open_sessions()}
		self.assertIn(name, names)

	def test_list_open_sessions_reports_line_count(self):
		name = self._start()
		stock_count.upsert_count_line(name, self.item_a, 5)
		session = next(s for s in stock_count.list_open_sessions() if s["name"] == name)
		self.assertEqual(session["line_count"], 1)

	# --- upsert / remove lines ------------------------------------------

	def test_upsert_adds_line_with_difference(self):
		name = self._start()
		line = stock_count.upsert_count_line(name, self.item_a, 10)
		self.assertEqual(line["counted_qty"], 10)
		self.assertEqual(line["system_qty"], 0)
		self.assertEqual(line["difference"], 10)

	def test_upsert_negative_difference(self):
		name = self._start()
		line = stock_count.upsert_count_line(name, self.item_c, 25)
		self.assertEqual(line["system_qty"], 30)
		self.assertEqual(line["difference"], -5)

	def test_upsert_overwrites_existing_line(self):
		name = self._start()
		stock_count.upsert_count_line(name, self.item_a, 10)
		stock_count.upsert_count_line(name, self.item_a, 7)
		doc = frappe.get_doc("EE Stock Count", name)
		self.assertEqual(len(doc.count_lines), 1)
		self.assertEqual(doc.count_lines[0].counted_qty, 7)

	def test_upsert_unknown_item_raises(self):
		name = self._start()
		with self.assertRaises(frappe.ValidationError):
			stock_count.upsert_count_line(name, "_TEST-SC-GHOST", 1)

	def test_remove_count_line(self):
		name = self._start()
		stock_count.upsert_count_line(name, self.item_a, 10)
		stock_count.upsert_count_line(name, self.item_b, 3)
		result = stock_count.remove_count_line(name, self.item_a)
		self.assertEqual(result["line_count"], 1)
		doc = frappe.get_doc("EE Stock Count", name)
		self.assertEqual(doc.count_lines[0].item_code, self.item_b)

	# --- get_session ----------------------------------------------------

	def test_get_session_returns_lines_newest_first(self):
		name = self._start()
		stock_count.upsert_count_line(name, self.item_a, 4)
		stock_count.upsert_count_line(name, self.item_b, 9)
		session = stock_count.get_session(name)
		self.assertEqual(session["lines"][0]["item_code"], self.item_b)
		self.assertEqual(session["lines"][1]["item_code"], self.item_a)

	# --- finish_session -------------------------------------------------

	def test_finish_builds_draft_reconciliation(self):
		name = self._start()
		stock_count.upsert_count_line(name, self.item_a, 12)
		result = stock_count.finish_session(name)
		self.assertIsNotNone(result["stock_reconciliation"])
		sr = frappe.get_doc("Stock Reconciliation", result["stock_reconciliation"])
		self.assertEqual(sr.docstatus, 0)  # draft, not submitted
		self.assertEqual(sr.items[0].item_code, self.item_a)
		self.assertEqual(sr.items[0].qty, 12)
		self.assertEqual(frappe.get_doc("EE Stock Count", name).status, "Finished")

	def test_finish_with_no_difference_creates_no_reconciliation(self):
		# item_c has 30 on hand; counting exactly 30 needs no correction.
		name = self._start()
		stock_count.upsert_count_line(name, self.item_c, 30)
		result = stock_count.finish_session(name)
		self.assertIsNone(result["stock_reconciliation"])
		self.assertEqual(frappe.get_doc("EE Stock Count", name).status, "Finished")

	def test_finish_empty_session_raises(self):
		name = self._start()
		with self.assertRaises(frappe.ValidationError):
			stock_count.finish_session(name)

	def test_finish_twice_raises(self):
		name = self._start()
		stock_count.upsert_count_line(name, self.item_a, 5)
		stock_count.finish_session(name)
		with self.assertRaises(frappe.ValidationError):
			stock_count.finish_session(name)

	def test_upsert_on_finished_session_raises(self):
		name = self._start()
		stock_count.upsert_count_line(name, self.item_a, 5)
		stock_count.finish_session(name)
		with self.assertRaises(frappe.ValidationError):
			stock_count.upsert_count_line(name, self.item_b, 2)
