# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

import frappe
from mu_car_care.setup import sync_print_formats


def execute():
	"""
	v1.1.5 Patch:
	1. Sync Car Care Tax Invoice Print Format (4-column warranty table, dynamic service terms box, right-car left-slogan footer).
	2. Clear all relevant caches.
	"""
	try:
		sync_print_formats()
	except Exception as e:
		frappe.log_error(title="mu_car_care v1_1_5 sync_print_formats error", message=str(e))

	try:
		frappe.clear_cache()
	except Exception:
		pass
