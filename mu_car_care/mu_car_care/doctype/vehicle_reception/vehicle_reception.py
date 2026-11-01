# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class VehicleReception(Document):
	"""
	Controller for Vehicle Reception & Inspection.
	Handles vehicle check-in, customer link, service summary, and status workflow.
	"""

	def validate(self):
		self.validate_plate_number()
		self.set_customer_details()
		self.summarize_requested_services()

	def validate_plate_number(self):
		"""Clean and standardize plate number."""
		if self.plate_number:
			self.plate_number = self.plate_number.strip().upper()

	def set_customer_details(self):
		"""Ensure customer details are populated if not already fetched."""
		if self.customer:
			if not self.customer_name:
				self.customer_name = frappe.db.get_value("Customer", self.customer, "customer_name")
			if not self.contact_mobile:
				mobile = frappe.db.get_value("Customer", self.customer, "mobile_no")
				if mobile:
					self.contact_mobile = mobile

	def summarize_requested_services(self):
		"""
		Build a clean, human-readable summary of requested services
		from checkboxes and specifications into requested_services.
		"""
		summary_lines = []

		# 1. Window Film
		if self.service_window_film or self.film_front_window or self.film_back_window or self.film_triangle_window or self.film_rear_driver or self.film_rear_passenger or self.film_sunroof or self.film_panorama:
			glass_items = [
				(self.film_front_window, _("Front Window"), self.film_front_degree, self.film_front_uom),
				(self.film_back_window, _("Back Window"), self.film_back_degree, self.film_back_uom),
				(self.film_triangle_window, _("Triangle Window"), self.film_triangle_degree, self.film_triangle_uom),
				(self.film_rear_driver, _("Behind Driver Window"), self.film_rear_driver_degree, self.film_rear_driver_uom),
				(self.film_rear_passenger, _("Behind Passenger Window"), self.film_rear_passenger_degree, self.film_rear_passenger_uom),
				(self.film_sunroof, _("Sunroof"), self.film_sunroof_degree, self.film_sunroof_uom),
				(self.film_panorama, _("Panorama Roof"), self.film_panorama_degree, self.film_panorama_uom),
			]
			film_lines = []
			for is_selected, name, degree, uom in glass_items:
				if is_selected:
					specs = []
					if degree:
						specs.append(f"{_('Degree')}: {degree}")
					if uom:
						specs.append(f"{_('Type')}: {uom}")
					spec_str = f" [{', '.join(specs)}]" if specs else ""
					film_lines.append(f"{name}{spec_str}")

			loc_str = ", ".join(film_lines) if film_lines else _("Not specified")
			summary_lines.append(f"• {_('Window Film')}: {loc_str}")

		# 2. PPF Protection
		if self.service_ppf_protection or self.ppf_front_bumper or self.ppf_rear_bumper or self.ppf_front_doors or self.ppf_back_doors or self.ppf_headlights or self.ppf_hood or self.ppf_fenders or self.ppf_mirrors or self.ppf_grille or self.ppf_full_body or self.ppf_front_window:
			ppf_parts = []
			if self.ppf_full_body:
				ppf_parts.append(_("Full Car Body"))
			if self.ppf_front_bumper:
				ppf_parts.append(_("Front Bumper"))
			if self.ppf_rear_bumper:
				ppf_parts.append(_("Rear Bumper"))
			if self.ppf_front_doors:
				ppf_parts.append(_("Front Doors"))
			if self.ppf_back_doors:
				ppf_parts.append(_("Back Doors"))
			if self.ppf_headlights:
				ppf_parts.append(_("Headlights / Lights"))
			if self.ppf_hood:
				ppf_parts.append(_("Hood"))
			if self.ppf_fenders:
				ppf_parts.append(_("Fenders"))
			if self.ppf_mirrors:
				ppf_parts.append(_("Mirrors"))
			if self.ppf_grille:
				ppf_parts.append(_("Grille"))
			if self.ppf_front_window:
				ppf_parts.append(_("Front Windshield (PPF)"))

			loc_str = ", ".join([str(p) for p in ppf_parts]) if ppf_parts else _("Not specified")
			summary_lines.append(f"• {_('PPF Protection')}: {loc_str}")

		# 3. Polishing
		if self.service_polishing or self.polish_inside or self.polish_outside or self.polish_wax_layer or self.polish_seats or self.polish_headlights or self.polish_rims or self.polish_scratch_removal or self.polish_wax_coat or self.polish_nano_ceramic:
			polish_parts = []
			if self.polish_inside:
				polish_parts.append(_("Interior Polishing"))
			if self.polish_outside:
				polish_parts.append(_("Exterior Polishing"))
			if self.polish_wax_layer:
				polish_parts.append(_("Wax Layer"))
			if self.polish_seats:
				polish_parts.append(_("Seats"))
			if self.polish_headlights:
				polish_parts.append(_("Headlights Polishing"))
			if self.polish_rims:
				polish_parts.append(_("Rims"))
			if self.polish_scratch_removal:
				polish_parts.append(_("Scratch Removal"))
			if self.polish_wax_coat:
				polish_parts.append(_("Wax Coat"))
			if self.polish_nano_ceramic:
				polish_parts.append(_("Nano Ceramic"))

			loc_str = ", ".join([str(p) for p in polish_parts]) if polish_parts else _("Not specified")
			extra = ""
			if self.nano_layers_count:
				extra = f" [{_('Nano Layers Count')}: {self.nano_layers_count}]"
			summary_lines.append(f"• {_('Polishing')}: {loc_str}{extra}")

		# 4. Legacy accessories if present
		if self.get("accessories"):
			summary_lines.append(f"• {_('Accessories')}: {self.accessories.strip()}")

		self.requested_services = "\n".join(summary_lines)
