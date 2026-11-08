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
		// Create and workflow buttons only available once the document is submitted (تسجيل / docstatus === 1)
		if (frm.doc.docstatus === 1) {
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

		// Ensure notes boxes have equal height
		frm.trigger("set_notes_equal_height");

		// Ensure window film table is cleared if service is not enabled, or has a default row if active
		if (frm.doc.docstatus === 0) {
			if (!frm.doc.service_window_film && frm.doc.window_film_items && frm.doc.window_film_items.length > 0) {
				frm.clear_table("window_film_items");
				frm.refresh_field("window_film_items");
			} else if (frm.doc.service_window_film && (!frm.doc.window_film_items || frm.doc.window_film_items.length === 0)) {
				frm.add_child("window_film_items");
				frm.refresh_field("window_film_items");
			}
		}
	},

	validate: function (frm) {
		if (!frm.doc.service_window_film) {
			frm.clear_table("window_film_items");
			frm.refresh_field("window_film_items");
		} else if (frm.doc.window_film_items) {
			// Remove rows where all fields are blank
			const valid_rows = (frm.doc.window_film_items || []).filter(function (r) {
				return r.window_location || r.shade_degree || r.film_type || r.notes;
			});
			if (valid_rows.length !== frm.doc.window_film_items.length) {
				frm.doc.window_film_items = valid_rows;
				frm.refresh_field("window_film_items");
			}
		}
	},

	service_window_film: function (frm) {
		if (frm.doc.service_window_film) {
			if (!frm.doc.window_film_items || frm.doc.window_film_items.length === 0) {
				frm.add_child("window_film_items");
				frm.refresh_field("window_film_items");
			}
		} else {
			frm.clear_table("window_film_items");
			frm.refresh_field("window_film_items");
		}
	},

	set_notes_equal_height: function (frm) {
		const notes_fields = ["personal_belongings", "external_condition_notes", "notes"];
		notes_fields.forEach(function (f) {
			if (frm.fields_dict[f] && frm.fields_dict[f].$wrapper) {
				frm.fields_dict[f].$wrapper.find("textarea").css({
					"height": "95px",
					"min-height": "95px",
					"max-height": "95px",
					"resize": "none",
				});
			}
		});
	},

	customer: function (frm) {
		if (frm.doc.customer) {
			frappe.db.get_value("Customer", frm.doc.customer, ["customer_name", "mobile_no"], function (r) {
				if (r) {
					frm.set_value("customer_name", r.customer_name);
					frm.set_value("contact_mobile", r.mobile_no || "");
				}
			});
		} else {
			frm.set_value("customer_name", "");
			frm.set_value("contact_mobile", "");
		}
	},
});
