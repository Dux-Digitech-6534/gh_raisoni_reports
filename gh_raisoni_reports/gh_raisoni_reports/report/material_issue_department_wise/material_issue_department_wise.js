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
            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            options: "Company"
        },
        {
            fieldname: "custom_department",
            label: "User Department",
            fieldtype: "Link",
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