frappe.query_reports["Sales Person Selling History - 3"] = {
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
