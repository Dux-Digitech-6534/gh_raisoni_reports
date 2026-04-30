frappe.query_reports["Purchase Orders Outstanding Report"] = {
    "filters": [

        {
            "fieldname": "company",
            "label": "Company",
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 1
        },

        {
            "fieldname": "supplier",
            "label": "Supplier",
            "fieldtype": "Link",
            "options": "Supplier"
        },

        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date"
        },

        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date"
        }

    ]
};