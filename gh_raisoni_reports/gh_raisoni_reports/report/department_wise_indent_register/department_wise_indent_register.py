


# # import frappe




# # def execute(filters=None):
# #     filters = frappe._dict(filters or {})
# #     columns = get_columns()
# #     data = get_data(filters)
# #     return columns, data


# # def get_columns():
# #     return [
# #         {
# #             "label":"Material Request ID",
# #             "fieldname":"name",
# #             "fieldtype":"Link",
# #             "options":"Material Indent",
# #             "width":180
# #         },
# #         {
# #             "label":"Transaction Date",
# #             "fieldname":"transaction_date",
# #             "fieldtype":"Date",
# #             "width":120
# #         },
# #         {
# #             "label":"User Department",
# #             "fieldname":"custom_department",
# #             "fieldtype":"Link",
# #             "options":"Department",
# #             "width":150
# #         },
# #         {
# #             "label":"Item Code",
# #             "fieldname":"item_code",
# #             "fieldtype":"Link",
# #             "options":"Item",
# #             "width":150
# #         },
# #         {
# #             "label":"Purchase Request Qty",
# #             "fieldname":"purchase_request_qty",
# #             "fieldtype":"Float",
# #             "width":150
# #         },
# #         {
# #             "label":"Indent Qty",
# #             "fieldname":"indent_qty",
# #             "fieldtype":"Float",
# #             "width":120
# #         },
# #         {
# #             "label":"PO Pending Qty",
# #             "fieldname":"qty_to_order",
# #             "fieldtype":"Float",
# #             "width":140
# #         },
# #         {
# #             "label":"GRN Qty",
# #             "fieldname":"grn_qty",
# #             "fieldtype":"Float",
# #             "width":120
# #         },
# #         {
# #             "label":"GRN Pending Qty",
# #             "fieldname":"qty_to_receive",
# #             "fieldtype":"Float",
# #             "width":140
# #         },
# #         {
# #             "label":"Level 1 Approval",
# #             "fieldname":"level1",
# #             "fieldtype":"Data",
# #             "width":200
# #         },
# #         {
# #             "label":"Level 2 Approval",
# #             "fieldname":"level2",
# #             "fieldtype":"Data",
# #             "width":200
# #         },
# #         {
# #             "label":"Level 3 Approval",
# #             "fieldname":"level3",
# #             "fieldtype":"Data",
# #             "width":200
# #         }
# #     ]


# # def get_data(filters):

# #     conditions=[]
# #     values={}

# #     conditions.append("mi.docstatus=1")
# #     conditions.append("IFNULL(mi.status,'')!='Rejected'")
# #     conditions.append("IFNULL(mi.status,'')!='Cancelled'")


# #     if filters.get("from_date") and filters.get("to_date"):
# #         conditions.append(
# #             "mi.transaction_date BETWEEN %(from_date)s AND %(to_date)s"
# #         )
# #         values["from_date"]=filters.from_date
# #         values["to_date"]=filters.to_date


# #     if filters.get("users_department"):
# #         conditions.append(
# #             "mi.custom_department=%(users_department)s"
# #         )
# #         values["users_department"]=filters.users_department


# #     if filters.get("item_code"):
# #         conditions.append(
# #             "mri.item_code=%(item_code)s"
# #         )
# #         values["item_code"]=filters.item_code


# #     condition_str=""
# #     if conditions:
# #         condition_str=" AND " + " AND ".join(conditions)



# #     raw_data=frappe.db.sql(f"""
# #         SELECT
# #             mi.name,
# #             mi.transaction_date,
# #             mi.custom_department,

# #             mri.name as mri_name,
# #             mri.item_code,

# #             IFNULL(mri.purchase_qty,0) as purchase_request_qty,
# #             IFNULL(mri.qty,0) as indent_qty,


# #             IFNULL((
# #                 SELECT SUM(poi.qty)
# #                 FROM `tabPurchase Order Item` poi
# #                 INNER JOIN `tabPurchase Order` po
# #                 ON po.name=poi.parent
# #                 WHERE
# #                     poi.material_request=mi.name
# #                     AND poi.material_request_item=mri.name
# #                     AND po.docstatus=1
# #             ),0) as ordered_qty,


# #             IFNULL((
# #                 SELECT SUM(pri.qty)
# #                 FROM `tabPurchase Receipt Item` pri
# #                 INNER JOIN `tabPurchase Receipt` pr
# #                 ON pr.name=pri.parent
# #                 WHERE
# #                     pri.material_request=mi.name
# #                     AND pri.material_request_item=mri.name
# #                     AND pr.docstatus=1
# #             ),0) as grn_qty


# #         FROM `tabMaterial Indent` mi
# #         INNER JOIN `tabMaterial Request Item` mri
# #         ON mi.name = mri.parent

# #         WHERE 1=1
# #         {condition_str}

# #         ORDER BY mi.transaction_date DESC

# #     """,values,as_dict=1)



# #     user_cache={}

# #     def get_full_name(user):
# #         if not user:
# #             return ""

# #         if user in user_cache:
# #             return user_cache[user]

# #         name=frappe.db.get_value(
# #             "User",
# #             user,
# #             "full_name"
# #         ) or user

# #         user_cache[user]=name
# #         return name


# #     final_data=[]

# #     for row in raw_data:

# #         qty_to_order=max(
# #             row.purchase_request_qty-row.ordered_qty,
# #             0
# #         )

# #         qty_to_receive=max(
# #             row.ordered_qty-row.grn_qty,
# #             0
# #         )


