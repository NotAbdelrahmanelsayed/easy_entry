# bench console
import frappe
from frappe.utils import cstr

DRY_RUN = False  # ← set to False to apply
MAX_LEN = 140


def normalize_name(text: str) -> str:
    """Basic cleanup for docname safety: trim, collapse spaces, replace slashes."""
    t = cstr(text or "").strip()
    t = " ".join(t.split())  # collapse multiple spaces
    t = t.replace("/", "-")  # avoid path-like chars in name
    return t[:MAX_LEN]  # enforce Frappe docname limit


def unique_target(base: str) -> str:
    """Ensure the target name is unique; append -2, -3, ... if needed."""
    base = base[:MAX_LEN]
    if not frappe.db.exists("Item", base):
        return base
    for i in range(2, 1000):
        suffix = f"-{i}"
        room = MAX_LEN - len(suffix)
        candidate = (base[:room]).rstrip() + suffix
        if not frappe.db.exists("Item", candidate):
            return candidate
    raise Exception(f"Could not make a unique name for: {base}")


def plan_changes():
    rows = frappe.get_all("Item", fields=["name", "item_code", "item_name"])
    actions = []
    skipped_empty = 0
    skipped_same = 0

    for r in rows:
        current_name = cstr(r.name or "")
        code = cstr(r.item_code or "")
        arabic_name = cstr(r.item_name or "")

        # must have a non-empty item_name to convert
        if not arabic_name.strip():
            skipped_empty += 1
            continue

        target_base = normalize_name(arabic_name)

        # if already equal (code already Arabic), skip
        if current_name == target_base:
            skipped_same += 1
            continue

        # find unique target
        target = unique_target(target_base)

        actions.append(
            {
                "old": current_name,
                "new": target,
                "new_item_code": target,  # we’ll set item_code to match
                "item_name": arabic_name,
            }
        )

    return actions, skipped_empty, skipped_same


def apply(actions):
    renamed = 0
    for a in actions:
        # rename primary key
        frappe.rename_doc("Item", a["old"], a["new"], merge=False, force=False)

        # set item_code = new Arabic name as well
        item = frappe.get_doc("Item", a["new"])
        item.item_code = a["new_item_code"]
        item.save(ignore_permissions=True)

        renamed += 1
        if renamed % 50 == 0:
            frappe.db.commit()
            print(f"Committed {renamed} items...")
    frappe.db.commit()
    print(f"Done. Renamed/updated {renamed} items.")


def run():
    actions, skipped_empty, skipped_same = plan_changes()

    print(f"Planned renames: {len(actions)}")
    print(f"Skipped (empty item_name): {skipped_empty}")
    print(f"Skipped (already Arabic code == name): {skipped_same}")

    # preview a few
    for i, a in enumerate(actions[:10], 1):
        print(
            f"{i:02d}. '{a['old']}' → '{a['new']}'  (item_code → '{a['new_item_code']}')  [item_name='{a['item_name']}']"
        )

    if DRY_RUN:
        print("\nDRY_RUN=True → No changes applied.")
        return

    apply(actions)


run()
