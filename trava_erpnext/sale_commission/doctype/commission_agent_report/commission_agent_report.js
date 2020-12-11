// Copyright (c) 2020, trava and contributors
// For license information, please see license.txt
frappe.provide("trava_erpnext.selling");

frappe.ui.form.on('Commission Agent Report', {
	setup: function(frm) {
		frm.custom_make_buttons = {
			'Delivery Note': 'Delivery Note',
			'Pick List': 'Pick List',
			'Sales Invoice': 'Invoice',
			'Material Request': 'Material Request',
			'Purchase Order': 'Purchase Order',
			'Project': 'Project',
			'Payment Entry': "Payment",
			'Work Order': "Work Order"
		}
		frm.add_fetch('customer', 'tax_id', 'tax_id');

		frm.set_query('company_address', function(doc) {
			if(!doc.company) {
				frappe.throw(__('Please set Company'));
			}

			return {
				query: 'frappe.contacts.doctype.address.address.address_query',
				filters: {
					link_doctype: 'Company',
					link_name: doc.company
				}
			};
		})

		frm.set_query("bom_no", "items", function(doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			return {
				filters: {
					"item": row.item_code
				}
			}
		});
	},
	refresh: function(frm) {
		if(frm.doc.docstatus === 1 && frm.doc.status !== 'Closed'
			&& flt(frm.doc.per_billed, 6) < 100) {
			frm.add_custom_button(__('Update Items'), () => {
				erpnext.utils.update_child_items({
					frm: frm,
					child_docname: "items",
					child_doctype: "Commission Agent Report Detail",
					cannot_add_row: false,
				})
			});
		}
	},
	onload: function(frm) {
		if (!frm.doc.creation_date){
			frm.set_value('creation_date', frappe.datetime.get_today())
		}

		frm.set_query('project', function(doc, cdt, cdn) {
			return {
				query: "erpnext.controllers.queries.get_project_name",
				filters: {
					'customer': doc.customer
				}
			}
		});
	}
});

trava_erpnext.selling.SalesCommissionController = erpnext.TransactionController.extend({
	onload: function(doc, dt, dn) {
		this._super();
	},
	
	refresh: function(doc, dt, dn) {
		var me = this;
		this._super();
	},
	
	price_list_rate: function(doc, cdt, cdn) {
		var item = frappe.get_doc(cdt, cdn);
		frappe.model.round_floats_in(item, ["price_list_rate", "discount_percentage"]);

		// check if child doctype is Sales Order Item/Qutation Item and calculate the rate
		if(in_list(["Commission Agent Report Item", "Sales Order Item"]), cdt)
			this.apply_pricing_rule_on_item(item);
		else
			item.rate = flt(item.price_list_rate * (1 - item.discount_percentage / 100.0),
				precision("rate", item));

		this.calculate_taxes_and_totals();
	},
});
$.extend(cur_frm.cscript, new trava_erpnext.selling.SalesCommissionController({frm: cur_frm}));