# #         level1=""
# #         level2=""
# #         level3=""


# #         logs=frappe.get_all(
# #             "Material Request Activity",
# #             filters={
# #                 "parent":row.name
# #             },
# #             fields=[
# #                 "action",
# #                 "user",
# #                 "date_time"
# #             ],
# #             order_by="date_time asc"
# #         )


# #         for log in logs:

# #             action=log.action
# #             user_name=get_full_name(log.user)

# #             date_only=""
# #             if log.date_time:
# #                 date_only=log.date_time.strftime("%d-%m-%Y")


# #             if action=="L1 Approved" and not level1:
# #                 level1=f"{user_name} / {date_only}"

# #             elif action=="L2 Approved" and not level2:
# #                 level2=f"{user_name} / {date_only}"

# #             elif action=="L3 Approved" and not level3:
# #                 level3=f"{user_name} / {date_only}"


# #         final_data.append({
# #             "name":row.name,
# #             "transaction_date":row.transaction_date,
# #             "custom_department":row.custom_department,
# #             "item_code":row.item_code,

# #             "purchase_request_qty":row.purchase_request_qty,
# #             "indent_qty":row.indent_qty,

# #             "qty_to_order":qty_to_order,
# #             "grn_qty":row.grn_qty,
# #             "qty_to_receive":qty_to_receive,

# #             "level1":level1,
# #             "level2":level2,
# #             "level3":level3
# #         })

# #     return final_data





# # Copyright (c) 2026
# # Department Wise Indent Register








# # import frappe


# # def execute(filters=None):
# #     columns = get_columns()
# #     data = get_data(filters or {})
# #     return columns, data


# # def get_columns():
# #     return [
# #         {"label":"Material Request ID","fieldname":"material_indent","fieldtype":"Link","options":"Material Indent","width":170},
# #         {"label":"Transaction Date","fieldname":"transaction_date","fieldtype":"Date","width":120},
# #         {"label":"User Department","fieldname":"user_department","width":180},
# #         {"label":"Item Code","fieldname":"item_code","width":160},

# #         {"label":"Indent Qty","fieldname":"indent_qty","width":110},
       
# #         {"label":"Purchase Req Qty","fieldname":"purchase_req_qty","width":130},
# #         {"label":"Issued Qty","fieldname":"issued_qty","width":110},
# #         {"label":"Remaining Issue Qty","fieldname":"remaining_issue_qty","width":150},
# #          {"label":"PO Pending Qty","fieldname":"po_pending_qty","width":130},
# #         {"label":"GRN Qty","fieldname":"grn_qty","width":110},
# #         {"label":"GRN Pending Qty","fieldname":"grn_pending_qty","width":140},


# #         {"label":"L1 Approval","fieldname":"l1_approval","width":140},
# #         {"label":"L2 Approval","fieldname":"l2_approval","width":140},
# #         {"label":"L3 Approval","fieldname":"l3_approval","width":140},
# #     ]


# # def get_data(filters):

# #     conditions = " WHERE mi.docstatus < 2 "

# #     if filters.get("from_date"):
# #         conditions += " AND mi.transaction_date >= %(from_date)s "

# #     if filters.get("to_date"):
# #         conditions += " AND mi.transaction_date <= %(to_date)s "

# #     if filters.get("item_code"):
# #         conditions += " AND mii.item_code=%(item_code)s "

# #     if filters.get("users_department") and filters.get("users_department") != "All Departments":
# #         conditions += """
# #         AND (
# #             EXISTS(
# #                 SELECT 1
# #                 FROM `tabMaterial Request` mrf
# #                 WHERE mrf.custom_material_indent=mi.name
# #                 AND mrf.custom_department=%(users_department)s
# #             )
# #             OR
# #             EXISTS(
# #                 SELECT 1
# #                 FROM `tabStock Entry` sef
# #                 WHERE sef.custom_material_indent=mi.name
# #                 AND sef.custom_department=%(users_department)s
# #             )
# #         )
# #         """

# #     data = frappe.db.sql(f"""

# # SELECT

# # mi.name material_indent,
# # mi.transaction_date,


# # /* Department from Purchase Request first else Stock Issue */
# # COALESCE(

# # (
# # SELECT mr.custom_department
# # FROM `tabMaterial Request` mr
# # WHERE mr.custom_material_indent=mi.name
# # AND IFNULL(mr.custom_department,'')!=''
# # LIMIT 1
# # ),

# # (
# # SELECT se.custom_department
# # FROM `tabStock Entry` se
# # WHERE se.custom_material_indent=mi.name
# # AND IFNULL(se.custom_department,'')!=''
# # LIMIT 1
# # ),

# # ''

# # ) user_department,


# # mii.item_code,

# # IFNULL(mii.qty,0) indent_qty,


# # /* Purchase Request Qty */
# # IFNULL(
# # (
# # SELECT SUM(pri.qty)
# # FROM `tabMaterial Request` mr
# # JOIN `tabMaterial Request Item` pri
# # ON pri.parent=mr.name
# # WHERE mr.custom_material_indent=mi.name
# # AND pri.item_code=mii.item_code
# # AND mr.docstatus < 2
# # ),0
# # ) purchase_req_qty,



# # /* OLD RAISONI PO PENDING LOGIC */
# # (
# # IFNULL(mii.qty,0)
# # -
# # IFNULL(
# # (
# # SELECT SUM(poi.qty)
# # FROM `tabPurchase Order Item` poi
# # JOIN `tabPurchase Order` po
# # ON po.name=poi.parent
# # WHERE poi.material_request=mi.name
# # AND poi.item_code=mii.item_code
# # AND po.docstatus=1
# # ),0
# # )
# # ) po_pending_qty,



