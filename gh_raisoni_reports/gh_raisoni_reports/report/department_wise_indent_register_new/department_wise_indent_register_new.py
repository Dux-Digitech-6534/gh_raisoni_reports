
# import frappe


# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters or {})
#     return columns, data


# def get_columns():
#     return [
#         {"label":"Material Indent ID","fieldname":"material_indent","fieldtype":"Link","options":"Material Indent","width":170},
#         {"label":"Transaction Date","fieldname":"transaction_date","fieldtype":"Date","width":120},

#         {"label":"Company","fieldname":"company","width":220},

#         {"label":"User Department","fieldname":"user_department","width":180},
#         {"label":"Item Code","fieldname":"item_code","width":160},

#         {"label":"Indent Qty","fieldname":"indent_qty","width":110},

#         {"label":"Purchase Req Qty","fieldname":"purchase_req_qty","width":130},
#         {"label":"Issued Qty","fieldname":"issued_qty","width":110},
#         {"label":"Remaining Issue Qty","fieldname":"remaining_issue_qty","width":150},

#         {"label":"PO Pending Qty","fieldname":"po_pending_qty","width":130},
#         {"label":"GRN Qty","fieldname":"grn_qty","width":110},
#         {"label":"GRN Pending Qty","fieldname":"grn_pending_qty","width":140},

#         {"label":"L1 Approval","fieldname":"l1_approval","width":180},
#         {"label":"L2 Approval","fieldname":"l2_approval","width":180},
#         {"label":"L3 Approval","fieldname":"l3_approval","width":180},
#     ]


# def get_data(filters):

#     conditions = " WHERE mi.docstatus < 2 "

#     if filters.get("from_date"):
#         conditions += " AND mi.transaction_date >= %(from_date)s "

#     if filters.get("to_date"):
#         conditions += " AND mi.transaction_date <= %(to_date)s "

#     if filters.get("company"):
#         conditions += " AND mi.company=%(company)s "

#     if filters.get("item_code"):
#         conditions += " AND mii.item_code=%(item_code)s "

#     if filters.get("custom_department"):
#         conditions += """
#         AND (
#             CASE
#                 WHEN mi.custom_username LIKE '%% - %%'
#                 THEN TRIM(SUBSTRING_INDEX(mi.custom_username,' - ',-1))
#                 ELSE mi.custom_username
#             END
#         )=%(custom_department)s
#         """


#     data = frappe.db.sql(f"""

# SELECT

# mi.name material_indent,
# mi.transaction_date,

# mi.company,


# CASE
# WHEN mi.custom_username LIKE '%% - %%'
# THEN TRIM(SUBSTRING_INDEX(mi.custom_username,' - ',-1))
# ELSE mi.custom_username
# END user_department,


# mii.item_code,

# IFNULL(mii.qty,0) indent_qty,


# IFNULL(
# (
# SELECT SUM(pri.qty)
# FROM `tabMaterial Request` mr
# JOIN `tabMaterial Request Item` pri
# ON pri.parent=mr.name
# WHERE mr.custom_material_indent=mi.name
# AND pri.item_code=mii.item_code
# AND mr.docstatus<2
# ),0
# ) purchase_req_qty,


# IFNULL(
# (
# SELECT SUM(pri.qty)
# FROM `tabMaterial Request` mr
# JOIN `tabMaterial Request Item` pri
# ON pri.parent=mr.name
# WHERE mr.custom_material_indent=mi.name
# AND pri.item_code=mii.item_code
# AND mr.docstatus<2
# ),0
# ) po_pending_qty,


# IFNULL(
# (
# SELECT SUM(poi.qty)
# FROM `tabPurchase Order Item` poi
# JOIN `tabPurchase Order` po
# ON po.name=poi.parent
# WHERE poi.material_request=mi.name
# AND poi.item_code=mii.item_code
# AND po.docstatus=1
# ),0
# ) grn_qty,


