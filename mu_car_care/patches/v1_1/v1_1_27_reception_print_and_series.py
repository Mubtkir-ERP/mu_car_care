# -*- coding: utf-8 -*-
"""Install the approved reception layout and normalize future receipt numbers."""
import re
import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

SERIES = "REC-.YY.-.MM.-.#####"


def receipt_sequence(name):
    """Read counters from both clean and previously malformed receipt IDs."""
    match = re.fullmatch(r"REC-(\d{2})-(\d{2})-#*(\d+)", name or "")
    if not match:
        return None
    return f"REC-{match[1]}-{match[2]}-", int(match[3])


def execute():
    frappe.reload_doc("mu_car_care", "doctype", "vehicle_reception", force=True)
    # Override site-level naming customizations that could retain literal hashes.
    make_property_setter("Vehicle Reception", "naming_series", "options", SERIES, "Text")
    make_property_setter("Vehicle Reception", "naming_series", "default", SERIES, "Text")
    make_property_setter("Vehicle Reception", None, "autoname", "naming_series:", "Data")
    # Respect existing monthly counters and existing receipt suffixes. Never reset them.
    maximums = {}
    for receipt_name in frappe.get_all("Vehicle Reception", pluck="name"):
        parsed = receipt_sequence(receipt_name)
        if parsed:
            prefix, number = parsed
            maximums[prefix] = max(maximums.get(prefix, 0), number)
    for prefix, number in maximums.items():
        frappe.db.sql(
            """INSERT INTO `tabSeries` (`name`, `current`) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE `current` = GREATEST(`current`, VALUES(`current`))""",
            (prefix, number),
        )
    from mu_car_care.setup import sync_print_formats
    sync_print_formats()
    frappe.clear_cache(doctype="Vehicle Reception")
    frappe.clear_cache(doctype="Print Format")
