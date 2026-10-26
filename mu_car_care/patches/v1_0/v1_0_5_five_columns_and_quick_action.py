# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	Rebuild custom fields for 5-column single-row vehicle layout and ensure
	clean form restoration across Sales Invoice, Quotation, and Sales Order.
	"""
	doctypes = ["Sales Invoice", "Quotation", "Sales Order"]

	# 1. Purge field_order property setters
	frappe.db.sql(
		"""
		DELETE FROM `tabProperty Setter`
		WHERE property = 'field_order'
		AND doc_type IN ('Sales Invoice', 'Quotation', 'Sales Order')
		"""
	)

	# 2. Delete all existing custom fields related to mu_car_care to re-import the 5-column layout cleanly
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

	# 3. Clear cache
	for dt in doctypes:
		frappe.clear_cache(doctype=dt)

	frappe.cache.delete_key("bootinfo")
	frappe.clear_cache()
