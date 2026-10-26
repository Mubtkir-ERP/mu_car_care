# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import frappe


def after_migrate():
	"""
	Mubtkir ERP Master Guidelines (Rule 5):
	Auto-sync workspaces and clear Desk cache on every bench migrate
	to ensure updates and workspace cards appear immediately without manual intervention.
	"""
	try:
		# Clear desk bootinfo cache
		frappe.cache.delete_key("bootinfo")

		# Clear cache for key transaction DocTypes
		for dt in ["Sales Invoice", "Quotation", "Sales Order", "Vehicle Reception"]:
			frappe.clear_cache(doctype=dt)

		# Clear site cache
		frappe.clear_cache()
	except Exception:
		pass