# 0 grn_pending_qty,


# IFNULL(
# (
# SELECT SUM(sd.qty)
# FROM `tabStock Entry` se
# JOIN `tabStock Entry Detail` sd
# ON sd.parent=se.name
# WHERE se.custom_material_indent=mi.name
# AND sd.item_code=mii.item_code
# AND se.docstatus=1
# ),0
# ) issued_qty,


# (
# IFNULL(mii.qty,0)
# -
# IFNULL(
# (
# SELECT SUM(sd.qty)
# FROM `tabStock Entry` se
# JOIN `tabStock Entry Detail` sd
# ON sd.parent=se.name
# WHERE se.custom_material_indent=mi.name
# AND sd.item_code=mii.item_code
# AND se.docstatus=1
# ),0
# )
# ) remaining_issue_qty,


# IFNULL(
# (
# SELECT CONCAT(a1.user,' / ',DATE_FORMAT(a1.date_time,'%%d-%%m-%%Y'))
# FROM `tabMaterial Request Activity` a1
# WHERE a1.parent IN (
# SELECT mr.name
# FROM `tabMaterial Request` mr
# WHERE mr.custom_material_indent=mi.name
# )
# AND a1.action='L1 Approved'
# ORDER BY a1.date_time
# LIMIT 1
# ),''
# ) l1_approval,


# IFNULL(
# (
# SELECT CONCAT(a2.user,' / ',DATE_FORMAT(a2.date_time,'%%d-%%m-%%Y'))
# FROM `tabMaterial Request Activity` a2
# WHERE a2.parent IN (
# SELECT mr.name
# FROM `tabMaterial Request` mr
# WHERE mr.custom_material_indent=mi.name
# )
# AND a2.action='L2 Approved'
# ORDER BY a2.date_time
# LIMIT 1
# ),''
# ) l2_approval,


# IFNULL(
# (
# SELECT CONCAT(a3.user,' / ',DATE_FORMAT(a3.date_time,'%%d-%%m-%%Y'))
# FROM `tabMaterial Request Activity` a3
# WHERE a3.parent IN (
# SELECT mr.name
# FROM `tabMaterial Request` mr
# WHERE mr.custom_material_indent=mi.name
# )
# AND a3.action='L3 Approved'
# ORDER BY a3.date_time
# LIMIT 1
# ),''
# ) l3_approval


# FROM `tabMaterial Indent` mi

# LEFT JOIN `tabMaterial Request Item` mii
# ON mi.name=mii.parent

# {conditions}

# ORDER BY mi.name DESC

# """, filters, as_dict=1)

#     return data



# import frappe


# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters or {})
#     return columns, data


# def get_columns():
#     return [
#         {"label":"Material Indent ID","fieldname":"material_indent","fieldtype":"Link","options":"Material Indent","width":170},
#         {"label":"Transaction Date","fieldname":"transaction_date","fieldtype":"Date","width":120},
#         {"label":"Company","fieldname":"company","width":220},

#         {"label":"User Department","fieldname":"user_department","width":180},
#         {"label":"Item Code","fieldname":"item_code","width":160},

#         {"label":"Indent Qty","fieldname":"indent_qty","width":110},
#         {"label":"Purchase Req Qty","fieldname":"purchase_req_qty","width":130},
#         {"label":"Issued Qty","fieldname":"issued_qty","width":110},
#         {"label":"Remaining Issue Qty","fieldname":"remaining_issue_qty","width":150},

#         {"label":"PO Qty","fieldname":"po_qty","width":120},
#         {"label":"PO Pending Qty","fieldname":"po_pending_qty","width":130},

#         {"label":"GRN Qty","fieldname":"grn_qty","width":110},
#         {"label":"GRN Pending Qty","fieldname":"grn_pending_qty","width":140},