# # /* ACTUAL GRN QTY */
# # IFNULL(
# # (
# # SELECT SUM(pri.qty)
# # FROM `tabPurchase Receipt Item` pri
# # JOIN `tabPurchase Receipt` pr
# # ON pr.name=pri.parent
# # WHERE pri.purchase_order IN (
# #     SELECT poi.parent
# #     FROM `tabPurchase Order Item` poi
# #     WHERE poi.material_request=mi.name
# #     AND poi.item_code=mii.item_code
# # )
# # AND pr.docstatus=1
# # ),0
# # ) grn_qty,



# # /* OLD RAISONI GRN PENDING */
# # (
# # IFNULL(
# # (
# # SELECT SUM(poi.qty)
# # FROM `tabPurchase Order Item` poi
# # JOIN `tabPurchase Order` po
# # ON po.name=poi.parent
# # WHERE poi.material_request=mi.name
# # AND poi.item_code=mii.item_code
# # AND po.docstatus=1
# # ),0
# # )

# # -

# # IFNULL(
# # (
# # SELECT SUM(pri.qty)
# # FROM `tabPurchase Receipt Item` pri
# # JOIN `tabPurchase Receipt` pr
# # ON pr.name=pri.parent
# # WHERE pri.purchase_order IN (
# #     SELECT poi.parent
# #     FROM `tabPurchase Order Item` poi
# #     WHERE poi.material_request=mi.name
# #     AND poi.item_code=mii.item_code
# # )
# # AND pr.docstatus=1
# # ),0
# # )

# # ) grn_pending_qty,



# # /* Issued Qty */
# # IFNULL(
# # (
# # SELECT SUM(sd.qty)
# # FROM `tabStock Entry` se
# # JOIN `tabStock Entry Detail` sd
# # ON sd.parent=se.name
# # WHERE se.custom_material_indent=mi.name
# # AND sd.item_code=mii.item_code
# # AND se.docstatus=1
# # ),0
# # ) issued_qty,



# # /* Remaining Issue */
# # (
# # IFNULL(mii.qty,0)
# # -
# # IFNULL(
# # (
# # SELECT SUM(sd.qty)
# # FROM `tabStock Entry` se
# # JOIN `tabStock Entry Detail` sd
# # ON sd.parent=se.name
# # WHERE se.custom_material_indent=mi.name
# # AND sd.item_code=mii.item_code
# # AND se.docstatus=1
# # ),0
# # )
# # ) remaining_issue_qty,



# # mi.workflow_state l1_approval,
# # mi.workflow_state l2_approval,
# # mi.workflow_state l3_approval


# # FROM `tabMaterial Indent` mi
# # LEFT JOIN `tabMaterial Request Item` mii
# # ON mi.name=mii.parent

# # {conditions}

# # ORDER BY mi.name DESC

# # """, filters, as_dict=1)

# #     return data


# # import frappe


# # def execute(filters=None):
# #     columns = get_columns()
# #     data = get_data(filters or {})
# #     return columns, data


# # def get_columns():
# #     return [
# #         {"label":"Material Request ID","fieldname":"material_indent","fieldtype":"Link","options":"Material Indent","width":170},
# #         {"label":"Transaction Date","fieldname":"transaction_date","fieldtype":"Date","width":120},
# #         {"label":"User Department","fieldname":"user_department","width":180},
# #         {"label":"Item Code","fieldname":"item_code","width":160},

# #         {"label":"Indent Qty","fieldname":"indent_qty","width":110},
       
# #         {"label":"Purchase Req Qty","fieldname":"purchase_req_qty","width":130},
# #         {"label":"Issued Qty","fieldname":"issued_qty","width":110},
# #         {"label":"Remaining Issue Qty","fieldname":"remaining_issue_qty","width":150},
# #          {"label":"PO Pending Qty","fieldname":"po_pending_qty","width":130},
# #         {"label":"GRN Qty","fieldname":"grn_qty","width":110},
# #         {"label":"GRN Pending Qty","fieldname":"grn_pending_qty","width":140},


# #         {"label":"L1 Approval","fieldname":"l1_approval","width":180},
# #         {"label":"L2 Approval","fieldname":"l2_approval","width":180},
# #         {"label":"L3 Approval","fieldname":"l3_approval","width":180},
# #     ]


# # def get_data(filters):

# #     conditions = " WHERE mi.docstatus < 2 "

# #     if filters.get("from_date"):
# #         conditions += " AND mi.transaction_date >= %(from_date)s "

# #     if filters.get("to_date"):
# #         conditions += " AND mi.transaction_date <= %(to_date)s "

# #     if filters.get("item_code"):
# #         conditions += " AND mii.item_code=%(item_code)s "

# #     if filters.get("users_department") and filters.get("users_department")!="All Departments":
# #         conditions += """
# #         AND (
# #             EXISTS(
# #                 SELECT 1
# #                 FROM `tabMaterial Request` mr
# #                 WHERE mr.custom_material_indent=mi.name
# #                 AND mr.custom_department=%(users_department)s
# #             )
# #             OR
# #             EXISTS(
# #                 SELECT 1
# #                 FROM `tabStock Entry` se
# #                 WHERE se.custom_material_indent=mi.name
# #                 AND se.custom_department=%(users_department)s
# #             )
# #         )
# #         """


# #     data=frappe.db.sql(f"""

# # SELECT

