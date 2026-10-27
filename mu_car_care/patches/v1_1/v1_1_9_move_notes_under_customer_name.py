# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	v1.1.9 Patch:
	Move Notes (custom_warranty_notes) field directly under Customer Name (customer_name)
	in Sales Invoice, Sales Order, and Quotation.
	"""
	try:
		frappe.db.sql(
			"""
			UPDATE `tabCustom Field`
			SET insert_after = 'customer_name'
			WHERE fieldname = 'custom_warranty_notes'
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		frappe.db.commit()
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_9 move notes error", message=str(e))

	# Clear cache
	try:
		frappe.cache.delete_key("bootinfo")
		for dt in ["Sales Invoice", "Quotation", "Sales Order"]:
			frappe.clear_cache(doctype=dt)
		frappe.clear_cache()
	except Exception:
		pass
