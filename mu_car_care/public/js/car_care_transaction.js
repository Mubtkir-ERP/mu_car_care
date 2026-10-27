// -*- coding: utf-8 -*-
// Copyright (c) 2026, Mubtkir and contributors
// For license information, please see license.txt

frappe.provide("mu_car_care");

mu_car_care.setup_transaction = function (frm) {
	// Add Quick Action button whenever maintenance schedule is active
	if (frm.doc.custom_has_maintenance_schedule && !frm.is_new()) {
		const btn = frm.add_custom_button(
			__("زيارة صيانة"),
			function () {
				mu_car_care.open_maintenance_dialog(frm);
			}
		);
		btn.addClass("btn-primary btn-sm");
		btn.css({
			"padding": "3px 8px",
			"font-size": "12px",
			"white-space": "nowrap",
		});
	}
};

mu_car_care.generate_schedule = function (frm) {
	const start_date =
		frm.doc.custom_maintenance_start_date ||
		frm.doc.posting_date ||
		frm.doc.transaction_date ||
		frappe.datetime.get_today();

	const duration_years = cint(frm.doc.custom_maintenance_duration_years) || 1;
	const method = frm.doc.custom_distribution_method || "Annual";

	frappe.call({
		method: "mu_car_care.api.calculate_maintenance_schedule",
		args: {
			start_date: start_date,
			duration_years: duration_years,
			distribution_method: method,
		},
		freeze: true,
		freeze_message: __("Generating maintenance schedule..."),
		callback: function (r) {
			if (r.message && Array.isArray(r.message)) {
				frm.clear_table("custom_maintenance_schedule");
				r.message.forEach(function (item) {
					const row = frm.add_child("custom_maintenance_schedule");
					row.visit_date = item.visit_date;
					row.visit_status = item.visit_status;
					row.notes = item.notes;
				});
				frm.refresh_field("custom_maintenance_schedule");
				frappe.show_alert({
					message: __("Generated {0} maintenance visits.").format(r.message.length),
					indicator: "green",
				});
			} else {
				frappe.msgprint({
					title: __("Maintenance Schedule"),
					message: __("No visits were generated. Please check the duration and start date."),
					indicator: "orange",
				});
			}
		},
	});
};

mu_car_care.open_maintenance_dialog = function (frm) {
	const schedule = frm.doc.custom_maintenance_schedule || [];
	const pending_visits = schedule.filter(function (row) {
		return row.visit_status === "Scheduled";
	});

	if (pending_visits.length === 0) {
		frappe.msgprint({
			title: __("زيارة صيانة"),
			message: __("All scheduled maintenance visits have been completed or none are scheduled."),
			indicator: "blue",
		});
		return;
	}

	// Format options as clean strings compatible with Frappe Dialog Select control
	const visit_options = pending_visits.map(function (row) {
		return `${row.idx}: ${row.visit_date} - ${row.notes || __("Scheduled")}`;
	});

	const dialog = new frappe.ui.Dialog({
		title: __("زيارة صيانة"),
		size: "small",
		fields: [
			{
				fieldtype: "Select",
				fieldname: "visit_selection",
				label: __("Select Due Visit"),
				options: visit_options,
				default: visit_options[0],
				reqd: 1,
			},
			{
				fieldtype: "Date",
				fieldname: "actual_visit_date",
				label: __("Actual Visit Date"),
				default: frappe.datetime.get_today(),
				reqd: 1,
			},
			{
				fieldtype: "Small Text",
				fieldname: "notes",
				label: __("Notes"),
			},
		],
		primary_action_label: __("تأكيد إنجاز الزيارة"),
		primary_action: function (values) {
			const selected_str = values.visit_selection || "";
			const row_idx = cint(selected_str.split(":")[0]);

			if (!row_idx) {
				frappe.msgprint(__("Please select a valid visit from the list."));
				return;
			}

			frappe.call({
				method: "mu_car_care.api.record_maintenance_visit",
				args: {
					doctype: frm.doctype,
					docname: frm.docname,
					row_idx: row_idx,
					actual_visit_date: values.actual_visit_date,
					notes: values.notes,
				},
				freeze: true,
				freeze_message: __("Updating maintenance record..."),
				callback: function (r) {
					if (r.message && r.message.success) {
						dialog.hide();
						frm.reload_doc();
						frappe.show_alert({
							message: r.message.message,
							indicator: "green",
						});
					}
				},
			});
		},
	});

	dialog.$wrapper.find(".modal-dialog").css({
		"max-width": "420px",
		"margin": "1.75rem auto",
	});

	dialog.show();
};

