# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	v1.1.23 Patch:
	1. Reload Vehicle Reception DocType definition to apply is_submittable = 1 and amended_from.
	2. Ensure column amended_from exists on tabVehicle Reception.
	3. Update tabDocType to enforce is_submittable = 1.
	4. Clear cache to reflect new submit buttons in desk.
	"""
	try:
		# 1. Reload DocType
		frappe.reload_doc("mu_car_care", "doctype", "vehicle_reception", force=True)

		# 2. Add amended_from column to MariaDB table if not present
		table_cols = frappe.db.get_table_columns("Vehicle Reception")
		if "amended_from" not in table_cols:
			try:
				frappe.db.sql(
					"""
					ALTER TABLE `tabVehicle Reception`
					ADD COLUMN `amended_from` VARCHAR(140) DEFAULT NULL
					"""
				)
			except Exception:
				pass

		# 3. Explicitly enforce is_submittable in tabDocType
		frappe.db.set_value("DocType", "Vehicle Reception", "is_submittable", 1)
		frappe.db.commit()

		# 4. Clear cache
		frappe.clear_cache(doctype="Vehicle Reception")
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_23 Patch Error", message=str(e))
