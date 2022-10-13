frappe.query_reports["New Supplier Wise Warehouse Item Sales Summary"] = {
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
                }
        ]
}

