# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import add_months, cint, getdate, nowdate


@frappe.whitelist()
def calculate_maintenance_schedule(start_date=None, duration_years=None, distribution_method=None, duration_months=None):
	"""
	Calculate maintenance schedule visit dates based on warranty duration in years and frequency.
	"""
	if not start_date:
		start_date = nowdate()

	start_date = getdate(start_date)

	if duration_years:
		total_months = cint(duration_years) * 12
	elif duration_months:
		total_months = cint(duration_months)
	else:
		total_months = 12

	if total_months <= 0:
		total_months = 12

	method = (distribution_method or "Annual").strip()

	step_map = {
		"Monthly": 1,
		"شهري": 1,
		"Quarterly": 3,
		"ربع سنوي": 3,
		"Semi-Annual": 6,
		"نصف سنوي": 6,
		"Annual": 12,
		"سنوي": 12,
	}

	step = step_map.get(method, 12)
	visits = []

	current_month_offset = step
	while current_month_offset <= total_months:
		visit_date = add_months(start_date, current_month_offset)
		if current_month_offset % 12 == 0:
			period_label = _("Year {0}").format(current_month_offset // 12)
		else:
			period_label = _("Month {0}").format(current_month_offset)

		visits.append({
			"visit_date": str(visit_date),
			"visit_status": "Scheduled",
			"notes": _("Scheduled Maintenance Visit ({0})").format(period_label),
		})
		current_month_offset += step

	return visits


@frappe.whitelist()
def record_maintenance_visit(doctype, docname, row_idx, actual_visit_date=None, odometer_km=None, technician=None, notes=None):
	"""
	Whitelisted API for Sales/Service staff to record a completed maintenance visit directly.
	Works on Submitted Sales Invoices & Sales Orders without triggering accounting/cost-center validations.
	"""
	try:
		if not frappe.has_permission(doctype, "read", doc=docname):
			frappe.throw(_("Not permitted to access {0} {1}").format(doctype, docname), frappe.PermissionError)

		doc = frappe.get_doc(doctype, docname)
		if not doc.get("custom_maintenance_schedule"):
			frappe.throw(_("No maintenance schedule found on {0}").format(docname))

		target_row = None
		row_idx = cint(row_idx)

		for row in doc.custom_maintenance_schedule:
			if row.idx == row_idx:
				target_row = row
				break

		if not target_row:
			frappe.throw(_("Selected maintenance visit row #{0} was not found.").format(row_idx))

		actual_date = actual_visit_date or nowdate()

		# Update the child row in the database directly
		frappe.db.set_value(
			"Vehicle Maintenance Schedule Item",
			target_row.name,
			{
				"actual_visit_date": actual_date,
				"visit_status": "Completed",
				"odometer_km": cint(odometer_km) if odometer_km else target_row.odometer_km,
				"technician": technician or target_row.technician,
				"notes": notes or target_row.notes,
			},
		)
		frappe.db.commit()

		# Add a timeline audit comment safely
		try:
			doc.add_comment(
				"Comment",
				_("Maintenance visit #{0} recorded as Completed on {1}. Technician: {2}, Odometer: {3} KM").format(
					row_idx,
					actual_date,
					technician or _("Not specified"),
					odometer_km or _("Not specified"),
				),
			)
		except Exception:
			pass

		return {
			"success": True,
			"message": _("Maintenance visit #{0} updated to Completed successfully.").format(row_idx),
		}

	except Exception as e:
		frappe.log_error(title=_("Error Recording Maintenance Visit"), message=frappe.get_traceback())
		frappe.throw(_("Failed to record maintenance visit: {0}").format(str(e)))


@frappe.whitelist()
def make_sales_invoice_from_reception(source_name, target_doc=None):
	"""Create a Sales Invoice pre-filled with vehicle details from Vehicle Reception."""
	def set_missing_values(source, target):
		target.custom_has_maintenance_schedule = 1
		target.custom_maintenance_start_date = source.posting_date

	doclist = get_mapped_doc(
		"Vehicle Reception",
		source_name,
		{
			"Vehicle Reception": {
				"doctype": "Sales Invoice",
				"field_map": {
					"customer": "customer",
					"plate_number": "custom_plate_number",
					"vehicle_make": "custom_vehicle_make",
					"vehicle_model": "custom_vehicle_model",
					"vehicle_color": "custom_vehicle_color",
					"odometer_km": "custom_odometer_reading",
					"chassis_no": "custom_chassis_no",
					"name": "custom_vehicle_reception_ref",
				},
			}
		},
		target_doc,
		set_missing_values,
	)

	return doclist


@frappe.whitelist()
def make_quotation_from_reception(source_name, target_doc=None):
	"""Create a Quotation pre-filled with vehicle details from Vehicle Reception."""
	def set_missing_values(source, target):
		target.custom_has_maintenance_schedule = 1
		target.custom_maintenance_start_date = source.posting_date

	doclist = get_mapped_doc(
		"Vehicle Reception",
		source_name,
		{
			"Vehicle Reception": {
				"doctype": "Quotation",
				"field_map": {
					"customer": "party_name",
					"plate_number": "custom_plate_number",
					"vehicle_make": "custom_vehicle_make",
					"vehicle_model": "custom_vehicle_model",
					"vehicle_color": "custom_vehicle_color",
					"odometer_km": "custom_odometer_reading",
					"chassis_no": "custom_chassis_no",
					"name": "custom_vehicle_reception_ref",
				},
			}
		},
		target_doc,
		set_missing_values,
	)

	return doclist
