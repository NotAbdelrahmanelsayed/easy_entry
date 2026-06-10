from easy_entry.utils.supplier_code import backfill_all_supplier_codes


def execute():
    # Replace the old 6-char alphanumeric codes with the new 3-letter scheme
    backfill_all_supplier_codes(force=True)
