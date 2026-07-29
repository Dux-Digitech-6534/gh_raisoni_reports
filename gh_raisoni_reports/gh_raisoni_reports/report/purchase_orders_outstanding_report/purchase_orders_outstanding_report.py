import frappe
from frappe.utils import today, date_diff, getdate, flt


def execute(filters=None):
    filters = frappe._dict(filters or {})

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {
            "label": "Date",
            "fieldname": "transaction_date",
            "fieldtype": "Date",
            "width": 100,
        },
        {
            "label": "Order Number",
            "fieldname": "po",
            "fieldtype": "Link",
            "options": "Purchase Order",
            "width": 150,
        },
        {
            "label": "Party's Name",
            "fieldname": "supplier",
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 180,
        },
        {
            "label": "Name of Item",
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 220,
        },
        {
            "label": "Ordered Qty",
            "fieldname": "ordered_qty",
            "fieldtype": "Float",
            "width": 100,
        },
        {
            "label": "Balance Qty",
            "fieldname": "balance_qty",
            "fieldtype": "Float",
            "width": 100,
        },
        {
            "label": "Rate",
            "fieldname": "rate",
            "fieldtype": "Currency",
            "width": 100,
        },
        {
            "label": "Value",
            "fieldname": "value",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": "Due Date",
            "fieldname": "schedule_date",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": "Overdue Days",
            "fieldname": "overdue_days",
            "fieldtype": "Int",
            "width": 120,
        },
    ]


def get_data(filters):
    conditions = []

    if filters.get("company"):
        conditions.append("po.company = %(company)s")

    if filters.get("supplier"):
        conditions.append("po.supplier = %(supplier)s")

    if filters.get("from_date"):
        conditions.append("po.transaction_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("po.transaction_date <= %(to_date)s")

    condition_sql = ""

    if conditions:
        condition_sql = " AND " + " AND ".join(conditions)

    data = frappe.db.sql(
        f"""
        SELECT
            po.transaction_date,
            po.name AS po,
            po.supplier,

            poi.name AS purchase_order_item,
            poi.item_code,
            poi.item_name,

            poi.qty AS ordered_qty,
            IFNULL(poi.received_qty, 0) AS received_qty,

            (
                poi.qty - IFNULL(poi.received_qty, 0)
            ) AS balance_qty,

            poi.rate,

            (
                (
                    poi.qty - IFNULL(poi.received_qty, 0)
                ) * poi.rate
            ) AS value,

            poi.schedule_date

        FROM `tabPurchase Order` po

        INNER JOIN `tabPurchase Order Item` poi
            ON poi.parent = po.name
            AND poi.parenttype = 'Purchase Order'

        WHERE
            po.docstatus = 1
            AND IFNULL(po.status, '') NOT IN (
                'Closed',
                'Cancelled',
                'Completed'
            )
            {condition_sql}

        ORDER BY
            po.transaction_date DESC,
            po.name DESC,
            poi.idx ASC
        """,
        filters,
        as_dict=True,
    )

    final_data = []
    today_date = getdate(today())

    for row in data:
        balance_qty = flt(row.get("balance_qty"))

        if balance_qty <= 0:
            continue

        schedule_date = row.get("schedule_date")

        if not schedule_date:
            continue

        schedule_date = getdate(schedule_date)

        # Report mein keval due/overdue items dikhane hain.
        if schedule_date > today_date:
            continue

        overdue_days = date_diff(today_date, schedule_date)

        row["balance_qty"] = balance_qty
        row["value"] = balance_qty * flt(row.get("rate"))
        row["overdue_days"] = overdue_days if overdue_days > 0 else 0

        final_data.append(row)

    return final_data













# Pooja Code------------



# import frappe
# from frappe.utils import today, date_diff, getdate


# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data


# def get_columns():
#     return [
#         {"label": "Date", "fieldname": "transaction_date", "fieldtype": "Date", "width": 100},
#         {"label": "Order Number", "fieldname": "po", "fieldtype": "Link", "options": "Purchase Order", "width": 150},
#         {"label": "Party's Name", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
#         {"label": "Name of Item", "fieldname": "item_name", "fieldtype": "Data", "width": 220},
#         {"label": "Ordered Qty", "fieldname": "ordered_qty", "fieldtype": "Float", "width": 100},
#         {"label": "Balance Qty", "fieldname": "balance_qty", "fieldtype": "Float", "width": 100},
#         {"label": "Rate", "fieldname": "rate", "fieldtype": "Currency", "width": 100},
#         {"label": "Value", "fieldname": "value", "fieldtype": "Currency", "width": 120},
#         {"label": "Due Date", "fieldname": "schedule_date", "fieldtype": "Date", "width": 110},
#         {"label": "Overdue Days", "fieldname": "overdue_days", "fieldtype": "Int", "width": 120},
#     ]


# def get_data(filters):
#     conditions = ""

#     if filters.get("company"):
#         conditions += " AND po.company = %(company)s"

#     if filters.get("supplier"):
#         conditions += " AND po.supplier = %(supplier)s"

#     if filters.get("from_date") and filters.get("to_date"):
#         conditions += " AND po.transaction_date BETWEEN %(from_date)s AND %(to_date)s"

#     data = frappe.db.sql(f"""
#         SELECT
#             po.transaction_date,
#             po.name as po,
#             po.supplier,
#             poi.item_name,
#             poi.qty as ordered_qty,

#             -- Balance Qty
#             poi.qty - IFNULL((
#                 SELECT SUM(pri.qty)
#                 FROM `tabPurchase Receipt Item` pri
#                 WHERE pri.purchase_order = po.name
#                 AND pri.item_code = poi.item_code
#             ), 0) as balance_qty,

#             poi.rate,

#             -- Value = Balance Qty * Rate
#             (
#                 (poi.qty - IFNULL((
#                     SELECT SUM(pri.qty)
#                     FROM `tabPurchase Receipt Item` pri
#                     WHERE pri.purchase_order = po.name
#                     AND pri.item_code = poi.item_code
#                 ), 0)) * poi.rate
#             ) as value,

#             poi.schedule_date

#         FROM `tabPurchase Order` po
#         INNER JOIN `tabPurchase Order Item` poi
#             ON poi.parent = po.name

#         WHERE po.docstatus = 1
#         {conditions}

#         ORDER BY po.transaction_date DESC
#     """, filters, as_dict=1)

#     # 🔥 FINAL FILTER LOGIC (ONLY DUE + PENDING)
#     final_data = []

#     for d in data:
#         today_date = getdate(today())

#         # Overdue calculation
#         overdue = date_diff(today_date, d.schedule_date) if d.schedule_date else 0
#         d["overdue_days"] = overdue if overdue > 0 else 0

#         # ✅ ONLY show:
#         # 1. Due Date <= Today
#         # 2. Balance Qty > 0
#         if d.schedule_date and getdate(d.schedule_date) <= today_date and d.balance_qty > 0:
#             final_data.append(d)

#     return final_data