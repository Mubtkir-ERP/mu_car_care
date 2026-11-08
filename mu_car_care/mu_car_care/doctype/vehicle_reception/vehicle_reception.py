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

	def before_naming(self):
		"""Use a numeric five-digit suffix even for forms opened before the update."""
		self.naming_series = "REC-.YY.-.MM.-.#####"

	def before_validate(self):
		self.cleanup_window_film_items()

	def validate(self):
		self.cleanup_window_film_items()
		self.validate_plate_number()
		self.set_customer_details()
		self.summarize_requested_services()

	def cleanup_window_film_items(self):
		"""Ensure no lingering empty rows in window_film_items when disabled or unselected."""
		if not self.service_window_film:
			self.set("window_film_items", [])
		else:
			valid_rows = [
				r for r in self.get("window_film_items", [])
				if r.get("window_location") or r.get("shade_degree") or r.get("film_type") or r.get("notes")
			]
			self.set("window_film_items", valid_rows)

	def on_submit(self):
		"""When submitted (تسجيل), transition to Received if Draft, locking the record."""
		if self.status == "Draft":
			self.db_set("status", "Received")

	def on_cancel(self):
		"""When cancelled, transition status to Cancelled."""
		self.db_set("status", "Cancelled")

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
		if self.service_window_film:
			film_lines = []
			if self.get("window_film_items"):
				for row in self.window_film_items:
					specs = []
					if row.get("shade_degree"):
						specs.append(f"{_('Degree')}: {row.shade_degree}")
					if row.get("film_type"):
						specs.append(f"{_('Type')}: {row.film_type}")
					if row.get("notes"):
						specs.append(str(row.notes))
					spec_str = f" [{', '.join(specs)}]" if specs else ""
					loc_label = _(row.window_location) if row.window_location else ""
					film_lines.append(f"{loc_label}{spec_str}")
			else:
				glass_items = [
					(self.film_front_window, _("Front Window"), self.film_front_degree, self.film_front_uom),
					(self.film_back_window, _("Back Window"), self.film_back_degree, self.film_back_uom),
					(self.film_triangle_window, _("Triangle Window"), self.film_triangle_degree, self.film_triangle_uom),
					(self.film_rear_driver, _("Behind Driver Window"), self.film_rear_driver_degree, self.film_rear_driver_uom),
					(self.film_rear_passenger, _("Behind Passenger Window"), self.film_rear_passenger_degree, self.film_rear_passenger_uom),
					(self.film_sunroof, _("Sunroof"), self.film_sunroof_degree, self.film_sunroof_uom),
					(self.film_panorama, _("Panorama Roof"), self.film_panorama_degree, self.film_panorama_uom),
				]
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
		if (
			self.service_ppf_protection
			or self.ppf_full_body
			or self.ppf_front_bumper
			or self.ppf_rear_bumper
			or self.ppf_driver_door
			or self.ppf_passenger_door
			or self.ppf_rear_driver_door
			or self.ppf_rear_passenger_door
			or self.ppf_trunk_door
			or self.ppf_front_headlights
			or self.ppf_rear_lights
			or self.ppf_hood
			or self.ppf_fenders
			or self.ppf_mirrors
			or self.ppf_grille
			or self.ppf_front_window
		):
			ppf_items = [
				(self.ppf_full_body, _("Full Car Body")),
				(self.ppf_front_bumper, _("Front Bumper")),
				(self.ppf_rear_bumper, _("Rear Bumper")),
				(self.ppf_driver_door, _("Driver Door")),
				(self.ppf_passenger_door, _("Passenger Door")),
				(self.ppf_rear_driver_door, _("Behind Driver Door")),
				(self.ppf_rear_passenger_door, _("Behind Passenger Door")),
				(self.ppf_trunk_door, _("Trunk Door")),
				(self.ppf_front_headlights, _("Front Headlights")),
				(self.ppf_rear_lights, _("Rear Tail Lights")),
				(self.ppf_hood, _("Hood")),
				(self.ppf_fenders, _("Fenders")),
				(self.ppf_mirrors, _("Mirrors")),
				(self.ppf_grille, _("Grille")),
				(self.ppf_front_window, _("Front Windshield (PPF)")),
			]
			ppf_parts = [name for is_selected, name in ppf_items if is_selected]
			loc_str = ", ".join(ppf_parts) if ppf_parts else _("Not specified")
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
