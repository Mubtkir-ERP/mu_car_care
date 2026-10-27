# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import os
import frappe


def after_migrate():
	"""
	Mubtkir ERP Master Guidelines (Rule 5):
	Auto-sync workspaces and clear Desk cache on every bench migrate.
	Ensures Car Care Tax Invoice Print Format and collapsible custom fields are always active.
	"""
	# 1. Clean up obsolete sections and ensure collapsible = 1
	try:
		frappe.db.sql(
			"""
			DELETE FROM `tabCustom Field`
			WHERE fieldname = 'custom_maintenance_section'
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		frappe.db.sql(
			"""
			UPDATE `tabCustom Field`
			SET insert_after = 'custom_chassis_no'
			WHERE fieldname = 'custom_has_maintenance_schedule'
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		frappe.db.sql(
			"""
			UPDATE `tabCustom Field`
			SET collapsible = 1
			WHERE fieldname IN ('custom_schedule_config_section', 'custom_schedule_visits_section', 'custom_warranty_section')
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		frappe.db.commit()
	except Exception:
		pass

	# 2. Sync Print Formats
	try:
		sync_print_formats()
	except Exception:
		pass

	# 3. Clear Caches
	try:
		frappe.cache.delete_key("bootinfo")
		for dt in ["Sales Invoice", "Quotation", "Sales Order", "Vehicle Reception", "Print Format"]:
			frappe.clear_cache(doctype=dt)
		frappe.clear_cache()
	except Exception:
		pass


def sync_print_formats():
	try:
		app_path = frappe.get_app_path("mu_car_care")
		html_file = os.path.join(
			app_path, "mu_car_care", "print_format", "car_care_tax_invoice", "car_care_tax_invoice.html"
		)
		if os.path.exists(html_file):
			with open(html_file, "r", encoding="utf-8") as f:
				html_content = f.read()

			pf_name = "Car Care Tax Invoice"
			if frappe.db.exists("Print Format", pf_name):
				pf = frappe.get_doc("Print Format", pf_name)
			else:
				pf = frappe.new_doc("Print Format")
				pf.name = pf_name

			pf.doc_type = "Sales Invoice"
			pf.module = "Mu Car Care"
			pf.custom_format = 1
			pf.print_format_type = "Jinja"
			pf.pdf_generator = "wkhtmltopdf"
			pf.html = html_content
			pf.standard = "No"
			pf.disabled = 0
			pf.default_print_language = "ar"
			pf.font_size = 13
			pf.margin_top = 8.0
			pf.margin_bottom = 8.0
			pf.margin_left = 8.0
			pf.margin_right = 8.0
			pf.save(ignore_permissions=True)
			frappe.db.commit()
	except Exception:
		pass