# # mi.name material_indent,
# # mi.transaction_date,


# # COALESCE(
# # (
# # SELECT mr.custom_department
# # FROM `tabMaterial Request` mr
# # WHERE mr.custom_material_indent=mi.name
# # AND IFNULL(mr.custom_department,'')!=''
# # LIMIT 1
# # ),

# # (
# # SELECT se.custom_department
# # FROM `tabStock Entry` se
# # WHERE se.custom_material_indent=mi.name
# # AND IFNULL(se.custom_department,'')!=''
# # LIMIT 1
# # ),

# # ''
# # ) user_department,


# # mii.item_code,

# # IFNULL(mii.qty,0) indent_qty,


# # /* Purchase Request Qty */
# # IFNULL(
# # (
# # SELECT SUM(pri.qty)
# # FROM `tabMaterial Request` mr
# # JOIN `tabMaterial Request Item` pri
# # ON pri.parent=mr.name
# # WHERE mr.custom_material_indent=mi.name
# # AND pri.item_code=mii.item_code
# # AND mr.docstatus<2
# # ),0
# # ) purchase_req_qty,



# # /* PO Pending Qty (old logic like old report) */
# # IFNULL(
# # (
# # SELECT SUM(pri.qty)
# # FROM `tabMaterial Request` mr
# # JOIN `tabMaterial Request Item` pri
# # ON pri.parent=mr.name
# # WHERE mr.custom_material_indent=mi.name
# # AND pri.item_code=mii.item_code
# # AND mr.docstatus<2
# # ),0
# # ) po_pending_qty,



# # /* GRN Qty */
# # IFNULL(
# # (
# # SELECT SUM(poi.qty)
# # FROM `tabPurchase Order Item` poi
# # JOIN `tabPurchase Order` po
# # ON po.name=poi.parent
# # WHERE poi.material_request=mi.name
# # AND poi.item_code=mii.item_code
# # AND po.docstatus=1
# # ),0
# # ) grn_qty,



# # /* GRN Pending Qty */
# # 0 grn_pending_qty,



# # /* Issued Qty */
# # IFNULL(
# # (
# # SELECT SUM(sd.qty)
# # FROM `tabStock Entry` se
# # JOIN `tabStock Entry Detail` sd
# # ON sd.parent=se.name
# # WHERE se.custom_material_indent=mi.name
# # AND sd.item_code=mii.item_code
# # AND se.docstatus=1
# # ),0
# # ) issued_qty,



# # /* Remaining Issue */
# # (
# # IFNULL(mii.qty,0)
# # -
# # IFNULL(
# # (
# # SELECT SUM(sd.qty)
# # FROM `tabStock Entry` se
# # JOIN `tabStock Entry Detail` sd
# # ON sd.parent=se.name
# # WHERE se.custom_material_indent=mi.name
# # AND sd.item_code=mii.item_code
# # AND se.docstatus=1
# # ),0
# # )
# # ) remaining_issue_qty,



# # /* L1 Approval Name + Date */
# # IFNULL(
# # (
# # SELECT CONCAT(a1.user,' / ',DATE_FORMAT(a1.date_time,'%%d-%%m-%%Y'))
# # FROM `tabMaterial Request Activity` a1
# # WHERE a1.parent IN
# # (
# # SELECT mr.name
# # FROM `tabMaterial Request` mr
# # WHERE mr.custom_material_indent=mi.name
# # )
# # AND a1.action='L1 Approved'
# # ORDER BY a1.date_time
# # LIMIT 1
# # ),''
# # ) l1_approval,



# # /* L2 Approval Name + Date */
# # IFNULL(
# # (
# # SELECT CONCAT(a2.user,' / ',DATE_FORMAT(a2.date_time,'%%d-%%m-%%Y'))
# # FROM `tabMaterial Request Activity` a2
# # WHERE a2.parent IN
# # (
# # SELECT mr.name
# # FROM `tabMaterial Request` mr
# # WHERE mr.custom_material_indent=mi.name
# # )
# # AND a2.action='L2 Approved'
# # ORDER BY a2.date_time
# # LIMIT 1
# # ),''
# # ) l2_approval,



# # /* L3 Approval Name + Date */
# # IFNULL(
# # (
# # SELECT CONCAT(a3.user,' / ',DATE_FORMAT(a3.date_time,'%%d-%%m-%%Y'))
# # FROM `tabMaterial Request Activity` a3
# # WHERE a3.parent IN
# # (
# # SELECT mr.name
# # FROM `tabMaterial Request` mr
# # WHERE mr.custom_material_indent=mi.name
# # )
# # AND a3.action='L3 Approved'
# # ORDER BY a3.date_time
# # LIMIT 1
# # ),''
# # ) l3_approval



# # FROM `tabMaterial Indent` mi
# # LEFT JOIN `tabMaterial Request Item` mii
# # ON mi.name=mii.parent

# # {conditions}

# # ORDER BY mi.name DESC

# # """,filters,as_dict=1)

# #     return data


# # import frappe


# # def execute(filters=None):
# #     columns = get_columns()
# #     data = get_data(filters or {})
# #     return columns, data


# # def get_columns():
# #     return [
# #         {"label":"Material Indent ID","fieldname":"material_indent","fieldtype":"Link","options":"Material Indent","width":170},
# #         {"label":"Transaction Date","fieldname":"transaction_date","fieldtype":"Date","width":120},
# #         {"label":"User Department","fieldname":"user_department","width":180},
# #         {"label":"Item Code","fieldname":"item_code","width":160},

