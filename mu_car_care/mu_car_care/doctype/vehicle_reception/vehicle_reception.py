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
		if self.customer and not self.contact_mobile:
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
		film_parts = []
		if self.film_front_window:
			film_parts.append(_("Front Window"))
		if self.film_front_doors:
			film_parts.append(_("Front Doors"))
		if self.film_back_doors:
			film_parts.append(_("Back Doors"))
		if self.film_back_window:
			film_parts.append(_("Back Window"))
		if self.film_triangle_window:
			film_parts.append(_("Triangle Window"))

		if film_parts or self.film_type:
			details = ", ".join([str(p) for p in film_parts]) if film_parts else ""
			if self.film_type:
				details = f"{details} ({self.film_type})" if details else self.film_type
			summary_lines.append(f"• {_('Window Film')}: {details}")

		# 2. Protection
		prot_parts = []
		if self.prot_front:
			prot_parts.append(_("Front"))
		if self.prot_headlights:
			prot_parts.append(_("Headlights"))
		if self.prot_body:
			prot_parts.append(_("Car Body"))
		if self.prot_leather_mat:
			prot_parts.append(_("Leather Mat"))
		if self.prot_leather:
			prot_parts.append(_("Leather"))
		if self.prot_velvet:
			prot_parts.append(_("Velvet"))

		if prot_parts:
			summary_lines.append(f"• {_('Car Protection')}: {', '.join([str(p) for p in prot_parts])}")

		# 3. Polishing
		polish_parts = []
		if self.polish_inside:
			polish_parts.append(_("Inside Polishing"))
		if self.polish_outside:
			polish_parts.append(_("Outside Polishing"))
		if self.polish_wax:
			polish_parts.append(_("Wax Coat"))
		if self.polish_nano_ceramic:
			polish_parts.append(_("Nano Ceramic"))

		if polish_parts or self.nano_layers_warranty:
			details = ", ".join([str(p) for p in polish_parts]) if polish_parts else ""
			if self.nano_layers_warranty:
				details = f"{details} ({self.nano_layers_warranty})" if details else self.nano_layers_warranty
			summary_lines.append(f"• {_('Polishing')}: {details}")

		# 4. Accessories
		if self.accessories:
			summary_lines.append(f"• {_('Accessories')}: {self.accessories.strip()}")

		self.requested_services = "\n".join(summary_lines)