#         {"label":"L1 Approval","fieldname":"l1_approval","width":180},
#         {"label":"L2 Approval","fieldname":"l2_approval","width":180},
#         {"label":"L3 Approval","fieldname":"l3_approval","width":180},
#     ]


# def get_data(filters):

#     conditions = " WHERE mi.docstatus < 2 "

#     if filters.get("from_date"):
#         conditions += " AND mi.transaction_date >= %(from_date)s "

#     if filters.get("to_date"):
#         conditions += " AND mi.transaction_date <= %(to_date)s "

#     if filters.get("company"):
#         conditions += " AND mi.company=%(company)s "

#     if filters.get("item_code"):
#         conditions += " AND mii.item_code=%(item_code)s "

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
#         )=%(custom_department)s
#         """


#     data = frappe.db.sql(f"""

# SELECT

# mi.name material_indent,
# mi.transaction_date,
# mi.company,

# CASE
# WHEN mi.custom_username LIKE '%% - %% - %%'
# THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(mi.custom_username, ' - ', 2), ' - ', -1))
# WHEN mi.custom_username LIKE '%% - %%'
# THEN TRIM(SUBSTRING_INDEX(mi.custom_username, ' - ', 1))
# ELSE mi.custom_username
# END user_department,

# mii.item_code,
# IFNULL(mii.qty,0) indent_qty,


# -- MR
# IFNULL(
# (
# SELECT SUM(pri.qty)
# FROM `tabMaterial Request` mr
# JOIN `tabMaterial Request Item` pri ON pri.parent=mr.name
# WHERE mr.custom_material_indent=mi.name
# AND pri.item_code=mii.item_code
# AND mr.docstatus<2
# ),0
# ) purchase_req_qty,


# -- Issued
# IFNULL(
# (
# SELECT SUM(sd.qty)
# FROM `tabStock Entry` se
# JOIN `tabStock Entry Detail` sd ON sd.parent=se.name
# WHERE se.custom_material_indent=mi.name
# AND sd.item_code=mii.item_code
# AND se.docstatus=1
# ),0
# ) issued_qty,


# -- Remaining Issue
# (
# IFNULL(mii.qty,0)
# -
# IFNULL(
# (
# SELECT SUM(sd.qty)
# FROM `tabStock Entry` se
# JOIN `tabStock Entry Detail` sd ON sd.parent=se.name
# WHERE se.custom_material_indent=mi.name
# AND sd.item_code=mii.item_code
# AND se.docstatus=1
# ),0)
# ) remaining_issue_qty,


# -- ✅ PO Qty
# IFNULL(
# (
# SELECT SUM(poi.qty)
# FROM `tabPurchase Order Item` poi
# JOIN `tabPurchase Order` po ON po.name = poi.parent
# JOIN `tabMaterial Request` mr ON mr.name = poi.material_request
# WHERE mr.custom_material_indent = mi.name
# AND poi.item_code = mii.item_code
# AND po.docstatus = 1
# ),0
# ) po_qty,


# -- ✅ PO Pending
# (
#     (
#         IFNULL(mii.qty,0)
#         -
#         IFNULL(
#         (
#             SELECT SUM(sd.qty)
#             FROM `tabStock Entry` se
#             JOIN `tabStock Entry Detail` sd ON sd.parent=se.name
#             WHERE se.custom_material_indent=mi.name
#             AND sd.item_code=mii.item_code
#             AND se.docstatus=1
#         ),0)
#     )
#     -
#     IFNULL(
#     (
#         SELECT SUM(poi.qty)
#         FROM `tabPurchase Order Item` poi
#         JOIN `tabPurchase Order` po ON po.name = poi.parent
#         JOIN `tabMaterial Request` mr ON mr.name = poi.material_request
#         WHERE mr.custom_material_indent = mi.name
#         AND poi.item_code = mii.item_code
#         AND po.docstatus = 1
#     ),0)
# ) po_pending_qty,


