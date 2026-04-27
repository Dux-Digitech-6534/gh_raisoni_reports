# import frappe

# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data


# def get_columns():
#     return [
#         {
#             "label": "Stock Entry",
#             "fieldname": "name",
#             "fieldtype": "Link",
#             "options": "Stock Entry",
#             "width": 180
#         },
#         {
#             "label": "Posting Date",
#             "fieldname": "posting_date",
#             "fieldtype": "Date",
#             "width": 120
#         },
#         {
#             "label": "User / Department",
#             "fieldname": "custom_username",
#             "fieldtype": "Data",
#             "width": 200
#         },
#         {
#             "label": "Item Code",
#             "fieldname": "item_code",
#             "fieldtype": "Link",
#             "options": "Item",
#             "width": 150
#         },
#         {
#             "label": "Item Name",
#             "fieldname": "item_name",
#             "fieldtype": "Data",
#             "width": 180
#         },
#         {
#             "label": "Qty",
#             "fieldname": "qty",
#             "fieldtype": "Float",
#             "width": 100
#         },
#         {
#             "label": "UOM",
#             "fieldname": "uom",
#             "fieldtype": "Data",
#             "width": 80
#         },
#         {
#             "label": "Warehouse",
#             "fieldname": "s_warehouse",
#             "fieldtype": "Link",
#             "options": "Warehouse",
#             "width": 180
#         }
#     ]


# def get_data(filters):
#     conditions = ""

#     if filters.get("from_date") and filters.get("to_date"):
#         conditions += " AND se.posting_date BETWEEN %(from_date)s AND %(to_date)s"

#     if filters.get("custom_username"):
#         conditions += " AND se.custom_username = %(custom_username)s"

#     if filters.get("item_code"):
#         conditions += " AND sed.item_code = %(item_code)s"

#     data = frappe.db.sql(f"""
#         SELECT
#             se.name,
#             se.posting_date,
#             se.custom_username,
#             sed.item_code,
#             sed.item_name,
#             sed.qty,
#             sed.uom,
#             sed.s_warehouse
#         FROM
#             `tabStock Entry` se
#         INNER JOIN
#             `tabStock Entry Detail` sed
#             ON se.name = sed.parent
#         WHERE
#             se.stock_entry_type = 'Material Issue'   -- 🔥 IMPORTANT FILTER
#             AND se.docstatus = 1                     -- only submitted
#             {conditions}
#         ORDER BY
#             se.posting_date DESC
#     """, filters, as_dict=1)

#     return data


# import frappe

# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data


# def get_columns():
#     return [
#         {
#             "label": "Material Issue ID",
#             "fieldname": "name",
#             "fieldtype": "Link",
#             "options": "Stock Entry",
#             "width": 180
#         },
#         {
#             "label": "Posting Date",
#             "fieldname": "posting_date",
#             "fieldtype": "Date",
#             "width": 120
#         },
#         {
#             "label": "User Department",
#             "fieldname": "custom_department",   # ✅ replaced
#             "fieldtype": "Link",
#             "options": "Department",
#             "width": 200
#         },
#         {
#             "label": "Item Code",
#             "fieldname": "item_code",
#             "fieldtype": "Link",
#             "options": "Item",
#             "width": 150
#         },
       
#         {
#             "label": "Qty",
#             "fieldname": "qty",
#             "fieldtype": "Float",
#             "width": 100
#         },
#         {
#             "label": "UOM",
#             "fieldname": "uom",
#             "fieldtype": "Data",
#             "width": 80
#         },
#         {
#             "label": "Warehouse",
#             "fieldname": "s_warehouse",
#             "fieldtype": "Link",
#             "options": "Warehouse",
#             "width": 180
#         }
#     ]


# def get_data(filters):
#     conditions = ""

#     if filters.get("from_date") and filters.get("to_date"):
#         conditions += " AND se.posting_date BETWEEN %(from_date)s AND %(to_date)s"

#     if filters.get("custom_department"):   # ✅ replaced
#         conditions += " AND se.custom_department = %(custom_department)s"

#     if filters.get("item_code"):
#         conditions += " AND sed.item_code = %(item_code)s"

