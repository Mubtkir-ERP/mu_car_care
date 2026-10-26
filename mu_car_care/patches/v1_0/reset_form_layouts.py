# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	Clean up previous custom fields for Mu Car Care and clear doctype cache
	to ensure standard form layouts (Details, Items, Taxes) are 100% restored.
	"""
	doctypes = ["Sales Invoice", "Quotation", "Sales Order"]

	# Delete any previous Custom Field records associated with this module
	frappe.db.delete("Custom Field", {"module": "Mu Car Care"})

	# Clear cache for affected doctypes
	for dt in doctypes:
		frappe.clear_cache(doctype=dt)
