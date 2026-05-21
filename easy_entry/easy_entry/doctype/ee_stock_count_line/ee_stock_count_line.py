# For license information, please see license.txt

from frappe.model.document import Document


class EEStockCountLine(Document):
	"""One counted item inside an EE Stock Count session.

	``difference`` (counted_qty - system_qty) is kept fresh by the parent
	``EE Stock Count`` controller's ``validate`` -- never set it directly.
	"""

	pass