# #         {"label":"Indent Qty","fieldname":"indent_qty","width":110},

# #         {"label":"Purchase Req Qty","fieldname":"purchase_req_qty","width":130},
# #         {"label":"Issued Qty","fieldname":"issued_qty","width":110},
# #         {"label":"Remaining Issue Qty","fieldname":"remaining_issue_qty","width":150},

# #         {"label":"PO Pending Qty","fieldname":"po_pending_qty","width":130},
# #         {"label":"GRN Qty","fieldname":"grn_qty","width":110},
# #         {"label":"GRN Pending Qty","fieldname":"grn_pending_qty","width":140},

# #         {"label":"L1 Approval","fieldname":"l1_approval","width":180},
# #         {"label":"L2 Approval","fieldname":"l2_approval","width":180},
# #         {"label":"L3 Approval","fieldname":"l3_approval","width":180},
# #     ]


# # def get_data(filters):

# #     conditions = " WHERE mi.docstatus < 2 "

# #     if filters.get("from_date"):
# #         conditions += " AND mi.transaction_date >= %(from_date)s "

# #     if filters.get("to_date"):
# #         conditions += " AND mi.transaction_date <= %(to_date)s "

# #     if filters.get("item_code"):
# #         conditions += " AND mii.item_code=%(item_code)s "

# #     if filters.get("users_department") and filters.get("users_department")!="All Departments":
# #         conditions += """
# #         AND (
# #             EXISTS(
# #                 SELECT 1
# #                 FROM `tabMaterial Request` mr
# #                 WHERE mr.custom_material_indent=mi.name
# #                 AND mr.custom_department=%(users_department)s
# #             )
# #             OR
# #             EXISTS(
# #                 SELECT 1
# #                 FROM `tabStock Entry` se
# #                 WHERE se.custom_material_indent=mi.name
# #                 AND se.custom_department=%(users_department)s
# #             )
# #         )
# #         """


# #     data = frappe.db.sql(f"""

# # SELECT

# # mi.name material_indent,
# # mi.transaction_date,


# # /* Department Fix */
# # COALESCE(
# # (
# # SELECT mr.custom_department
# # FROM `tabMaterial Request` mr
# # WHERE mr.custom_material_indent=mi.name
# # AND IFNULL(mr.custom_department,'')!=''
# # AND mr.custom_department!='All Departments'
# # LIMIT 1
# # ),

# # (
# # SELECT se.custom_department
# # FROM `tabStock Entry` se
# # WHERE se.custom_material_indent=mi.name
# # AND IFNULL(se.custom_department,'')!=''
# # AND se.custom_department!='All Departments'
# # LIMIT 1
# # ),

# # 'All Departments'
# # ) user_department,

# # mii.item_code,

# # IFNULL(mii.qty,0) indent_qty,


# # /* Purchase Req Qty */
# # IFNULL(
# # (
# # SELECT SUM(pri.qty)
# # FROM `tabMaterial Request` mr
# # JOIN `tabMaterial Request Item` pri
# # ON pri.parent=mr.name
# # WHERE mr.custom_material_indent=mi.name
# # AND pri.item_code=mii.item_code
# # AND mr.docstatus<2
# # ),0
# # ) purchase_req_qty,


# # /* PO Pending Qty */
# # IFNULL(
# # (
# # SELECT SUM(pri.qty)
# # FROM `tabMaterial Request` mr
# # JOIN `tabMaterial Request Item` pri
# # ON pri.parent=mr.name
# # WHERE mr.custom_material_indent=mi.name
# # AND pri.item_code=mii.item_code
# # AND mr.docstatus<2
# # ),0
# # ) po_pending_qty,


# # /* GRN Qty */
# # IFNULL(
# # (
# # SELECT SUM(poi.qty)
# # FROM `tabPurchase Order Item` poi
# # JOIN `tabPurchase Order` po
# # ON po.name=poi.parent
# # WHERE poi.material_request=mi.name
# # AND poi.item_code=mii.item_code
# # AND po.docstatus=1
# # ),0
# # ) grn_qty,


# # 0 grn_pending_qty,


# # /* Issued Qty */
# # IFNULL(
# # (
# # SELECT SUM(sd.qty)
# # FROM `tabStock Entry` se
# # JOIN `tabStock Entry Detail` sd
# # ON sd.parent=se.name
# # WHERE se.custom_material_indent=mi.name
# # AND sd.item_code=mii.item_code
# # AND se.docstatus=1
# # ),0
# # ) issued_qty,


# # (
# # IFNULL(mii.qty,0)
# # -
# # IFNULL(
# # (
# # SELECT SUM(sd.qty)
# # FROM `tabStock Entry` se
# # JOIN `tabStock Entry Detail` sd
# # ON sd.parent=se.name
# # WHERE se.custom_material_indent=mi.name
# # AND sd.item_code=mii.item_code
# # AND se.docstatus=1
# # ),0
# # )
# # ) remaining_issue_qty,



# # /* L1 */
# # IFNULL(
# # (
# # SELECT CONCAT(a1.user,' / ',DATE_FORMAT(a1.date_time,'%%d-%%m-%%Y'))
# # FROM `tabMaterial Request Activity` a1
# # WHERE a1.parent IN (
# # SELECT mr.name
# # FROM `tabMaterial Request` mr
# # WHERE mr.custom_material_indent=mi.name
# # )
# # AND a1.action='L1 Approved'
# # ORDER BY a1.date_time
# # LIMIT 1
# # ),''
# # ) l1_approval,


