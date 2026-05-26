// // Copyright (c) 2026, Abhijeet and contributors
// // For license information, please see license.txt

// frappe.query_reports["Department Wise Indent Register"] = {
// 	"filters": [

// 	]
// };




// frappe.query_reports["Department Wise Indent Register"] = {
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
//             "fieldname": "custom_department",
//             "label": "User Department",
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



// frappe.query_reports["Department Wise Indent Register"] = {
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
//         {
//             "fieldname": "custom_department",
//             "label": "User Department",
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



frappe.query_reports["Department Wise Indent Register"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.month_start()
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.nowdate()
        },
        {
            "fieldname": "company",
            "label": "Company",
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company")
        },
        {
            "fieldname": "custom_department",
            "label": "User Department",
            "fieldtype": "Select",
            "options": "",          // populated dynamically in onload
        },
        {
            "fieldname": "item_code",
            "label": "Item Code",
            "fieldtype": "Link",
            "options": "Item"
        }
    ],

    onload: function(report) {
        // Dynamically load all distinct custom_username values from Material Indent
        // so the dropdown shows entries like "Administrator - All Departments"
        frappe.db.get_list("Material Indent", {
            fields: ["custom_username"],
            filters: { docstatus: ["<", 2] },
            group_by: "custom_username",
            limit: 500
        }).then(rows => {
            // Build a unique sorted list of values
            let options = [...new Set(
                rows
                    .map(r => r.custom_username)
                    .filter(v => v)
                    .sort()
            )];

            // Prepend blank so user can clear the filter
            options.unshift("");

            // Update the filter's option list
            let filter = report.get_filter("custom_department");
            if (filter) {
                filter.df.options = options.join("\n");
                filter.refresh();
            }
        });
    }
};