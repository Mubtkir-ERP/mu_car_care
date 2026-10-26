# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	Clean up any misplaced custom fields and clear doctype cache
	to ensure clean layout restoration.
	"""
	doctypes = ["Sales Invoice", "Quotation", "Sales Order"]

	# Delete previous custom fields for mu_car_care to re-import them correctly
	frappe.db.delete("Custom Field", {"module": "Mu Car Care"})

	for dt in doctypes:
		frappe.clear_cache(doctype=dt)
