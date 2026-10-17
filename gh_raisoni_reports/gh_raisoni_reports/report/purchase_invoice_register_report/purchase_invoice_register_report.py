import json

import frappe
from frappe import _
from frappe.utils import flt, formatdate
from erpnext.accounts.report.purchase_register.purchase_register import execute as purchase_register_execute


def execute(filters=None):
    # The standard Purchase Register decides which invoices match the filters
    # (including accounting dimensions); the rows are rebuilt in the Tally
    # Purchase Register layout: one invoice row followed by its item rows.
    filters = frappe._dict(filters or {})
    filters.include_payments = 0
    result = purchase_register_execute(filters)
    invoices = result[1] if len(result) > 1 else []

    names = []
    std_rows = {}
    for d in invoices:
        if d.get("voucher_no") and d.get("voucher_no") not in names:
            names.append(d.get("voucher_no"))
            std_rows[d.get("voucher_no")] = d

    std_columns = {c.get("fieldname"): c for c in result[0]}
    # the expense and tax account columns are the Purchase Register columns not named below
    account_columns = [c for f, c in std_columns.items() if f not in STD_FIXED_COLUMNS]
    account_fields = [c["fieldname"] for c in account_columns]

    headers = _get_invoice_headers(names)
    items = _get_invoice_items(names)
    item_taxes = _get_item_taxes(names, items)
    po_dates = _get_po_dates(items)
    gl_heads = _get_gl_heads(names)
    currency = frappe.get_cached_value("Company", filters.company, "default_currency") if filters.company else None

    item_groups = sorted({it.item_group or _("Other") for it in items})
    group_field = {g: "ig_" + frappe.scrub(g) for g in item_groups}

    items_by_invoice = {}
    for it in items:
        items_by_invoice.setdefault(it.parent, []).append(it)

    data = []
    total_fields = [
        "value",
        "tax_amount",
        "net_total",
        "addl_cost",
        "total_tax",
        "grand_total",
        "rounding",
        "gross_total",
        "outstanding_amount",
        *account_fields,
        *group_field.values(),
    ]
    totals = dict.fromkeys(total_fields, 0)
    for name in names:
        inv = headers.get(name)
        if not inv:
            continue
        inv_items = items_by_invoice.get(name, [])
        std = std_rows.get(name) or {}

        net_total = flt(inv.base_net_total)
        # taxes, charges and discounts on top of the item values
        addl_cost = flt(inv.base_grand_total) - net_total

        orders = []
        for it in inv_items:
            if it.purchase_order and it.purchase_order not in orders:
                orders.append(it.purchase_order)

        item_rows = []
        for it in inv_items:
            tax_rate, tax_amount = item_taxes.get(it.name, (0, 0))
            amount = flt(it.base_net_amount) + tax_amount
            item_rows.append(
                {
                    "indent": 1,
                    "invoice": name,
                    "particulars": _item_label(it),
                    "item_group": it.item_group,
                    "qty": flt(it.qty),
                    "uom": it.uom,
                    "rate_without_tax": flt(it.base_net_rate),
                    "tax_percent": tax_rate,
                    "tax_amount": tax_amount,
                    "rate": amount / flt(it.qty) if flt(it.qty) else 0,
                    "value": amount,
                    "debit_head": it.expense_account,
                    "currency": currency,
                }
            )

        debit_heads, credit_heads = gl_heads.get(name, ([], []))
        row = {
            "indent": 0,
            "is_invoice": 1,
            "posting_date": inv.posting_date,
            "voucher_type": std.get("voucher_type") or "Purchase Invoice",
            "voucher_no": name,
            "particulars": _supplier_label(inv),
            "supplier_group": std.get("supplier_group"),
            "tax_id": std.get("tax_id"),
            "bill_no": inv.bill_no,
            "bill_date": inv.bill_date,
            "order_no_date": ", ".join(_po_label(po, po_dates.get(po)) for po in orders),
            "purchase_receipt": std.get("purchase_receipt"),
            "project": std.get("project"),
            "mode_of_payment": std.get("mode_of_payment"),
            "remarks": "" if (inv.remarks or "").strip() == "No Remarks" else inv.remarks,
            "qty": flt(inv.total_qty),
            "net_total": net_total,
            "tax_amount": sum(r["tax_amount"] for r in item_rows),
            "value": sum(r["value"] for r in item_rows),
            "addl_cost": addl_cost,
            "total_tax": std.get("total_tax"),
            "grand_total": flt(inv.base_grand_total),
            "rounding": flt(inv.base_rounding_adjustment),
            "gross_total": flt(inv.base_rounded_total) or flt(inv.base_grand_total),
            "outstanding_amount": std.get("outstanding_amount"),
            "credit_head": ", ".join(credit_heads),
            "debit_head": ", ".join(debit_heads),
            "currency": currency,
        }
        row.update({f: std.get(f) for f in account_fields})

        # item group columns carry their share of taxes/charges, so that
        # (sum of item groups + rounding) = gross total, as in Tally
        for it in inv_items:
            fieldname = group_field[it.item_group or _("Other")]
            share = flt(it.base_net_amount)
            if net_total:
                share += addl_cost * flt(it.base_net_amount) / net_total
            row[fieldname] = flt(row.get(fieldname)) + share

        data.append(row)
        data.extend(item_rows)
        for key in total_fields:
            totals[key] += flt(row.get(key))

    if data:
        total_row = {"indent": 0, "is_total": 1, "particulars": _("Grand Total"), "currency": currency}
        total_row.update(totals)
        data.append(total_row)

    return get_columns(item_groups, group_field, account_columns), data


