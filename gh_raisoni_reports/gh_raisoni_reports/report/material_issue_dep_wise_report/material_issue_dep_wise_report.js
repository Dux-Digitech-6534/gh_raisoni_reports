frappe.query_reports["Material Issue Dep Wise Report"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "name",
			label: __("Material Issue ID"),
			fieldtype: "Link",
			options: "Stock Entry",
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
		},
		{
			fieldname: "custom_department",
			label: __("User Department"),
			fieldtype: "Link",
			options: "Department",
		},
		{
			fieldname: "s_warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			options: "Warehouse",
		},
		{
			fieldname: "item_name",
			label: __("Item Name"),
			fieldtype: "Data",
		},
	],
};


// ✅ Read checked rows
function mi_read_checked(report) {
    var dt = report.datatable;
    if (!dt || !report.data) return;

    var selected = {};

    // ✅ Correct way to read checked rows in Frappe datatable
    $(dt.wrapper).find(".dt-row").each(function() {
        var $row = $(this);

        var is_checked =
            $row.find("input[type='checkbox']:checked").length > 0 ||
            $row.hasClass("dt-row--highlight");

        if (!is_checked) return;

        // ✅ Get row index from data-row-index attribute
        var row_idx = parseInt(
            $row.find(".dt-cell[data-row-index]").first().attr("data-row-index"), 10
        );

        if (isNaN(row_idx) || row_idx < 0) return;

        var rd = report.data[row_idx];
        if (rd && rd.name) {
            selected[rd.name] = rd;
        }
    });

    report._mi_selected = selected;
    mi_update_button(report);
}

// ✅ Update button count
function mi_update_button(report) {
    var count = Object.keys(report._mi_selected || {}).length;
    if (!report._dp_btn) return;
    report._dp_btn
        .text(__("Detail View") + " (" + count + ")")
        .toggleClass("active", count > 0);
}


// ✅ Fetch item details and open new tab
function mi_fetch_and_render(report) {
    var se_names = Object.keys(report._mi_selected || {});

    if (!se_names.length) {
        frappe.show_alert({
            message: __("Please select at least one Material Issue."),
            indicator: "orange"
        });
        return;
    }

    frappe.call({
        // ✅ UPDATE this path to match your app name
        method: "gh_raisoni_reports.gh_raisoni_reports.report.material_issue_department_wise.material_issue_department_wise.get_material_issue_item_details",
        args: { se_names: se_names },
        freeze: true,
        freeze_message: __("Loading item details..."),
        callback: function(r) {
            var items = r.message || [];
            mi_open_detail_tab(items, se_names);
        },
        error: function() {
            frappe.msgprint(__("Could not load Material Issue item details."));
        }
    });
}


// ✅ Open detail tab
function mi_open_detail_tab(items, se_names) {
    var meta =
        se_names.length + " Material Issue" + (se_names.length > 1 ? "s" : "") +
        ", " + items.length + " item" + (items.length !== 1 ? "s" : "");

    var html =
        '<!doctype html><html><head><title>Material Issue Item Details</title>' +
        '<style>' +
        'body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;margin:0;color:#1f272e;background:#fff;font-size:14px;}' +
        '.page{padding:16px 24px;}' +
        '.report-card{border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;}' +
        '.report-header{padding:14px 16px 10px;border-bottom:1px solid #eef0f2;}' +
        '.title{font-size:18px;font-weight:700;color:#0f172a;margin-bottom:4px;}' +
        '.meta{font-size:13px;color:#64748b;font-weight:600;}' +
        '.filter-row{display:flex;gap:10px;align-items:center;padding:10px 12px;background:#fff;}' +
        '.filter-row input{height:28px;border:0;background:#f3f4f6;border-radius:7px;padding:4px 10px;font-size:13px;outline:none;color:#111827;}' +
        '.filter-row button{height:28px;border:1px solid #d1d5db;background:#fff;border-radius:6px;padding:3px 12px;font-size:13px;font-weight:600;cursor:pointer;color:#111827;}' +
        '.filter-row button:hover{background:#f3f4f6;}' +
        '.table-wrap{overflow:auto;max-height:calc(100vh - 140px);border-top:1px solid #eef0f2;}' +
        'table{width:100%;border-collapse:collapse;}' +
        'th,td{border-right:1px solid #e5e7eb;border-bottom:1px solid #e5e7eb;padding:8px;font-size:13px;white-space:nowrap;}' +
        'th{background:#f3f4f6;font-weight:600;position:sticky;top:0;z-index:2;}' +
        '.text-right{text-align:right;}' +
        '.group-row td{background:#e8f0fe;font-weight:800;color:#1f2937;}' +
        '.doc-link{color:#111827;text-decoration:none;font-weight:700;}' +
        '.doc-link:hover{text-decoration:underline;color:#2563eb;}' +
        '.group-count{margin-left:10px;color:#6b7280;font-size:12px;}' +
        '.indent-link{color:#2563eb;text-decoration:none;font-size:12px;}' +
        '.indent-link:hover{text-decoration:underline;}' +
        '@media print{.filter-row{display:none!important;}.table-wrap{max-height:none;overflow:visible;}th{position:static;}}' +
        '</style></head><body>' +
        '<div class="page"><div class="report-card">' +
        '<div class="report-header">' +
        '<div class="title">Material Issue Item Details</div>' +
        '<div class="meta">' + mi_esc(meta) + '</div>' +
        '</div>' +
        '<div class="filter-row">' +
        '<input id="f-se" placeholder="Material Issue ID" oninput="filterTable()">' +
        '<input id="f-item" placeholder="Item Name" oninput="filterTable()">' +
        '<input id="f-indent" placeholder="Material Indent" oninput="filterTable()">' +
        '<div style="flex:1;"></div>' +
        '<button onclick="window.print()">PDF / Print</button>' +
        '<button onclick="downloadExcel()">Excel</button>' +
        '</div>' +
        '<div class="table-wrap">' +
        mi_make_table(items) +
        '</div></div></div>' +

        '<script>' +
        'function filterTable(){' +
        'var se=(document.getElementById("f-se").value||"").toLowerCase().trim();' +
        'var item=(document.getElementById("f-item").value||"").toLowerCase().trim();' +
        'var indent=(document.getElementById("f-indent").value||"").toLowerCase().trim();' +
        'document.querySelectorAll("tr.group-row").forEach(function(g){' +
        'var seId=(g.getAttribute("data-se")||"").toLowerCase();' +
        'var next=g.nextElementSibling;var vis=0;' +
        'while(next&&!next.classList.contains("group-row")){' +
        'var iName=(next.getAttribute("data-item")||"").toLowerCase();' +
        'var iIndent=(next.getAttribute("data-indent")||"").toLowerCase();' +
        'var show=true;' +
        'if(se&&seId.indexOf(se)===-1)show=false;' +
        'if(item&&iName.indexOf(item)===-1)show=false;' +
        'if(indent&&iIndent.indexOf(indent)===-1)show=false;' +
        'next.style.display=show?"":"none";' +
        'if(show)vis++;next=next.nextElementSibling;}' +
        'g.style.display=vis?"":"none";});' +
        '}' +
        'function downloadExcel(){' +
        'var t=document.querySelector("table").cloneNode(true);' +
        'Array.from(t.querySelectorAll("tbody tr")).forEach(function(r){if(r.style.display==="none")r.remove();});' +
        'var h="<!doctype html><html><head><meta charset=\\"utf-8\\"></head><body>"+t.outerHTML+"</body></html>";' +
        'var b=new Blob([h],{type:"application/vnd.ms-excel"});' +
        'var a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="material_issue_details.xls";' +
        'document.body.appendChild(a);a.click();document.body.removeChild(a);' +
        '}' +
        '</script>' +
        '</body></html>';

    var tab = window.open("", "_blank");
    if (!tab) {
        frappe.msgprint(__("Please allow pop-ups to open Detail View."));
        return;
    }
    tab.document.open();
    tab.document.write(html);
    tab.document.close();
}


