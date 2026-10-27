# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import json
import os
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	1. Ensure Vehicle Warranty Item DocType is reloaded and table created.
	2. Install / Sync Car Care Tax Invoice Print Format directly in database.
	3. Clean up obsolete Tab Break and conflicting property setters.
	4. Rebuild all custom fields directly in the Details Tab.
	5. Clear caches across Desk and transactions.
	"""
	# 1. Reload DocTypes
	try:
		frappe.reload_doc("mu_car_care", "doctype", "vehicle_maintenance_schedule_item")
		frappe.reload_doc("mu_car_care", "doctype", "vehicle_warranty_item")
		frappe.reload_doc("mu_car_care", "doctype", "vehicle_reception")
	except Exception as e:
		frappe.log_error(title="mu_car_care reload_doc error", message=str(e))

	# 2. Sync Car Care Tax Invoice Print Format directly into tabPrint Format
	try:
		app_path = frappe.get_app_path("mu_car_care")
		pf_dir = os.path.join(app_path, "mu_car_care", "print_format", "car_care_tax_invoice")
		json_file = os.path.join(pf_dir, "car_care_tax_invoice.json")
		html_file = os.path.join(pf_dir, "car_care_tax_invoice.html")

		if os.path.exists(json_file) and os.path.exists(html_file):
			with open(html_file, "r", encoding="utf-8") as f:
				pf_html = f.read()

			pf_name = "Car Care Tax Invoice"
			if frappe.db.exists("Print Format", pf_name):
				pf_doc = frappe.get_doc("Print Format", pf_name)
			else:
				pf_doc = frappe.new_doc("Print Format")
				pf_doc.name = pf_name

			pf_doc.doc_type = "Sales Invoice"
			pf_doc.module = "Mu Car Care"
			pf_doc.custom_format = 1
			pf_doc.print_format_type = "Jinja"
			pf_doc.html = pf_html
			pf_doc.standard = "No"  # Ensures it is immediately selectable in desk without dev mode restrictions
			pf_doc.disabled = 0
			pf_doc.default_print_language = "ar"
			pf_doc.font_size = 13
			pf_doc.margin_top = 8.0
			pf_doc.margin_bottom = 8.0
			pf_doc.margin_left = 8.0
			pf_doc.margin_right = 8.0
			pf_doc.save(ignore_permissions=True)
			frappe.db.commit()
	except Exception as e:
		frappe.log_error(title="mu_car_care sync print format error", message=str(e))

	# 3. Clean up conflicting property setters and old tab break
	try:
		frappe.db.sql(
			"""
			DELETE FROM `tabProperty Setter`
			WHERE doc_type IN ('Sales Invoice', 'Quotation', 'Sales Order')
			AND field_name IN ('tc_name', 'terms', 'terms_section_break')
			"""
		)
		frappe.db.sql(
			"""
			DELETE FROM `tabCustom Field`
			WHERE fieldname IN ('custom_maintenance_schedule_tab', 'custom_terms_section')
			"""
		)
		frappe.db.commit()
	except Exception:
		pass

	# 4. Import / Update all custom fields in the Details tab from fixtures/custom_field.json
	try:
		app_path = frappe.get_app_path("mu_car_care")
		cf_file = os.path.join(app_path, "fixtures", "custom_field.json")
		if os.path.exists(cf_file):
			with open(cf_file, "r", encoding="utf-8") as f:
				custom_fields = json.load(f)

			grouped = {}
			for cf in custom_fields:
				dt = cf.get("dt")
				if dt not in grouped:
					grouped[dt] = []
				grouped[dt].append(cf)

			for dt, fields_list in grouped.items():
				create_custom_fields({dt: fields_list}, update=True)

			frappe.db.commit()
	except Exception as e:
		frappe.log_error(title="mu_car_care custom fields install error", message=str(e))

	# 5. Clear Caches
	for dt in ["Sales Invoice", "Quotation", "Sales Order", "Print Format"]:
		frappe.clear_cache(doctype=dt)
	frappe.cache.delete_key("bootinfo")
	frappe.clear_cache()