// Form event handlers
const transaction_events = {
	refresh: function (frm) {
		mu_car_care.setup_transaction(frm);

		// Ensure schedule and warranty sections are collapsible
		frm.set_df_property("custom_schedule_visits_section", "collapsible", 1);
		frm.set_df_property("custom_warranty_section", "collapsible", 1);

		// Automatically add default first row in warranty table if empty on new doc
		if (frm.is_new() && (!frm.doc.custom_warranty_details || frm.doc.custom_warranty_details.length === 0)) {
			const row = frm.add_child("custom_warranty_details");
			const start_date =
				frm.doc.posting_date || frm.doc.transaction_date || frappe.datetime.get_today();
			row.start_date = start_date;
			row.warranty_period = 1;
			mu_car_care.calculate_warranty_end_date(frm, row.doctype, row.name);
			frm.refresh_field("custom_warranty_details");
		}

		// Center ONLY column headers (names) for Warranty and Maintenance tables
		if (!$("#car-care-center-grid-style").length) {
			$("<style id='car-care-center-grid-style'>\
				[data-fieldname='custom_warranty_details'] .grid-heading-row .grid-static-col, \
				[data-fieldname='custom_warranty_details'] .grid-heading-row .static-area, \
				[data-fieldname='custom_warranty_details'] .grid-heading-row th, \
				[data-fieldname='custom_maintenance_schedule'] .grid-heading-row .grid-static-col, \
				[data-fieldname='custom_maintenance_schedule'] .grid-heading-row .static-area, \
				[data-fieldname='custom_maintenance_schedule'] .grid-heading-row th { \
					text-align: center !important; \
					justify-content: center !important; \
				} \
				[data-fieldname='custom_warranty_details'] .grid-heading-row .static-area, \
				[data-fieldname='custom_maintenance_schedule'] .grid-heading-row .static-area { \
					width: 100% !important; \
					text-align: center !important; \
				} \
				.form-column:has([data-fieldname='custom_maintenance_schedule']) { \
					flex: 0 0 100% !important; \
					max-width: 100% !important; \
					width: 100% !important; \
				} \
			</style>").appendTo("head");
		}

		// Double-bind the button to guarantee click response across all Frappe versions
		if (frm.fields_dict && frm.fields_dict.custom_generate_schedule_btn) {
			const btn = frm.fields_dict.custom_generate_schedule_btn;
			if (btn.$input) {
				btn.$input.off("click").on("click", function () {
					mu_car_care.generate_schedule(frm);
				});
			}
			if (btn.$wrapper) {
				btn.$wrapper.find("button").off("click").on("click", function () {
					mu_car_care.generate_schedule(frm);
				});
			}
		}
	},

	custom_has_maintenance_schedule: function (frm) {
		if (frm.doc.custom_has_maintenance_schedule) {
			if (!frm.doc.custom_maintenance_start_date) {
				frm.set_value(
					"custom_maintenance_start_date",
					frm.doc.posting_date || frm.doc.transaction_date || frappe.datetime.get_today()
				);
			}
			if (!frm.doc.custom_maintenance_duration_years) {
				frm.set_value("custom_maintenance_duration_years", 1);
			}
			if (!frm.doc.custom_distribution_method) {
				frm.set_value("custom_distribution_method", "Annual");
			}
		}
	},

	custom_generate_schedule_btn: function (frm) {
		mu_car_care.generate_schedule(frm);
	},
};

frappe.ui.form.on("Sales Invoice", transaction_events);
frappe.ui.form.on("Quotation", transaction_events);
frappe.ui.form.on("Sales Order", transaction_events);

// Child table handlers for Vehicle Warranty Item
frappe.ui.form.on("Vehicle Warranty Item", {
	custom_warranty_details_add: function (frm, cdt, cdn) {
		const start_date =
			frm.doc.posting_date || frm.doc.transaction_date || frappe.datetime.get_today();
		frappe.model.set_value(cdt, cdn, "start_date", start_date);
		frappe.model.set_value(cdt, cdn, "warranty_period", 1);
		mu_car_care.calculate_warranty_end_date(frm, cdt, cdn);
	},
	service_type: function (frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.service_type) {
			frappe.call({
				method: "mu_car_care.api.get_item_warranty_details",
				args: {
					item_code: row.service_type,
				},
				callback: function (r) {
					if (r && r.message) {
						if (r.message.warranty_period) {
							frappe.model.set_value(cdt, cdn, "warranty_period", r.message.warranty_period);
						}
						if (r.message.terms) {
							frappe.model.set_value(cdt, cdn, "terms", r.message.terms);
						}
						mu_car_care.calculate_warranty_end_date(frm, cdt, cdn);
					}
				},
			});
		}
	},
	warranty_period: function (frm, cdt, cdn) {
		mu_car_care.calculate_warranty_end_date(frm, cdt, cdn);
	},
	start_date: function (frm, cdt, cdn) {
		mu_car_care.calculate_warranty_end_date(frm, cdt, cdn);
	},
});

mu_car_care.calculate_warranty_end_date = function (frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	const start_date =
		row.start_date || frm.doc.posting_date || frm.doc.transaction_date || frappe.datetime.get_today();
	const years = cint(row.warranty_period);

	if (start_date && years > 0) {
		// Calculate end date: start_date + (years * 12 months) - 1 day (e.g. 2025-04-24 to 2030-04-23)
		let end_date = frappe.datetime.add_months(start_date, years * 12);
		end_date = frappe.datetime.add_days(end_date, -1);
		frappe.model.set_value(cdt, cdn, "end_date", end_date);
		if (!row.start_date) {
			frappe.model.set_value(cdt, cdn, "start_date", start_date);
		}
	}
};
