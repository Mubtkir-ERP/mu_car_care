# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import json
import os
import frappe
from mu_car_care.setup import sync_print_formats


def execute():
	"""
	v1.1.8 Patch:
	1. Delete obsolete custom_schedule_config_section from database.
	2. Move maintenance settings fields directly into custom_schedule_visits_section above the table.
	3. Force sync all Custom Fields from fixtures/custom_field.json directly.
	4. Reload DocTypes and sync Print Format.
	5. Flush Redis and DocType caches.
	"""
	# 1. Delete obsolete sections from tabCustom Field
	try:
		frappe.db.sql(
			"""
			DELETE FROM `tabCustom Field`
			WHERE fieldname IN ('custom_schedule_config_section', 'custom_maintenance_section')
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		frappe.db.commit()
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_8 delete obsolete custom fields", message=str(e))

	# 2. Update insert_after and collapsibility on tabCustom Field directly
	try:
		frappe.db.sql(
			"""
			UPDATE `tabCustom Field`
			SET insert_after = 'custom_vehicle_make'
			WHERE fieldname = 'custom_has_maintenance_schedule'
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		frappe.db.sql(
			"""
			UPDATE `tabCustom Field`
			SET insert_after = 'items', collapsible = 1, label = 'Maintenance Schedule'
			WHERE fieldname = 'custom_schedule_visits_section'
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		frappe.db.sql(
			"""
			UPDATE `tabCustom Field`
			SET insert_after = 'custom_schedule_visits_section'
			WHERE fieldname = 'custom_maintenance_start_date'
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		frappe.db.sql(
			"""
			UPDATE `tabCustom Field`
			SET insert_after = 'custom_generate_schedule_btn'
			WHERE fieldname = 'custom_maintenance_schedule'
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		frappe.db.sql(
			"""
			UPDATE `tabCustom Field`
			SET insert_after = 'custom_maintenance_schedule', collapsible = 1, label = 'Warranty Details'
			WHERE fieldname = 'custom_warranty_section'
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		# Clear auto-generated notes from database
		frappe.db.sql(
			"""
			UPDATE `tabVehicle Maintenance Schedule Item`
			SET notes = ''
			WHERE notes LIKE 'زيارة صيانة دورية%'
			"""
		)
		frappe.db.commit()
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_8 update custom fields", message=str(e))

	# 3. Force-sync all custom fields from fixtures/custom_field.json directly
	try:
		app_path = frappe.get_app_path("mu_car_care")
		cf_json_path = os.path.join(app_path, "fixtures", "custom_field.json")
		if os.path.exists(cf_json_path):
			with open(cf_json_path, "r", encoding="utf-8") as f:
				cfields = json.load(f)
			for cf in cfields:
				dt = cf.get("dt")
				fieldname = cf.get("fieldname")
				name = f"{dt}-{fieldname}"
				if frappe.db.exists("Custom Field", name):
					doc = frappe.get_doc("Custom Field", name)
					doc.update(cf)
					doc.save(ignore_permissions=True)
				else:
					doc = frappe.new_doc("Custom Field")
					doc.update(cf)
					doc.save(ignore_permissions=True)
			frappe.db.commit()
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_8 sync fixtures error", message=str(e))

	# 4. Reload child doctypes
	try:
		frappe.reload_doc("mu_car_care", "doctype", "vehicle_maintenance_schedule_item", force=True)
		frappe.reload_doc("mu_car_care", "doctype", "vehicle_warranty_item", force=True)
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_8 reload_doc error", message=str(e))

	# 5. Synchronize Print Format
	try:
		sync_print_formats()
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_8 sync_print_formats error", message=str(e))

	# 6. Flush caches completely
	try:
		frappe.cache.delete_key("bootinfo")
		for dt in ["Sales Invoice", "Quotation", "Sales Order", "Item", "Vehicle Reception", "Print Format"]:
			frappe.clear_cache(doctype=dt)
		frappe.clear_cache()
	except Exception:
		pass
