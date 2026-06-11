import json
import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {
            "fieldname": "name",
            "label": _("Material Issue ID"),
            "fieldtype": "Link",
            "options": "Stock Entry",
            "width": 190,
        },
        {
            "fieldname": "posting_date",
            "label": _("Posting Date"),
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "fieldname": "company",
            "label": _("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "width": 200,
        },
        {
            "fieldname": "custom_department",
            "label": _("User Department"),
            "fieldtype": "Data",
            "width": 220,
        },
        {
            "fieldname": "item_code",
            "label": _("Item Code"),
            "fieldtype": "Link",
            "options": "Item",
            "width": 180,
        },
        {
            "fieldname": "qty",
            "label": _("Qty"),
            "fieldtype": "Float",
            "width": 100,
        },
        {
            "fieldname": "uom",
            "label": _("UOM"),
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "fieldname": "basic_rate",
            "label": _("Rate"),
            "fieldtype": "Float",
            "width": 100,
        },
        {
            "fieldname": "amount",
            "label": _("Amount"),
            "fieldtype": "Float",
            "width": 100,
        },
        
        {
            "fieldname": "s_warehouse",
            "label": _("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 180,
        },
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    return frappe.db.sql(
        """
        SELECT
            se.name,
            se.posting_date,
            se.company,
            CONCAT(
                IFNULL(se.custom_username, ''),
                ' - ',
                IFNULL(se.custom_department, '')
            ) AS custom_department,
            sed.item_code,
            sed.qty,
            sed.uom,
            sed.basic_rate,
            sed.amount,
            sed.s_warehouse
        FROM `tabStock Entry` se
        INNER JOIN `tabStock Entry Detail` sed
            ON se.name = sed.parent
        WHERE
            se.stock_entry_type = 'Material Issue'
            AND se.docstatus IN (0, 1)
            {conditions}
        ORDER BY
            se.posting_date DESC
        """.format(conditions=conditions),
        filters,
        as_dict=True,
    )


def get_conditions(filters):
    conditions = ""

    if not filters:
        return conditions

    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND se.posting_date BETWEEN %(from_date)s AND %(to_date)s"

    if filters.get("company"):
        conditions += " AND se.company = %(company)s"

    if filters.get("custom_department"):
        conditions += " AND se.custom_department = %(custom_department)s"

    if filters.get("item_code"):
        conditions += " AND sed.item_code = %(item_code)s"

    return conditions


# ✅ Detail View API — returns child rows for selected Stock Entries
@frappe.whitelist()
def get_material_issue_item_details(se_names):
    if isinstance(se_names, str):
        se_names = json.loads(se_names)

    if not se_names:
        return []

    return frappe.db.get_all(
        "Stock Entry Detail",           # ✅ Child DocType
        filters={
            "parent": ["in", se_names],
            "docstatus": ["!=", 2],
        },
        fields=[
            "parent",                   # Stock Entry ID
            "idx",                      # Row number
            "item_code",
            "item_name",
            "qty",
            "uom",
            "basic_rate",              # Rate
            "basic_amount",            # Basic Amount
            "amount",                  # Final Amount
            "s_warehouse",             # Source Warehouse
            "material_indent",         # ✅ Material Indent ID (MAT-MR-...)
        ],
        order_by="parent asc, idx asc",
    )