# -- ✅ GRN Qty
# IFNULL(
# (
# SELECT SUM(pri.qty)
# FROM `tabPurchase Receipt Item` pri
# JOIN `tabPurchase Receipt` pr ON pr.name = pri.parent
# WHERE pri.purchase_order IN (
#     SELECT po.name
#     FROM `tabPurchase Order` po
#     JOIN `tabPurchase Order Item` poi ON poi.parent = po.name
#     JOIN `tabMaterial Request` mr ON mr.name = poi.material_request
#     WHERE mr.custom_material_indent = mi.name
# )
# AND pri.item_code = mii.item_code
# AND pr.docstatus = 1
# ),0
# ) grn_qty,


# -- ✅ GRN Pending
# (
#     IFNULL(
#     (
#         SELECT SUM(poi.qty)
#         FROM `tabPurchase Order Item` poi
#         JOIN `tabPurchase Order` po ON po.name = poi.parent
#         JOIN `tabMaterial Request` mr ON mr.name = poi.material_request
#         WHERE mr.custom_material_indent = mi.name
#         AND poi.item_code = mii.item_code
#         AND po.docstatus = 1
#     ),0)
#     -
#     IFNULL(
#     (
#         SELECT SUM(pri.qty)
#         FROM `tabPurchase Receipt Item` pri
#         JOIN `tabPurchase Receipt` pr ON pr.name = pri.parent
#         WHERE pri.purchase_order IN (
#             SELECT po.name
#             FROM `tabPurchase Order` po
#             JOIN `tabPurchase Order Item` poi ON poi.parent = po.name
#             JOIN `tabMaterial Request` mr ON mr.name = poi.material_request
#             WHERE mr.custom_material_indent = mi.name
#         )
#         AND pri.item_code = mii.item_code
#         AND pr.docstatus = 1
#     ),0)
# ) grn_pending_qty,


# -- Approvals
# IFNULL(
# (
# SELECT CONCAT(a1.user,' / ',DATE_FORMAT(a1.date_time,'%%d-%%m-%%Y'))
# FROM `tabMaterial Request Activity` a1
# WHERE a1.parent IN (
# SELECT mr.name FROM `tabMaterial Request` mr WHERE mr.custom_material_indent=mi.name
# )
# AND a1.action='L1 Approved'
# ORDER BY a1.date_time LIMIT 1
# ),'') l1_approval,

# IFNULL(
# (
# SELECT CONCAT(a2.user,' / ',DATE_FORMAT(a2.date_time,'%%d-%%m-%%Y'))
# FROM `tabMaterial Request Activity` a2
# WHERE a2.parent IN (
# SELECT mr.name FROM `tabMaterial Request` mr WHERE mr.custom_material_indent=mi.name
# )
# AND a2.action='L2 Approved'
# ORDER BY a2.date_time LIMIT 1
# ),'') l2_approval,

# IFNULL(
# (
# SELECT CONCAT(a3.user,' / ',DATE_FORMAT(a3.date_time,'%%d-%%m-%%Y'))
# FROM `tabMaterial Request Activity` a3
# WHERE a3.parent IN (
# SELECT mr.name FROM `tabMaterial Request` mr WHERE mr.custom_material_indent=mi.name
# )
# AND a3.action='L3 Approved'
# ORDER BY a3.date_time LIMIT 1
# ),'') l3_approval


# FROM `tabMaterial Indent` mi
# LEFT JOIN `tabMaterial Request Item` mii ON mi.name=mii.parent

# {conditions}
# ORDER BY mi.name DESC

# """, filters, as_dict=1)

#     return data