# # /* L2 */
# # IFNULL(
# # (
# # SELECT CONCAT(a2.user,' / ',DATE_FORMAT(a2.date_time,'%%d-%%m-%%Y'))
# # FROM `tabMaterial Request Activity` a2
# # WHERE a2.parent IN (
# # SELECT mr.name
# # FROM `tabMaterial Request` mr
# # WHERE mr.custom_material_indent=mi.name
# # )
# # AND a2.action='L2 Approved'
# # ORDER BY a2.date_time
# # LIMIT 1
# # ),''
# # ) l2_approval,


# # /* L3 */
# # IFNULL(
# # (
# # SELECT CONCAT(a3.user,' / ',DATE_FORMAT(a3.date_time,'%%d-%%m-%%Y'))
# # FROM `tabMaterial Request Activity` a3
# # WHERE a3.parent IN (
# # SELECT mr.name
# # FROM `tabMaterial Request` mr
# # WHERE mr.custom_material_indent=mi.name
# # )
# # AND a3.action='L3 Approved'
# # ORDER BY a3.date_time
# # LIMIT 1
# # ),''
# # ) l3_approval


# # FROM `tabMaterial Indent` mi
# # LEFT JOIN `tabMaterial Request Item` mii
# # ON mi.name=mii.parent

# # {conditions}

# # ORDER BY mi.name DESC

# # """, filters, as_dict=1)

# #     return data




# # import frappe


# # def execute(filters=None):
# #     columns = get_columns()
# #     data = get_data(filters or {})
# #     return columns, data


# # def get_columns():
# #     return [
# #         {"label":"Material Indent ID","fieldname":"material_indent","fieldtype":"Link","options":"Material Indent","width":170},
# #         {"label":"Transaction Date","fieldname":"transaction_date","fieldtype":"Date","width":120},

# #         {"label":"Company","fieldname":"company","width":220},   # added

# #         {"label":"User Department","fieldname":"user_department","width":180},
# #         {"label":"Item Code","fieldname":"item_code","width":160},

# #         {"label":"Indent Qty","fieldname":"indent_qty","width":110},

# #         {"label":"Purchase Req Qty","fieldname":"purchase_req_qty","width":130},
# #         {"label":"Issued Qty","fieldname":"issued_qty","width":110},
# #         {"label":"Remaining Issue Qty","fieldname":"remaining_issue_qty","width":150},

# #         {"label":"PO Pending Qty","fieldname":"po_pending_qty","width":130},
# #         {"label":"GRN Qty","fieldname":"grn_qty","width":110},
# #         {"label":"GRN Pending Qty","fieldname":"grn_pending_qty","width":140},

# #         {"label":"L1 Approval","fieldname":"l1_approval","width":180},
# #         {"label":"L2 Approval","fieldname":"l2_approval","width":180},
# #         {"label":"L3 Approval","fieldname":"l3_approval","width":180},
# #     ]


# # def get_data(filters):

# #     conditions = " WHERE mi.docstatus < 2 "

# #     if filters.get("from_date"):
# #         conditions += " AND mi.transaction_date >= %(from_date)s "

# #     if filters.get("to_date"):
# #         conditions += " AND mi.transaction_date <= %(to_date)s "

# #     if filters.get("company"):
# #         conditions += " AND mi.company=%(company)s "

# #     if filters.get("item_code"):
# #         conditions += " AND mii.item_code=%(item_code)s "

# #     if filters.get("custom_department") and filters.get("custom_department")!="All Departments":
# #         conditions += """
# #         AND (
# #             EXISTS(
# #                 SELECT 1
# #                 FROM `tabMaterial Request` mr
# #                 WHERE mr.custom_material_indent=mi.name
# #                 AND mr.custom_department=%(custom_department)s
# #             )
# #             OR
# #             EXISTS(
# #                 SELECT 1
# #                 FROM `tabStock Entry` se
# #                 WHERE se.custom_material_indent=mi.name
# #                 AND se.custom_department=%(custom_department)s
# #             )
# #         )
# #         """


# #     data = frappe.db.sql(f"""

# # SELECT

# # mi.name material_indent,
# # mi.transaction_date,

# # mi.company,


# # COALESCE(
# # (
# # SELECT mr.custom_department
# # FROM `tabMaterial Request` mr
# # WHERE mr.custom_material_indent=mi.name
# # AND IFNULL(mr.custom_department,'')!=''
# # AND mr.custom_department!='All Departments'
# # LIMIT 1
# # ),

# # (
# # SELECT se.custom_department
# # FROM `tabStock Entry` se
# # WHERE se.custom_material_indent=mi.name
# # AND IFNULL(se.custom_department,'')!=''
# # AND se.custom_department!='All Departments'
# # LIMIT 1
# # ),

# # 'All Departments'
# # ) user_department,

# # mii.item_code,

# # IFNULL(mii.qty,0) indent_qty,


# # IFNULL(
# # (
# # SELECT SUM(pri.qty)
# # FROM `tabMaterial Request` mr
# # JOIN `tabMaterial Request Item` pri
# # ON pri.parent=mr.name
# # WHERE mr.custom_material_indent=mi.name
# # AND pri.item_code=mii.item_code
# # AND mr.docstatus<2
# # ),0
# # ) purchase_req_qty,


# # IFNULL(
# # (
# # SELECT SUM(pri.qty)
# # FROM `tabMaterial Request` mr
# # JOIN `tabMaterial Request Item` pri
# # ON pri.parent=mr.name
# # WHERE mr.custom_material_indent=mi.name
# # AND pri.item_code=mii.item_code
# # AND mr.docstatus<2
# # ),0
# # ) po_pending_qty,


