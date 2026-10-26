# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class VehicleReception(Document):
	"""
	Controller for Vehicle Reception & Inspection.
	Handles vehicle check-in, customer link, odometer check, and status workflow.
	"""

	def validate(self):
		self.validate_plate_number()
		self.set_customer_details()

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
