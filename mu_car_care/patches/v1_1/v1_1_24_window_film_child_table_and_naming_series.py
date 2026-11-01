# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	v1.1.24 Patch:
	1. Reload Vehicle Film Item child DocType.
	2. Reload Vehicle Reception DocType to apply window_film_items child table and clean naming_series.
	3. Clean up any corrupted series entry 'REC-26-11-###' in tabSeries.
	4. Clear cache to reflect new child table in desk.
	"""
	try:
		# 1. Reload child DocType
		frappe.reload_doc("mu_car_care", "doctype", "vehicle_film_item", force=True)

		# 2. Reload Vehicle Reception
		frappe.reload_doc("mu_car_care", "doctype", "vehicle_reception", force=True)

		# 3. Clean up tabSeries
		try:
			frappe.db.sql("DELETE FROM `tabSeries` WHERE name = 'REC-26-11-###'")
			frappe.db.commit()
		except Exception:
			pass

		# 4. Clear cache
		frappe.clear_cache(doctype="Vehicle Film Item")
		frappe.clear_cache(doctype="Vehicle Reception")
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_24 Patch Error", message=str(e))
