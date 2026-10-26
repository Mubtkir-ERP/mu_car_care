# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	Automatically migrate historical car data from legacy fields to standard mu_car_care fields.
	Handles variations like car_type, car_mudel, car_color, etc.
	"""
	doctypes = ["Sales Invoice", "Quotation", "Sales Order"]

	field_mapping_patterns = {
		"custom_vehicle_make": [
			"car_type", "cartype", "car_make", "carmake",
			"vehicle_type", "vehicletype", "vehicle_make", "make"
		],
		"custom_vehicle_model": [
			"car_mudel", "carmudel", "car_model", "carmodel",
			"mudel", "model", "vehicle_model", "car_year"
		],
		"custom_vehicle_color": [
			"car_color", "carcolor", "car_colour", "carcolour",
			"vehicle_color", "color", "colour"
		],
		"custom_plate_number": [
			"plate_number", "platenumber", "plate_no", "plateno",
			"car_plate", "carplate", "plate"
		],
		"custom_chassis_no": [
			"chassis_no", "chassisno", "car_chassis", "vin", "car_vin"
		],
	}

	for dt in doctypes:
		try:
			table = f"tab{dt}"
			existing_columns = frappe.db.get_table_columns(dt)
			existing_cols_lower = {col.lower(): col for col in existing_columns}

			for target_field, candidates in field_mapping_patterns.items():
				matched_col = None
				for candidate in candidates:
					test_candidates = [
						candidate,
						f"custom_{candidate}",
						candidate.replace("_", ""),
						f"custom_{candidate.replace('_', '')}",
					]
					for cand in test_candidates:
						if cand.lower() in existing_cols_lower:
							actual_col = existing_cols_lower[cand.lower()]
							if actual_col != target_field:
								matched_col = actual_col
								break
					if matched_col:
						break

				if matched_col and target_field in existing_columns:
					frappe.db.sql(f"""
						UPDATE `{table}`
						SET `{target_field}` = `{matched_col}`
						WHERE (`{target_field}` IS NULL OR `{target_field}` = '')
						  AND (`{matched_col}` IS NOT NULL AND `{matched_col}` != '')
					""")
					frappe.db.commit()

		except Exception:
			frappe.log_error(
				title=f"Error migrating legacy car fields for {dt}",
				message=frappe.get_traceback()
			)
