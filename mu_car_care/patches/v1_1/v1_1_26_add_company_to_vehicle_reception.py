"""Backfill company on old Vehicle Reception rows (without replacing existing values)."""

import frappe
from erpnext import get_default_company


def execute():
    if "company" not in frappe.db.get_table_columns("Vehicle Reception"):
        return
    fallback = get_default_company()
    rows = frappe.db.sql(
        """SELECT name, sales_invoice, sales_order, quotation
           FROM `tabVehicle Reception`
           WHERE company IS NULL OR company = ''""",
        as_dict=True,
    )
    for row in rows:
        company = None
        for doctype, field in (
            ("Sales Invoice", "sales_invoice"),
            ("Sales Order", "sales_order"),
            ("Quotation", "quotation"),
        ):
            if row.get(field):
                company = frappe.db.get_value(doctype, row.get(field), "company")
            if company:
                break
        if not company:
            company = fallback
        if company:
            frappe.db.set_value("Vehicle Reception", row.name, "company", company, update_modified=False)
