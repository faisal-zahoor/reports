// Copyright (c) 2022, Hardik Gadesha and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Person Wise Analytics', {
	refresh: function(frm) {

	},

get_details: function (frm) {
  frappe.call({
    method: "reports.reports.doctype.sales_person_wise_analytics.sales_person_wise_analytics.get_details",
    freeze: true,
    args: {
      from_date: frm.doc.from_date,
      to_date: frm.doc.to_date
    },
    callback: function(r) {
      if(r.message) {
        frm.set_value('sales' , r.message.sales)
        frm.set_value('cogs' , r.message.cogs)
        frm.set_value('profitloss' , r.message.gross_profit)
        frm.set_value('percentage' , r.message.profit_percentage)
	frm.set_value('effective_cogs' , r.message.effective_cogs)
	frm.set_value('unbilled_amount' , r.message.unbilled_amount)
	frm.set_value('main' , r.message.main)
	frm.set_value('decor' , r.message.decor)
	frm.set_value('jv_passed' , r.message.jv_passed)
      }
      frm.refresh_fields();
    }
  });
},
load_data: function (frm) {
  frappe.call({
    method: "reports.reports.doctype.sales_person_wise_analytics.sales_person_wise_analytics.get_sales_man_details",
    freeze: true,
    args: {
      from_date: frm.doc.from_date,
      to_date: frm.doc.to_date,
      effective_cogs: frm.doc.effective_cogs
    },
    callback: function(r) {
      if(r.message) {
        frm.set_value('sales_person' , r.message)
      }
      frm.refresh_fields();
    }
  });
},
unbilled_dn: function (frm) {
  frappe.call({
    method: "reports.reports.doctype.sales_person_wise_analytics.sales_person_wise_analytics.get_dn_pending_to_bill",
    freeze: true,
    args: {
      from_date: frm.doc.from_date,
      to_date: frm.doc.to_date
    },
    callback: function(r) {
      if(r.message) {
        frm.set_value('unbilled_delivery_note_details' , r.message)
      }
      frm.refresh_fields();
    }
  });
}



});
