# # # Copyright (c) 2026, Abhijeet and contributors
# # # For license information, please see license.txt

# # import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data


# import frappe
# from datetime import datetime


# def execute(filters=None):
#     filters = frappe._dict(filters or {})
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data


# # ---------------- COLUMNS ----------------

# def get_columns():
#     return [
#         {"label": "Material Request ID", "fieldname": "name", "fieldtype": "Link", "options": "Material Request", "width": 180},
#         {"label": "Transaction Date", "fieldname": "transaction_date", "fieldtype": "Date", "width": 120},
#         {"label": "User Department", "fieldname": "custom_department", "fieldtype": "Link", "options": "Department", "width": 150},
#         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
#         {"label": "Indent Qty", "fieldname": "qty", "fieldtype": "Float", "width": 120},
#         {"label": "PO Pending Qty", "fieldname": "qty_to_order", "fieldtype": "Float", "width": 140},
#         {"label": "GRN Qty", "fieldname": "grn_qty", "fieldtype": "Float", "width": 120},
#         {"label": "GRN Pending Qty", "fieldname": "qty_to_receive", "fieldtype": "Float", "width": 140},
#         {"label": "Level 1 Approval", "fieldname": "level1", "fieldtype": "Data", "width": 200},
#         {"label": "Level 2 Approval", "fieldname": "level2", "fieldtype": "Data", "width": 200},
#         {"label": "Level 3 Approval", "fieldname": "level3", "fieldtype": "Data", "width": 200},
#         {"label": "Level 4 Approval", "fieldname": "level4", "fieldtype": "Data", "width": 200},
#     ]


# # ---------------- DATA ----------------

# def get_data(filters):

#     conditions = []
#     values = {}

#     if filters.get("from_date") and filters.get("to_date"):
#         conditions.append("mr.transaction_date BETWEEN %(from_date)s AND %(to_date)s")
#         values["from_date"] = filters.get("from_date")
#         values["to_date"] = filters.get("to_date")

#     if filters.get("custom_department"):
#         conditions.append("custom_department = %(users_department)s")
#         values["custom_department"] = filters.get("custom_department")

#     if filters.get("item_code"):
#         conditions.append("mri.item_code = %(item_code)s")
#         values["item_code"] = filters.get("item_code")

#     condition_str = ""
#     if conditions:
#         condition_str = " AND " + " AND ".join(conditions)

#     raw_data = frappe.db.sql(f"""
#         SELECT
#             mr.name,
#             mr.transaction_date,
#             custom_department,
#             mri.name as mri_name,
#             mri.item_code,
#             mri.qty,

#             IFNULL((
#                 SELECT SUM(poi.qty)
#                 FROM `tabPurchase Order Item` poi
#                 INNER JOIN `tabPurchase Order` po ON po.name = poi.parent
#                 WHERE
#                     poi.material_request = mr.name
#                     AND poi.material_request_item = mri.name
#                     AND po.docstatus = 1
#             ), 0) as ordered_qty,

#             IFNULL((
#                 SELECT SUM(pri.qty)
#                 FROM `tabPurchase Receipt Item` pri
#                 INNER JOIN `tabPurchase Receipt` pr ON pr.name = pri.parent
#                 WHERE
#                     pri.material_request = mr.name
#                     AND pri.material_request_item = mri.name
#                     AND pr.docstatus = 1
#             ), 0) as grn_qty

#         FROM
#             `tabMaterial Request` mr
#         INNER JOIN
#             `tabMaterial Request Item` mri
#             ON mr.name = mri.parent
#         WHERE
#             1=1 {condition_str}
#         ORDER BY
#             mr.transaction_date DESC
#     """, values, as_dict=1)

#     final_data = []

#     # 🔥 USER CACHE (performance optimization)
#     user_cache = {}

#     def get_full_name(user):
#         if not user:
#             return ""
#         if user in user_cache:
#             return user_cache[user]

#         full_name = frappe.db.get_value("User", user, "full_name") or user
#         user_cache[user] = full_name
#         return full_name

#     for row in raw_data:

#         qty_to_order = max(row.qty - row.ordered_qty, 0)
#         qty_to_receive = max(row.ordered_qty - row.grn_qty, 0)

#         level1 = ""
#         level2 = ""
#         level3 = ""
#         level4 = ""

#         # -------- GET WORKFLOW APPROVALS --------
#         workflow_logs = frappe.get_all(
#             "Workflow Action",
#             filters={
#                 "reference_doctype": "Material Request",
#                 "reference_name": row.name
#             },
#             fields=["workflow_state", "owner", "creation"],
#             order_by="creation asc"
#         )

#         for log in workflow_logs:

#             state = log.workflow_state
#             user_full_name = get_full_name(log.owner)
#             date_only = log.creation.strftime("%d-%m-%Y")

#             if state == "L2 Approval Pending" and not level1:
#                 level1 = f"{user_full_name} / {date_only}"

#             elif state == "L3 Approval Pending" and not level2:
#                 level2 = f"{user_full_name} / {date_only}"

#             elif state == "L4 Approval Pending" and not level3:
#                 level3 = f"{user_full_name} / {date_only}"

#         # -------- FINAL APPROVAL --------
#         mr_doc = frappe.get_doc("Material Request", row.name)

#         if mr_doc.workflow_state == "Approved":
#             final_user_name = get_full_name(mr_doc.modified_by)
#             level4 = f"{final_user_name} / {mr_doc.modified.strftime('%d-%m-%Y')}"

