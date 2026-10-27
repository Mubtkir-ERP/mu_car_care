# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import os
import frappe


def after_migrate():
	"""
	Mubtkir ERP Master Guidelines (Rule 5):
	Auto-sync workspaces and clear Desk cache on every bench migrate
	to ensure updates and workspace cards appear immediately without manual intervention.
	Also ensures Car Care Tax Invoice Print Format is always active and present.
	"""
	try:
		sync_print_formats()
	except Exception:
		pass

	try:
		# Clear desk bootinfo cache
		frappe.cache.delete_key("bootinfo")

		# Clear cache for key transaction DocTypes
		for dt in ["Sales Invoice", "Quotation", "Sales Order", "Vehicle Reception", "Print Format"]:
			frappe.clear_cache(doctype=dt)

		# Clear site cache
		frappe.clear_cache()
	except Exception:
		pass


def sync_print_formats():
	try:
		app_path = frappe.get_app_path("mu_car_care")
		html_file = os.path.join(
			app_path, "mu_car_care", "print_format", "car_care_tax_invoice", "car_care_tax_invoice.html"
		)
		if os.path.exists(html_file):
			with open(html_file, "r", encoding="utf-8") as f:
				html_content = f.read()

			pf_name = "Car Care Tax Invoice"
			if frappe.db.exists("Print Format", pf_name):
				pf = frappe.get_doc("Print Format", pf_name)
			else:
				pf = frappe.new_doc("Print Format")
				pf.name = pf_name

			pf.doc_type = "Sales Invoice"
			pf.module = "Mu Car Care"
			pf.custom_format = 1
			pf.print_format_type = "Jinja"
			pf.html = html_content
			pf.standard = "No"
			pf.disabled = 0
			pf.default_print_language = "ar"
			pf.font_size = 13
			pf.margin_top = 8.0
			pf.margin_bottom = 8.0
			pf.margin_left = 8.0
			pf.margin_right = 8.0
			pf.save(ignore_permissions=True)
			frappe.db.commit()
	except Exception:
		pass