# # IFNULL(
# # (
# # SELECT SUM(poi.qty)
# # FROM `tabPurchase Order Item` poi
# # JOIN `tabPurchase Order` po
# # ON po.name=poi.parent
# # WHERE poi.material_request=mi.name
# # AND poi.item_code=mii.item_code
# # AND po.docstatus=1
# # ),0
# # ) grn_qty,


# # 0 grn_pending_qty,


# # IFNULL(
# # (
# # SELECT SUM(sd.qty)
# # FROM `tabStock Entry` se
# # JOIN `tabStock Entry Detail` sd
# # ON sd.parent=se.name
# # WHERE se.custom_material_indent=mi.name
# # AND sd.item_code=mii.item_code
# # AND se.docstatus=1
# # ),0
# # ) issued_qty,


# # (
# # IFNULL(mii.qty,0)
# # -
# # IFNULL(
# # (
# # SELECT SUM(sd.qty)
# # FROM `tabStock Entry` se
# # JOIN `tabStock Entry Detail` sd
# # ON sd.parent=se.name
# # WHERE se.custom_material_indent=mi.name
# # AND sd.item_code=mii.item_code
# # AND se.docstatus=1
# # ),0
# # )
# # ) remaining_issue_qty,


# # IFNULL(
# # (
# # SELECT CONCAT(a1.user,' / ',DATE_FORMAT(a1.date_time,'%%d-%%m-%%Y'))
# # FROM `tabMaterial Request Activity` a1
# # WHERE a1.parent IN (
# # SELECT mr.name
# # FROM `tabMaterial Request` mr
# # WHERE mr.custom_material_indent=mi.name
# # )
# # AND a1.action='L1 Approved'
# # ORDER BY a1.date_time
# # LIMIT 1
# # ),''
# # ) l1_approval,


# # IFNULL(
# # (
# # SELECT CONCAT(a2.user,' / ',DATE_FORMAT(a2.date_time,'%%d-%%m-%%Y'))
# # FROM `tabMaterial Request Activity` a2
# # WHERE a2.parent IN (
# # SELECT mr.name
# # FROM `tabMaterial Request` mr
# # WHERE mr.custom_material_indent=mi.name
# # )
# # AND a2.action='L2 Approved'
# # ORDER BY a2.date_time
# # LIMIT 1
# # ),''
# # ) l2_approval,


# # IFNULL(
# # (
# # SELECT CONCAT(a3.user,' / ',DATE_FORMAT(a3.date_time,'%%d-%%m-%%Y'))
# # FROM `tabMaterial Request Activity` a3
# # WHERE a3.parent IN (
# # SELECT mr.name
# # FROM `tabMaterial Request` mr
# # WHERE mr.custom_material_indent=mi.name
# # )
# # AND a3.action='L3 Approved'
# # ORDER BY a3.date_time
# # LIMIT 1
# # ),''
# # ) l3_approval


# # FROM `tabMaterial Indent` mi
# # LEFT JOIN `tabMaterial Request Item` mii
# # ON mi.name=mii.parent

# # {conditions}

# # ORDER BY mi.name DESC

# # """, filters, as_dict=1)

# #     return data
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



import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {"label": "Material Indent ID", "fieldname": "material_indent", "fieldtype": "Link", "options": "Material Indent", "width": 170},
        {"label": "Transaction Date", "fieldname": "transaction_date", "fieldtype": "Date", "width": 120},
        {"label": "Company", "fieldname": "company", "width": 220},
        {"label": "User Department", "fieldname": "user_department", "width": 180},
        {"label": "Item Code", "fieldname": "item_code", "width": 160},
        {"label": "Indent Qty", "fieldname": "indent_qty", "width": 110},
        {"label": "Purchase Req Qty", "fieldname": "purchase_req_qty", "width": 130},
        {"label": "Issued Qty", "fieldname": "issued_qty", "width": 110},
        {"label": "Remaining Issue Qty", "fieldname": "remaining_issue_qty", "width": 150},
        {"label": "PO Pending Qty", "fieldname": "po_pending_qty", "width": 130},
        {"label": "GRN Qty", "fieldname": "grn_qty", "width": 110},
        {"label": "GRN Pending Qty", "fieldname": "grn_pending_qty", "width": 140},
        {"label": "L1 Approval", "fieldname": "l1_approval", "width": 180},
        {"label": "L2 Approval", "fieldname": "l2_approval", "width": 180},
        {"label": "L3 Approval", "fieldname": "l3_approval", "width": 180},
    ]


