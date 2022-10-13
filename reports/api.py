from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, datetime
from erpnext.stock.utils import get_latest_stock_qty
import json
from frappe import _, throw, msgprint, utils
from frappe.utils import cint, flt, cstr, comma_or, getdate, add_days, getdate, rounded, date_diff, money_in_words


@frappe.whitelist()
def hellosub(loggedInUser):
	return 'pong'

#su testManul
@frappe.whitelist()
def get_item_data_qa(item_code,customer):
	item = get_item_details(item_code)
	if  item :
		it_bar_code = frappe.db.get_value("Item Barcode", {"parent":item_code},"barcode")
		row_dic = {
		"item_name":item.get("item_name"),
		"description":item.get("description"),
		"item_code":item.get("item_code"),
		"barcode":it_bar_code,
		"sel_price":item.get("standard_rate"),
		"price_a":item.get("price_a_60_days"),
		"price_b":item.get("price_a_90_days"),
		"price_c":item.get("price_c"),
		"cash":item.get("cash_price"),
		"sell_off_price":item.get("sell_off_price"),
		"market_price":item.get("market_price"),
		"brand":item.get("brand"),
		"stock_uom":item.get("stock_uom")
		}
		#wh_details_start
		item_wh_data,total_wh_qty,total_wh_stock_value = get_item_wh_data(item_code)

		if item_wh_data:
			wh_dic = {
			"decor_wh":item_wh_data.get("Decor - Shuwaikh - SB").get("bal_qty") if item_wh_data.get("Decor - Shuwaikh - SB") else 0  ,
			"store_wh":item_wh_data.get("Store - Shuwaikh - SB").get("bal_qty") if item_wh_data.get("Store - Shuwaikh - SB") else 0 ,
			"ahmadi_wh":item_wh_data.get("Ahmadi S/R - SB").get("bal_qty") if  item_wh_data.get("Ahmadi S/R - SB") else 0,
			"shuwaikh_wh":item_wh_data.get("Shuwaikh S/R - SB").get("bal_qty") if item_wh_data.get("Shuwaikh S/R - SB") else 0 ,
			"main_wh" : item_wh_data.get("Main SB - SB").get("bal_qty") if item_wh_data.get("Main SB - SB") else 0,
			"all_wh_total_qty" : total_wh_qty,
			"val_rate" : item_wh_data.get("Main SB - SB").get("valuation_rate") if item_wh_data.get("Main SB - SB") else 0,
			"stock_in_transit" :item_wh_data.get("Main SB - SB").get("ordered_qty") if item_wh_data.get("Main SB - SB") else 0
			}
			row_dic.update(wh_dic)
		"""
		print "item_wh_data",item_wh_data
		if item_wh_data:
			wh_dic = {
			"decor_wh":item_wh_data.get("GMP2 - EPCH").get("bal_qty") if item_wh_data.get("GMP2 - EPCH") else 0,
			"store_wh":item_wh_data.get("Yard - EPCH").get("bal_qty") if item_wh_data.get("Yard - EPCH") else 0,
			"ahmadi_wh":item_wh_data.get("TableStore - EPCH").get("bal_qty") if item_wh_data.get("TableStore - EPCH") else 0,
			"shuwaikh_wh":item_wh_data.get("Stores - EPCH").get("bal_qty") if item_wh_data.get("Stores - EPCH") else 0,
			"main_wh" : item_wh_data.get("Showroom - Indiranagar - EPCH").get("bal_qty") if item_wh_data.get("Showroom - Indiranagar - EPCH") else 0,
			"all_wh_total_qty" : total_wh_qty,
			"val_rate" : item_wh_data.get("TableStore - EPCH").get("valuation_rate") if item_wh_data.get("TableStore - EPCH") else 0,
			"stock_in_transit" :item_wh_data.get("TableStore - EPCH").get("ordered_qty") if item_wh_data.get("TableStore - EPCH") else 0
			}
			row_dic.update(wh_dic)
		"""
		#wh_details_end

		#po_details_end
		po_details = get_po_details(item_code)
		if po_details:
			po_dic ={
			 "order_qty":po_details[0]["qty"],
			 "exp_del_date":po_details[0]["schedule_date"]
			}
			row_dic.update(po_dic)
		#po_details_end

		#si_details_start
		si_details = get_si_details(item_code)
		if si_details :
			si_dic ={
			 "last_sold_price":si_details[0]["rate"]
			}
			row_dic.update(si_dic)
		#si_details_end

		#qou_details_start
		qou_details = get_qou_details(item_code)
		if qou_details :
			qou_dic ={
			 "last_quoted_price":qou_details[0]["rate"]
			}
			row_dic.update(qou_dic)
		#qou_details_end


		#sales Invoice
		cus_si_details = get_cus_si_details(item_code,customer)
		if cus_si_details :
			cus_si_dic ={
			 "last_sold_price_customer":cus_si_details[0]["rate"],
			 "last_sold_date_customer":cus_si_details[0]["posting_date"]
			}
			row_dic.update(cus_si_dic)

		#quotation
		cus_qou_details = get_cus_qou_details(item_code,customer)
		if cus_qou_details :
			cus_qou_dic ={
			 "last_quoted_price_customer":cus_qou_details[0]["rate"],
			 "last_quoted_date_customer":cus_qou_details[0]["transaction_date"]
			}
			row_dic.update(cus_qou_dic)
		#filtered_customer_end
		return row_dic
	else:
		return None

