{% include 'trava_erpnext/public/js/selling/commission_sales/commission_sales.js' %};

frappe.provide("erpnext.accounts");

erpnext.accounts.SalesInvoiceController = trava_erpnext.selling.SellingCommission.extend({
	
});

$.extend(cur_frm.cscript, new erpnext.accounts.SalesInvoiceController({frm: cur_frm}));