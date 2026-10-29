# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import os
import frappe


def after_migrate():
	"""
	Mubtkir ERP Master Guidelines (Rule 5):
	Auto-sync workspaces and clear Desk cache on every bench migrate.
	Ensures Car Care Tax Invoice Print Format and collapsible custom fields are always active.
	"""
	# 1. Clean up obsolete sections and ensure collapsible = 1 and correct section placement
	try:
		frappe.db.sql(
			"""
			DELETE FROM `tabCustom Field`
			WHERE fieldname IN ('custom_maintenance_section', 'custom_schedule_config_section')
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		frappe.db.sql(
			"""
			UPDATE `tabCustom Field`
			SET insert_after = 'custom_vehicle_make'
			WHERE fieldname = 'custom_has_maintenance_schedule'
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		frappe.db.sql(
			"""
			UPDATE `tabCustom Field`
			SET insert_after = 'items', collapsible = 1
			WHERE fieldname = 'custom_schedule_visits_section'
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		frappe.db.sql(
			"""
			UPDATE `tabCustom Field`
			SET insert_after = 'custom_schedule_visits_section'
			WHERE fieldname = 'custom_maintenance_start_date'
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		frappe.db.sql(
			"""
			UPDATE `tabCustom Field`
			SET insert_after = 'custom_generate_schedule_btn'
			WHERE fieldname = 'custom_maintenance_schedule'
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		frappe.db.sql(
			"""
			UPDATE `tabCustom Field`
			SET insert_after = 'custom_maintenance_schedule', collapsible = 1
			WHERE fieldname = 'custom_warranty_section'
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		frappe.db.sql(
			"""
			UPDATE `tabCustom Field`
			SET insert_after = 'customer_name'
			WHERE fieldname = 'custom_warranty_notes'
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		# Delete legacy custom fields and old section
		frappe.db.sql(
			"""
			DELETE FROM `tabCustom Field`
			WHERE fieldname IN (
				'custom_section_break_khlav',
				'custom_car_type',
				'custom_car_plate',
				'custom_car_model',
				'custom_car_color'
			)
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		# Set allow_on_submit = 0 for locked maintenance settings and warranty details
		frappe.db.sql(
			"""
			UPDATE `tabCustom Field`
			SET allow_on_submit = 0
			WHERE fieldname IN (
				'custom_has_maintenance_schedule',
				'custom_maintenance_start_date',
				'custom_maintenance_duration_years',
				'custom_distribution_method',
				'custom_warranty_details'
			)
			AND dt IN ('Sales Invoice', 'Quotation', 'Sales Order')
			"""
		)
		# Migrate legacy car data if old columns exist
		for dt in ["Sales Invoice", "Sales Order", "Quotation"]:
			try:
				existing_cols = frappe.db.get_table_columns(dt)
				updates = []
				if "custom_car_type" in existing_cols and "custom_vehicle_make" in existing_cols:
					updates.append("`custom_vehicle_make` = COALESCE(NULLIF(`custom_vehicle_make`, ''), `custom_car_type`)")
				if "custom_car_plate" in existing_cols and "custom_plate_number" in existing_cols:
					updates.append("`custom_plate_number` = COALESCE(NULLIF(`custom_plate_number`, ''), `custom_car_plate`)")
				if "custom_car_model" in existing_cols and "custom_vehicle_model" in existing_cols:
					updates.append("`custom_vehicle_model` = COALESCE(NULLIF(`custom_vehicle_model`, ''), `custom_car_model`)")
				if "custom_car_color" in existing_cols and "custom_vehicle_color" in existing_cols:
					updates.append("`custom_vehicle_color` = COALESCE(NULLIF(`custom_vehicle_color`, ''), `custom_car_color`)")
				if updates:
					frappe.db.sql(f"UPDATE `tab{dt}` SET {', '.join(updates)}")
			except Exception:
				pass
		# Clear auto-generated notes from database
		frappe.db.sql(
			"""
			UPDATE `tabVehicle Maintenance Schedule Item`
			SET notes = ''
			WHERE notes LIKE 'زيارة صيانة دورية%'
			"""
		)
		frappe.db.commit()
	except Exception:
		pass

	# 2. Sync Print Formats
	try:
		sync_print_formats()
	except Exception:
		pass

	# 3. Clear Caches
	try:
		frappe.cache.delete_key("bootinfo")
		for dt in ["Sales Invoice", "Quotation", "Sales Order", "Vehicle Reception", "Print Format"]:
			frappe.clear_cache(doctype=dt)
		frappe.clear_cache()
	except Exception:
		pass


def sync_print_formats():
    """مزامنة قوالب الفاتورة وعرض السعر وطلب المبيعات مع ملفات التطبيق بعد التحديث."""
    formats = (
        ("Car Care Tax Invoice", "Sales Invoice", "car_care_tax_invoice"),
        ("Car Care Quotation", "Quotation", "car_care_quotation"),
        ("Car Care Sales Order", "Sales Order", "car_care_sales_order"),
    )
    app_path = frappe.get_app_path("mu_car_care")
    for pf_name, doctype, slug in formats:
        try:
            html_file = os.path.join(app_path, "mu_car_care", "print_format", slug, slug + ".html")
            if not os.path.exists(html_file):
                continue
            with open(html_file, "r", encoding="utf-8") as f:
                html_content = f.read()
            if frappe.db.exists("Print Format", pf_name):
                pf = frappe.get_doc("Print Format", pf_name)
            else:
                pf = frappe.new_doc("Print Format")
                pf.name = pf_name
            pf.doc_type = doctype
            pf.module = "Mu Car Care"
            pf.custom_format = 1
            pf.print_format_type = "Jinja"
            pf.pdf_generator = "wkhtmltopdf"
            pf.html = html_content
            pf.standard = "No"
            pf.disabled = 0
            pf.default_print_language = "ar"
            pf.font_size = 13
            pf.margin_top = 0.0
            pf.margin_bottom = 0.0
            pf.margin_left = 0.0
            pf.margin_right = 0.0
            pf.save(ignore_permissions=True)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Mu Car Care Print Format Sync: " + pf_name)
    frappe.db.commit()