def get_data(filters):

    conditions = " WHERE mi.docstatus < 2 "

    if filters.get("from_date"):
        conditions += " AND mi.transaction_date >= %(from_date)s "

    if filters.get("to_date"):
        conditions += " AND mi.transaction_date <= %(to_date)s "

    if filters.get("company"):
        conditions += " AND mi.company = %(company)s "

    if filters.get("item_code"):
        conditions += " AND mii.item_code = %(item_code)s "

    # Filter by full custom_username value e.g. "Administrator - All Departments"
    if filters.get("custom_department"):
        conditions += " AND mi.custom_username = %(custom_department)s "

    data = frappe.db.sql(f"""

SELECT

    mi.name AS material_indent,
    mi.transaction_date,
    mi.company,

    -- Display: extract department part after " - ", or show full value
    CASE
        WHEN mi.custom_username LIKE '%% - %%'
        THEN TRIM(SUBSTRING_INDEX(mi.custom_username, ' - ', -1))
        ELSE mi.custom_username
    END AS user_department,

    mii.item_code,

    IFNULL(mii.qty, 0) AS indent_qty,

    -- Purchase Request Qty
    IFNULL((
        SELECT SUM(pri.qty)
        FROM `tabMaterial Request` mr
        JOIN `tabMaterial Request Item` pri ON pri.parent = mr.name
        WHERE mr.custom_material_indent = mi.name
          AND pri.item_code = mii.item_code
          AND mr.docstatus < 2
    ), 0) AS purchase_req_qty,

    -- Issued Qty (from Stock Entry)
    IFNULL((
        SELECT SUM(sd.qty)
        FROM `tabStock Entry` se
        JOIN `tabStock Entry Detail` sd ON sd.parent = se.name
        WHERE se.custom_material_indent = mi.name
          AND sd.item_code = mii.item_code
          AND se.docstatus = 1
    ), 0) AS issued_qty,

    -- Remaining Issue Qty = Indent Qty - Issued Qty
    (
        IFNULL(mii.qty, 0)
        -
        IFNULL((
            SELECT SUM(sd.qty)
            FROM `tabStock Entry` se
            JOIN `tabStock Entry Detail` sd ON sd.parent = se.name
            WHERE se.custom_material_indent = mi.name
              AND sd.item_code = mii.item_code
              AND se.docstatus = 1
        ), 0)
    ) AS remaining_issue_qty,

    -- PO Pending Qty = Purchase Req Qty - GRN Qty
    (
        IFNULL((
            SELECT SUM(pri.qty)
            FROM `tabMaterial Request` mr
            JOIN `tabMaterial Request Item` pri ON pri.parent = mr.name
            WHERE mr.custom_material_indent = mi.name
              AND pri.item_code = mii.item_code
              AND mr.docstatus < 2
        ), 0)
        -
        IFNULL((
            SELECT SUM(poi.qty)
            FROM `tabPurchase Order Item` poi
            JOIN `tabPurchase Order` po ON po.name = poi.parent
            WHERE poi.material_request IN (
                SELECT mr.name
                FROM `tabMaterial Request` mr
                WHERE mr.custom_material_indent = mi.name
            )
              AND poi.item_code = mii.item_code
              AND po.docstatus = 1
        ), 0)
    ) AS po_pending_qty,

    -- GRN Qty (from Purchase Order Items)
    IFNULL((
        SELECT SUM(poi.qty)
        FROM `tabPurchase Order Item` poi
        JOIN `tabPurchase Order` po ON po.name = poi.parent
        WHERE poi.material_request IN (
            SELECT mr.name
            FROM `tabMaterial Request` mr
            WHERE mr.custom_material_indent = mi.name
        )
          AND poi.item_code = mii.item_code
          AND po.docstatus = 1
    ), 0) AS grn_qty,

    -- GRN Pending Qty = Purchase Req Qty - GRN Qty
    (
        IFNULL((
            SELECT SUM(pri.qty)
            FROM `tabMaterial Request` mr
            JOIN `tabMaterial Request Item` pri ON pri.parent = mr.name
            WHERE mr.custom_material_indent = mi.name
              AND pri.item_code = mii.item_code
              AND mr.docstatus < 2
        ), 0)
        -
        IFNULL((
            SELECT SUM(poi.qty)
            FROM `tabPurchase Order Item` poi
            JOIN `tabPurchase Order` po ON po.name = poi.parent
            WHERE poi.material_request IN (
                SELECT mr.name
                FROM `tabMaterial Request` mr
                WHERE mr.custom_material_indent = mi.name
            )
              AND poi.item_code = mii.item_code
              AND po.docstatus = 1
        ), 0)
    ) AS grn_pending_qty,

    -- L1 Approval
    IFNULL((
        SELECT CONCAT(a1.user, ' / ', DATE_FORMAT(a1.date_time, '%%d-%%m-%%Y'))
        FROM `tabMaterial Request Activity` a1
        WHERE a1.parent IN (
            SELECT mr.name FROM `tabMaterial Request` mr
            WHERE mr.custom_material_indent = mi.name
        )
          AND a1.action = 'L1 Approved'
        ORDER BY a1.date_time
        LIMIT 1
    ), '') AS l1_approval,

    -- L2 Approval
    IFNULL((
        SELECT CONCAT(a2.user, ' / ', DATE_FORMAT(a2.date_time, '%%d-%%m-%%Y'))
        FROM `tabMaterial Request Activity` a2
        WHERE a2.parent IN (
            SELECT mr.name FROM `tabMaterial Request` mr
            WHERE mr.custom_material_indent = mi.name
        )
          AND a2.action = 'L2 Approved'
        ORDER BY a2.date_time
        LIMIT 1
    ), '') AS l2_approval,

    -- L3 Approval
    IFNULL((
        SELECT CONCAT(a3.user, ' / ', DATE_FORMAT(a3.date_time, '%%d-%%m-%%Y'))
        FROM `tabMaterial Request Activity` a3
        WHERE a3.parent IN (
            SELECT mr.name FROM `tabMaterial Request` mr
            WHERE mr.custom_material_indent = mi.name
        )
          AND a3.action = 'L3 Approved'
        ORDER BY a3.date_time
        LIMIT 1
    ), '') AS l3_approval

FROM `tabMaterial Indent` mi
LEFT JOIN `tabMaterial Indent Item` mii ON mii.parent = mi.name

{conditions}

ORDER BY mi.name DESC

""", filters, as_dict=1)

    return data