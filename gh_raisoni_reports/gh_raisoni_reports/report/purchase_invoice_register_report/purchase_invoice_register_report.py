import json
import re

import frappe
from frappe import _
from erpnext.accounts.report.purchase_register.purchase_register import execute as purchase_register_execute


def execute(filters=None):
    # The standard Purchase Register decides which invoices match the filters
    # (including accounting dimensions); only its columns are replaced below.
    filters = frappe._dict(filters or {})
    filters.include_payments = 0
    result = purchase_register_execute(filters)
    invoices = result[1] if len(result) > 1 else []

    names = [d.get("voucher_no") for d in invoices if d.get("voucher_no")]
    extra = _get_invoice_extra(names)
    material_requests = _get_material_requests(names)

    data = []
    for inv in invoices:
        name = inv.get("voucher_no")
        if not name:
            continue
        x = extra.get(name, {})
        data.append(
            {
                "posting_date": inv.get("posting_date"),
                "voucher_no": name,
                "purchase_receipt": inv.get("purchase_receipt") or "",
                "purchase_order": inv.get("purchase_order") or "",
                "material_request": material_requests.get(name, ""),
                "company": x.get("company"),
                "supplier": inv.get("supplier_id"),
                "address": x.get("address"),
                "status": x.get("status"),
                "grand_total": inv.get("grand_total"),
                "remarks": inv.get("remarks"),
                "tax_id": inv.get("tax_id"),
                "project": inv.get("project"),
                "bill_no": inv.get("bill_no"),
                "bill_date": inv.get("bill_date"),
            }
        )

    return get_columns(), data


def get_columns():
    return [
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {
            "label": _("Purchase Invoice ID"),
            "fieldname": "voucher_no",
            "fieldtype": "Link",
            "options": "Purchase Invoice",
            "width": 170,
        },
        {"label": _("Purchase Receipt No."), "fieldname": "purchase_receipt", "fieldtype": "Data", "width": 170},
        {"label": _("Purchase Order"), "fieldname": "purchase_order", "fieldtype": "Data", "width": 170},
        {"label": _("Material Request"), "fieldname": "material_request", "fieldtype": "Data", "width": 170},
        {"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 180},
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
        {"label": _("Address"), "fieldname": "address", "fieldtype": "Data", "width": 240},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110},
        {
            "label": _("Grand Total"),
            "fieldname": "grand_total",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 130,
        },
        {"label": _("Narration"), "fieldname": "remarks", "fieldtype": "Data", "width": 220},
        {"label": _("Tax Id"), "fieldname": "tax_id", "fieldtype": "Data", "width": 130},
        {"label": _("Project"), "fieldname": "project", "fieldtype": "Data", "width": 130},
        {"label": _("Bill No"), "fieldname": "bill_no", "fieldtype": "Data", "width": 120},
        {"label": _("Bill Date"), "fieldname": "bill_date", "fieldtype": "Date", "width": 100},
    ]


def _plain_address(html, fallback=None):
    """address_display is HTML with <br>; the report wants one plain line."""
    text = re.sub(r"<br\s*/?>|</p>|</div>", ", ", html or "", flags=re.I)
    text = frappe.utils.strip_html(text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"(,\s*)+", ", ", text).strip(", ")
    return text or (fallback or "")


def _get_invoice_extra(names):
    if not names:
        return {}
    rows = frappe.db.sql(
        """
        SELECT name, company, status, address_display, supplier_address
        FROM `tabPurchase Invoice`
        WHERE name IN %(names)s
        """,
        {"names": tuple(names)},
        as_dict=True,
    )
    return {
        r.name: {
            "company": r.company,
            "status": r.status,
            "address": _plain_address(r.address_display, r.supplier_address),
        }
        for r in rows
    }


def _get_material_requests(names):
    if not names:
        return {}
    rows = frappe.db.sql(
        """
        SELECT parent, GROUP_CONCAT(DISTINCT material_request ORDER BY material_request SEPARATOR ', ') AS mr
        FROM `tabPurchase Invoice Item`
        WHERE parent IN %(names)s AND material_request IS NOT NULL AND material_request != ''
        GROUP BY parent
        """,
        {"names": tuple(names)},
        as_dict=True,
    )
    return {r.parent: r.mr for r in rows}


@frappe.whitelist()
def get_invoice_item_details(invoice_names):
    if isinstance(invoice_names, str):
        invoice_names = json.loads(invoice_names)

    frappe.has_permission("Purchase Invoice", "read", throw=True)

    # honour the user's permissions: only invoices they can read
    invoice_names = frappe.get_list(
        "Purchase Invoice",
        filters={"name": ["in", list(invoice_names or [])]},
        pluck="name",
        limit_page_length=0,
    )

    if not invoice_names:
        return []

    # tax columns are custom fields; fall back to NULL on a site that does not have them
    def tax_col(fieldname, alias):
        if frappe.db.has_column("Purchase Invoice Item", fieldname):
            return f"pii.{fieldname} AS {alias}"
        return f"NULL AS {alias}"

    tax_columns = ", ".join(
        [
            tax_col("custom_rate_without_tax", "rate_without_tax"),
            tax_col("custom_tax_amount", "tax_amount"),
        ]
    )

    rows = frappe.db.sql(
        f"""
        SELECT
            /* Parent Purchase Invoice data */
            pi.posting_date AS posting_date,
            pi.posting_date AS date,
            pi.name AS invoice_id,
            pi.company AS company,
            pi.supplier AS supplier,
            pi.address_display AS address_display,
            pi.supplier_address AS supplier_address,
            pi.status AS status,
            pi.base_grand_total AS grand_total,
            pi.remarks AS remarks,
            COALESCE(NULLIF(pi.tax_id, ''), sup.tax_id) AS tax_id,
            COALESCE(NULLIF(pii.project, ''), pi.project) AS project,
            pi.bill_no AS bill_no,
            pi.bill_date AS bill_date,

            /* References from the child row */
            pii.purchase_order AS purchase_order,
            pii.material_request AS material_request,
            pii.purchase_receipt AS purchase_receipt,

            /* Child item data */
            pii.expense_account AS expense_head,
            pii.idx AS idx,
            pii.item_code AS item_code,
            pii.item_name AS item_name,
            pii.item_group AS item_group,
            pii.qty AS qty,
            pii.uom AS uom,
            {tax_columns},
            pii.rate AS rate,
            pii.amount AS amount

        FROM
            `tabPurchase Invoice Item` pii
        INNER JOIN
            `tabPurchase Invoice` pi ON pi.name = pii.parent
        LEFT JOIN
            `tabSupplier` sup ON sup.name = pi.supplier
        WHERE
            pii.parent IN %(invoice_names)s
        ORDER BY
            pi.posting_date DESC, pii.parent ASC, pii.idx ASC
        """,
        {"invoice_names": tuple(invoice_names)},
        as_dict=True,
    )

    for row in rows:
        row["address"] = _plain_address(row.pop("address_display", None), row.pop("supplier_address", None))

    return rows