// ✅ Build item table with Material Indent column
function mi_make_table(items) {
    if (!items.length) {
        return '<div style="padding:16px;color:#6b7280;">No items found.</div>';
    }

    var by_se = {};
    items.forEach(function(it) {
        var id = it.parent || "-";
        if (!by_se[id]) by_se[id] = [];
        by_se[id].push(it);
    });

    var rows = "";

    Object.keys(by_se).forEach(function(se_id) {
        var se_items = by_se[se_id];

        // ✅ Group header row
        rows +=
            '<tr class="group-row" data-se="' + mi_esc(se_id) + '">' +
            '<td colspan="8">' +
            '<a class="doc-link" href="/app/stock-entry/' + encodeURIComponent(se_id) + '" target="_blank">' +
            mi_esc(se_id) + '</a>' +
            '<span class="group-count">' + se_items.length + ' item' + (se_items.length !== 1 ? 's' : '') + '</span>' +
            '</td></tr>';

        // ✅ Item rows with Material Indent
        se_items.forEach(function(it, idx) {
            var indent_html = it.material_indent
                ? '<a class="indent-link" href="/app/material-request/' + encodeURIComponent(it.material_indent) + '" target="_blank">' + mi_esc(it.material_indent) + '</a>'
                : '-';

            rows +=
                '<tr class="item-row" data-se="' + mi_esc(se_id) + '" data-item="' + mi_esc(it.item_name || "") + '" data-indent="' + mi_esc(it.material_indent || "") + '">' +
                '<td class="text-right">' + (idx + 1) + '</td>' +
                '<td>' + mi_esc(it.item_code || "-") + '</td>' +
                '<td>' + mi_esc(it.item_name || "-") + '</td>' +
                '<td class="text-right">' + mi_fmt_num(it.qty) + '</td>' +
                '<td>' + mi_esc(it.uom || "-") + '</td>' +
                '<td class="text-right">Rs. ' + mi_fmt_money(it.basic_rate) + '</td>' +
                '<td class="text-right">Rs. ' + mi_fmt_money(it.amount) + '</td>' +
                '<td>' + indent_html + '</td>' +           // ✅ Material Indent
                '<td>' + mi_esc(it.s_warehouse || "-") + '</td>' +
                '</tr>';
        });
    });

    return '<table>' +
        '<thead><tr>' +
        '<th style="width:45px;" class="text-right">No.</th>' +
        '<th>Item Code</th>' +
        '<th>Item Name</th>' +
        '<th>Item Group</th>' +
        '<th style="width:100px;" class="text-right">Qty</th>' +
        '<th style="width:80px;">UOM</th>' +
        '<th style="width:120px;" class="text-right">Rate</th>' +
        '<th style="width:130px;" class="text-right">Amount</th>' +
        '<th style="width:160px;">Material Indent</th>' +  // ✅ New column
        '<th style="width:160px;">Warehouse</th>' +
        '</tr></thead>' +
        '<tbody>' + rows + '</tbody>' +
        '</table>';
}


function mi_esc(v) {
    return String(v == null ? "" : v)
        .replace(/&/g, "&amp;").replace(/</g, "&lt;")
        .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function mi_fmt_money(v) {
    return parseFloat(v || 0).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function mi_fmt_num(v) {
    return parseFloat(v || 0).toLocaleString("en-IN");
}