#         final_data.append({
#             "name": row.name,
#             "transaction_date": row.transaction_date,
#             "custom_department": row.custom_department,
#             "item_code": row.item_code,
#             "qty": row.qty,
#             "qty_to_order": qty_to_order,
#             "grn_qty": row.grn_qty,
#             "qty_to_receive": qty_to_receive,
#             "level1": level1,
#             "level2": level2,
#             "level3": level3,
#             "level4": level4
#         })

#     return final_data





import frappe


def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label":"Material Request ID",
            "fieldname":"name",
            "fieldtype":"Link",
            "options":"Material Request",
            "width":180
        },
        {
            "label":"Transaction Date",
            "fieldname":"transaction_date",
            "fieldtype":"Date",
            "width":120
        },
        {
            "label":"User Department",
            "fieldname":"custom_department",
            "fieldtype":"Link",
            "options":"Department",
            "width":150
        },
        {
            "label":"Item Code",
            "fieldname":"item_code",
            "fieldtype":"Link",
            "options":"Item",
            "width":150
        },
        {
            "label":"Indent Qty",
            "fieldname":"qty",
            "fieldtype":"Float",
            "width":120
        },
        {
            "label":"PO Pending Qty",
            "fieldname":"qty_to_order",
            "fieldtype":"Float",
            "width":140
        },
        {
            "label":"GRN Qty",
            "fieldname":"grn_qty",
            "fieldtype":"Float",
            "width":120
        },
        {
            "label":"GRN Pending Qty",
            "fieldname":"qty_to_receive",
            "fieldtype":"Float",
            "width":140
        },
        {
            "label":"Level 1 Approval",
            "fieldname":"level1",
            "fieldtype":"Data",
            "width":200
        },
        {
            "label":"Level 2 Approval",
            "fieldname":"level2",
            "fieldtype":"Data",
            "width":200
        },
        {
            "label":"Level 3 Approval",
            "fieldname":"level3",
            "fieldtype":"Data",
            "width":200
        }
    ]


def get_data(filters):

    conditions=[]
    values={}

    # show submitted but exclude rejected/cancelled
    conditions.append("mr.docstatus=1")
    conditions.append("IFNULL(mr.status,'')!='Rejected'")
    conditions.append("IFNULL(mr.status,'')!='Cancelled'")


    if filters.get("from_date") and filters.get("to_date"):
        conditions.append(
            "mr.transaction_date BETWEEN %(from_date)s AND %(to_date)s"
        )
        values["from_date"]=filters.from_date
        values["to_date"]=filters.to_date


    if filters.get("users_department"):
        conditions.append(
            "mr.custom_department=%(users_department)s"
        )
        values["users_department"]=filters.users_department


    if filters.get("item_code"):
        conditions.append(
            "mri.item_code=%(item_code)s"
        )
        values["item_code"]=filters.item_code


    condition_str=""
    if conditions:
        condition_str=" AND " + " AND ".join(conditions)


    raw_data=frappe.db.sql(f"""
        SELECT
            mr.name,
            mr.transaction_date,
            mr.custom_department,
            mri.name as mri_name,
            mri.item_code,
            mri.qty,

            IFNULL((
                SELECT SUM(poi.qty)
                FROM `tabPurchase Order Item` poi
                INNER JOIN `tabPurchase Order` po
                ON po.name=poi.parent
                WHERE
                    poi.material_request=mr.name
                    AND poi.material_request_item=mri.name
                    AND po.docstatus=1
            ),0) as ordered_qty,

            IFNULL((
                SELECT SUM(pri.qty)
                FROM `tabPurchase Receipt Item` pri
                INNER JOIN `tabPurchase Receipt` pr
                ON pr.name=pri.parent
                WHERE
                    pri.material_request=mr.name
                    AND pri.material_request_item=mri.name
                    AND pr.docstatus=1
            ),0) as grn_qty

        FROM `tabMaterial Request` mr
        INNER JOIN `tabMaterial Request Item` mri
        ON mr.name=mri.parent

        WHERE 1=1
        {condition_str}

        ORDER BY mr.transaction_date DESC

    """,values,as_dict=1)



    user_cache={}

    def get_full_name(user):
        if not user:
            return ""

        if user in user_cache:
            return user_cache[user]

        name=frappe.db.get_value(
            "User",
            user,
            "full_name"
        ) or user

        user_cache[user]=name
        return name


    final_data=[]

    for row in raw_data:

        qty_to_order=max(row.qty-row.ordered_qty,0)
        qty_to_receive=max(row.ordered_qty-row.grn_qty,0)

        level1=""
        level2=""
        level3=""

        logs=frappe.get_all(
            "Material Request Activity",
            filters={
                "parent":row.name,
                "parenttype":"Material Request"
            },
            fields=[
                "action",
                "user",
                "date_time"
            ],
            order_by="date_time asc"
        )


        for log in logs:

            action=log.action
            user_name=get_full_name(log.user)

            date_only=""
            if log.date_time:
                date_only=log.date_time.strftime("%d-%m-%Y")


            if action=="L1 Approved" and not level1:
                level1=f"{user_name} / {date_only}"

            elif action=="L2 Approved" and not level2:
                level2=f"{user_name} / {date_only}"

            elif action=="L3 Approved" and not level3:
                level3=f"{user_name} / {date_only}"


        final_data.append({
            "name":row.name,
            "transaction_date":row.transaction_date,
            "custom_department":row.custom_department,
            "item_code":row.item_code,
            "qty":row.qty,
            "qty_to_order":qty_to_order,
            "grn_qty":row.grn_qty,
            "qty_to_receive":qty_to_receive,
            "level1":level1,
            "level2":level2,
            "level3":level3
        })

    return final_data