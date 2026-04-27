

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
#             "width": 150
#         },
#         {
#             "label": "User Department",
#             "fieldname": "custom_department",   # ✅ changed
#             "fieldtype": "Link",
#             "options": "Department",
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

#     if filters.get("custom_department"):
#         conditions += " AND mr.custom_department = %(custom_department)s"

#     if filters.get("item_code"):
#         conditions += " AND mri.item_code = %(item_code)s"

#     data = frappe.db.sql(f"""
#         SELECT
#             mr.name,
#             mr.transaction_date,
#             mr.custom_department,
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
#     data = get_data(filters or {})
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
#             "width": 150
#         },
#         {
#             "label": "User Department",
#             "fieldname": "custom_department",
#             "fieldtype": "Link",
#             "options": "Department",
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

#     if filters.get("custom_department"):
#         conditions += " AND mr.custom_department = %(custom_department)s"

#     if filters.get("item_code"):
#         conditions += " AND mri.item_code = %(item_code)s"

#     data = frappe.db.sql(f"""
#         SELECT
#             mr.name,
#             mr.transaction_date,
#             mr.custom_department,
#             mri.item_code,
#             mri.qty
#         FROM
#             `tabMaterial Request` mr
#         INNER JOIN
#             `tabMaterial Request Item` mri
#             ON mr.name = mri.parent
#         WHERE
#             mr.docstatus = 1
            
#             AND EXISTS (
#                 SELECT 1
#                 FROM `tabMaterial Request Activity` act
#                 WHERE act.parent = mr.name
#                 AND act.action = 'L3 Approved'
#             )

#             {conditions}

#         ORDER BY
#             mr.transaction_date DESC
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
#             "label":"Material Indent ID",
#             "fieldname":"name",
#             "fieldtype":"Link",
#             "options":"Material Indent",
#             "width":180
#         },
#         {
#             "label":"Transaction Date",
#             "fieldname":"transaction_date",
#             "fieldtype":"Date",
#             "width":130
#         },
#         {
#             "label":"Company",
#             "fieldname":"company",
#             "width":220
#         },
#         {
#             "label":"Department",
#             "fieldname":"department",
#             "width":180
#         },
#         {
#             "label":"Status",
#             "fieldname":"custom_status",
#             "width":180
#         },
#         {
#             "label":"Item Code",
#             "fieldname":"item_code",
#             "width":180
#         },
#         {
#             "label":"Quantity",
#             "fieldname":"qty",
#             "fieldtype":"Float",
#             "width":100
#         }
#     ]


# def get_data(filters):

#     conditions = " WHERE mi.docstatus < 2 "

#     if filters.get("from_date"):
#         conditions += """
#         AND mi.transaction_date >= %(from_date)s
#         """

#     if filters.get("to_date"):
#         conditions += """
#         AND mi.transaction_date <= %(to_date)s
#         """

#     if filters.get("item_code"):
#         conditions += """
#         AND mii.item_code=%(item_code)s
#         """

#     # FIXED STATUS FILTER (using correct field)
#     if filters.get("custom_status"):
#         conditions += """
#         AND mi.custom_indent_status=%(custom_status)s
#         """

#     if filters.get("custom_department") and filters.get("custom_department")!="All Departments":
#         conditions += """
#         AND (
#             EXISTS(
#                 SELECT 1
#                 FROM `tabMaterial Request` mr
#                 WHERE mr.custom_material_indent=mi.name
#                 AND mr.custom_department=%(custom_department)s
#             )

#             OR

#             EXISTS(
#                 SELECT 1
#                 FROM `tabStock Entry` se
#                 WHERE se.custom_material_indent=mi.name
#                 AND se.custom_department=%(custom_department)s
#             )
#         )
#         """


#     data = frappe.db.sql(f"""
#         SELECT
#             mi.name,
#             mi.transaction_date,
#             mi.company,

#             COALESCE(
#                 (
#                     SELECT se.custom_department
#                     FROM `tabStock Entry` se
#                     WHERE se.custom_material_indent=mi.name
#                     LIMIT 1
#                 ),
#                 (
#                     SELECT mr.custom_department
#                     FROM `tabMaterial Request` mr
#                     WHERE mr.custom_material_indent=mi.name
#                     LIMIT 1
#                 )
#             ) as department,

#             mi.custom_indent_status as custom_status,
#             mii.item_code,
#             mii.qty

#         FROM
#             `tabMaterial Indent` mi

#         INNER JOIN
#             `tabMaterial Request Item` mii
#             ON mi.name = mii.parent

#         {conditions}

#         ORDER BY
#             mi.transaction_date DESC

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
#             "label":"Material Indent ID",
#             "fieldname":"name",
#             "fieldtype":"Link",
#             "options":"Material Indent",
#             "width":180
#         },
#         {
#             "label":"Transaction Date",
#             "fieldname":"transaction_date",
#             "fieldtype":"Date",
#             "width":130
#         },
#         {
#             "label":"Company",
#             "fieldname":"company",
#             "width":220
#         },
#         {
#             "label":"Department",
#             "fieldname":"department",
#             "width":180
#         },
#         {
#             "label":"Status",
#             "fieldname":"custom_status",
#             "width":180
#         },
#         {
#             "label":"Item Code",
#             "fieldname":"item_code",
#             "width":180
#         },
#         {
#             "label":"Quantity",
#             "fieldname":"qty",
#             "fieldtype":"Float",
#             "width":100
#         }
#     ]


