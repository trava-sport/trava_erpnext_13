// Copyright (c) 2016, trava and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["WB Price"] = {
	"filters": [
		{
			"fieldname":"warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"get_query": function() {
				const company = frappe.query_report.get_filter_value('company');
				return {
					filters: { 'company': company }
				}
			}
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"brand",
			"label": __("Brand"),
			"fieldtype": "Link",
			"options": "Brand"
		},
		{
			"label": _("From the new discount"),
			"fieldtype": "Int",
			"fieldname": "from_new_discount",
			"width": 100
		},
		{
			"label": _("To the new discount"),
			"fieldtype": "Int",
			"fieldname": "to_new_discount",
			"width": 100
		},
		{
			"label": _("From the new promo code"),
			"fieldtype": "Int",
			"fieldname": "from_new_promo_code",
			"width": 70
		},
		{
			"label": _("To the new promo code"),
			"fieldtype": "Int",
			"fieldname": "to_new_promo_code",
			"width": 70
		},
		{
			"label": _("From the current price without discounts"),
			"fieldtype": "Float",
			"fieldname": "from_current_price",
			"width": 100
		},
		{
			"label": _("To the current price without discounts"),
			"fieldtype": "Float",
			"fieldname": "to_current_price",
			"width": 100
		},
		{
			"label": _("From the current price with discount"),
			"fieldtype": "Float",
			"fieldname": "from_current_price_discount",
			"width": 100
		},
		{
			"label": _("To the current price with discount"),
			"fieldtype": "Float",
			"fieldname": "to_current_price_discount",
			"width": 100
		},
		{
			"label": _("From the current price with discount and promo code"),
			"fieldtype": "Float",
			"fieldname": "from_current_price_discount_promo",
			"width": 100
		},
		{
			"label": _("To the current price with discount and promo code"),
			"fieldtype": "Float",
			"fieldname": "to_current_price_discount_promo",
			"width": 100
		},
		{
			"label": _("From the new price with discount"),
			"fieldtype": "Float",
			"fieldname": "from_new_price_discount",
			"width": 100
		},
		{
			"label": _("To the new price with discount"),
			"fieldtype": "Float",
			"fieldname": "to_new_price_discount",
			"width": 100
		},
		{
			"label": _("From the new price with discount and promo code"),
			"fieldtype": "Float",
			"fieldname": "from_new_price_discount_promo",
			"width": 100
		},
		{
			"label": _("To the new price with discount and promo code"),
			"fieldtype": "Float",
			"fieldname": "to_new_price_discount_promo",
			"width": 100
		},
		{
			"label": _("From current net profit"),
			"fieldtype": "Float",
			"fieldname": "from_current_net_profit",
			"width": 100
		},
		{
			"label": _("To current net profit"),
			"fieldtype": "Float",
			"fieldname": "to_current_net_profit",
			"width": 100
		},
		{
			"label": _("From new net profit"),
			"fieldtype": "Float",
			"fieldname": "from_new_net_profit",
			"width": 100
		},
		{
			"label": _("To new net profit"),
			"fieldtype": "Float",
			"fieldname": "to_new_net_profit",
			"width": 100
		},
		{
			"fieldname":"from_date_sales",
			"label": __("From the date of sales"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname":"to_date_sales",
			"label": __("To the date of sales"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"label": _("From sales"),
			"fieldtype": "Float",
			"fieldname": "from_sales",
			"width": 100
		},
		{
			"label": _("To sales"),
			"fieldtype": "Float",
			"fieldname": "to_sales",
			"width": 100
		},
		{
			"label": _("From the remnant"),
			"fieldtype": "Float",
			"fieldname": "from_remnant",
			"width": 100
		},
		{
			"label": _("To the remnant"),
			"fieldtype": "Float",
			"fieldname": "to_remnant",
			"width": 100
		},
	]
};
