# -*- coding: utf-8 -*-
# Copyright (c) 2022, Hardik Gadesha and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SupplierWiseItemAnalytics(Document):
	pass


@frappe.whitelist()
def get_item_details(from_date, to_date, effective_cogs):
	sales_query = frappe.db.sql(''' select voucher_no, sum(credit - debit) as sales from `tabGL Entry` as gle where gle.posting_date between %s and %s 
	and account = 'SALES ACCOUNT - SB' group by voucher_no ''', (from_date, to_date), as_dict = True)
	if not len(sales_query):
		return

	cogs_sum = 0
	sales_sum = 0
	item_wise_details = frappe._dict({})
	for voucher in sales_query:
		invoice = frappe.get_doc('Sales Invoice', voucher.voucher_no)
		if not invoice.items:
			continue


		for item in invoice.items:
			item_code = item.item_code
			if item_code not in item_wise_details:
				vendor = frappe.db.get_value('Item', item_code, 'vendor')
				balance_qty_query = frappe.db.sql(''' select sum(actual_qty) as qty from tabBin where item_code = %s ''', (item_code), as_dict = True)
				balance_qty = 0
				if len(balance_qty_query):
					balance_qty = balance_qty_query[0].qty

				item_wise_details[item_code] = frappe._dict({'sales': 0, 'cogs': 0, 'supplier': vendor, 'item_code': item_code, 'item_name': item.item_name, 'sold_qty': 0, 'balance_qty': balance_qty})


			try:
				item_wise_details[item_code].sales += item.amount
				item_wise_details[item_code].sold_qty += item.stock_qty
				sales_sum += item.amount
			except:
				frappe.msgprint("Issues identified in invoice " + voucher.voucher_no)
			# Identify if it is a pos or non pos invoice
			# if pos invoice, check the SLE for the billed qty and get the cogs
			# if non pos invoice, identify the associated delivery note along with the billed qty and find the cogs
			# Add sales, cogs, profit and percentage in the sales person

			cogs = 0
			if not frappe.db.get_value('Item', item_code, 'is_stock_item'):
				item_wise_details[item_code].cogs += 0
				continue
			valuation_rate = 0
			if invoice.update_stock:
				valuation_rate = frappe.db.get_value('Stock Ledger Entry', {'voucher_no': invoice.name, 'item_code': item_code}, 'valuation_rate')
			else:
				delivery_note = item.delivery_note
				if delivery_note:
					valuation_rate = frappe.db.get_value('Stock Ledger Entry', {'voucher_no': delivery_note, 'item_code': item_code}, 'valuation_rate')
			cogs = valuation_rate * item.stock_qty
			item_wise_details[item_code].cogs += cogs
			cogs_sum += cogs

	difference = float(effective_cogs) - cogs_sum
	sales_query = frappe.db.sql(''' select sum(credit - debit) as sales from `tabGL Entry` as gle 
	where gle.posting_date between %s and %s and account = 'SALES ACCOUNT - SB' ''', (from_date, to_date), as_dict = True)
	effective_sales = 0
	if sales_query:
		effective_sales = sales_query[0]['sales']
	sales_difference = float(effective_sales) - sales_sum

	data = item_wise_details.values()
	result = []
	for datum in data:
		datum = frappe._dict(datum)
		datum.sales += ((sales_difference/sales_sum) * datum.sales)
		datum.cogs += ((difference/cogs_sum) * datum.cogs)
		datum['profit'] = datum['sales'] - datum['cogs']
		if datum['sales']:
			datum['profit_percentage'] = (datum.profit/datum.sales) * 100
		else:
			datum['profit_percentage'] = 0
		datum.sales = round(datum.sales, 2)
		datum.cogs = round(datum.cogs, 2)
		datum['profit'] = round(datum['profit'], 2)
		datum['profit_percentage'] = round(datum['profit_percentage'], 2)
		result.append(datum)
	return result
