// frappe.query_reports["Purchase Bill Pending Report"] = {
//     "filters": [

//         {
//             "fieldname": "company",
//             "label": "Company",
//             "fieldtype": "Link",
//             "options": "Company",
//             "reqd": 1
//         },

//         {
//             "fieldname": "supplier",
//             "label": "Supplier",
//             "fieldtype": "Link",
//             "options": "Supplier"
//         },

//         {
//             "fieldname": "from_date",
//             "label": "From Date",
//             "fieldtype": "Date",
//             "default": frappe.datetime.month_start(),
//             "reqd": 1
//         },

//         {
//             "fieldname": "to_date",
//             "label": "To Date",
//             "fieldtype": "Date",
//             "default": frappe.datetime.month_end(),
//             "reqd": 1
//         },

//         {
//             "fieldname": "billing_status",
//             "label": "Billing Status",
//             "fieldtype": "Select",
//             "options": "\nGoods Received but Not Billed\nBills Cleared (Invoiced)",
//             "default": "Goods Received but Not Billed"
//         }

//     ]
// };

frappe.query_reports["Purchase Bill Pending Report"] = {
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
            "fieldtype": "Date",
            "default": frappe.datetime.month_start(),
            "reqd": 1
        },

        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "default": frappe.datetime.month_end(),
            "reqd": 1
        },

        {
            "fieldname": "billing_status",
            "label": "Billing Status",
            "fieldtype": "Select",
            "options": [
                { "label": "All", "value": "" },
                { "label": "Goods Received but Not Billed", "value": "Pending" },
                { "label": "Bills Cleared (Invoiced)", "value": "Cleared" }
            ],
            "default": ""
        }

    ]
};