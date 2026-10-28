# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	v1.1.10 Patch:
	1. Delete legacy car fields and section (custom_section_break_khlav, custom_car_type, custom_car_plate, custom_car_model, custom_car_color) from tabCustom Field.
	2. Migrate legacy car data into standard vehicle fields.
	3. Set allow_on_submit = 0 for maintenance settings and warranty details.
	4. Reload Vehicle Warranty Item DocType.
	5. Flush cache.
	"""
	# 1. Delete legacy custom fields and old section
	try:
		frappe.db.sql(
			"""
			DELETE FROM `tabCustom Field`
			WHERE fieldname IN (
				'custom_section_break_khlav',
				'custom_car_type',
				'custom_car_plate',
				'custom_car_model',
				'custom_car_color'
			)
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		frappe.db.commit()
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_10 delete legacy fields error", message=str(e))

	# 2. Migrate legacy car data if old columns exist
	for dt in ["Sales Invoice", "Sales Order", "Quotation"]:
		try:
			existing_cols = frappe.db.get_table_columns(dt)
			updates = []
			if "custom_car_type" in existing_cols and "custom_vehicle_make" in existing_cols:
				updates.append("`custom_vehicle_make` = COALESCE(NULLIF(`custom_vehicle_make`, ''), `custom_car_type`)")
			if "custom_car_plate" in existing_cols and "custom_plate_number" in existing_cols:
				updates.append("`custom_plate_number` = COALESCE(NULLIF(`custom_plate_number`, ''), `custom_car_plate`)")
			if "custom_car_model" in existing_cols and "custom_vehicle_model" in existing_cols:
				updates.append("`custom_vehicle_model` = COALESCE(NULLIF(`custom_vehicle_model`, ''), `custom_car_model`)")
			if "custom_car_color" in existing_cols and "custom_vehicle_color" in existing_cols:
				updates.append("`custom_vehicle_color` = COALESCE(NULLIF(`custom_vehicle_color`, ''), `custom_car_color`)")
			if updates:
				frappe.db.sql(f"UPDATE `tab{dt}` SET {', '.join(updates)}")
				frappe.db.commit()
		except Exception as e:
			frappe.log_error(title=f"mu_car_care v1_1_10 migrate legacy {dt} error", message=str(e))

	# 3. Set allow_on_submit = 0 for locked maintenance settings and warranty details
	try:
		frappe.db.sql(
			"""
			UPDATE `tabCustom Field`
			SET allow_on_submit = 0
			WHERE fieldname IN (
				'custom_has_maintenance_schedule',
				'custom_maintenance_start_date',
				'custom_maintenance_duration_years',
				'custom_distribution_method',
				'custom_warranty_details'
			)
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		frappe.db.commit()
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_10 lock fields error", message=str(e))

	# 4. Reload Vehicle Warranty Item DocType
	try:
		frappe.reload_doc("mu_car_care", "doctype", "vehicle_warranty_item")
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_10 reload_doc error", message=str(e))

	# 5. Flush Redis and DocType caches
	try:
		frappe.cache.delete_key("bootinfo")
		for dt in ["Sales Invoice", "Quotation", "Sales Order", "Vehicle Warranty Item"]:
			frappe.clear_cache(doctype=dt)
		frappe.clear_cache()
	except Exception:
		pass