# def get_data(filters):

#     conditions = " WHERE mi.docstatus < 2 "

#     if filters.get("from_date"):
#         conditions += """
#         AND mi.transaction_date >= %(from_date)s
#         """

#     if filters.get("to_date"):
#         conditions += """
#         AND mi.transaction_date <= %(to_date)s
#         """

#     if filters.get("item_code"):
#         conditions += """
#         AND mii.item_code=%(item_code)s
#         """

#     if filters.get("company"):
#         conditions += """
#         AND mi.company=%(company)s
#         """

#     if filters.get("custom_status"):
#         conditions += """
#         AND mi.custom_indent_status=%(custom_status)s
#         """

#     if filters.get("custom_department") and filters.get("custom_department")!="All Departments":
#         conditions += """
#         AND (
#             EXISTS(
#                 SELECT 1
#                 FROM `tabMaterial Request` mr
#                 WHERE mr.custom_material_indent=mi.name
#                 AND mr.custom_department=%(custom_department)s
#             )

#             OR

#             EXISTS(
#                 SELECT 1
#                 FROM `tabStock Entry` se
#                 WHERE se.custom_material_indent=mi.name
#                 AND se.custom_department=%(custom_department)s
#             )
#         )
#         """


#     data = frappe.db.sql(f"""
#         SELECT
#             mi.name,
#             mi.transaction_date,
#             mi.company,

#             COALESCE(
#                 (
#                     SELECT se.custom_department
#                     FROM `tabStock Entry` se
#                     WHERE se.custom_material_indent=mi.name
#                     LIMIT 1
#                 ),
#                 (
#                     SELECT mr.custom_department
#                     FROM `tabMaterial Request` mr
#                     WHERE mr.custom_material_indent=mi.name
#                     LIMIT 1
#                 )
#             ) as department,

#             mi.custom_indent_status as custom_status,
#             mii.item_code,
#             mii.qty

#         FROM
#             `tabMaterial Indent` mi

#         INNER JOIN
#             `tabMaterial Request Item` mii
#             ON mi.name = mii.parent

#         {conditions}

#         ORDER BY
#             mi.transaction_date DESC

#     """, filters, as_dict=1)

#     return data


import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {
            "label":"Material Indent ID",
            "fieldname":"name",
            "fieldtype":"Link",
            "options":"Material Indent",
            "width":180
        },
        {
            "label":"Transaction Date",
            "fieldname":"transaction_date",
            "fieldtype":"Date",
            "width":130
        },
        {
            "label":"Company",
            "fieldname":"company",
            "width":220
        },
        {
            "label":"Department",
            "fieldname":"department",
            "width":180
        },
        {
            "label":"Status",
            "fieldname":"custom_status",
            "width":180
        },
        {
            "label":"Item Code",
            "fieldname":"item_code",
            "width":180
        },
        {
            "label":"Quantity",
            "fieldname":"qty",
            "fieldtype":"Float",
            "width":100
        }
    ]


def get_data(filters):

    conditions = " WHERE mi.docstatus < 2 "

    if filters.get("from_date"):
        conditions += """
        AND mi.transaction_date >= %(from_date)s
        """

    if filters.get("to_date"):
        conditions += """
        AND mi.transaction_date <= %(to_date)s
        """

    if filters.get("item_code"):
        conditions += """
        AND mii.item_code=%(item_code)s
        """

    if filters.get("company"):
        conditions += """
        AND mi.company=%(company)s
        """

    if filters.get("custom_status"):
        conditions += """
        AND mi.custom_indent_status=%(custom_status)s
        """

    # only department part changed
    if filters.get("custom_department"):
        conditions += """
        AND (
            CASE
                WHEN mi.custom_username LIKE '%% - %%'
                THEN TRIM(SUBSTRING_INDEX(mi.custom_username,' - ',-1))
                ELSE mi.custom_username
            END
        ) = %(custom_department)s
        """


    data = frappe.db.sql(f"""
        SELECT
            mi.name,
            mi.transaction_date,
            mi.company,

            CASE
                WHEN mi.custom_username LIKE '%% - %%'
                THEN TRIM(SUBSTRING_INDEX(mi.custom_username,' - ',-1))
                ELSE mi.custom_username
            END as department,

            mi.custom_indent_status as custom_status,
            mii.item_code,
            mii.qty

        FROM
            `tabMaterial Indent` mi

        INNER JOIN
            `tabMaterial Request Item` mii
            ON mi.name = mii.parent

        {conditions}

        ORDER BY
            mi.transaction_date DESC

    """, filters, as_dict=1)

    return data