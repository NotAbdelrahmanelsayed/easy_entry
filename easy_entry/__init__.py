__version__ = "0.0.1"

import erpnext.stock.reorder_item as _reorder_module

from easy_entry.overrides.reorder_item import send_email_notification as _arabic_send

_reorder_module.send_email_notification = _arabic_send

# Patch Frappe's printview so window.print() fires only after all page resources
# (including external barcode images) have fully loaded. The stock script calls
# window.print() synchronously, which races against image fetches on first load.
import frappe.www.printview as _printview_module

_printview_module.trigger_print_script = """<script>
window.addEventListener('load', function () {
	var elements = document.getElementsByTagName("tr");
	var i = elements.length;
	while (i--) {
		if (elements[i].clientHeight > 300) {
			elements[i].setAttribute("style", "page-break-inside: auto;");
		}
	}
	window.print();
	setTimeout(function () { window.close(); }, 5000);
});
</script>
"""
