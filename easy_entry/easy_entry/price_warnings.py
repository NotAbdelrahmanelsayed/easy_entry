import frappe


def warn_missing_prices(doc, method=None):
    missing = []

    for row in doc.items:
        item_code = row.get("item_code")
        if not item_code:
            continue

        has_buying = frappe.db.exists(
            "Item Price", {"item_code": item_code, "price_list": "Standard Buying"}
        )
        has_selling = frappe.db.exists(
            "Item Price", {"item_code": item_code, "price_list": "Standard Selling"}
        )

        if not has_buying or not has_selling:
            if not has_buying and not has_selling:
                status = "No buying price & no selling price"
            elif not has_buying:
                status = "No buying price"
            else:
                status = "No selling price"
            missing.append((item_code, status))

    if not missing:
        return

    rows_html = "".join(
        f"<tr><td>{item}</td><td>{status}</td></tr>"
        for item, status in missing
    )
    message = f"""
        <table class="table table-bordered table-sm" style="margin-top:8px">
          <thead><tr><th>Item</th><th>Missing</th></tr></thead>
          <tbody>{rows_html}</tbody>
        </table>
    """
    frappe.msgprint(
        msg=message,
        title="Missing Item Prices",
        indicator="orange",
        is_minimizable=True,
    )
