# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	Complete cleanup and restoration of Sales Invoice, Quotation, and Sales Order:
	1. Remove any frozen field_order Property Setters that corrupted the form layouts.
	2. Remove previous custom fields for Mu Car Care to allow clean re-import.
	3. Reload standard ERPNext DocTypes to factory clean layout.
	4. Clear cache.
	"""
	doctypes = ["Sales Invoice", "Quotation", "Sales Order"]

	# 1. Delete frozen field_order Property Setters
	frappe.db.sql(
		"""
		DELETE FROM `tabProperty Setter`
		WHERE property = 'field_order'
		AND doc_type IN ('Sales Invoice', 'Quotation', 'Sales Order')
		"""
	)

	# 2. Delete all existing custom fields related to mu_car_care
	frappe.db.sql(
		"""
		DELETE FROM `tabCustom Field`
		WHERE dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
		AND (
			module = 'Mu Car Care'
			OR fieldname LIKE 'custom_vehicle_%'
			OR fieldname LIKE 'custom_maintenance_%'
			OR fieldname LIKE 'custom_schedule_%'
			OR fieldname LIKE 'custom_plate_%'
			OR fieldname LIKE 'custom_chassis_%'
			OR fieldname = 'custom_has_maintenance_schedule'
			OR fieldname = 'custom_distribution_method'
			OR fieldname = 'custom_generate_schedule_btn'
		)
		"""
	)

	# 3. Reload standard DocTypes to restore core ERPNext fields and tabs
	try:
		frappe.reload_doc("accounts", "doctype", "sales_invoice")
	except Exception:
		pass

	try:
		frappe.reload_doc("selling", "doctype", "quotation")
	except Exception:
		pass

	try:
		frappe.reload_doc("selling", "doctype", "sales_order")
	except Exception:
		pass

	# 4. Clear cache for affected DocTypes and Desk
	for dt in doctypes:
		frappe.clear_cache(doctype=dt)

	frappe.cache.delete_key("bootinfo")
	frappe.clear_cache()