# Purchase Register columns this report places itself (or leaves out as duplicates:
# rounded_total = Gross Total, payable_account = Credit Head, supplier_id and supplier_name = Particulars,
# purchase_order = Purchase Order with dates); every other column is an account column
STD_FIXED_COLUMNS = (
    "voucher_type",
    "voucher_no",
    "posting_date",
    "supplier_id",
    "supplier_name",
    "supplier_group",
    "tax_id",
    "payable_account",
    "mode_of_payment",
    "project",
    "bill_no",
    "bill_date",
    "purchase_order",
    "purchase_receipt",
    "currency",
    "net_total",
    "total_tax",
    "grand_total",
    "rounded_total",
    "outstanding_amount",
    "remarks",
)


def get_columns(item_groups=None, group_field=None, account_columns=None):
    def col(label, fieldname, fieldtype="Data", width=120, options=None):
        c = {"label": label, "fieldname": fieldname, "fieldtype": fieldtype, "width": width}
        if options:
            c["options"] = options
        return c

    def currency_col(label, fieldname, width=120):
        return col(label, fieldname, "Currency", width, "currency")

    columns = [
        # voucher and supplier
        col(_("Posting Date"), "posting_date", "Date", 100),
        col(_("Voucher Type"), "voucher_type", "Data", 130),
        col(_("Voucher"), "voucher_no", "Link", 160, "Purchase Invoice"),
        col(_("Particulars"), "particulars", "Data", 300),
        col(_("Supplier Group"), "supplier_group", "Link", 140, "Supplier Group"),
        col(_("Tax Id"), "tax_id", "Data", 130),
        col(_("Bill No"), "bill_no", "Data", 150),
        col(_("Bill Date"), "bill_date", "Date", 110),
        col(_("Purchase Order"), "order_no_date", "Data", 240),
        col(_("Purchase Receipt"), "purchase_receipt", "Data", 170),
        col(_("Project"), "project", "Data", 130),
        col(_("Mode Of Payment"), "mode_of_payment", "Data", 130),
        col(_("Remarks"), "remarks", "Data", 220),
        # item details
        col(_("Item Group"), "item_group", "Link", 140, "Item Group"),
        col(_("Quantity"), "qty", "Float", 90),
        col(_("UOM"), "uom", "Data", 80),
        currency_col(_("Rate Without Tax"), "rate_without_tax", 130),
        col(_("Tax %"), "tax_percent", "Percent", 80),
        currency_col(_("Tax Amount"), "tax_amount", 120),
        currency_col(_("Rate"), "rate", 120),
        currency_col(_("Value"), "value", 130),
        # invoice totals
        currency_col(_("Net Total"), "net_total", 130),
        currency_col(_("Addl. Cost"), "addl_cost", 120),
        currency_col(_("Total Tax"), "total_tax", 120),
        currency_col(_("Grand Total"), "grand_total", 130),
        currency_col(_("Rounding Off"), "rounding", 110),
        currency_col(_("Gross Total"), "gross_total", 130),
        currency_col(_("Outstanding Amount"), "outstanding_amount", 130),
        # accounts
        col(_("Credit Head"), "credit_head", "Data", 200),
        col(_("Debit Head"), "debit_head", "Data", 280),
    ]
    columns.extend(account_columns or [])
    for group in item_groups or []:
        columns.append(currency_col(group, group_field[group], 150))
    columns.append(col(_("Currency"), "currency", "Data", 80))
    return columns


