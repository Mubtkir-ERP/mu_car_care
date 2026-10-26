# -*- coding: utf-8 -*-
# Copyright (c) 2026, Mubtkir and contributors
# For license information, please see license.txt

app_name = "mu_car_care"
app_title = "العناية بالسيارات والحماية"
app_publisher = "Mubtkir"
app_description = "إدارة خدمات العناية بالسيارات، العازل الحراري، أفلام الحماية PPF، الفحص وجدولة الصيانة الدورية - مُبتكِر ERP"
app_email = "apps@mubtkir.com"
app_license = "mit"
required_apps = ["erpnext"]

# Client Scripts attached to standard DocTypes
doctype_js = {
	"Sales Invoice": "public/js/car_care_transaction.js",
	"Quotation": "public/js/car_care_transaction.js",
	"Sales Order": "public/js/car_care_transaction.js",
}

# Exported Fixtures for automatic installation on bench migrate
fixtures = [
	{
		"dt": "Custom Field",
		"filters": [["module", "=", "Mu Car Care"]],
	}
]

# Mubtkir ERP Master Guidelines (Rule 5): Auto-sync Workspaces and Desk Cache
after_migrate = "mu_car_care.setup.after_migrate"
