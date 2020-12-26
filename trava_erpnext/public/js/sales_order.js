{% include 'trava_erpnext/public/js/commission_sales.js' %};

frappe.provide("erpnext.selling");

erpnext.selling.SalesOrderController = trava_erpnext.selling.SellingCommission.extend({
	
});

$.extend(cur_frm.cscript, new erpnext.selling.SalesOrderController({frm: cur_frm}));