def _supplier_label(inv):
    name = inv.supplier_name or inv.supplier
    if inv.supplier and inv.supplier != name:
        return f"{name} ({inv.supplier})"
    return name


def _item_label(it):
    name = (it.item_name or "").strip()
    code = (it.item_code or "").strip()
    if name and code and name != code:
        return f"{name}_{code}"
    return name or code


def _po_label(po, po_date):
    if not po_date:
        return po
    return f"{po} dt.{formatdate(po_date, 'd-MMM-yy')}"


def _get_invoice_headers(names):
    if not names:
        return {}
    rows = frappe.db.sql(
        """
        SELECT name, posting_date, supplier, supplier_name, bill_no, bill_date, remarks,
            total_qty, base_net_total, base_grand_total, base_rounded_total, base_rounding_adjustment
        FROM `tabPurchase Invoice`
        WHERE name IN %(names)s
        """,
        {"names": tuple(names)},
        as_dict=True,
    )
    return {r.name: r for r in rows}


def _get_invoice_items(names):
    if not names:
        return []
    return frappe.db.sql(
        """
        SELECT name, parent, item_code, item_name, item_group, qty, uom, base_net_rate, base_net_amount,
            purchase_order, expense_account
        FROM `tabPurchase Invoice Item`
        WHERE parent IN %(names)s
        ORDER BY parent, idx
        """,
        {"names": tuple(names)},
        as_dict=True,
    )


def _get_item_taxes(names, items):
    """{item row name: (tax %, tax amount)} from the invoice's Taxes and Charges table.

    Each tax row's item shares are scaled to its base amount after discount, so
    the item tax amounts add up to the invoice's taxes in company currency.
    """
    if not names:
        return {}

    # ERPNext v15 keeps the item split as JSON on the tax row; v16 moved it to
    # the Item Wise Tax Detail child table
    legacy = frappe.db.has_column("Purchase Taxes and Charges", "item_wise_tax_detail")
    taxes = frappe.db.sql(
        """
        SELECT name, parent, charge_type, rate, add_deduct_tax, category,
            base_tax_amount_after_discount_amount AS base_amount{legacy_col}
        FROM `tabPurchase Taxes and Charges`
        WHERE parent IN %(names)s AND parenttype = 'Purchase Invoice'
        ORDER BY parent, idx
        """.format(legacy_col=", item_wise_tax_detail" if legacy else ""),
        {"names": tuple(names)},
        as_dict=True,
    )

    rows_by_invoice = {}
    for it in items:
        rows_by_invoice.setdefault(it.parent, []).append(it)

    split = {} if legacy else _get_item_wise_tax_details(names)

    result = {it.name: [0.0, 0.0] for it in items}
    for tax in taxes:
        # valuation-only charges do not reach the invoice total
        if tax.category == "Valuation":
            continue
        rows = rows_by_invoice.get(tax.parent) or []
        if not rows:
            continue
        sign = -1 if tax.add_deduct_tax == "Deduct" else 1

        # {item row name: (rate, amount)}
        detail = _split_legacy_detail(tax.item_wise_tax_detail, rows) if legacy else split.get(tax.name, {})

        weights = {}
        rates = {}
        for it in rows:
            d = detail.get(it.name)
            if d:
                rates[it.name], weights[it.name] = d
            else:
                weights[it.name] = 0
                rates[it.name] = 0 if tax.charge_type == "Actual" else flt(tax.rate)

        total_weight = sum(weights.values())
        if not total_weight:
            # no item-wise split stored: spread by net amount
            weights = {it.name: flt(it.base_net_amount) for it in rows}
            total_weight = sum(weights.values())

        for it in rows:
            result[it.name][0] += sign * rates[it.name]
            if total_weight:
                result[it.name][1] += sign * flt(tax.base_amount) * weights[it.name] / total_weight

    return {k: (v[0], v[1]) for k, v in result.items()}


