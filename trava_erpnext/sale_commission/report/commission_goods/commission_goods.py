# Copyright (c) 2013, trava and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from frappe.utils.nestedset import get_descendants_of

def execute(filters=None):
	filters = frappe._dict(filters or {})

	columns, data = [], []
	data = get_data(filters)
	return columns, data

def get_data(filters):

	data = []

	company_list = get_descendants_of("Company", filters.get("company"))
	company_list.append(filters.get("company"))

	customer_details = get_customer_details()
	sales_order_records = get_sales_order_details(company_list, filters)

	for record in sales_order_records:
		customer_record = customer_details.get(record.customer)
		row = {
			"item_code": record.item_code,
			"item_name": record.item_name,
			"item_group": record.item_group,
			"description": record.description,
			"quantity": record.qty,
			"uom": record.uom,
			"rate": record.base_rate,
			"amount": record.base_amount,
			"sales_order": record.name,
			"transaction_date": record.transaction_date,
			"customer": record.customer,
			"customer_name": customer_record.customer_name,
			"customer_group": customer_record.customer_group,
			"territory": record.territory,
			"project": record.project,
			"delivered_quantity": flt(record.delivered_qty),
			"billed_amount": flt(record.billed_amt),
			"company": record.company
		}
		data.append(row)

	return data

def get_conditions(filters):
	conditions = ''
	if filters.get('item_group'):
		conditions += "AND so_item.item_group = %s" %frappe.db.escape(filters.item_group)

	if filters.get('from_date'):
		conditions += "AND so.transaction_date >= '%s'" %filters.from_date

	if filters.get('to_date'):
		conditions += "AND so.transaction_date <= '%s'" %filters.to_date

	if filters.get("item_code"):
		conditions += "AND so_item.item_code = %s" %frappe.db.escape(filters.item_code)

	if filters.get("customer"):
		conditions += "AND so.customer = %s" %frappe.db.escape(filters.customer)

	return conditions

def get_customer_details():
	details = frappe.get_all('Customer',
		fields=['name', 'customer_name', "customer_group"])
	customer_details = {}
	for d in details:
		customer_details.setdefault(d.name, frappe._dict({
			"customer_name": d.customer_name,
			"customer_group": d.customer_group
		}))
	return customer_details

def get_sales_order_details(company_list, filters):
	conditions = get_conditions(filters)

	return frappe.db.sql("""
		SELECT
			so_item.item_code, so_item.item_name, so_item.item_group,
			so_item.description, SUM(so_item.qty) qty, so_item.uom,
			so_item.base_rate, so_item.base_amount, so.name,
			so.transaction_date, so.customer, so.territory,
			so.project, so_item.delivered_qty,
			so_item.billed_amt, so.company,
			(SELECT SUM(car_item.qty)
                FROM `tabCommission Agent Report` car
                LEFT JOIN `tabCommission Agent Report Item` car_item 
                ON car.name = car_item.parent
                WHERE car_item.item_code = so_item.item_code) car,
             (SELECT SUM(dn_item.qty)
                FROM `tabDelivery Note` dn
                LEFT JOIN `tabDelivery Note Item` dn_item 
                ON dn.name = dn_item.parent
                WHERE dn_item.item_code = so_item.item_code AND
                dn.is_return = 1) dn
		FROM
			`tabSales Order` so 
			JOIN `tabSales Order Item` so_item
			ON so.name = so_item.parent
		GROUP BY
			so_item.item_code
		WHERE
			so.company in ({0})
			AND so.docstatus = 1 {1}
	""".format(','.join(["%s"] * len(company_list)), conditions), tuple(company_list), as_dict=1)