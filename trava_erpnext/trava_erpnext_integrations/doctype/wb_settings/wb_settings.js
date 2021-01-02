// Copyright (c) 2020, trava and contributors
// For license information, please see license.txt

frappe.ui.form.on('WB Settings', {
	// refresh: function(frm) {

	// }
	refresh: function(frm) {
		var me = this;
		frm.add_custom_button(__('Отчет склад'), function() {
			console.log("rembo")
			frm.call({
				method: "trava_erpnext.trava_erpnext_integrations.doctype.wb_settings.wb_report_methods.get_report",
				args: {
					//"dateFrom": frappe.datetime.get_today(),
					"dateFrom": '2020-12-01',
					"dateTo": '2020-12-30',
					"reportType": 'reportDetailByPeriod',
					"doc": 'WB Sales by Sales'
				}
			});
		});
		frm.add_custom_button(__('Отчет склад 2'), function() {
			console.log("rembo")
			frm.call({
				method: "trava_erpnext.trava_erpnext_integrations.doctype.wb_settings.wb_settings.schedule_get_report_stocks"
			});
		});
	}
});

/* var make_sales_invoice = function(frm) {
	console.log("rembo")
	frappe.model.open_mapped_doc({
		method: "trava_erpnext.trava_erpnext_integrations.doctype.wb_settings.wb_report_methods.get_report_stocks",
		frm: frm
	})
} */