def _split_legacy_detail(raw, rows):
    """v15 item_wise_tax_detail is keyed by item code; an item code that appears
    on several rows is split between them by net amount."""
    try:
        detail = json.loads(raw or "{}") or {}
    except ValueError:
        return {}

    code_net = {}
    for it in rows:
        code_net[it.item_code] = code_net.get(it.item_code, 0) + flt(it.base_net_amount)

    out = {}
    for it in rows:
        d = detail.get(it.item_code)
        if isinstance(d, (list, tuple)) and len(d) > 1:
            share_of_code = flt(it.base_net_amount) / code_net[it.item_code] if code_net[it.item_code] else 0
            out[it.name] = (flt(d[0]), flt(d[1]) * share_of_code)
    return out


def _get_item_wise_tax_details(names):
    """v16: {tax row name: {item row name: (rate, amount)}}"""
    if not frappe.db.table_exists("Item Wise Tax Detail"):
        return {}
    rows = frappe.db.sql(
        """
        SELECT tax_row, item_row, SUM(rate) AS rate, SUM(amount) AS amount
        FROM `tabItem Wise Tax Detail`
        WHERE parent IN %(names)s AND parenttype = 'Purchase Invoice'
        GROUP BY tax_row, item_row
        """,
        {"names": tuple(names)},
        as_dict=True,
    )
    out = {}
    for r in rows:
        out.setdefault(r.tax_row, {})[r.item_row] = (flt(r.rate), flt(r.amount))
    return out



def _get_gl_heads(names):
    """Accounts the invoice actually posted to: (debited accounts, credited accounts)."""
    if not names:
        return {}
    rows = frappe.db.sql(
        """
        SELECT voucher_no, account, SUM(debit) AS debit, SUM(credit) AS credit
        FROM `tabGL Entry`
        WHERE voucher_type = 'Purchase Invoice' AND voucher_no IN %(names)s AND is_cancelled = 0
        GROUP BY voucher_no, account
        ORDER BY voucher_no, MIN(creation)
        """,
        {"names": tuple(names)},
        as_dict=True,
    )
    heads = {}
    for r in rows:
        debits, credits = heads.setdefault(r.voucher_no, ([], []))
        net = flt(r.debit) - flt(r.credit)
        if net > 0:
            debits.append(r.account)
        elif net < 0:
            credits.append(r.account)
    return heads


def _get_po_dates(items):
    orders = list({it.purchase_order for it in items if it.purchase_order})
    if not orders:
        return {}
    return dict(
        frappe.db.sql(
            "SELECT name, transaction_date FROM `tabPurchase Order` WHERE name IN %(orders)s",
            {"orders": tuple(orders)},
        )
    )
