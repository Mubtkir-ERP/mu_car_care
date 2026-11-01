# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	v1.1.25 Patch:
	1. Reload Vehicle Reception DocType to apply:
	   - 3-digit naming series REC-.YY.-.MM.-.### (e.g. REC-26-11-001)
	   - Small Text notes field
	2. Reload Vehicle Film Item child DocType to apply Film Type label.
	3. Clean up corrupted series entries with literal '###' in tabSeries.
	4. Ensure custom_paid_amount field and column exist on Sales Invoice, Sales Order, Quotation.
	5. Clear cache.
	"""
	try:
		# 1. Reload DocTypes
		frappe.reload_doc("mu_car_care", "doctype", "vehicle_film_item", force=True)
		frappe.reload_doc("mu_car_care", "doctype", "vehicle_reception", force=True)

		# 2. Clean up tabSeries
		try:
			frappe.db.sql("DELETE FROM `tabSeries` WHERE name LIKE '%###%'")
			frappe.db.commit()
		except Exception:
			pass

		# 3. Add custom_paid_amount to transactions if not present
		for dt in ["Sales Invoice", "Sales Order", "Quotation"]:
			try:
				cols = frappe.db.get_table_columns(dt)
				if "custom_paid_amount" not in cols:
					frappe.db.sql(f"ALTER TABLE `tab{dt}` ADD COLUMN `custom_paid_amount` decimal(21,9) DEFAULT 0.0")
			except Exception:
				pass

			if not frappe.db.exists("Custom Field", {"dt": dt, "fieldname": "custom_paid_amount"}):
				try:
					cf = frappe.get_doc({
						"doctype": "Custom Field",
						"dt": dt,
						"fieldname": "custom_paid_amount",
						"label": "Paid Deposit Amount",
						"fieldtype": "Currency",
						"options": "Company:company:default_currency",
						"insert_after": "custom_odometer_reading",
						"read_only": 0,
						"allow_on_submit": 0,
					})
					cf.insert(ignore_permissions=True)
				except Exception:
					pass

		frappe.db.commit()

		# 4. Clear cache
		frappe.clear_cache(doctype="Vehicle Reception")
		frappe.clear_cache(doctype="Vehicle Film Item")
		for dt in ["Sales Invoice", "Sales Order", "Quotation"]:
			frappe.clear_cache(doctype=dt)

	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_25 Patch Error", message=str(e))
