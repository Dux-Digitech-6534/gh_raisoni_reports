

// frappe.query_reports["Department Wise Indent Register New"] = {
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
//             "fieldname":"company",
//             "label":"Company",
//             "fieldtype":"Link",
//             "options":"Company"
//         },
//        {
//             fieldname: "custom_department",
//             label: "User Department",
//             fieldtype: "Link",
//             options: "Department"
//         },
        
//         {
//             "fieldname": "item_code",
//             "label": "Item Code",
//             "fieldtype": "Link",
//             "options": "Item"
//         }
//     ]
// };


frappe.query_reports["Department Wise Indent Register New"] = {

    filters: [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.month_start()
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.month_end()
        },
        {
            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company")
        },
        {
            fieldname: "user_name",
            label: "User Name",
            fieldtype: "Data"
        },
        {
            fieldname: "custom_department",
            label: "User Department",
            fieldtype: "Link",
            options: "Department"
        },
        {
            fieldname: "item_code",
            label: "Item Code",
            fieldtype: "Link",
            options: "Item"
        }
    ],

    // ✅ Excel & PDF buttons under Download
    onload: function(report) {
        setTimeout(function() {
            report.page.add_inner_button(__("Excel"), function() {
                frappe.query_report.export_report("Excel");
            }, __("Download"));

            report.page.add_inner_button(__("PDF"), function() {
                frappe.query_report.export_report("PDF");
            }, __("Download"));
        }, 1000);
    }
};