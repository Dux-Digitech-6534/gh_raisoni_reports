

// frappe.query_reports["Cost Centre and Department wise Requisition Register"] = {
//     "filters": [
//         {
//             "fieldname": "from_date",
//             "label": "From Date",
//             "fieldtype": "Date",
//             "reqd": 1
//         },
//         {
//             "fieldname": "to_date",
//             "label": "To Date",
//             "fieldtype": "Date",
//             "reqd": 1
//         },
//         {
//             "fieldname": "users_department",
//             "label": "Users Department",
//             "fieldtype": "Link",
//             "options": "Department"
//         },
//         {
//             "fieldname": "item_code",
//             "label": "Item Code",
//             "fieldtype": "Link",
//             "options": "Item"
//         }
//     ]
// };


// frappe.query_reports["Cost Centre and Department wise Requisition Register"] = {
//     "filters": [
//         {
//             "fieldname": "from_date",
//             "label": "From Date",
//             "fieldtype": "Date",
//             "reqd": 1
//         },
//         {
//             "fieldname": "to_date",
//             "label": "To Date",
//             "fieldtype": "Date",
//             "reqd": 1
//         },
//         {
//             "fieldname": "custom_username",   // ✅ changed
//             "label": "Username",
//             "fieldtype": "Data"               // ✅ Link nahi, Data
//         },
//         {
//             "fieldname": "item_code",
//             "label": "Item Code",
//             "fieldtype": "Link",
//             "options": "Item"
//         }
//     ]
// };


// frappe.query_reports["Cost Centre and Department wise Requisition Register"] = {
//     "filters": [
//         {
//             "fieldname": "from_date",
//             "label": "From Date",
//             "fieldtype": "Date",
//             "reqd": 1
//         },
//         {
//             "fieldname": "to_date",
//             "label": "To Date",
//             "fieldtype": "Date",
//             "reqd": 1
//         },
//         {
//             "fieldname": "custom_department",   // ✅ Link field
//             "label": "User Department",
//             "fieldtype": "Link",
//             "options": "Department"             // ✅ important
//         },
//         {
//             "fieldname": "item_code",
//             "label": "Item Code",
//             "fieldtype": "Link",
//             "options": "Item"
//         }
//     ]
// };




// frappe.query_reports["Cost Centre and Department wise Requisition Register"] = {
//     filters: [
//         {
//             fieldname:"from_date",
//             label:"From Date",
//             fieldtype:"Date",
//             reqd:1
//         },
//         {
//             fieldname:"to_date",
//             label:"To Date",
//             fieldtype:"Date",
//             reqd:1
//         },
//         {
//             fieldname:"custom_department",
//             label:"User Department",
//             fieldtype:"Link",
//             options:"Department"
//         },
//         {
//             fieldname:"item_code",
//             label:"Item Code",
//             fieldtype:"Link",
//             options:"Item"
//         },
//         {
//             fieldname:"custom_status",
//             label:"Status",
//             fieldtype:"Select",
//             options:"\nOpen\nPurchase Request Raised\nPartially Issued\nClosed"
//         }
//     ]
// };

frappe.query_reports["Cost Centre and Department wise Requisition Register"] = {
    filters: [
        {
            fieldname:"from_date",
            label:"From Date",
            fieldtype:"Date",
            reqd:1
        },
        {
            fieldname:"to_date",
            label:"To Date",
            fieldtype:"Date",
            reqd:1
        },
         {
            fieldname:"company",
            label:"Company",
            fieldtype:"Link",
            options:"Company"
        },
        {
            fieldname:"custom_department",
            label:"User Department",
            fieldtype:"Link",
            options:"Department"
        },
       
        {
            fieldname:"item_code",
            label:"Item Code",
            fieldtype:"Link",
            options:"Item"
        },
        {
            fieldname:"custom_status",
            label:"Status",
            fieldtype:"Select",
            options:"\nOpen\nPurchase Request Raised\nPartially Issued\nClosed"
        }
    ]
};