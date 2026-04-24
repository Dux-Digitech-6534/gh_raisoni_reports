// // Copyright (c) 2026, Abhijeet and contributors
// // For license information, please see license.txt

// frappe.query_reports["Department Wise Indent Register"] = {
// 	"filters": [

// 	]
// };




frappe.query_reports["Department Wise Indent Register"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "users_department",
            "label": "Users Department",
            "fieldtype": "Link",
            "options": "Department"
        },
        {
            "fieldname": "item_code",
            "label": "Item Code",
            "fieldtype": "Link",
            "options": "Item"
        }
    ]
};

