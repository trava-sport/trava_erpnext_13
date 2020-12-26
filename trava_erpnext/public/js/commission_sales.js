{% include 'erpnext/selling/sales_common.js' %};


frappe.provide("trava_erpnext.selling.");
trava_erpnext.selling.SellingCommission = erpnext.selling.SellingController.extend({
	customer: function() {
		this.frm.doc.agreement = '';
		this._super();
		var me = this;
		this.frm.set_query('agreement', function() {
			return {
				filters: {
					customer: me.frm.doc.customer
				}
			};
		});
	},

	agreement: function() {
		var me = this;
		if (this.frm.doc.agreement) {
			frappe.call({
				"method": "frappe.client.get_value",
				"args": {
					"doctype": "Agreement",
					"name": this.frm.doc.agreement,
					"fieldname":'agreement_type'
				},
				"callback": function(response) {
					me.frm.doc.agreement_type = response.message.agreement_type
					console.log(response.message.agreement_type);
				}
			});
		}
	},

    change_grid_labels: function(company_currency) {
		this._super(company_currency);

		// toggle columns
		var item_grid = this.frm.fields_dict["items"].grid;
		$.each(["base_award"], function(i, fname) {
			if(frappe.meta.get_docfield(item_grid.doctype, fname))
				item_grid.set_column_disp(fname, me.frm.doc.currency != company_currency);
		});
	},

	change_form_labels: function(company_currency) {
		this._super(company_currency);

		// toggle fields
		this.frm.toggle_display(["base_commission_agents_remuneration", "base_amount_principal"],
		this.frm.doc.currency != company_currency);
	},

	award: function(doc, cdt, cdn) {
		$.each(this.frm.doc["items"] || [], function(i, item) {
			frappe.model.round_floats_in(item);
			item.base_award = flt(item.award * item.conversion_rate)
		});
		this.calculate_commission_agent();
		this.calculate_taxes_and_totals();
	},

	calculate_totals: function() {
		this.calculate_commission_agent();
		// Changing sequence can cause rounding_adjustmentng issue and on-screen discrepency
		var me = this;
		var tax_count = this.frm.doc["taxes"] ? this.frm.doc["taxes"].length : 0;
		this.frm.doc.grand_total = flt(tax_count
			? this.frm.doc["taxes"][tax_count - 1].total + flt(this.frm.doc.rounding_adjustment) - this.frm.doc.commission_agents_remuneration
			: this.frm.doc.net_total - this.frm.doc.commission_agents_remuneration);

		if(in_list(["Quotation", "Sales Order", "Delivery Note", "Sales Invoice", "POS Invoice"], this.frm.doc.doctype)) {
			this.frm.doc.base_grand_total = (this.frm.doc.total_taxes_and_charges) ?
				flt(this.frm.doc.grand_total * this.frm.doc.conversion_rate) : this.frm.doc.base_net_total;
		} else {
			// other charges added/deducted
			this.frm.doc.taxes_and_charges_added = this.frm.doc.taxes_and_charges_deducted = 0.0;
			if(tax_count) {
				$.each(this.frm.doc["taxes"] || [], function(i, tax) {
					if (in_list(["Valuation and Total", "Total"], tax.category)) {
						if(tax.add_deduct_tax == "Add") {
							me.frm.doc.taxes_and_charges_added += flt(tax.tax_amount_after_discount_amount);
						} else {
							me.frm.doc.taxes_and_charges_deducted += flt(tax.tax_amount_after_discount_amount);
						}
					}
				});

				frappe.model.round_floats_in(this.frm.doc,
					["taxes_and_charges_added", "taxes_and_charges_deducted"]);
			}

			this.frm.doc.base_grand_total = flt((this.frm.doc.taxes_and_charges_added || this.frm.doc.taxes_and_charges_deducted) ?
				flt(this.frm.doc.grand_total * this.frm.doc.conversion_rate) : this.frm.doc.base_net_total);

			this.set_in_company_currency(this.frm.doc,
				["taxes_and_charges_added", "taxes_and_charges_deducted"]);
		}

		this.frm.doc.total_taxes_and_charges = flt(this.frm.doc.grand_total - this.frm.doc.net_total
			- flt(this.frm.doc.rounding_adjustment), precision("total_taxes_and_charges"));

		this.set_in_company_currency(this.frm.doc, ["total_taxes_and_charges", "rounding_adjustment"]);

		// Round grand total as per precision
		frappe.model.round_floats_in(this.frm.doc, ["grand_total", "base_grand_total"]);

		// rounded totals
		this.set_rounded_total();
		if(in_list(["Commission Agent Report"], this.frm.doc.doctype)){
			this.calculate_amount_principal();
		}
	},

	calculate_commission_agent: function() {
		var me = this;

		this.frm.doc.commission_agents_remuneration = this.frm.doc.base_commission_agents_remuneration = 0.0;

		$.each(this.frm.doc["items"] || [], function(i, item) {
			me.frm.doc.commission_agents_remuneration += item.award;
			me.frm.doc.base_commission_agents_remuneration += item.base_award;
			});

		frappe.model.round_floats_in(this.frm.doc, ["commission_agents_remuneration", "base_commission_agents_remuneration"]);
		this.frm.refresh_fields();
	},

	calculate_amount_principal: function() {
		this.frm.doc.amount_principal = flt(this.frm.doc.grand_total);
		this.frm.doc.base_amount_principal = flt(this.frm.doc.base_grand_total);

		this.frm.refresh_fields();
	},
});