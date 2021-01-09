# Copyright (c) 2013, trava and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from frappe.utils.nestedset import get_descendants_of

def execute(filters=None):
	filters = frappe._dict(filters or {})

	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	return [
		{
			"label": _("Brand"),
			"fieldtype": "Link",
			"fieldname": "brand",
			"options": "Brand",
			"width": 100
		},
		{
			"label": _("Subject"),
			"fieldtype": "Data",
			"fieldname": "subject",
			"width": 100
		},
		{
			"label": _("Collection"),
			"fieldtype": "Data",
			"fieldname": "collection",
			"width": 100
		},
		{
			"label": _("Suppliers article"),
			"fieldtype": "Data",
			"fieldname": "supplier_article",
			"width": 100
		},
		{
			"label": _("Nomenclature (Code 1C)"),
			"fieldtype": "Data",
			"fieldname": "nomenclature",
			"width": 100
		},
		{
			"label": _("Last barcode"),
			"fieldtype": "Data",
			"fieldname": "last_barcode",
			"width": 120
		},
		{
			"label": _("Number of days on the site"),
			"fieldtype": "Int",
			"fieldname": "number_days_site",
			"width": 100
		},
		{
			"label": _("Unmarketable"),
			"fieldtype": "Data",
			"fieldname": "unmarketable",
			"width": 100
		},
		{
			"label": _("Date of appearance of the illiquid"),
			"fieldtype": "Date",
			"fieldname": "date_unmarketable",
			"width": 100
		},
		{
			"label": _("Turnover"),
			"fieldtype": "Data",
			"fieldname": "turnover",
			"width": 100
		},
		{
			"label": _("The remainder of the goods (units)"),
			"fieldtype": "Int",
			"fieldname": "remainder_goods",
			"width": 100
		},
		{
			"label": _("Current retail price(before discount)"),
			"options": "Currency",
			"fieldname": "current_retail_price",
			"width": 100
		},
		{
			"label": _("New retail price (before discount)"),
			"options": "Currency",
			"fieldname": "new_retail_price",
			"width": 100
		},
		{
			"label": _("Current discount on the site,%"),
			"fieldtype": "Int",
			"fieldname": "current_discount_site",
			"width": 100
		},
		{
			"label": _("Recommended discount,%"),
			"fieldtype": "Int",
			"fieldname": "recommended_discount",
			"width": 100
		},
		{
			"label": _("The agreed discount,%"),
			"fieldtype": "Int",
			"fieldname": "agreed_discount",
			"width": 100
		},
		{
			"label": _("Current promo code discount,%"),
			"fieldtype": "Int",
			"fieldname": "current_promo_code_discount",
			"width": 100
		},
		{
			"label": _("New promo code discount,%"),
			"fieldtype": "Int",
			"fieldname": "new_promo_code_discount",
			"width": 100
		},
		{
			"label": _("Current price with discounts"),
			"options": "Currency",
			"fieldname": "current_price_discounts",
			"width": 100
		},
		{
			"label": _("Current price with discounts and promo codes"),
			"options": "Currency",
			"fieldname": "current_price_disc_promo_code",
			"width": 100
		},
		{
			"label": _("New price with discounts"),
			"options": "Currency",
			"fieldname": "new_price_discounts",
			"width": 100
		},
		{
			"label": _("New price with discounts and promo codes"),
			"options": "Currency",
			"fieldname": "new_price_disc_promo_code",
			"width": 100
		},
		{
			"label": _("Cost"),
			"options": "Currency",
			"fieldname": "standard_price",
			"width": 100
		},
		{
			"label": _("Current net profit"),
			"options": "Currency",
			"fieldname": "current_net_profit",
			"width": 100
		},
		{
			"label": _("New net profit"),
			"options": "Currency",
			"fieldname": "new_net_profit",
			"width": 100
		},
		{
			"label": _("Number of sales in the last month"),
			"fieldtype": "Int",
			"fieldname": "number_of_sales",
			"width": 100
		},
		{
			"label": _("Remains"),
			"fieldtype": "Int",
			"fieldname": "remains",
			"width": 100
		}
	]

