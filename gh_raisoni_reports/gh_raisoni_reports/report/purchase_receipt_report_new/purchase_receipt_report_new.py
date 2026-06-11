# import json

# import frappe
# from frappe import _


# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data


# def get_columns():
#     return [
#         {
#             "label": _("Date"),
#             "fieldname": "posting_date",
#             "fieldtype": "Date",
#             "width": 130,
#         },
#         {
#             "label": _("Purchase Receipt No."),
#             "fieldname": "name",
#             "fieldtype": "Link",
#             "options": "Purchase Receipt",
#             "width": 230,
#         },
#         {
#             "label": _("Purchase Order"),
#             "fieldname": "purchase_order",
#             "fieldtype": "Data",
#             "width": 230,
#         },
#         {
#             "label": _("Material Request"),
#             "fieldname": "material_request",
#             "fieldtype": "Data",
#             "width": 230,
#         },
#         {
#             "label": _("Supplier"),
#             "fieldname": "supplier",
#             "fieldtype": "Link",
#             "options": "Supplier",
#             "width": 230,
#         },
#         {
#             "label": _("Company"),
#             "fieldname": "company",
#             "fieldtype": "Link",
#             "options": "Company",
#             "width": 230,
#         },
#         {
#             "label": _("Grand Total"),
#             "fieldname": "grand_total",
#             "fieldtype": "Currency",
#             "options": "currency",
#             "width": 140,
#         },
#         {
#             "label": _("Status"),
#             "fieldname": "status",
#             "fieldtype": "Data",
#             "width": 120,
#         },
#     ]


# def get_data(filters=None):
#     filters = filters or {}
#     conditions = get_conditions(filters)

#     receipts = frappe.db.sql(
#         f"""
#         SELECT
#             pr.posting_date,
#             pr.name,
#             pr.company,
#             pr.supplier,
#             pr.grand_total,
#             pr.status
#         FROM
#             `tabPurchase Receipt` pr
#         WHERE
#             pr.docstatus != 2
#             {conditions}
#         ORDER BY
#             pr.posting_date DESC, pr.name DESC
#         """,
#         filters,
#         as_dict=True,
#     )

#     if not receipts:
#         return []

#     receipt_names = [r.name for r in receipts]

#     items = frappe.db.sql(
#         """
#         SELECT
#             parent,
#             purchase_order,
#             material_request
#         FROM
#             `tabPurchase Receipt Item`
#         WHERE
#             parent IN %(names)s
#         """,
#         {"names": receipt_names},
#         as_dict=True,
#     )

#     po_map = {}
#     mr_map = {}

#     for item in items:
#         if item.purchase_order:
#             po_map.setdefault(item.parent, set()).add(item.purchase_order)
#         if item.material_request:
#             mr_map.setdefault(item.parent, set()).add(item.material_request)

#     data = []

#     for receipt in receipts:
#         po_list = sorted(po_map.get(receipt.name, []))
#         mr_list = sorted(mr_map.get(receipt.name, []))

#         data.append(
#             {
#                 "posting_date": receipt.posting_date,
#                 "name": receipt.name,
#                 "purchase_order": ", ".join(po_list) if po_list else "-",
#                 "material_request": ", ".join(mr_list) if mr_list else "-",
#                 "supplier": receipt.supplier,
#                 "company": receipt.company,
#                 "grand_total": receipt.grand_total,
#                 "status": receipt.status,
#             }
#         )

#     return data


# def get_conditions(filters):
#     conditions = ""

#     if filters.get("from_date"):
#         conditions += " AND pr.posting_date >= %(from_date)s"

#     if filters.get("to_date"):
#         conditions += " AND pr.posting_date <= %(to_date)s"

#     if filters.get("supplier"):
#         conditions += " AND pr.supplier = %(supplier)s"

#     if filters.get("company"):
#         conditions += " AND pr.company = %(company)s"

#     if filters.get("status"):
#         conditions += " AND pr.status = %(status)s"

#     return conditions


# @frappe.whitelist()
# def get_receipt_item_details(receipt_names):
#     if isinstance(receipt_names, str):
#         receipt_names = json.loads(receipt_names)

#     if not receipt_names:
#         return []

#     return frappe.db.sql(
#         """
#         SELECT
#             pri.parent AS receipt_id,
#             pri.idx,
#             pri.purchase_order,
#             pri.material_request,
#             pri.item_code,
#             pri.item_name,
#             COALESCE(pri.received_qty, pri.qty, 0) AS qty,
#             pri.uom,
#             pri.rate,
#             pri.amount,
#             item.image AS item_image
#         FROM
#             `tabPurchase Receipt Item` pri
#         LEFT JOIN
#             `tabItem` item ON item.name = pri.item_code
#         WHERE
#             pri.parent IN %(receipt_names)s
#         ORDER BY
#             pri.parent ASC, pri.idx ASC
#         """,
#         {"receipt_names": receipt_names},
#         as_dict=True,
#     )


