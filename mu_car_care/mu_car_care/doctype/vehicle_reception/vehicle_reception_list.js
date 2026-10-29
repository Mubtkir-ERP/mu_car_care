// -*- coding: utf-8 -*-
// Copyright (c) 2026, Mubtkir and contributors
// For license information, please see license.txt

frappe.listview_settings["Vehicle Reception"] = {
	add_fields: ["status", "plate_number", "customer", "posting_date"],
	get_indicator: function (doc) {
		if (doc.status === "Received") {
			return [__("Received"), "blue", "status,=,Received"];
		} else if (doc.status === "In Progress") {
			return [__("In Progress"), "orange", "status,=,In Progress"];
		} else if (doc.status === "Work Completed") {
			return [__("Work Completed"), "green", "status,=,Work Completed"];
		} else if (doc.status === "Delivered") {
			return [__("Delivered"), "gray", "status,=,Delivered"];
		} else if (doc.status === "Cancelled") {
			return [__("Cancelled"), "red", "status,=,Cancelled"];
		} else {
			return [__("Draft"), "darkgrey", "status,=,Draft"];
		}
	},
};