import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {"label":"Material Indent ID","fieldname":"material_indent","fieldtype":"Link","options":"Material Indent","width":170},
        {"label":"Transaction Date","fieldname":"transaction_date","fieldtype":"Date","width":120},
        {"label":"Company","fieldname":"company","width":220},

        {"label":"User Department","fieldname":"user_department","width":180},
        {"label":"Item Code","fieldname":"item_code","width":160},

        {"label":"Indent Qty","fieldname":"indent_qty","width":110},
        {"label":"Purchase Req Qty","fieldname":"purchase_req_qty","width":130},
        {"label":"Issued Qty","fieldname":"issued_qty","width":110},
        {"label":"Remaining Issue Qty","fieldname":"remaining_issue_qty","width":150},

        {"label":"PO Qty","fieldname":"po_qty","width":120},
        {"label":"PO Pending Qty","fieldname":"po_pending_qty","width":130},

        {"label":"GRN Qty","fieldname":"grn_qty","width":110},
        {"label":"GRN Pending Qty","fieldname":"grn_pending_qty","width":140},

        {"label":"L1 Approval","fieldname":"l1_approval","width":180},
        {"label":"L2 Approval","fieldname":"l2_approval","width":180},
        {"label":"L3 Approval","fieldname":"l3_approval","width":180},
    ]