def get_data(filters):

	data = []

	sales_order_records = get_sales_order_details(filters)

	for record in sales_order_records:
		remainder_qty = record.qty - record.car_qty - record.dn_qty
		if filters.didnt_report_back == 'Greater than zero':
			if remainder_qty == 0:
				continue
		
		if filters.didnt_report_back == 'Zero':
			if remainder_qty != 0:
				continue

		row = {
			"customer": record.customer,
			"item_name": record.item_name,
			"item_code": record.item_code,
			"stock_uom": record.uom,
			"handed_qty": record.qty,
			"sales_qty": record.car_qty,
			"sales_amount": record.amount_principal,
			"return_qty": record.dn_qty,
			"remainder_qty": remainder_qty
		}
		data.append(row)

	return data

def get_conditions_sle(filters):
	conditions = ''
	if filters.get("warehouse"):
		conditions += "AND sle.warehouse = %s" %frappe.db.escape(filters.warehouse)

	if filters.get("company"):
		conditions += "AND sle.company = %s" %frappe.db.escape(filters.company)

	return conditions

def get_conditions_wb_sales(filters):
	conditions = ''
	if filters.get('from_date_sales'):
		conditions += "AND wb_sales.date >= '%s'" %filters.from_date_sales

	if filters.get('to_date_sales'):
		conditions += "AND wb_sales.date <= '%s'" %filters.to_date_sales

	return conditions

def get_conditions_wbp(filters):
	conditions = ''
	if filters.get('item_group'):
		conditions += "AND dn_item.item_group = %s" %frappe.db.escape(filters.item_group)

	if filters.get('on_date'):
		conditions += "AND dn.posting_date <= '%s'" %filters.on_date

	if filters.get('agreement'):
		conditions += "AND dn.agreement = '%s'" %frappe.db.escape(filters.agreement)

	if filters.get("item_code"):
		conditions += "AND dn_item.item_code = %s" %frappe.db.escape(filters.item_code)

	if filters.get("company"):
		conditions += "AND dn.company = %s" %frappe.db.escape(filters.company)

	return conditions

def get_sales_order_details(filters):
	conditions_sle = get_conditions_sle(filters)
	conditions_wb_sales = get_conditions_wb_sales(filters)
	conditions_wbp = get_conditions_wbp(filters)

	return frappe.db.sql("""
		SELECT
			wbp.brand, wbp.subject, wbp.collection, wbp.supplier_article, 
			wbp.nomenclature, wbp.last_barcode, wbp.number_days_site,
			wbp.unmarketable, wbp.date_unmarketable, wbp.turnover,
			wbp.remainder_goods, wbp.current_retail_price, wbp.new_retail_price,
			wbp.current_discount_site, wbp.recommended_discount,
			wbp.agreed_discount, wbp.current_promo_code_discount,
			wbp.new_promo_code_discount,
			IFNULL((SELECT sle.valuation_rate
				FROM `tabStock Ledger Entry` sle
				WHERE sle.item_code = (select parent from `tabItem Barcode` where barcode = wbp.last_barcode)
				AND sle.creation = (SELECT max(creation) FROM `tabStock Ledger Entry` sle 
				WHERE sle.item_code = (select parent from `tabItem Barcode` where barcode = wbp.last_barcode))
				AND sle.modified = (SELECT max(modified) FROM `tabStock Ledger Entry` sle 
				WHERE sle.item_code = (select parent from `tabItem Barcode` where barcode = wbp.last_barcode)) {0}), 0) valuation_rate,
			IFNULL((SELECT SUM(wb_sales.quantity)
                FROM `tabWB Sales` wb_sales
                WHERE wb_sales.supplier_article = wbp.supplier_article {1}), 0) wb_sales_qty,
            IFNULL((SELECT SUM(wb_stocks.quantity)
                FROM `tabWB Stocks` wb_stocks
                WHERE wb_stocks.supplier_article = wbp.supplier_article), 0) wb_stocks_qty
		FROM
			`tabWB Price` wbp
		WHERE
			so.docstatus = 1 AND so.agreement_type = 'Commission'
			AND so.docstatus = 1 {0}
		GROUP BY
			so_item.item_code
	""".format(conditions_sle, conditions_wb_sales, conditions_wbp), as_dict=1)