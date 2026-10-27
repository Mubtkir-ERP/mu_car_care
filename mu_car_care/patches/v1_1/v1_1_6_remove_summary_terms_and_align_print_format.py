# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import frappe
from mu_car_care.setup import sync_print_formats


def execute():
	"""
	v1.1.6 Patch:
	1. Reload Vehicle Warranty Item DocType (removes summary_terms from schema).
	2. Drop summary_terms column from tabVehicle Warranty Item in database.
	3. Synchronize Car Care Tax Invoice Print Format (3-card header, fixed page 1 terms, 4-col warranty, dynamic page 2 terms, exact margins).
	4. Clear cache across Desk and Print formats.
	"""
	# 1. Reload DocType
	try:
		frappe.reload_doc("mu_car_care", "doctype", "vehicle_warranty_item", force=True)
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_6 reload_doc error", message=str(e))

	# 2. Drop summary_terms column from DB table if it exists
	try:
		columns = frappe.db.get_table_columns("Vehicle Warranty Item")
		if "summary_terms" in columns:
			frappe.db.sql("ALTER TABLE `tabVehicle Warranty Item` DROP COLUMN `summary_terms`")
			frappe.db.commit()
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_6 drop summary_terms column error", message=str(e))

	# 3. Synchronize Print Format
	try:
		sync_print_formats()
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_6 sync_print_formats error", message=str(e))

	# 4. Clear cache
	try:
		frappe.clear_cache()
	except Exception:
		pass