#     data = frappe.db.sql(f"""
#         SELECT
#             se.name,
#             se.posting_date,
#             se.custom_department,   -- ✅ replaced
#             sed.item_code,
#             sed.item_name,
#             sed.qty,
#             sed.uom,
#             sed.s_warehouse
#         FROM
#             `tabStock Entry` se
#         INNER JOIN
#             `tabStock Entry Detail` sed
#             ON se.name = sed.parent
#         WHERE
#             se.stock_entry_type = 'Material Issue'
#             AND se.docstatus = 1
#             {conditions}
#         ORDER BY
#             se.posting_date DESC
#     """, filters, as_dict=1)

#     return data




# import frappe

# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters or {})
#     return columns, data


# def get_columns():
#     return [
#         {
#             "label": "Material Issue ID",
#             "fieldname": "name",
#             "fieldtype": "Link",
#             "options": "Stock Entry",
#             "width": 180
#         },
#         {
#             "label": "Posting Date",
#             "fieldname": "posting_date",
#             "fieldtype": "Date",
#             "width": 120
#         },
#         {
#             "label": "User Department",
#             "fieldname": "custom_department",
#             "fieldtype": "Link",
#             "options": "Department",
#             "width": 200
#         },
#         {
#             "label": "Item Code",
#             "fieldname": "item_code",
#             "fieldtype": "Link",
#             "options": "Item",
#             "width": 180
#         },
#         {
#             "label": "Qty",
#             "fieldname": "qty",
#             "fieldtype": "Float",
#             "width": 100
#         },
#         {
#             "label": "UOM",
#             "fieldname": "uom",
#             "fieldtype": "Data",
#             "width": 100
#         },
#         {
#             "label": "Warehouse",
#             "fieldname": "s_warehouse",
#             "fieldtype": "Link",
#             "options": "Warehouse",
#             "width": 180
#         }
#     ]


# def get_data(filters):
#     conditions = ""

#     if filters.get("from_date") and filters.get("to_date"):
#         conditions += " AND se.posting_date BETWEEN %(from_date)s AND %(to_date)s"

#     if filters.get("custom_department"):
#         conditions += " AND se.custom_department = %(custom_department)s"

#     if filters.get("item_code"):
#         conditions += " AND sed.item_code = %(item_code)s"

#     data = frappe.db.sql("""
#         SELECT
#             se.name,
#             se.posting_date,
#             se.custom_department,
#             sed.item_code,
#             sed.qty,
#             sed.uom,
#             sed.s_warehouse
#         FROM `tabStock Entry` se
#         INNER JOIN `tabStock Entry Detail` sed
#             ON se.name = sed.parent
#         WHERE
#             se.stock_entry_type = 'Material Issue'
#             AND se.docstatus = 1
#             {conditions}
#         ORDER BY
#             se.posting_date DESC
#     """.format(conditions=conditions), filters, as_dict=1)

#     return data

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {
            "label": "Material Issue ID",
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Stock Entry",
            "width": 180
        },
        {
            "label": "Posting Date",
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label":"Company",
            "fieldname":"company",
            "fieldtype":"Link",
            "options":"Company",
            "width":180
        },
        {
            "label": "User Department",
            "fieldname": "custom_department",
            "fieldtype": "Link",
            "options": "Department",
            "width": 200
        },
        {
            "label": "Item Code",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 180
        },
        {
            "label": "Qty",
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": "UOM",
            "fieldname": "uom",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": "Warehouse",
            "fieldname": "s_warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 180
        }
    ]


def get_data(filters):
    conditions = ""

    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND se.posting_date BETWEEN %(from_date)s AND %(to_date)s"

    if filters.get("custom_department"):
        conditions += " AND se.custom_department = %(custom_department)s"

    if filters.get("company"):
        conditions += " AND se.company = %(company)s"

    if filters.get("item_code"):
        conditions += " AND sed.item_code = %(item_code)s"

    data = frappe.db.sql("""
        SELECT
            se.name,
            se.posting_date,
            se.company,
            se.custom_department,
            sed.item_code,
            sed.qty,
            sed.uom,
            sed.s_warehouse

        FROM `tabStock Entry` se

        INNER JOIN `tabStock Entry Detail` sed
            ON se.name = sed.parent

        WHERE
            se.stock_entry_type='Material Issue'
            AND se.docstatus=1
            {conditions}

        ORDER BY
            se.posting_date DESC
    """.format(conditions=conditions), filters, as_dict=1)

    return data