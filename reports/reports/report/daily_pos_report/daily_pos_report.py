# Copyright (c) 2013, Hardik Gadesha and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _

def execute(filters=None):
	conditions, filters = get_conditions(filters)
	columns = get_column()
	data = get_data(conditions,filters)
	return columns,data

def get_column():
	return [_("Date") + ":Date:120",
		_("Invoice No") + ":Link/Sales Invoice:120",
		_("Customer") + ":Link/Customer:150",
		_("Gross") + ":Currency:100",
		_("Discount") + ":Currency:100",
		_("Net Total") + ":Currency:100"]

def get_data(conditions,filters):
	invoice = frappe.db.sql("""select posting_date,name, customer_name, total, discount_amount, grand_total 
				from `tabSales Invoice` where docstatus = 1 and is_pos = 1 %s
				order by posting_date asc;"""%conditions, filters, as_list=1)
	return invoice

def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"): conditions += " and posting_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and posting_date <= %(to_date)s"
	if filters.get("warehouse"): conditions += "and set_warehouse = %(warehouse)s"

	return conditions, filters
