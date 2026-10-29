// -*- coding: utf-8 -*-
// Copyright (c) 2026, Mubtkir and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Reception", {
	setup: function (frm) {
		frm.set_query("customer", function () {
			return {
				filters: {
					disabled: 0,
				},
			};
		});
	},

	refresh: function (frm) {
		// Style inspection diagram canvas with vehicle silhouette backdrop
		setup_diagram_background(frm);

		// Add quick document creation buttons
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

			if (!frm.doc.sales_order) {
				frm.add_custom_button(
					__("Create Sales Order"),
					function () {
						frappe.model.open_mapped_doc({
							method: "mu_car_care.api.make_sales_order_from_reception",
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

			// Add workflow action buttons
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

function setup_diagram_background(frm) {
	if (!frm.fields_dict || !frm.fields_dict.inspection_diagram) return;
	setTimeout(function () {
		let $wrapper = frm.fields_dict.inspection_diagram.$wrapper;
		if ($wrapper && $wrapper.length) {
			let $targets = $wrapper.find(".signature-field, .signature-box, .signature-display, canvas");
			if ($targets.length) {
				$targets.css({
					"background-image": "url('/assets/mu_car_care/images/car_inspection_diagram.png')",
					"background-size": "contain",
					"background-repeat": "no-repeat",
					"background-position": "center center",
					"min-height": "220px",
					"background-color": "#ffffff",
				});
			}
		}
	}, 250);
}
