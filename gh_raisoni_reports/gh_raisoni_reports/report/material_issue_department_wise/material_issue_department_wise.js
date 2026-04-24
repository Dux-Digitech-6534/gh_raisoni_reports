// frappe.query_reports["Material Issue Department Wise"] = {
//     "filters": [
//         {
//             fieldname: "from_date",
//             label: "From Date",
//             fieldtype: "Date",
//             reqd: 1
//         },
//         {
//             fieldname: "to_date",
//             label: "To Date",
//             fieldtype: "Date",
//             reqd: 1
//         },
//         {
//             fieldname: "custom_username",
//             label: "User / Department",
//             fieldtype: "Data"
//         },
//         {
//             fieldname: "item_code",
//             label: "Item",
//             fieldtype: "Link",
//             options: "Item"
//         }
//     ]
// };

frappe.query_reports["Material Issue Department Wise"] = {
    "filters": [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            reqd: 1
        },
        {
            fieldname: "custom_department",   // ✅ replaced
            label: "User Department",
            fieldtype: "Link",                // ✅ better for department
            options: "Department"
        },
        {
            fieldname: "item_code",
            label: "Item",
            fieldtype: "Link",
            options: "Item"
        }
    ]
};