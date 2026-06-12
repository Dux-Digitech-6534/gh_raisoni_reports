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
            "fieldname": "name",
            "label": _("PO ID"),
            "fieldtype": "Link",
            "options": "Purchase Order",
            "width": 190,
        },
        {
            "fieldname": "material_request",
            "label": _("Material Request ID"),
            "fieldtype": "Data",
            "width": 190,
        },
        {
            "fieldname": "date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "fieldname": "company",
            "label": _("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "width": 230,
        },
        {
            "fieldname": "supplier",
            "label": _("Supplier"),
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 200,
        },
        {
            "fieldname": "required_by",
            "label": _("Required By"),
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "fieldname": "grand_total",
            "label": _("Grand Total (Rs.)"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120,
        },
        {
            "fieldname": "net_total",
            "label": _("Net Total (Rs.)"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 130,
        },
        {
            "fieldname": "total_qty",
            "label": _("Total Qty"),
            "fieldtype": "Float",
            "width": 90,
        },
        {
            "fieldname": "workflow_state",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 150,
        },
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    return frappe.db.sql(
        f"""
        SELECT
            po.name,
            GROUP_CONCAT(DISTINCT poi.material_request ORDER BY poi.material_request SEPARATOR ', ') AS material_request,
            po.transaction_date AS date,
            po.company,
            po.supplier,
            po.schedule_date AS required_by,
            po.grand_total,
            po.net_total,
            po.total_qty,
            po.workflow_state
        FROM
            `tabPurchase Order` po
        LEFT JOIN
            `tabPurchase Order Item` poi ON poi.parent = po.name
        WHERE
            po.docstatus < 2
            {conditions}
        GROUP BY
            po.name
        ORDER BY
            po.transaction_date DESC
        """,
        filters or {},
        as_dict=True,
    )


def get_conditions(filters):
    conditions = ""

    if not filters:
        return conditions

    if filters.get("name"):
        conditions += " AND po.name = %(name)s"

    if filters.get("company"):
        conditions += " AND po.company = %(company)s"

    if filters.get("from_date"):
        conditions += " AND po.transaction_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND po.transaction_date <= %(to_date)s"

    if filters.get("supplier"):
        conditions += " AND po.supplier = %(supplier)s"

    if filters.get("workflow_state"):
        conditions += " AND po.workflow_state = %(workflow_state)s"

    return conditions


@frappe.whitelist()
def get_po_item_details(po_names):
    if isinstance(po_names, str):
        po_names = json.loads(po_names)

    if not po_names:
        return []

    return frappe.db.sql(
        """
        SELECT
            po.name AS po_id,
            po.transaction_date AS date,
            po.company,
            po.supplier,
            po.schedule_date AS required_by,
            po.grand_total,
            po.net_total,
            po.total_qty,
            po.workflow_state,

            poi.parent,
            poi.idx,
            poi.material_request,
            poi.item_name,
            poi.item_group,
            poi.qty,
            poi.uom,
            poi.rate,
            poi.amount
        FROM
            `tabPurchase Order Item` poi
        INNER JOIN
            `tabPurchase Order` po ON po.name = poi.parent
        WHERE
            poi.parent IN %(po_names)s
        ORDER BY
            poi.parent ASC, poi.idx ASC
        """,
        {"po_names": tuple(po_names)},
        as_dict=True,
    )