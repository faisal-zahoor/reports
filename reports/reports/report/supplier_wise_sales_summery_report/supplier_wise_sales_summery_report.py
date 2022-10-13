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
        return [_("Supplier") + ":Data:180",
		_("Item Code") + ":Data:120",
                _("Description") + ":Data:320",
                _("Net Sales") + ":Currency:100",
                _("COGS") + ":Currency:100",
                _("Profit") + ":Currency:100",
                _("Profit %") + ":Percent:100",
		_("Sold Qty") + ":Int:100",
		_("Bal Qty") + ":Int:100",
		_("AVG SP") + ":Float:100",
		_("AVG Cost") + ":Float:100",
		_("CL 1") + ":Data:120",
		_("CL 2") + ":Data:120"]

def get_data(conditions,filters):
        invoice = frappe.db.sql("""select
	(select supplier from `tabItem Supplier` where parent = si_item.item_code),
    	si_item.item_code,
	si_item.description,
	sum(si_item.base_net_amount),
	
	(select ((sum(stock_value)/sum(qty_after_transaction)) * sum(si_item.stock_qty)) from `tabStock Ledger Entry` 
		where item_code = si_item.item_code 
		and (warehouse = 'Store - Shuwaikh - SB' or warehouse = 'Ahmadi S/R - SB' or warehouse = 'Decor - Shuwaikh - SB' 
		or warehouse = 'Main SB - SB' or warehouse = 'Shuwaikh S/R - SB') and is_cancelled='No'),
	
	(sum(si_item.base_net_amount) - (select (sum(stock_value)/sum(qty_after_transaction) * sum(si_item.stock_qty))
		 from `tabStock Ledger Entry` where item_code = si_item.item_code 
		 and (warehouse = 'Store - Shuwaikh - SB' or warehouse = 'Ahmadi S/R - SB' or warehouse = 'Decor - Shuwaikh - SB' 
		 or warehouse = 'Main SB - SB' or warehouse = 'Shuwaikh S/R - SB') and is_cancelled='No')),
	
	(((sum(si_item.base_net_amount) - (select (sum(stock_value)/sum(qty_after_transaction) * sum(si_item.stock_qty)) 
		from `tabStock Ledger Entry` where item_code = si_item.item_code 
		and (warehouse = 'Store - Shuwaikh - SB' or warehouse = 'Ahmadi S/R - SB' or warehouse = 'Decor - Shuwaikh - SB' 
		or warehouse = 'Main SB - SB' or warehouse = 'Shuwaikh S/R - SB') 
		and is_cancelled='No')) / sum(si_item.base_net_amount)) * 100),
	
	sum(si_item.stock_qty),
	
	(select sum(actual_qty) from `tabBin` where item_code = si_item.item_code 
		and (warehouse = 'Ahmadi S/R - SB' or warehouse = 'Decor - Shuwaikh - SB' or warehouse = 'Main SB - SB' 
		or warehouse = 'Shuwaikh S/R - SB' or warehouse = 'Store - Shuwaikh - SB')),
	
	sum(si_item.base_net_amount) / sum(si_item.stock_qty),
	
	(select (sum(stock_value)/sum(qty_after_transaction) * sum(si_item.stock_qty)) 
		from `tabStock Ledger Entry` where item_code = si_item.item_code and (warehouse = 'Store - Shuwaikh - SB' 
		or warehouse = 'Ahmadi S/R - SB' or warehouse = 'Decor - Shuwaikh - SB' or warehouse = 'Main SB - SB' 
		or warehouse = 'Shuwaikh S/R - SB') and is_cancelled='No') / sum(si_item.stock_qty),
	(select cl_1 from `tabItem` where item_code = si_item.item_code),
	(select cl_2 from `tabItem` where item_code = si_item.item_code)
from
	`tabSales Invoice` si, `tabSales Invoice Item` si_item
where
	(si.name = si_item.parent) and (si.docstatus = 1) %s group by si_item.item_code;"""%conditions, filters, as_list=1)
        return invoice

def get_conditions(filters):
        conditions = ""
        if filters.get("from_date"): conditions += " and si.posting_date >= %(from_date)s"
        if filters.get("to_date"): conditions += " and si.posting_date <= %(to_date)s"
        if filters.get("cost_center"): conditions += "and si.cost_center = %(cost_center)s"

        return conditions, filters
