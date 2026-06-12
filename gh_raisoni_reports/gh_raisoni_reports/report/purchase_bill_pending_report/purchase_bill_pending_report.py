# # Copyright (c) 2026, Abhijeet and contributors
# # For license information, please see license.txt

# # import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data
# import frappe

# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data


# def get_columns():
#     return [
#         {"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
#         {"label": "Tracking Number", "fieldname": "grn", "fieldtype": "Link", "options": "Purchase Receipt", "width": 150},
#         {"label": "Party's Name", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
#         {"label": "Name of Item", "fieldname": "item_name", "fieldtype": "Data", "width": 220},
#         {"label": "Initial Qty", "fieldname": "qty", "fieldtype": "Float", "width": 100},
#         {"label": "Pending Qty", "fieldname": "pending_qty", "fieldtype": "Float", "width": 100},
#         {"label": "Rate", "fieldname": "rate", "fieldtype": "Currency", "width": 100},
#         {"label": "Value", "fieldname": "amount", "fieldtype": "Currency", "width": 120},
#         {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
#     ]


# def get_data(filters):
#     conditions = ""

#     if filters.get("company"):
#         conditions += " AND pr.company = %(company)s"

#     if filters.get("supplier"):
#         conditions += " AND pr.supplier = %(supplier)s"

#     if filters.get("from_date") and filters.get("to_date"):
#         conditions += " AND pr.posting_date BETWEEN %(from_date)s AND %(to_date)s"

#     billing_condition = ""

#     if filters.get("billing_status") == "Pending":
#         billing_condition = """
#             AND NOT EXISTS (
#                 SELECT 1 FROM `tabPurchase Invoice Item` pii
#                 WHERE pii.purchase_receipt = pr.name
#             )
#         """
#     elif filters.get("billing_status") == "Cleared":
#         billing_condition = """
#             AND EXISTS (
#                 SELECT 1 FROM `tabPurchase Invoice Item` pii
#                 WHERE pii.purchase_receipt = pr.name
#             )
#         """

#     data = frappe.db.sql(f"""
#         SELECT
#             pr.posting_date,
#             pr.name as grn,
#             pr.supplier,
#             pri.item_name,
#             pri.qty,

#             pri.qty - IFNULL((
#                 SELECT SUM(pii.qty)
#                 FROM `tabPurchase Invoice Item` pii
#                 WHERE pii.purchase_receipt = pr.name
#                 AND pii.item_code = pri.item_code
#             ), 0) as pending_qty,

#             pri.rate,
#             (pri.qty * pri.rate) as amount,

#             CASE 
#                 WHEN EXISTS (
#                     SELECT 1 FROM `tabPurchase Invoice Item` pii
#                     WHERE pii.purchase_receipt = pr.name
#                 ) THEN 'Cleared'
#                 ELSE 'Pending'
#             END as status

#         FROM `tabPurchase Receipt` pr
#         INNER JOIN `tabPurchase Receipt Item` pri
#             ON pri.parent = pr.name

#         WHERE pr.docstatus = 1
#         {conditions}
#         {billing_condition}

#         ORDER BY pr.posting_date DESC
#     """, filters, as_dict=1)

#     return data


# Durgesh sir code--------------------

# import frappe

# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data


# def get_columns():
#     return [
#         {"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
#         {"label": "Tracking Number", "fieldname": "grn", "fieldtype": "Link", "options": "Purchase Receipt", "width": 150},
#         {"label": "Party's Name", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
#         {"label": "Name of Item", "fieldname": "item_name", "fieldtype": "Data", "width": 220},
#         {"label": "Initial Qty", "fieldname": "qty", "fieldtype": "Float", "width": 100},
#         {"label": "Pending Qty", "fieldname": "pending_qty", "fieldtype": "Float", "width": 100},
#         {"label": "Rate", "fieldname": "rate", "fieldtype": "Currency", "width": 100},
#         {"label": "Value", "fieldname": "amount", "fieldtype": "Currency", "width": 120},
#     ]


# def get_data(filters):
#     conditions = ""

#     if filters.get("company"):
#         conditions += " AND pr.company = %(company)s"

#     if filters.get("supplier"):
#         conditions += " AND pr.supplier = %(supplier)s"

#     if filters.get("from_date") and filters.get("to_date"):
#         conditions += " AND pr.posting_date BETWEEN %(from_date)s AND %(to_date)s"

#     billing_condition = ""

