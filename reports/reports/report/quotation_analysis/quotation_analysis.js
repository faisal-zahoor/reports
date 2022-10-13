// Copyright (c) 2016, Hardik Gadesha and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Quotation Analysis"] = {
	"filters": [
	{
        "fieldname": "customer_filter",
        "label": __("Customer"),
        "fieldtype": "Link",
				"options": "Customer",
        "reqd": 0
	}

	]
}
