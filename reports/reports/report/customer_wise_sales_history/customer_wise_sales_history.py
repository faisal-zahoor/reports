from __future__ import unicode_literals
import frappe
from frappe import msgprint, _

def execute(filters=None):
	columns = get_column()
	data = get_silo(filters)
	return columns,data

def get_column():
	return [_("Invoice") + ":Link/Sales Invoice:120",_("Item Code") + ":Link/Item:150",_("Item Name") + ":Data:180",_("Price List Rate") + ":Currency:100",_("Rate") + ":Currency:100",_("Qty") + ":Float:80",_("Amount") + ":Currency:150"]

def get_silo(filters):
	if filters.get("customer"):
		customer = filters.get("customer")
		sales_history = frappe.db.sql(""" select 
	sinv.name, sitem.item_code, sitem.item_name, 
	sitem.price_list_rate,sitem.rate,sitem.qty,sitem.amount 
		from `tabSales Invoice` sinv, `tabSales Invoice Item` sitem 
	where (sinv.name = sitem.parent) and (sinv.docstatus != 2) and sinv.customer = '%s'; """%(customer), as_list=1)

		return sales_history
