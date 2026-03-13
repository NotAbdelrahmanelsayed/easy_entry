__version__ = "0.0.1"

import erpnext.stock.reorder_item as _reorder_module
from easy_entry.overrides.reorder_item import send_email_notification as _arabic_send

_reorder_module.send_email_notification = _arabic_send