def get_item_details(item_code):
	#items_data = frappe.db.sql("""select it.item_name,it.item_code,it.description,it.standard_rate,it.brand from `tabItem` it where it.item_code= %s""", (item_code), as_dict=1)
	items_data = frappe.db.sql("""select it.item_name,it.item_code,it.stock_uom,it.description,it.standard_rate,it.brand,it.price_a_60_days,it.price_a_90_days,it.cash_price,it.sell_off_price,it.market_price from `tabItem` it where it.item_code=%s""", (item_code), as_dict=1)
	return items_data[0] if items_data else None

def get_item_wh_data(item_code):
	item_wh_data = {}
	wh_list = [	"Decor - Shuwaikh - SB","Store - Shuwaikh - SB","Ahmadi S/R - SB","Shuwaikh S/R - SB","Main SB - SB"]
	wh_list_local = ["Stores - EPCH","TableStore - EPCH","GMP2 - EPCH","Yard - EPCH","Showroom - Indiranagar - EPCH"]
	total_wh_qty = 0.0
	total_wh_stock_value = 0
	for wh in wh_list :
		actual_qty = 0.0
		ordered_qty = 0.0
		valuation_rate = 0.0
		stock_value = 0.0
		wh_details = get_warehouse_qty(wh,item_code)
		if  wh_details :
			actual_qty = wh_details[0]["actual_qty"]
			ordered_qty =  wh_details[0]["ordered_qty"]
			valuation_rate =  wh_details[0]["valuation_rate"]
			stock_value =  wh_details[0]["stock_value"]
			print "actual_qty",actual_qty
			details = {"bal_qty": actual_qty,"ordered_qty":ordered_qty,"valuation_rate":valuation_rate,"stock_value":stock_value }
			item_wh_data[wh] = details
			total_wh_qty = total_wh_qty + actual_qty
			total_wh_stock_value = total_wh_stock_value + stock_value

	print "total_wh_qty",total_wh_qty
	return item_wh_data,total_wh_qty,total_wh_stock_value

def get_warehouse_qty(warehouse,item_code):
	whse_qt = 0
	wh_details = frappe.db.sql("""select actual_qty,ordered_qty,valuation_rate,stock_value from `tabBin` where warehouse=%s and item_code=%s and actual_qty > 0 """, (warehouse,item_code), as_dict=1)
	return wh_details if wh_details else None

def get_po_details(item_code) :
	details = frappe.db.sql("""select po.name,poi.qty,po.schedule_date from  `tabPurchase Order` po,`tabPurchase Order Item` poi  where po.name = poi.parent and poi.item_code=%s and status="To Receive and Bill" order by po.creation desc limit 1""", (item_code), as_dict=1)
	return details if details else None

def get_si_details(item_code):
	details = frappe.db.sql("""select si.name,sii.rate,si.posting_date from `tabSales Invoice` si,`tabSales Invoice Item` sii  where si.name = sii.parent and si.docstatus=1 and sii.item_code=%s order by si.creation desc limit 1""", (item_code), as_dict=1)
	return details if details else None

def get_qou_details(item_code):
	details = frappe.db.sql("""select qou.name,qoui.rate,qou.transaction_date from `tabQuotation` qou,`tabQuotation Item` qoui  where qou.name = qoui.parent and qou.docstatus=1 and qoui.item_code=%s order by qou.creation desc limit 1""", (item_code), as_dict=1)
	return details if details else None

def get_cus_si_details(item_code,customer):
	details = frappe.db.sql("""select si.name,sii.rate,si.posting_date from `tabSales Invoice` si,`tabSales Invoice Item` sii  where si.name = sii.parent and si.docstatus=1 and sii.item_code=%s and si.customer =%s order by si.creation desc limit 1""", (item_code,customer), as_dict=1)
	return details if details else None

def get_cus_qou_details(item_code,customer):
	details = frappe.db.sql("""select qou.name,qoui.rate,qou.transaction_date from `tabQuotation` qou,`tabQuotation Item` qoui  where qou.name = qoui.parent and qou.docstatus=1 and qoui.item_code=%s and qou.party_name =%s order by qou.creation desc limit 1""", (item_code,customer), as_dict=1)
	return details if details else None



@frappe.whitelist()
def report_test2():
	return "without arg"
