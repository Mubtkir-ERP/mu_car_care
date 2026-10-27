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
	v1.1.2 Patch:
	1. Reload Vehicle Maintenance Schedule Item & Vehicle Warranty Item DocTypes.
	2. Update Custom Fields: collapsible: 1, insert_after: items.
	3. Re-sync Car Care Tax Invoice Print Format with exact RTL design.
	4. Clear cache.
	"""
	# 1. Reload DocTypes
	try:
		frappe.reload_doc("mu_car_care", "doctype", "vehicle_maintenance_schedule_item")
		frappe.reload_doc("mu_car_care", "doctype", "vehicle_warranty_item")
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_2 reload_doc error", message=str(e))

	# 2. Update custom field properties
	try:
		frappe.db.sql(
			"""
			UPDATE `tabCustom Field`
			SET collapsible = 1, insert_after = 'items'
			WHERE fieldname = 'custom_maintenance_section'
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		frappe.db.sql(
			"""
			UPDATE `tabCustom Field`
			SET collapsible = 1, insert_after = 'custom_maintenance_schedule'
			WHERE fieldname = 'custom_warranty_section'
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		frappe.db.commit()
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_2 update fields error", message=str(e))

	# 3. Sync Print Format
	try:
		sync_print_formats()
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_2 sync print format error", message=str(e))

	# 4. Clear cache
	try:
		frappe.clear_cache()
	except Exception:
		pass
