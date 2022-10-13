# Copyright (c) 2013, Hardik Gadesha and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	if not filters: filters = {}
	validate_filters(filters)
	columns = get_columns()
	stock = get_total_stock(filters)

	return columns, stock

def get_columns():
	columns = [
		_("Company") + ":Link/Company:5",
		_("Warehouse") + ":Link/Warehouse:130",
		_("Supplier") + ":Link/Supplier:240",
		_("Item") + ":Link/Item:90",
		_("Item Name") + "::350",
		_("UOM") + ":Link/UOM:60",
		_("Current Qty") + ":Float:100",
		_("Valuation Rate") + ":Currency:120",
		_("Balance Value") + ":Currency:120"
	]

	return columns

def get_total_stock(filters):
	conditions = ""
	columns = ""

	if filters.get("group_by") == "Warehouse":
		if filters.get("company"):
			conditions += " AND warehouse.company = '%s'" % frappe.db.escape(filters.get("company"), percent=False)

		conditions += " GROUP BY ledger.warehouse, item.item_code"
		columns += " '' as company, ledger.warehouse"
	else:
		conditions += " GROUP BY warehouse.company, item.item_code"
		columns += " warehouse.company, '' as warehouse"

	return frappe.db.sql("""
			SELECT
				%s,
				(select supplier from `tabItem Supplier` where parent = item.item_code limit 1),
				item.item_code,
				item.item_name,
				item.stock_uom,
				sum(ledger.actual_qty) as actual_qty,
				sum(ledger.stock_value)/sum(ledger.actual_qty),
				sum(ledger.stock_value)
			FROM
				`tabBin` AS ledger
			INNER JOIN `tabItem` AS item
				ON ledger.item_code = item.item_code
			INNER JOIN `tabWarehouse` warehouse
				ON warehouse.name = ledger.warehouse and warehouse.disabled = 0
			WHERE
				actual_qty != 0 %s""" % (columns, conditions))

def validate_filters(filters):
	if filters.get("group_by") == 'Company' and \
		filters.get("company"):

		frappe.throw(_("Please set Company filter blank if Group By is 'Company'"))