#     # ✅ Billing Status Filter
#     if filters.get("billing_status") == "Pending":
#         billing_condition = """
#             AND NOT EXISTS (
#                 SELECT 1 FROM `tabPurchase Invoice Item` pii
#                 WHERE pii.purchase_receipt = pr.name
#             )
#         """
#     elif filters.get("billing_status") == "Cleared":
#         billing_condition = """
#             AND EXISTS (
#                 SELECT 1 FROM `tabPurchase Invoice Item` pii
#                 WHERE pii.purchase_receipt = pr.name
#             )
#         """

#     data = frappe.db.sql(f"""
#         SELECT
#             pr.posting_date,
#             pr.name as grn,
#             pr.supplier,
#             pri.item_name,
#             pri.qty,

#             pri.qty - IFNULL((
#                 SELECT SUM(pii.qty)
#                 FROM `tabPurchase Invoice Item` pii
#                 WHERE pii.purchase_receipt = pr.name
#                 AND pii.item_code = pri.item_code
#             ), 0) as pending_qty,

#             pri.rate,

#             (
#                 (pri.qty - IFNULL((
#                     SELECT SUM(pii.qty)
#                     FROM `tabPurchase Invoice Item` pii
#                     WHERE pii.purchase_receipt = pr.name
#                     AND pii.item_code = pri.item_code
#                 ), 0)) * pri.rate
#             ) as amount

#         FROM `tabPurchase Receipt` pr
#         INNER JOIN `tabPurchase Receipt Item` pri
#             ON pri.parent = pr.name

#         WHERE pr.docstatus = 1
#         {conditions}
#         {billing_condition}

#         ORDER BY pr.posting_date DESC
#     """, filters, as_dict=1)

#     return data











import frappe

def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": "Tracking Number", "fieldname": "grn", "fieldtype": "Link", "options": "Purchase Receipt", "width": 150},
        {"label": "Party's Name", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
        {"label": "Name of Item", "fieldname": "item_name", "fieldtype": "Data", "width": 220},
        {"label": "Initial Qty", "fieldname": "qty", "fieldtype": "Float", "width": 100},
        {"label": "Pending Qty", "fieldname": "pending_qty", "fieldtype": "Float", "width": 100},
        {"label": "Rate", "fieldname": "rate", "fieldtype": "Currency", "width": 100},
        {"label": "Value", "fieldname": "amount", "fieldtype": "Currency", "width": 120},
    ]


def get_data(filters):
    conditions = ""

    if filters.get("company"):
        conditions += " AND pr.company = %(company)s"

    if filters.get("supplier"):
        conditions += " AND pr.supplier = %(supplier)s"

    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND pr.posting_date BETWEEN %(from_date)s AND %(to_date)s"

    data = frappe.db.sql(f"""
        SELECT
            x.posting_date,
            x.grn,
            x.supplier,
            x.item_name,
            x.qty,
            x.pending_qty,
            x.rate,
            x.amount
        FROM (
            SELECT
                pr.posting_date,
                pr.name AS grn,
                pr.supplier,
                pri.item_name,
                pri.qty,

                GREATEST(
                    pri.qty - IFNULL(billed.billed_qty, 0),
                    0
                ) AS pending_qty,

                pri.rate,

                GREATEST(
                    pri.qty - IFNULL(billed.billed_qty, 0),
                    0
                ) * pri.rate AS amount

            FROM `tabPurchase Receipt` pr

            INNER JOIN `tabPurchase Receipt Item` pri
                ON pri.parent = pr.name

            LEFT JOIN (
                SELECT
                    pii.pr_detail,
                    SUM(pii.qty) AS billed_qty
                FROM `tabPurchase Invoice Item` pii
                INNER JOIN `tabPurchase Invoice` pi
                    ON pi.name = pii.parent
                WHERE pi.docstatus = 1
                AND pii.pr_detail IS NOT NULL
                GROUP BY pii.pr_detail
            ) billed
                ON billed.pr_detail = pri.name

            WHERE pr.docstatus = 1
            {conditions}
        ) x

        WHERE
            CASE
                WHEN %(billing_status)s = 'Pending' THEN x.pending_qty > 0
                WHEN %(billing_status)s = 'Cleared' THEN x.pending_qty = 0
                ELSE 1 = 1
            END

        ORDER BY x.posting_date DESC
    """, {
        "company": filters.get("company"),
        "supplier": filters.get("supplier"),
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "billing_status": filters.get("billing_status") or ""
    }, as_dict=1)

    return data