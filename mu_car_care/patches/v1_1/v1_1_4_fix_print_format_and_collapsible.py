# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import json
import os
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from mu_car_care.setup import sync_print_formats


def execute():
	"""
	v1.1.4 Patch:
	1. Reload DocTypes.
	2. Clean up obsolete sections and ensure collapsible = 1 on schedule & warranty sections.
	3. Ensure custom_has_maintenance_schedule is under vehicle information.
	4. Sync Car Care Tax Invoice Print Format with pdf_generator: wkhtmltopdf and exact layout.
	5. Clear all caches.
	"""
	try:
		frappe.reload_doc("mu_car_care", "doctype", "vehicle_maintenance_schedule_item")
		frappe.reload_doc("mu_car_care", "doctype", "vehicle_warranty_item")
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_4 reload_doc error", message=str(e))

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
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_4 update fields error", message=str(e))

	try:
		app_path = frappe.get_app_path("mu_car_care")
		cf_path = os.path.join(app_path, "fixtures", "custom_field.json")
		if os.path.exists(cf_path):
			with open(cf_path, "r", encoding="utf-8") as f:
				cf_data = json.load(f)
			fields_by_dt = {}
			for item in cf_data:
				dt = item.get("dt")
				fields_by_dt.setdefault(dt, []).append(item)
			create_custom_fields(fields_by_dt, update=True)
			frappe.db.commit()
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_4 sync custom fields error", message=str(e))

	try:
		sync_print_formats()
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_4 sync print format error", message=str(e))

	try:
		frappe.clear_cache()
	except Exception:
		pass
