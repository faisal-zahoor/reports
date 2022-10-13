# -*- coding: utf-8 -*-
# Copyright (c) 2022, Hardik Gadesha and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SalesPersonWiseAnalytics(Document):
	pass


@frappe.whitelist()
def get_details(from_date, to_date, ignore_last_year=False):
	ignore_last_year = False
	sales_query = frappe.db.sql(''' select sum(credit - debit) as sales from `tabGL Entry` as gle
	where gle.posting_date between %s and %s and
	account = 'SALES ACCOUNT - SB' ''', (from_date, to_date), as_dict = True)
	
	sales = 0 
	if sales_query:
		sales = sales_query[0]['sales']
	if not sales:
		sales = 0

	cogs_query = frappe.db.sql(''' select sum(debit - credit) as cogs from `tabGL Entry` as gle
	where gle.posting_date between  %s and %s and
	account = 'COST OF SALES - SB' ''', (from_date, to_date), as_dict = True)
	
	cogs = 0
	if cogs_query:
		cogs = cogs_query[0]['cogs']
	if not cogs:
		cogs = 0


        stock_query = frappe.db.sql(''' select sum(debit - credit) as non_cogs from `tabGL Entry` as gle
        where gle.posting_date between  '2022-01-01' and %s and
        account = 'Stock Delivered But Not Billed - SB' ''', (to_date), as_dict = True)
        
        jv = 0
        if stock_query:
                jv = stock_query[0]['non_cogs']
	if not jv:
		jv = 0

	if not ignore_last_year:
		breakup_query = frappe.db.sql(''' select sum(actual - billed_qty) as unbilled_amount, cost_center from (
select *, actual - billed_qty as unbilled from (select item_code, parent, actual, case when billed_qty is null then 0 else billed_qty end as billed_qty, cost_center from (
select summed_item.item_code, summed_item.parent, summed_item.actual as actual, summed_item.valuation_rate * sii.stock_qty as billed_qty, summed_item.cost_center from
  (select dni.item_code, dni.parent, sum(sle.valuation_rate * dni.stock_qty) as actual, dn.cost_center, sle.valuation_rate from `tabDelivery Note Item` as dni
inner join `tabDelivery Note` as dn on dn.name = dni.parent and dn.docstatus = 1
inner join `tabStock Ledger Entry` as sle on dni.parent = sle.voucher_no and dni.name = sle.voucher_detail_no
and dni.item_code = sle.item_code and dni.name = sle.voucher_detail_no
where sle.posting_date between  '2022-01-01' and %s
group by dni.item_code, dni.parent) as summed_item
left outer join (select si.name as invoice, sii.delivery_note, sii.item_code, sum( sii.stock_qty) as stock_qty from `tabSales Invoice` as si
inner join `tabSales Invoice Item` as sii on sii.parent = si.name and si.docstatus = 1
where si.docstatus = 1 and si.posting_date <= %s
group by si.name, sii.delivery_note, sii.item_code) as sii on summed_item.parent = sii.delivery_note and summed_item.item_code = sii.item_code
  )as a) as b)  as c group by cost_center
''', (to_date, to_date), as_dict = True)

	if ignore_last_year:
		breakup_query = frappe.db.sql(''' select sum(actual - billed_qty) as unbilled_amount, cost_center from (
select *, actual - billed_qty as unbilled from (select item_code, parent, actual, case when billed_qty is null then 0 else billed_qty end as billed_qty, cost_center from (
select summed_item.item_code, summed_item.parent, summed_item.actual as actual, summed_item.valuation_rate * sii.stock_qty as billed_qty, summed_item.cost_center from
  (select dni.item_code, dni.parent, sum(sle.valuation_rate * dni.stock_qty) as actual, dn.cost_center, sle.valuation_rate from `tabDelivery Note Item` as dni
inner join `tabDelivery Note` as dn on dn.name = dni.parent and dn.docstatus = 1
inner join `tabStock Ledger Entry` as sle on dni.parent = sle.voucher_no and dni.name = sle.voucher_detail_no
and dni.item_code = sle.item_code and dni.name = sle.voucher_detail_no
where sle.posting_date between  '2022-01-01' and %s
group by dni.item_code, dni.parent) as summed_item
left outer join (select si.name as invoice, sii.delivery_note, sii.item_code, sum( sii.stock_qty) as stock_qty from `tabSales Invoice` as si
inner join `tabSales Invoice Item` as sii on sii.parent = si.name and si.docstatus = 1
where si.docstatus = 1 and si.posting_date >= '2022-01-01' and si.posting_date <= %s
group by si.name, sii.delivery_note, sii.item_code) as sii on summed_item.parent = sii.delivery_note and summed_item.item_code = sii.item_code
  )as a) as b)  as c group by cost_center
''', (to_date, to_date), as_dict = True)


	unbilled_amount = 0
	main = 0
	decor = 0
	if breakup_query:
		for datum in breakup_query:
			unbilled_amount += datum.unbilled_amount
			if datum.cost_center == 'DECOR - SB':
				decor += datum.unbilled_amount
			else:
				main += datum.unbilled_amount


	effective_cogs = cogs + jv  - unbilled_amount

	gross_profit = sales - effective_cogs
	if sales: 
		profit_percentage = ((sales - effective_cogs)/ sales) * 100
	else:
		profit_percentage = 0

	return {'sales': sales, 'cogs': cogs, 'gross_profit': gross_profit, 'profit_percentage': profit_percentage, 'effective_cogs': effective_cogs, 'unbilled_amount': unbilled_amount, 'main': main, 'decor': decor, 'jv_passed': jv}



