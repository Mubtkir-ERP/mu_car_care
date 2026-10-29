// -*- coding: utf-8 -*-
// Copyright (c) 2026, Mubtkir and contributors
// For license information, please see license.txt

frappe.provide("mu_car_care");

mu_car_care.setup_transaction = function (frm) {
	// Add Quick Action button only when maintenance schedule is active and document is submitted/approved (docstatus === 1)
	if (frm.doc.custom_has_maintenance_schedule && frm.doc.docstatus === 1) {
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

mu_car_care.lock_registered_fields = function (frm) {
	// Only lock fields after registration / submission (docstatus === 1 or 2)
	// Draft documents (docstatus === 0) MUST remain completely editable
	const is_submitted = (frm.doc.docstatus === 1 || frm.doc.docstatus === 2);

	// 1. Hide legacy car fields and legacy section break
	const legacy_fields = [
		"custom_section_break_khlav",
		"custom_car_type",
		"custom_car_plate",
		"custom_car_model",
		"custom_car_color",
	];
	legacy_fields.forEach(function (f) {
		if (frm.fields_dict[f]) {
			frm.set_df_property(f, "hidden", 1);
		}
	});

	// 2. بعد التسجيل اظهار حقول معلومات السيارة للقراءة
	const vehicle_fields = [
		"custom_vehicle_make",
		"custom_vehicle_model",
		"custom_plate_number",
		"custom_vehicle_color",
		"custom_chassis_no",
	];
	vehicle_fields.forEach(function (f) {
		if (frm.fields_dict[f]) {
			frm.set_df_property(f, "read_only", is_submitted ? 1 : 0);
		}
	});

	// 3. عدم السماح بتحديث حقل تفعيل جدول الصيانة بعد التسجيل
	frm.set_df_property("custom_has_maintenance_schedule", "read_only", is_submitted ? 1 : 0);

	// 4. عدم السماح بتحديث حقول اعدادات الصيانة مثل تاريخ بداية الصيانة - والمدة وطريقة التوزيع
	const maintenance_setting_fields = [
		"custom_maintenance_start_date",
		"custom_maintenance_duration_years",
		"custom_distribution_method",
	];
	maintenance_setting_fields.forEach(function (f) {
		if (frm.fields_dict[f]) {
			frm.set_df_property(f, "read_only", is_submitted ? 1 : 0);
		}
	});

	if (frm.fields_dict.custom_generate_schedule_btn) {
		frm.set_df_property("custom_generate_schedule_btn", "read_only", is_submitted ? 1 : 0);
		frm.set_df_property("custom_generate_schedule_btn", "hidden", is_submitted ? 1 : 0);
	}

	// 5. عدم السماح بتحديث بيانات جدول الضمان كلها
	frm.set_df_property("custom_warranty_details", "read_only", is_submitted ? 1 : 0);
	if (frm.fields_dict.custom_warranty_details) {
		const grid = frm.fields_dict.custom_warranty_details.grid;
		if (grid) {
			// حذف عمود نوع الخدمة من جدول الضمان في الشاشة
			if (typeof grid.set_column_disp === "function") {
				grid.set_column_disp("service_type", false);
			}
			grid.cannot_add_rows = is_submitted;
			grid.only_sortable = is_submitted;
			if (is_submitted) {
				grid.wrapper.find(".grid-add-row").hide();
				grid.wrapper.find(".grid-remove-rows").hide();
				grid.wrapper.find(".grid-delete-row").hide();
				grid.wrapper.find(".grid-row-check").hide();
			} else {
				grid.wrapper.find(".grid-add-row").show();
				grid.wrapper.find(".grid-remove-rows").show();
				grid.wrapper.find(".grid-delete-row").show();
				grid.wrapper.find(".grid-row-check").show();
			}
			if (grid.docfields) {
				grid.docfields.forEach(function (df) {
					df.read_only = is_submitted ? 1 : 0;
					if (df.fieldname === "service_type") {
						df.in_list_view = 0;
						df.hidden = 1;
					}
				});
			}
		}
	}

	// Disable settings toolbar inputs if registered
	if (frm.fields_dict.custom_schedule_visits_section && frm.fields_dict.custom_schedule_visits_section.wrapper) {
		const $sec = frm.fields_dict.custom_schedule_visits_section.wrapper;
		if (is_submitted) {
			$sec.find(".car-care-settings-row input, .car-care-settings-row select, .car-care-settings-row button").prop("disabled", true);
			$sec.find(".car-care-settings-row button").hide();
		} else {
			$sec.find(".car-care-settings-row input, .car-care-settings-row select").prop("disabled", false);
			$sec.find(".car-care-settings-row button").show().prop("disabled", false);
		}
	}
};

mu_car_care.sync_warranty_from_items = function (frm) {
	if ((frm.doc.docstatus === 1 || frm.doc.docstatus === 2) || !frm.doc.items || frm.doc.items.length === 0) return;
	const current_warranty = frm.doc.custom_warranty_details || [];

	frm.doc.items.forEach(function (item, idx) {
		if (!item.item_code) return;
		let matching_row = current_warranty.find(function (w) {
			return w.service_type === item.item_code;
		});

		if (!matching_row) {
			const row = frm.add_child("custom_warranty_details");
			row.service_type = item.item_code;
			row.start_date =
				frm.doc.posting_date || frm.doc.transaction_date || frappe.datetime.get_today();
			row.warranty_period = 1;

			frappe.call({
				method: "mu_car_care.api.get_item_warranty_details",
				args: {
					item_code: item.item_code,
				},
				callback: function (r) {
					if (r && r.message) {
						if (r.message.warranty_period) {
							frappe.model.set_value(row.doctype, row.name, "warranty_period", r.message.warranty_period);
						}
						if (r.message.terms) {
							frappe.model.set_value(row.doctype, row.name, "terms", r.message.terms);
						}
						mu_car_care.calculate_warranty_end_date(frm, row.doctype, row.name);
						frm.refresh_field("custom_warranty_details");
					}
				},
			});
			mu_car_care.calculate_warranty_end_date(frm, row.doctype, row.name);
		}
	});
	frm.refresh_field("custom_warranty_details");
};

mu_car_care.generate_schedule = function (frm) {
	if (frm.doc.docstatus === 1 || frm.doc.docstatus === 2) {
		frappe.msgprint(__("لا يمكن تعديل جدول الصيانة بعد تسجيل المستند."));
		return;
	}

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
		return row.notes ? `${row.idx}: ${row.visit_date} - ${row.notes}` : `${row.idx}: ${row.visit_date}`;
	});

	const dialog = new frappe.ui.Dialog({
		title: __("زيارة صيانة"),
		fields: [
			{
				fieldtype: "Select",
				fieldname: "visit_selection",
				label: __("اختر موعد الزيارة"),
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

		// Ensure schedule and warranty sections are collapsible, and hide old config section
		frm.set_df_property("custom_schedule_visits_section", "collapsible", 1);
		frm.set_df_property("custom_warranty_section", "collapsible", 1);
		frm.set_df_property("custom_schedule_config_section", "hidden", 1);

		// Place maintenance settings toolbar directly above table inside custom_schedule_visits_section
		if (frm.fields_dict.custom_schedule_visits_section && frm.fields_dict.custom_maintenance_schedule) {
			const $sec = frm.fields_dict.custom_schedule_visits_section.wrapper;
			const $secBody = $sec ? $sec.find(".section-body") : null;
			const setting_fields = [
				"custom_maintenance_start_date",
				"custom_maintenance_duration_years",
				"custom_distribution_method",
				"custom_generate_schedule_btn",
			];

			if ($secBody && $secBody.length && !$sec.find(".car-care-settings-row").length) {
				const $settingsRow = $(
					"<div class='car-care-settings-row mx-0 mb-3 p-2' style='background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; display: flex; align-items: flex-end; gap: 12px; width: 100%;'></div>"
				);

				setting_fields.forEach(function (fname) {
					if (frm.fields_dict[fname] && frm.fields_dict[fname].$wrapper) {
						const $fw = frm.fields_dict[fname].$wrapper;
						$fw.css({ "flex": "1", "min-width": "140px", "margin": "0" });
						$settingsRow.append($fw);
					}
				});

				$secBody.prepend($settingsRow);
			}

			// Ensure maintenance table is full-width inside the section
			const $tableWrapper = frm.fields_dict.custom_maintenance_schedule.$wrapper;
			if ($secBody && $secBody.length && $tableWrapper && $tableWrapper.length && !$tableWrapper.parent().is($secBody)) {
				$tableWrapper.appendTo($secBody);
				$tableWrapper.css({ "width": "100%", "margin-top": "6px" });
			}
		}

		// Apply read-only locks after registration
		mu_car_care.lock_registered_fields(frm);

		// Auto sync warranty rows from items on new document
		if (frm.is_new()) {
			if (!frm.doc.custom_warranty_details || frm.doc.custom_warranty_details.length === 0) {
				if (frm.doc.items && frm.doc.items.length > 0) {
					mu_car_care.sync_warranty_from_items(frm);
				} else {
					const row = frm.add_child("custom_warranty_details");
					const start_date =
						frm.doc.posting_date || frm.doc.transaction_date || frappe.datetime.get_today();
					row.start_date = start_date;
					row.warranty_period = 1;
					mu_car_care.calculate_warranty_end_date(frm, row.doctype, row.name);
					frm.refresh_field("custom_warranty_details");
				}
			}
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
				/* Hide service_type column from warranty grid */ \
				[data-fieldname='custom_warranty_details'] [data-fieldname='service_type'] { \
					display: none !important; \
				} \
				/* Force cell values in RTL to align right, overriding Frappe numeric flip */ \
				[dir='rtl'] [data-fieldname='custom_warranty_details'] .grid-body .grid-static-col, \
				[dir='rtl'] [data-fieldname='custom_warranty_details'] .grid-body .static-area, \
				[dir='rtl'] [data-fieldname='custom_warranty_details'] .grid-body input, \
				[dir='rtl'] [data-fieldname='custom_warranty_details'] [data-fieldname='warranty_period'], \
				[dir='rtl'] [data-fieldname='custom_warranty_details'] [data-fieldname='warranty_period'] .static-area, \
				[dir='rtl'] [data-fieldname='custom_warranty_details'] [data-fieldname='warranty_period'] input, \
				[dir='rtl'] [data-fieldname='custom_maintenance_schedule'] .grid-body .grid-static-col, \
				[dir='rtl'] [data-fieldname='custom_maintenance_schedule'] .grid-body .static-area, \
				[dir='rtl'] [data-fieldname='custom_maintenance_schedule'] .grid-body input { \
					text-align: right !important; \
					direction: rtl !important; \
				} \
				.form-column:has([data-fieldname='custom_maintenance_schedule']) { \
					flex: 0 0 100% !important; \
					max-width: 100% !important; \
					width: 100% !important; \
				} \
			</style>").appendTo("head");
		}

		// Double-bind the button to guarantee click response across all Frappe versions
		if (frm.doc.docstatus === 0 && frm.fields_dict && frm.fields_dict.custom_generate_schedule_btn) {
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

	validate: function (frm) {
		// Populate service_type on warranty details from items if empty
		if (frm.doc.custom_warranty_details && frm.doc.items) {
			frm.doc.custom_warranty_details.forEach(function (w_row, idx) {
				if (!w_row.service_type && idx < frm.doc.items.length) {
					w_row.service_type = frm.doc.items[idx].item_code || frm.doc.items[idx].item_name;
				}
			});
		}
	},

	custom_has_maintenance_schedule: function (frm) {
		if (frm.doc.docstatus === 0 && frm.doc.custom_has_maintenance_schedule) {
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
		if (frm.doc.docstatus === 0) {
			mu_car_care.generate_schedule(frm);
		}
	},
};

frappe.ui.form.on("Sales Invoice", transaction_events);
frappe.ui.form.on("Quotation", transaction_events);
frappe.ui.form.on("Sales Order", transaction_events);

// Child table handlers for items to auto-sync warranty
const item_child_events = {
	item_code: function (frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row && row.item_code && frm.doc.docstatus === 0) {
			mu_car_care.sync_warranty_from_items(frm);
		}
	},
};

frappe.ui.form.on("Sales Invoice Item", item_child_events);
frappe.ui.form.on("Sales Order Item", item_child_events);
frappe.ui.form.on("Quotation Item", item_child_events);

// Child table handlers for Vehicle Warranty Item
frappe.ui.form.on("Vehicle Warranty Item", {
	custom_warranty_details_add: function (frm, cdt, cdn) {
		const start_date =
			frm.doc.posting_date || frm.doc.transaction_date || frappe.datetime.get_today();
		frappe.model.set_value(cdt, cdn, "start_date", start_date);
		frappe.model.set_value(cdt, cdn, "warranty_period", 1);

		// If items exist, assign service_type from corresponding item
		const row = locals[cdt][cdn];
		if (!row.service_type && frm.doc.items) {
			const idx = (frm.doc.custom_warranty_details || []).length - 1;
			if (idx >= 0 && idx < frm.doc.items.length) {
				const it = frm.doc.items[idx];
				if (it && it.item_code) {
					frappe.model.set_value(cdt, cdn, "service_type", it.item_code);
					frappe.call({
						method: "mu_car_care.api.get_item_warranty_details",
						args: { item_code: it.item_code },
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
			}
		}
		mu_car_care.calculate_warranty_end_date(frm, cdt, cdn);
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
		let end_date = frappe.datetime.add_months(start_date, years * 12);
		end_date = frappe.datetime.add_days(end_date, -1);
		frappe.model.set_value(cdt, cdn, "end_date", end_date);
		if (!row.start_date) {
			frappe.model.set_value(cdt, cdn, "start_date", start_date);
		}
	}
};