def get_data(filters):

    conditions = " WHERE mi.docstatus < 2 "

    if filters.get("from_date"):
        conditions += " AND mi.transaction_date >= %(from_date)s "

    if filters.get("to_date"):
        conditions += " AND mi.transaction_date <= %(to_date)s "

    if filters.get("company"):
        conditions += " AND mi.company=%(company)s "

    if filters.get("item_code"):
        conditions += " AND mii.item_code=%(item_code)s "

    # ✅ UPDATED FILTER LOGIC
    if filters.get("custom_department"):
        conditions += """
        AND TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(mi.custom_username, ' - ', 2), ' - ', -1)) = %(custom_department)s
        """


    data = frappe.db.sql(f"""

SELECT

mi.name material_indent,
mi.transaction_date,
mi.company,

-- ✅ FINAL DEPARTMENT FORMAT (Dept - Code)
CONCAT(
    TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(mi.custom_username, ' - ', 2), ' - ', -1)),
    ' - ',
    TRIM(SUBSTRING_INDEX(mi.custom_username, ' - ', -1))
) as user_department,

mii.item_code,
IFNULL(mii.qty,0) indent_qty,


-- MR
IFNULL(
(
SELECT SUM(pri.qty)
FROM `tabMaterial Request` mr
JOIN `tabMaterial Request Item` pri ON pri.parent=mr.name
WHERE mr.custom_material_indent=mi.name
AND pri.item_code=mii.item_code
AND mr.docstatus<2
),0
) purchase_req_qty,


-- Issued
IFNULL(
(
SELECT SUM(sd.qty)
FROM `tabStock Entry` se
JOIN `tabStock Entry Detail` sd ON sd.parent=se.name
WHERE se.custom_material_indent=mi.name
AND sd.item_code=mii.item_code
AND se.docstatus=1
),0
) issued_qty,


-- Remaining Issue
(
IFNULL(mii.qty,0)
-
IFNULL(
(
SELECT SUM(sd.qty)
FROM `tabStock Entry` se
JOIN `tabStock Entry Detail` sd ON sd.parent=se.name
WHERE se.custom_material_indent=mi.name
AND sd.item_code=mii.item_code
AND se.docstatus=1
),0)
) remaining_issue_qty,


-- PO Qty
IFNULL(
(
SELECT SUM(poi.qty)
FROM `tabPurchase Order Item` poi
JOIN `tabPurchase Order` po ON po.name = poi.parent
JOIN `tabMaterial Request` mr ON mr.name = poi.material_request
WHERE mr.custom_material_indent = mi.name
AND poi.item_code = mii.item_code
AND po.docstatus = 1
),0
) po_qty,


-- PO Pending
(
    (
        IFNULL(mii.qty,0)
        -
        IFNULL(
        (
            SELECT SUM(sd.qty)
            FROM `tabStock Entry` se
            JOIN `tabStock Entry Detail` sd ON sd.parent=se.name
            WHERE se.custom_material_indent=mi.name
            AND sd.item_code=mii.item_code
            AND se.docstatus=1
        ),0)
    )
    -
    IFNULL(
    (
        SELECT SUM(poi.qty)
        FROM `tabPurchase Order Item` poi
        JOIN `tabPurchase Order` po ON po.name = poi.parent
        JOIN `tabMaterial Request` mr ON mr.name = poi.material_request
        WHERE mr.custom_material_indent = mi.name
        AND poi.item_code = mii.item_code
        AND po.docstatus = 1
    ),0)
) po_pending_qty,


-- GRN Qty
IFNULL(
(
SELECT SUM(pri.qty)
FROM `tabPurchase Receipt Item` pri
JOIN `tabPurchase Receipt` pr ON pr.name = pri.parent
WHERE pri.purchase_order IN (
    SELECT po.name
    FROM `tabPurchase Order` po
    JOIN `tabPurchase Order Item` poi ON poi.parent = po.name
    JOIN `tabMaterial Request` mr ON mr.name = poi.material_request
    WHERE mr.custom_material_indent = mi.name
)
AND pri.item_code = mii.item_code
AND pr.docstatus = 1
),0
) grn_qty,


-- GRN Pending
(
    IFNULL(
    (
        SELECT SUM(poi.qty)
        FROM `tabPurchase Order Item` poi
        JOIN `tabPurchase Order` po ON po.name = poi.parent
        JOIN `tabMaterial Request` mr ON mr.name = poi.material_request
        WHERE mr.custom_material_indent = mi.name
        AND poi.item_code = mii.item_code
        AND po.docstatus = 1
    ),0)
    -
    IFNULL(
    (
        SELECT SUM(pri.qty)
        FROM `tabPurchase Receipt Item` pri
        JOIN `tabPurchase Receipt` pr ON pr.name = pri.parent
        WHERE pri.purchase_order IN (
            SELECT po.name
            FROM `tabPurchase Order` po
            JOIN `tabPurchase Order Item` poi ON poi.parent = po.name
            JOIN `tabMaterial Request` mr ON mr.name = poi.material_request
            WHERE mr.custom_material_indent = mi.name
        )
        AND pri.item_code = mii.item_code
        AND pr.docstatus = 1
    ),0)
) grn_pending_qty,


-- Approvals
IFNULL(
(
SELECT CONCAT(a1.user,' / ',DATE_FORMAT(a1.date_time,'%%d-%%m-%%Y'))
FROM `tabMaterial Request Activity` a1
WHERE a1.parent IN (
SELECT mr.name FROM `tabMaterial Request` mr WHERE mr.custom_material_indent=mi.name
)
AND a1.action='L1 Approved'
ORDER BY a1.date_time LIMIT 1
),'') l1_approval,

IFNULL(
(
SELECT CONCAT(a2.user,' / ',DATE_FORMAT(a2.date_time,'%%d-%%m-%%Y'))
FROM `tabMaterial Request Activity` a2
WHERE a2.parent IN (
SELECT mr.name FROM `tabMaterial Request` mr WHERE mr.custom_material_indent=mi.name
)
AND a2.action='L2 Approved'
ORDER BY a2.date_time LIMIT 1
),'') l2_approval,

IFNULL(
(
SELECT CONCAT(a3.user,' / ',DATE_FORMAT(a3.date_time,'%%d-%%m-%%Y'))
FROM `tabMaterial Request Activity` a3
WHERE a3.parent IN (
SELECT mr.name FROM `tabMaterial Request` mr WHERE mr.custom_material_indent=mi.name
)
AND a3.action='L3 Approved'
ORDER BY a3.date_time LIMIT 1
),'') l3_approval


FROM `tabMaterial Indent` mi
LEFT JOIN `tabMaterial Request Item` mii ON mi.name=mii.parent

{conditions}
ORDER BY mi.name DESC

""", filters, as_dict=1)

    return data