import json

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": _("Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 130,
        },
        {
            "label": _("Purchase Receipt No."),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Purchase Receipt",
            "width": 230,
        },
        {
            "label": _("Purchase Order"),
            "fieldname": "purchase_order",
            "fieldtype": "Link",
            "options": "Purchase Order",
            "width": 230,
        },
        {
            "label": _("Material Request"),
            "fieldname": "material_request",
            "fieldtype": "Data",
            "width": 230,
        },
        {
            "label": _("Purchase Invoice Details"),
            "fieldname": "purchase_invoice_details",
            "fieldtype": "Data",
            "width": 230,
        },
        # {
        #     "label": _("Supplier"),
        #     "fieldname": "supplier",
        #     "fieldtype": "Link",
        #     "options": "Supplier",
        #     "width": 230,
        # },
        {
            "label": _("Company"),
            "fieldname": "company",
            "fieldtype": "Link",
            "options": "Company",
            "width": 230,
        },
        {
            "label": _("Grand Total"),
            "fieldname": "grand_total",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 140,
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 120,
        },
    ]


def get_data(filters=None):
    filters = filters or {}
    conditions = get_conditions(filters)

    receipts = frappe.db.sql(
        f"""
        SELECT
            pr.posting_date,
            pr.name,
            pr.company,
            pr.supplier,
            pr.grand_total,
            pr.status
        FROM
            `tabPurchase Receipt` pr
        WHERE
            pr.docstatus != 2
            {conditions}
        ORDER BY
            pr.posting_date DESC, pr.name DESC
        """,
        filters,
        as_dict=True,
    )

    if not receipts:
        return []

    receipt_names = [r.name for r in receipts]

    items = frappe.db.sql(
        """
        SELECT
            parent,
            purchase_order,
            material_request
        FROM
            `tabPurchase Receipt Item`
        WHERE
            parent IN %(names)s
        """,
        {"names": tuple(receipt_names)},
        as_dict=True,
    )

    invoice_items = frappe.db.sql(
        """
        SELECT
            pii.purchase_receipt,
            pii.parent AS purchase_invoice
        FROM
            `tabPurchase Invoice Item` pii
        INNER JOIN
            `tabPurchase Invoice` pi ON pi.name = pii.parent
        WHERE
            pii.purchase_receipt IN %(names)s
            AND pi.docstatus < 2
        """,
        {"names": tuple(receipt_names)},
        as_dict=True,
    )

    po_map = {}
    mr_map = {}
    pi_map = {}

    for item in items:
        if item.purchase_order:
            po_map.setdefault(item.parent, set()).add(item.purchase_order)

        if item.material_request:
            mr_map.setdefault(item.parent, set()).add(item.material_request)

    for inv in invoice_items:
        if inv.purchase_receipt and inv.purchase_invoice:
            pi_map.setdefault(inv.purchase_receipt, set()).add(inv.purchase_invoice)

    data = []

    for receipt in receipts:
        po_list = sorted(po_map.get(receipt.name, []))
        mr_list = sorted(mr_map.get(receipt.name, []))
        pi_list = sorted(pi_map.get(receipt.name, []))

        data.append(
            {
                "posting_date": receipt.posting_date,
                "name": receipt.name,
                "purchase_order": ", ".join(po_list) if po_list else "-",
                "material_request": ", ".join(mr_list) if mr_list else "-",
                "purchase_invoice_details": ", ".join(pi_list) if pi_list else "-",
                "supplier": receipt.supplier,
                "company": receipt.company,
                "grand_total": receipt.grand_total,
                "status": receipt.status,
            }
        )

    return data


def get_conditions(filters):
    conditions = ""

    if filters.get("from_date"):
        conditions += " AND pr.posting_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND pr.posting_date <= %(to_date)s"

    if filters.get("supplier"):
        conditions += " AND pr.supplier = %(supplier)s"

    if filters.get("company"):
        conditions += " AND pr.company = %(company)s"

    if filters.get("status"):
        conditions += " AND pr.status = %(status)s"

    return conditions


@frappe.whitelist()
def get_receipt_item_details(receipt_names):
    if isinstance(receipt_names, str):
        receipt_names = json.loads(receipt_names)

    if not receipt_names:
        return []

    return frappe.db.sql(
        """
        SELECT
            pri.parent AS receipt_id,
            pr.supplier,
            GROUP_CONCAT(DISTINCT ptc.account_head ORDER BY ptc.account_head SEPARATOR ', ') AS expense_head,

            pri.idx,
            pri.purchase_order,
            pri.material_request,
            pri.item_code,
            pri.item_name,
            COALESCE(pri.received_qty, pri.qty, 0) AS qty,
            pri.uom,
            pri.rate,
            pri.amount,
            item.image AS item_image
        FROM
            `tabPurchase Receipt Item` pri
        INNER JOIN
            `tabPurchase Receipt` pr ON pr.name = pri.parent
        LEFT JOIN
            `tabPurchase Taxes and Charges` ptc
            ON ptc.parent = pr.name
            AND ptc.parenttype = 'Purchase Receipt'
        LEFT JOIN
            `tabItem` item ON item.name = pri.item_code
        WHERE
            pri.parent IN %(receipt_names)s
        GROUP BY
            pri.name
        ORDER BY
            pri.parent ASC, pri.idx ASC
        """,
        {"receipt_names": tuple(receipt_names)},
        as_dict=True,
    )