# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, scrub
from frappe.utils import getdate, flt, add_to_date, add_days
from six import iteritems
from erpnext.accounts.utils import get_fiscal_year

def execute(filters=None):
	return Analytics(filters).run()

class Analytics(object):
	def __init__(self, filters=None):
		print('filters:', filters)
		self.filters = frappe._dict(filters or {})
		self.date_field = 'transaction_date' \
			if self.filters.doc_type in ['Sales Order', 'Purchase Order'] else 'posting_date'
		self.months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
		self.get_period_date_ranges()

	def run(self):
		print('RUN')
		self.get_columns()
		print(self)
		self.get_data()
		self.get_chart_data()

		# Skipping total row for tree-view reports
		skip_total_row = 0

		if self.filters.tree_type in ["Supplier Group", "Item Group", "Customer Group", "Territory"]:
			skip_total_row = 1

		return self.columns, self.data, None, self.chart, None, skip_total_row

	def get_columns(self):
		self.columns = [{
				"label": _(self.filters.tree_type),
				"options": self.filters.tree_type if self.filters.tree_type != "Order Type" else "",
				"fieldname": "entity",
				"fieldtype": "Link" if self.filters.tree_type != "Order Type" else "Data",
				"width": 140 if self.filters.tree_type != "Order Type" else 200
			}]
		if self.filters.tree_type in ["Customer", "Supplier", "Item"]:
			self.columns.append({
				"label": _(self.filters.tree_type + " Name"),
				"fieldname": "entity_name",
				"fieldtype": "Data",
				"width": 140
			})

		if self.filters.tree_type == "Item":
			self.columns.append({
				"label": _("UOM"),
				"fieldname": 'stock_uom',
				"fieldtype": "Link",
				"options": "UOM",
				"width": 100
			})

		for end_date in self.periodic_daterange:
			period = self.get_period(end_date[1])
			self.columns.append({
				"label": _(period),
				"fieldname": scrub(period),
				"fieldtype": "Float",
				"width": 120
			})

		self.columns.append({
			"label": _("Total"),
			"fieldname": "total",
			"fieldtype": "Float",
			"width": 120
		})

	def get_data(self):
		if self.filters.tree_type in ["Customer", "Supplier"]:
			self.get_sales_transactions_based_on_customers_or_suppliers()
			self.get_rows()

		elif self.filters.tree_type == 'Item':
			self.get_sales_transactions_based_on_items()
			self.get_rows()

		elif self.filters.tree_type in ["Customer Group", "Supplier Group", "Territory"]:
			self.get_sales_transactions_based_on_customer_or_territory_group()
			self.get_rows_by_group()

		elif self.filters.tree_type == 'Item Group':
			self.get_sales_transactions_based_on_item_group()
			self.get_rows_by_group()

		elif self.filters.tree_type == "Order Type":
			if self.filters.doc_type != "Sales Order":
				self.data = []
				return
			self.get_sales_transactions_based_on_order_type()
			self.get_rows_by_group()

		elif self.filters.tree_type == "Project":
			self.get_sales_transactions_based_on_project()
			self.get_rows()

	def get_sales_transactions_based_on_order_type(self):
		if self.filters["value_quantity"] == 'Value':
			value_field = "base_net_total"
		else:
			value_field = "total_qty"

		self.entries = frappe.db.sql(""" select s.order_type as entity, s.{value_field} as value_field, s.{date_field}
			from `tab{doctype}` s where s.docstatus = 1 and s.company = %s and s.{date_field} between %s and %s
			and ifnull(s.order_type, '') != '' order by s.order_type
		"""
		.format(date_field=self.date_field, value_field=value_field, doctype=self.filters.doc_type),
		(self.filters.company, self.filters.from_date, self.filters.to_date), as_dict=1)

		self.get_teams()

	def get_sales_transactions_based_on_customers_or_suppliers(self):
		if self.filters["value_quantity"] == 'Value':
			value_field = "base_net_total as value_field"
		else:
			value_field = "total_qty as value_field"

		if self.filters.tree_type == 'Customer':
			entity = "customer as entity"
			entity_name = "customer_name as entity_name"
		else:
			entity = "supplier as entity"
			entity_name = "supplier_name as entity_name"

		self.entries = frappe.get_all(self.filters.doc_type,
			fields=[entity, entity_name, value_field, self.date_field],
			filters={
				"docstatus": 1,
				"company": self.filters.company,
				self.date_field: ('between', [self.filters.from_date, self.filters.to_date])
			}
		)

		self.entity_names = {}
		for d in self.entries:
			self.entity_names.setdefault(d.entity, d.entity_name)

	def get_sales_transactions_based_on_items(self):

		conditions = ''
		if self.filters.brand:
			conditions += "and wb_sas.brand_name = %s" %frappe.db.escape(self.filters.brand)
		warehouse = "%s" %frappe.db.escape(self.filters.warehouse)
		company = "%s" %frappe.db.escape(self.filters.company)

		all_entries = []
		for date in self.periodic_daterange:
			from_date = "'%s'" %date[0]
			to_date = "'%s'" %date[1]

			entries_sales = frappe.db.sql("""
				select sum(wb_sas.retail_price_withdisc_rub) as sales_amount, sum(wb_sas.retail_commission) as amount_commission_wb,
				sum(wb_sas.for_pay) as supplier_remuneration, sum(wb_sas.quantity) total_qty
				from `tabWB Sales by Sales` wb_sas
				where wb_sas.supplier_oper_name = "Продажа" and wb_sas.sale_dt between {1} and {2} {0}
			"""
			.format(conditions, from_date, to_date), as_dict=1)

			entries_logistics = frappe.db.sql("""
				select sum(wb_sas.delivery_rub) as amount_logistics
				from `tabWB Sales by Sales` wb_sas
				where wb_sas.supplier_oper_name = "Логистика" and wb_sas.sale_dt between {1} and {2} {0}
			"""
			.format(conditions, from_date, to_date), as_dict=1)

			entries_purchases = frappe.db.sql("""
				select sum(IFNULL((select avg(sle.valuation_rate)
					from `tabStock Ledger Entry` sle
					where sle.item_code = (select parent from `tabItem Barcode` where barcode = wb_sas.barcode)
					and sle.creation between {2} and {3}
					and sle.modified between {2} and {3} 
					and sle.warehouse = {0} and sle.company = {1}), 0)) amount_purchases
				from `tabWB Sales by Sales` wb_sas
				where wb_sas.supplier_oper_name = "Продажа" and wb_sas.sale_dt between {2} and {3} {4}
			"""
			.format(warehouse, company, from_date, to_date, conditions), as_dict=1)

			city_name = {"Коледино": "koledino", "Подольск": "podolsk", "Пушкино": "pushkino", "Электросталь": "elektrostal", 
				"Домодедово": "domodedovo", "Краснодар": "krasnodar", "Екатеринбург": "yekaterinburg", "Хабаровск": "khabarovsk", 
					"Санкт-Петербург": "piter", "Казань": "kazan","Новосибирск": "novosibirsk"}

			all_city = []
			for key, value in iteritems(city_name):
				city = "%s" %frappe.db.escape(key)
				city_qty = frappe.db.sql("""
					select sum(wb_sas.quantity) {4}
					from `tabWB Sales by Sales` wb_sas
					where wb_sas.supplier_oper_name = "Продажа" and wb_sas.office_name = {3} and wb_sas.sale_dt between {1} and {2} {0}
				"""
				.format(conditions, from_date, to_date, city, value), as_dict=1)

				all_city.extend(city_qty)

			entries = {}
			entries.update(entries_sales[0])
			entries.update(entries_logistics[0])
			entries.update(entries_purchases[0])
			for i in all_city:
				entries.update(i)
			entries.update({"from_date": date[0]})

			all_entries.append(entries)

		self.entries = all_entries

	def get_sales_transactions_based_on_customer_or_territory_group(self):
		if self.filters["value_quantity"] == 'Value':
			value_field = "base_net_total as value_field"
		else:
			value_field = "total_qty as value_field"

		if self.filters.tree_type == 'Customer Group':
			entity_field = 'customer_group as entity'
		elif self.filters.tree_type == 'Supplier Group':
			entity_field = "supplier as entity"
			self.get_supplier_parent_child_map()
		else:
			entity_field = "territory as entity"

		self.entries = frappe.get_all(self.filters.doc_type,
			fields=[entity_field, value_field, self.date_field],
			filters={
				"docstatus": 1,
				"company": self.filters.company,
				self.date_field: ('between', [self.filters.from_date, self.filters.to_date])
			}
		)
		self.get_groups()

	def get_sales_transactions_based_on_item_group(self):
		if self.filters["value_quantity"] == 'Value':
			value_field = "base_amount"
		else:
			value_field = "qty"

		self.entries = frappe.db.sql("""
			select i.item_group as entity, i.{value_field} as value_field, s.{date_field}
			from `tab{doctype} Item` i , `tab{doctype}` s
			where s.name = i.parent and i.docstatus = 1 and s.company = %s
			and s.{date_field} between %s and %s
		""".format(date_field=self.date_field, value_field=value_field, doctype=self.filters.doc_type),
		(self.filters.company, self.filters.from_date, self.filters.to_date), as_dict=1)

		self.get_groups()

	def get_sales_transactions_based_on_project(self):
		if self.filters["value_quantity"] == 'Value':
			value_field = "base_net_total as value_field"
		else:
			value_field = "total_qty as value_field"

		entity = "project as entity"

		self.entries = frappe.get_all(self.filters.doc_type,
			fields=[entity, value_field, self.date_field],
			filters={
				"docstatus": 1,
				"company": self.filters.company,
				"project": ["!=", ""],
				self.date_field: ('between', [self.filters.from_date, self.filters.to_date])
			}
		)

	def get_rows(self):
		self.data = []
		self.get_periodic_data()

		string_name = {"sales_amount": _("Sales amount"), "amount_commission_wb": _("Amount commission WB"), 
				"supplier_remuneration": _("Supplier remuneration"), "total_qty": _("Total qty"), "amount_logistics": _("Minus logistics"), 
				"amount_purchases": _("Amount purchases"), "koledino": _("Koledino Warehouse"), "podolsk": _("Podolsk Warehouse"), 
				"piter": _("Saint-Petersburg Warehouse"), "kazan": _("Kazan Warehouse"), "yekaterinburg": _("Yekaterinburg Warehouse"),
				"novosibirsk": _("Novosibirsk Warehouse"), "krasnodar": _("Krasnodar Warehouse"), "pushkino": _("Pushkino Warehouse"),
				"elektrostal": _("Elektrostal Warehouse"), "domodedovo": _("Domodedovo Warehouse"), "khabarovsk": _("Khabarovsk Warehouse")}

		for entity, period_data in iteritems(self.entity_periodic_data):
			if entity == 'from_date':
				continue
			
			row = {
				"entity": string_name[entity],
				"entity_name": None
			}
			total = 0
			for date in self.periodic_daterange:
				period = self.get_period(date[1])
				amount = flt(period_data.get(period, 0.0))
				row[scrub(period)] = amount
				total += amount

			row["total"] = total

			self.data.append(row)

	def get_rows_by_group(self):
		self.get_periodic_data()
		out = []

		for d in reversed(self.group_entries):
			row = {
				"entity": d.name,
				"indent": self.depth_map.get(d.name)
			}
			total = 0
			for end_date in self.periodic_daterange:
				period = self.get_period(end_date)
				amount = flt(self.entity_periodic_data.get(d.name, {}).get(period, 0.0))
				row[scrub(period)] = amount
				if d.parent and (self.filters.tree_type != "Order Type" or d.parent == "Order Types"):
					self.entity_periodic_data.setdefault(d.parent, frappe._dict()).setdefault(period, 0.0)
					self.entity_periodic_data[d.parent][period] += amount
				total += amount

			row["total"] = total
			out = [row] + out

		self.data = out

	def get_periodic_data(self):
		self.entity_periodic_data = frappe._dict()

		for d in self.entries:
			for key, value in d.items():
				period = self.get_period(d["from_date"])
				self.entity_periodic_data.setdefault(key, frappe._dict()).setdefault(period, 0.0)
				self.entity_periodic_data[key][period] += flt(value)

	def get_period(self, posting_date):
		if self.filters.range == 'Weekly':
			period = "Week " + str(posting_date.isocalendar()[1]) + " " + str(posting_date.year)
		elif self.filters.range == 'Monthly':
			period = str(self.months[posting_date.month - 1]) + " " + str(posting_date.year)
		elif self.filters.range == 'Quarterly':
			period = "Quarter " + str(((posting_date.month - 1) // 3) + 1) + " " + str(posting_date.year)
		else:
			year = get_fiscal_year(posting_date, company=self.filters.company)
			period = str(year[0])
		return period

	def get_period_date_ranges(self):
		from dateutil.relativedelta import relativedelta, MO
		from_date, to_date = getdate(self.filters.from_date), getdate(self.filters.to_date)

		increment = {
			"Monthly": 1,
			"Quarterly": 3,
			"Half-Yearly": 6,
			"Yearly": 12
		}.get(self.filters.range, 1)

		if self.filters.range in ['Monthly', 'Quarterly']:
			from_date = from_date.replace(day=1)
		elif self.filters.range == "Yearly":
			from_date = get_fiscal_year(from_date)[1]
		else:
			from_date = from_date + relativedelta(from_date, weekday=MO(-1))

		self.periodic_daterange = []
		for dummy in range(1, 53):
			if self.filters.range == "Weekly":
				period_end_date = add_days(from_date, 6)
			else:
				period_end_date = add_to_date(from_date, months=increment, days=-1)

			if period_end_date > to_date:
				period_end_date = to_date

			self.periodic_daterange.append((from_date, period_end_date))

			from_date = add_days(period_end_date, 1)
			if period_end_date == to_date:
				break

	def get_groups(self):
		if self.filters.tree_type == "Territory":
			parent = 'parent_territory'
		if self.filters.tree_type == "Customer Group":
			parent = 'parent_customer_group'
		if self.filters.tree_type == "Item Group":
			parent = 'parent_item_group'
		if self.filters.tree_type == "Supplier Group":
			parent = 'parent_supplier_group'

		self.depth_map = frappe._dict()

		self.group_entries = frappe.db.sql("""select name, lft, rgt , {parent} as parent
			from `tab{tree}` order by lft"""
		.format(tree=self.filters.tree_type, parent=parent), as_dict=1)

		for d in self.group_entries:
			if d.parent:
				self.depth_map.setdefault(d.name, self.depth_map.get(d.parent) + 1)
			else:
				self.depth_map.setdefault(d.name, 0)

	def get_teams(self):
		self.depth_map = frappe._dict()

		self.group_entries = frappe.db.sql(""" select * from (select "Order Types" as name, 0 as lft,
			2 as rgt, '' as parent union select distinct order_type as name, 1 as lft, 1 as rgt, "Order Types" as parent
			from `tab{doctype}` where ifnull(order_type, '') != '') as b order by lft, name
		"""
		.format(doctype=self.filters.doc_type), as_dict=1)

		for d in self.group_entries:
			if d.parent:
				self.depth_map.setdefault(d.name, self.depth_map.get(d.parent) + 1)
			else:
				self.depth_map.setdefault(d.name, 0)

	def get_supplier_parent_child_map(self):
		self.parent_child_map = frappe._dict(frappe.db.sql(""" select name, supplier_group from `tabSupplier`"""))

	def get_chart_data(self):
		length = len(self.columns)

		if self.filters.tree_type in ["Customer", "Supplier"]:
			labels = [d.get("label") for d in self.columns[2:length - 1]]
		elif self.filters.tree_type == "Item":
			labels = [d.get("label") for d in self.columns[3:length - 1]]
		else:
			labels = [d.get("label") for d in self.columns[1:length - 1]]
		self.chart = {
			"data": {
				'labels': labels,
				'datasets': []
			},
			"type": "line"
		}
