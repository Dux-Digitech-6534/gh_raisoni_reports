

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

#     # only department part changed
#     if filters.get("custom_department"):
#         conditions += """
#         AND (
#             CASE
#                 WHEN mi.custom_username LIKE '%% - %%'
#                 THEN TRIM(SUBSTRING_INDEX(mi.custom_username,' - ',-1))
#                 ELSE mi.custom_username
#             END
#         ) = %(custom_department)s
#         """


#     data = frappe.db.sql(f"""
#         SELECT
#             mi.name,
#             mi.transaction_date,
#             mi.company,

#             CASE
#                 WHEN mi.custom_username LIKE '%% - %%'
#                 THEN TRIM(SUBSTRING_INDEX(mi.custom_username,' - ',-1))
#                 ELSE mi.custom_username
#             END as department,

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
#             "label": "Material Indent ID",
#             "fieldname": "name",
#             "fieldtype": "Link",
#             "options": "Material Indent",
#             "width": 180
#         },
#         {
#             "label": "Transaction Date",
#             "fieldname": "transaction_date",
#             "fieldtype": "Date",
#             "width": 130
#         },
#         {
#             "label": "Company",
#             "fieldname": "company",
#             "width": 220
#         },
#         {
#             "label": "Department",
#             "fieldname": "department",
#             "width": 180
#         },
#         {
#             "label": "Status",
#             "fieldname": "custom_status",
#             "width": 180
#         },
#         {
#             "label": "Item Code",
#             "fieldname": "item_code",
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

#     conditions = " WHERE mi.docstatus < 2 "

#     if filters.get("from_date"):
#         conditions += " AND mi.transaction_date >= %(from_date)s"

#     if filters.get("to_date"):
#         conditions += " AND mi.transaction_date <= %(to_date)s"

#     if filters.get("item_code"):
#         conditions += " AND mii.item_code = %(item_code)s"

#     if filters.get("company"):
#         conditions += " AND mi.company = %(company)s"

#     if filters.get("custom_status"):
#         conditions += " AND mi.custom_indent_status = %(custom_status)s"

#     # ✅ FINAL DEPARTMENT FILTER (MIDDLE PART ONLY)
#     if filters.get("custom_department"):
#         conditions += """
#         AND (
#             CASE
#                 WHEN mi.custom_username LIKE '%% - %% - %%'
#                 THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(mi.custom_username, ' - ', 2), ' - ', -1))
#                 WHEN mi.custom_username LIKE '%% - %%'
#                 THEN TRIM(SUBSTRING_INDEX(mi.custom_username, ' - ', 1))
#                 ELSE mi.custom_username
#             END
#         ) = %(custom_department)s
#         """

#     data = frappe.db.sql(f"""
#         SELECT
#             mi.name,
#             mi.transaction_date,
#             mi.company,

#             -- ✅ FINAL DEPARTMENT LOGIC
#             CASE
#                 WHEN mi.custom_username LIKE '%% - %% - %%'
#                 THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(mi.custom_username, ' - ', 2), ' - ', -1))
#                 WHEN mi.custom_username LIKE '%% - %%'
#                 THEN TRIM(SUBSTRING_INDEX(mi.custom_username, ' - ', 1))
#                 ELSE mi.custom_username
#             END as department,

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
            "label": "Material Indent ID",
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Material Indent",
            "width": 180
        },
        {
            "label": "Transaction Date",
            "fieldname": "transaction_date",
            "fieldtype": "Date",
            "width": 130
        },
        {
            "label": "Company",
            "fieldname": "company",
            "width": 220
        },
        {
            "label": "Department",
            "fieldname": "department",
            "width": 180
        },
        {
            "label": "Status",
            "fieldname": "custom_status",
            "width": 180
        },
        {
            "label": "Item Code",
            "fieldname": "item_code",
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

    conditions = " WHERE mi.docstatus < 2 "

    if filters.get("from_date"):
        conditions += " AND mi.transaction_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND mi.transaction_date <= %(to_date)s"

    if filters.get("item_code"):
        conditions += " AND mii.item_code = %(item_code)s"

    if filters.get("company"):
        conditions += " AND mi.company = %(company)s"

    if filters.get("custom_status"):
        conditions += " AND mi.custom_indent_status = %(custom_status)s"

    # ✅ SAME FILTER LOGIC (bas correct extraction)
    if filters.get("custom_department"):
        conditions += """
        AND TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(mi.custom_username, ' - ', 2), ' - ', -1)) = %(custom_department)s
        """


    data = frappe.db.sql(f"""
        SELECT
            mi.name,
            mi.transaction_date,
            mi.company,

            -- ✅ FINAL FORMAT (Dept - Code)
            CONCAT(
                TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(mi.custom_username, ' - ', 2), ' - ', -1)),
                ' - ',
                TRIM(SUBSTRING_INDEX(mi.custom_username, ' - ', -1))
            ) as department,

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