// Copyright (c) 2016, Hardik Gadesha and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Supplier wise Sales Summery Report"] = {
	"filters": [
		{
            		"fieldname": "from_date",
            		"label": __("From Date"),
            		"fieldtype": "Date",
	    		"default": frappe.datetime.get_today()
        	},
		{
            		"fieldname": "to_date",
            		"label": __("To Date"),
            		"fieldtype": "Date",
	    		"default": frappe.datetime.get_today()
        	},
		{
        	    "fieldname": "cost_center",
       		    "label": __("Cost Center"),
        	    "fieldtype": "Link",
		    "options": "Cost Center"
        	}
	]
}
