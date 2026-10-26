// -*- coding: utf-8 -*-
// Copyright (c) 2026, Mubtkir and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Reception", {
	refresh: function (frm) {
		// Add quick creation buttons if document is saved
		if (!frm.is_new()) {
			if (!frm.doc.sales_invoice) {
				frm.add_custom_button(
					__("Create Sales Invoice"),
					function () {
						frappe.model.open_mapped_doc({
							method: "mu_car_care.api.make_sales_invoice_from_reception",
							frm: frm,
						});
					},
					__("Create")
				);
			}

			if (!frm.doc.quotation) {
				frm.add_custom_button(
					__("Create Quotation"),
					function () {
						frappe.model.open_mapped_doc({
							method: "mu_car_care.api.make_quotation_from_reception",
							frm: frm,
						});
					},
					__("Create")
				);
			}

			// Add quick status change buttons
			if (frm.doc.status === "Received") {
				frm.add_custom_button(__("Start Work"), function () {
					frm.set_value("status", "In Progress");
					frm.save();
				});
			} else if (frm.doc.status === "In Progress") {
				frm.add_custom_button(__("Mark Completed"), function () {
					frm.set_value("status", "Work Completed");
					frm.save();
				});
			} else if (frm.doc.status === "Work Completed") {
				frm.add_custom_button(__("Deliver Vehicle"), function () {
					frm.set_value("status", "Delivered");
					frm.save();
				});
			}
		}
	},

	customer: function (frm) {
		if (frm.doc.customer) {
			frappe.db.get_value("Customer", frm.doc.customer, ["customer_name", "mobile_no"], function (r) {
				if (r) {
					frm.set_value("customer_name", r.customer_name);
					if (r.mobile_no && !frm.doc.contact_mobile) {
						frm.set_value("contact_mobile", r.mobile_no);
					}
				}
			});
		}
	},
});