@frappe.whitelist()
def get_sales_man_details(from_date, to_date, effective_cogs):
	sales_query = frappe.db.sql(''' select voucher_no, sum(credit - debit) as sales from `tabGL Entry` as gle where gle.posting_date between %s and %s and account = 'SALES ACCOUNT - SB' group by voucher_no ''', (from_date, to_date), as_dict = True)
	if not len(sales_query):
		return

	cogs_sum = 0
	sales_person_wise_details = frappe._dict({'No Sales Person': frappe._dict( {'sales': 0, 'cogs': 0, 'sales_person': 'No Sales Person'})})
	for voucher in sales_query:
		invoice = frappe.get_doc('Sales Invoice', voucher.voucher_no)
		sales_person = 'No Sales Person'
		if invoice.sales_team:
			sales_person = invoice.sales_team[0].sales_person
		
		if sales_person not in sales_person_wise_details:
			sales_person_wise_details[sales_person] = frappe._dict({'sales': 0, 'cogs': 0, 'sales_person': sales_person})
		try:
			sales_person_wise_details[sales_person].sales += voucher.sales
		except:
			frappe.msgprint("Issues identified in invoice " + voucher.voucher_no)
		# Identify if it is a pos or non pos invoice
		# if pos invoice, check the SLE for the billed qty and get the cogs
		# if non pos invoice, identify the associated delivery note along with the billed qty and find the cogs
		# Add sales, cogs, profit and percentage in the sales person

		if invoice.update_stock:
			# This is a POS invoice
			# It has the SLE mapped directly to it
			cogs_query = frappe.db.sql(''' select sum(debit - credit) as cogs from `tabGL Entry` as gle where gle.posting_date between %s and %s and account = 'COST OF SALES - SB' and voucher_no = %s group by voucher_no ''', (from_date, to_date, invoice.name), as_dict = True)
			if not cogs_query:
				frappe.msgprint(('Invoice {0} does not have a GL entry for COGS').format(invoice.name))
			else:
				sales_person_wise_details[sales_person].cogs += cogs_query[0].cogs
				cogs_sum += cogs_query[0].cogs
		else:
			# This is a invoice with delivery note.
			# Find the related delivery note and only take COGS for the billed qty.
			cogs = 0
			for item in invoice.items:
				item_code = item.item_code
				qty = item.stock_qty
				delivery_note = item.delivery_note
				if delivery_note and frappe.db.get_value('Item', item_code, 'is_stock_item'):
					valuation_rate = frappe.db.get_value('Stock Ledger Entry', {'voucher_no': delivery_note, 'item_code': item_code}, 'valuation_rate')
					cogs += valuation_rate * qty
				else:
					frappe.errprint(invoice.name)
					frappe.errprint(item_code)
			sales_person_wise_details[sales_person].cogs += cogs
			cogs_sum += cogs

	difference = float(effective_cogs) - cogs_sum
	data = sales_person_wise_details.values()
	result = []
	for datum in data:
		datum = frappe._dict(datum)
		datum.cogs += ((difference/cogs_sum) * datum.cogs)
		datum['profitloss'] = datum['sales'] - datum['cogs']
		if datum['sales']:
			datum['percentage'] = (datum.profitloss/datum.sales) * 100
		else:
			datum['percentage'] = 0

		result.append(datum)

	return result


@frappe.whitelist()
def get_dn_pending_to_bill(from_date, to_date):
	return frappe.db.sql(''' select * from (
select *, actual - billed as unbilled from (select item_code, parent as delivery_note, actual, case when billed_qty is null then 0 else billed_qty end as billed, cost_center from (
select summed_item.item_code, summed_item.parent, summed_item.actual as actual, summed_item.valuation_rate * sii.stock_qty as billed_qty, summed_item.cost_center from
  (select dni.item_code, dni.parent, sum(sle.valuation_rate * dni.stock_qty) as actual, dn.cost_center, sle.valuation_rate from `tabDelivery Note Item` as dni
inner join `tabDelivery Note` as dn on dn.name = dni.parent and dn.docstatus = 1
inner join `tabStock Ledger Entry` as sle on dni.parent = sle.voucher_no and dni.name = sle.voucher_detail_no
and dni.item_code = sle.item_code and dni.name = sle.voucher_detail_no
where sle.posting_date between  '2022-01-01' and %s
group by dni.item_code, dni.parent) as summed_item
left outer join (select si.name as invoice, sii.delivery_note, sii.item_code, sum( sii.stock_qty) as stock_qty from `tabSales Invoice` as si
inner join `tabSales Invoice Item` as sii on sii.parent = si.name and si.docstatus = 1
where si.docstatus = 1 and si.posting_date <= %s
group by si.name, sii.delivery_note, sii.item_code) as sii on summed_item.parent = sii.delivery_note and summed_item.item_code = sii.item_code
  )as a) as b) as c where unbilled <> 0
''', (to_date, to_date), as_dict = True)
