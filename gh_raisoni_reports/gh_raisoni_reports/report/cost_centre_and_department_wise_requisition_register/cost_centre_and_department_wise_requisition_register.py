

# import frappe
# from frappe import _

# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data


# def get_columns():
#     return [
#         {
#             "label": "Material Request ID",
#             "fieldname": "name",
#             "fieldtype": "Link",
#             "options": "Material Request",
#             "width": 180
#         },
#         {
#             "label": "Transaction Date",
#             "fieldname": "transaction_date",
#             "fieldtype": "Date",
#             "width": 180
#         },
#         {
#             "label": "User Department",
#             "fieldname": "users_department",
#             "fieldtype": "Link",
#             "options": "Department",
#             "width": 180
#         },
#         {
#             "label": "Item Code",
#             "fieldname": "item_code",
#             "fieldtype": "Link",
#             "label": "Users Department",
#             "options": "Item",
#             "width": 180
#         },
#         {
#             "label": "Quantity",
#             "fieldname": "qty",
#             "fieldtype": "Float",
#             "width": 100
#         }
#     ]


# def get_data(filters):
#     conditions = ""

#     if filters.get("from_date") and filters.get("to_date"):
#         conditions += " AND mr.transaction_date BETWEEN %(from_date)s AND %(to_date)s"

#     if filters.get("users_department"):
#         conditions += " AND mr.users_department = %(users_department)s"

#     if filters.get("item_code"):
#         conditions += " AND mri.item_code = %(item_code)s"

#     data = frappe.db.sql(f"""
#         SELECT
#             mr.name,
#             mr.transaction_date,
#             mr.users_department,
#             mri.item_code,
#             mri.qty
#         FROM
#             `tabMaterial Request` mr
#         INNER JOIN
#             `tabMaterial Request Item` mri
#             ON mr.name = mri.parent
#         WHERE
#             1=1
#             {conditions}
#         ORDER BY
#             mr.transaction_date DESC
#     """, filters, as_dict=1)

#     return data




# import frappe
# from frappe import _

# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data


# def get_columns():
#     return [
#         {
#             "label": "Material Request ID",
#             "fieldname": "name",
#             "fieldtype": "Link",
#             "options": "Material Request",
#             "width": 180
#         },
#         {
#             "label": "Transaction Date",
#             "fieldname": "transaction_date",
#             "fieldtype": "Date",
#             "width": 180
#         },
#         {
#             "label": "Username",
#             "fieldname": "custom_username",   # ✅ changed
#             "fieldtype": "Data",
#             "width": 180
#         },
#         {
#             "label": "Item Code",
#             "fieldname": "item_code",
#             "fieldtype": "Link",
#             "options": "Item",
#             "width": 180
#         },
#         {
#             "label": "Quantity",
#             "fieldname": "qty",
#             "fieldtype": "Float",
#             "width": 100
#         }
#     ]


# def get_data(filters):
#     conditions = ""

#     if filters.get("from_date") and filters.get("to_date"):
#         conditions += " AND mr.transaction_date BETWEEN %(from_date)s AND %(to_date)s"

#     if filters.get("custom_username"):   # ✅ changed
#         conditions += " AND mr.custom_username = %(custom_username)s"

#     if filters.get("item_code"):
#         conditions += " AND mri.item_code = %(item_code)s"

#     data = frappe.db.sql(f"""
#         SELECT
#             mr.name,
#             mr.transaction_date,
#             mr.custom_username,   -- ✅ changed
#             mri.item_code,
#             mri.qty
#         FROM
#             `tabMaterial Request` mr
#         INNER JOIN
#             `tabMaterial Request Item` mri
#             ON mr.name = mri.parent
#         WHERE
#             1=1
#             {conditions}
#         ORDER BY
#             mr.transaction_date DESC
#     """, filters, as_dict=1)

#     return data


import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": "Material Request ID",
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Material Request",
            "width": 180
        },
        {
            "label": "Transaction Date",
            "fieldname": "transaction_date",
            "fieldtype": "Date",
            "width": 150
        },
        {
            "label": "User Department",
            "fieldname": "custom_department",   # ✅ changed
            "fieldtype": "Link",
            "options": "Department",
            "width": 180
        },
        {
            "label": "Item Code",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 180
        },
        {
            "label": "Quantity",
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 100
        }
    ]


def get_data(filters):
    conditions = ""

    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND mr.transaction_date BETWEEN %(from_date)s AND %(to_date)s"

    if filters.get("custom_department"):
        conditions += " AND mr.custom_department = %(custom_department)s"

    if filters.get("item_code"):
        conditions += " AND mri.item_code = %(item_code)s"

    data = frappe.db.sql(f"""
        SELECT
            mr.name,
            mr.transaction_date,
            mr.custom_department,
            mri.item_code,
            mri.qty
        FROM
            `tabMaterial Request` mr
        INNER JOIN
            `tabMaterial Request Item` mri
            ON mr.name = mri.parent
        WHERE
            1=1
            {conditions}
        ORDER BY
            mr.transaction_date DESC
    """, filters, as_dict=1)

    return data