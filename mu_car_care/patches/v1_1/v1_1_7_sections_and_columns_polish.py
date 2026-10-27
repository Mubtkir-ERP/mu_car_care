# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import frappe
from mu_car_care.setup import sync_print_formats


def execute():
	"""
	v1.1.7 Patch:
	1. Reload Vehicle Maintenance Schedule Item & Vehicle Warranty Item DocTypes.
	2. Drop obsolete columns (visit_type, odometer_km, technician, work_done) from tabVehicle Maintenance Schedule Item.
	3. Position custom_has_maintenance_schedule under custom_vehicle_make.
	4. Position car care sections under items (above taxes_section) and ensure collapsible = 1.
	5. Synchronize Car Care Tax Invoice Print Format and clear cache.
	"""
	# 1. Reload DocTypes
	try:
		frappe.reload_doc("mu_car_care", "doctype", "vehicle_maintenance_schedule_item", force=True)
		frappe.reload_doc("mu_car_care", "doctype", "vehicle_warranty_item", force=True)
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_7 reload_doc error", message=str(e))

	# 2. Drop obsolete columns from tabVehicle Maintenance Schedule Item
	try:
		columns = frappe.db.get_table_columns("Vehicle Maintenance Schedule Item")
		obsolete_cols = ["visit_type", "odometer_km", "technician", "work_done"]
		for col in obsolete_cols:
			if col in columns:
				try:
					frappe.db.sql(f"ALTER TABLE `tabVehicle Maintenance Schedule Item` DROP COLUMN `{col}`")
				except Exception:
					pass

		# Also check Vehicle Warranty Item for summary_terms
		w_columns = frappe.db.get_table_columns("Vehicle Warranty Item")
		if "summary_terms" in w_columns:
			try:
				frappe.db.sql("ALTER TABLE `tabVehicle Warranty Item` DROP COLUMN `summary_terms`")
			except Exception:
				pass

		frappe.db.commit()
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_7 drop columns error", message=str(e))

	# 3. Update Custom Field positions and collapsibility
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
			SET insert_after = 'items', collapsible = 1
			WHERE fieldname = 'custom_schedule_config_section'
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
		frappe.log_error(title="mu_car_care v1_1_7 update custom fields error", message=str(e))

	# 4. Synchronize Print Format
	try:
		sync_print_formats()
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_7 sync_print_formats error", message=str(e))

	# 5. Clear cache
	try:
		frappe.cache.delete_key("bootinfo")
		for dt in ["Sales Invoice", "Quotation", "Sales Order", "Vehicle Reception", "Print Format"]:
			frappe.clear_cache(doctype=dt)
		frappe.clear_cache()
	except Exception:
		pass
