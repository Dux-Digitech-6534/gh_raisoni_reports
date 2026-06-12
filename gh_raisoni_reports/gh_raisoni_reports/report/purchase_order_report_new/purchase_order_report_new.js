frappe.query_reports["Purchase Order Report New"] = {
	filters: [
		{
			fieldname: "name",
			label: __("PO ID"),
			fieldtype: "Link",
			options: "Purchase Order",
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "supplier",
			label: __("Supplier"),
			fieldtype: "Link",
			options: "Supplier",
		},
		{
			fieldname: "workflow_state",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nDraft\nPending\nTo Receive and Bill\nTo Bill\nTo Receive\nCompleted\nCancelled\nClosed\nApproved\nRejected",
		},
	],

	get_datatable_options: function (options) {
		options.checkboxColumn = true;
		return options;
	},
    
	formatter: function (value, row, column, data, default_formatter) {

		value = default_formatter(value, row, column, data);
        
		if (column.fieldname === "workflow_state" && data && data.workflow_state) {
			var map = {
				"Cancelled": { bg: "#fde8e8", color: "#c0392b" },
				"Completed": { bg: "#e8f8f0", color: "#1a7a4a" },
				"To Receive and Bill": { bg: "#fff3cd", color: "#856404" },
				"To Bill": { bg: "#fff7e6", color: "#e67e22" },
				"To Receive": { bg: "#e6f4ff", color: "#1971c2" },
				"Draft": { bg: "#f1f3f5", color: "#495057" },
				"Pending": { bg: "#fff0f6", color: "#c2255c" },
				"Closed": { bg: "#e8e8e8", color: "#555" },
				"Approved": { bg: "#e8f8f0", color: "#1a7a4a" },
				"Rejected": { bg: "#fde8e8", color: "#c0392b" },
			};

			var s = map[data.workflow_state] || { bg: "#f1f3f5", color: "#333" };

			return '<span style="background:' + s.bg + ';color:' + s.color + ';padding:2px 10px;border-radius:12px;font-size:11px;font-weight:700;">'
				+ po_esc(data.workflow_state) +
			'</span>';
		}
		if (column.fieldname === "material_request" && data && data.material_request) {
			var mr_list = String(data.material_request).split(",").map(function (mr) {
				return mr.trim();
			}).filter(Boolean);

			return mr_list.map(function (mr) {
				return '<a href="/app/material-request/' + encodeURIComponent(mr) + '" target="_blank">' +
					po_esc(mr) +
				'</a>';
			}).join(", ");
		}

		return value;
	},

	onload: function (report) {
		report._po_selected = {};
		report._po_poll_timer = null;
		
		po_add_styles();

		report._dp_btn = report.page
			.add_inner_button(__("Detail View") + " (0)", function () {
				console.log("DETAIL VIEW CLICKED");

				po_read_checked(report);

				console.log("SELECTED PO MAP:", report._po_selected);
				console.log("SELECTED PO NAMES:", Object.keys(report._po_selected || {}));

				po_fetch_and_render(report);
			})
		report._po_poll_timer = setInterval(function () {
			if (!report.datatable) return;
			po_read_checked(report);
		},);
	},


	after_datatable_render: function (report) {
		setTimeout(function () {
			po_read_checked(report);
		}, 500);
	},
};

function po_add_styles() {
	if ($("#po-rpt-style").length) return;

	$("head").append(`<style id="po-rpt-style">
		.po-detail-btn {
			font-weight: 700 !important;
			border-radius: 8px !important;
			border: 1px solid #d1d5db !important;
			background: #fff !important;
			color: #1f2937 !important;
		}
		.po-detail-btn.active {
			background: #111827 !important;
			color: #fff !important;
			border-color: #111827 !important;
		}
		#po-detail-panel {
			margin: 16px 0 24px;
			border-radius: 8px;
			background: #2f2f2c;
			border: 1px solid #4a4a46;
			color: #f5f5f0;
			overflow: hidden;
		}
		.po-dp-hdr {
			display: flex;
			align-items: center;
			gap: 8px;
			padding: 14px 18px;
			font-weight: 800;
			font-size: 16px;
			border-bottom: 1px solid #4a4a46;
		}
		.po-dp-meta {
			font-size: 13px;
			color: #c9c9c3;
			font-weight: 600;
		}
		.po-dp-body {
			padding: 16px 18px 18px;
		}
		.po-cards {
			display: flex;
			flex-wrap: wrap;
			gap: 14px;
		}
		.po-card {
			width: 220px;
			background: #1f1f1d;
			border: 1px solid #4a4a46;
			border-radius: 8px;
			padding: 14px;
		}
		.po-card-name {
			font-weight: 800;
			font-size: 14px;
			color: #fff;
			margin-bottom: 10px;
			line-height: 1.35;
		}
		.po-card-meta {
			font-size: 13px;
			color: #ddd;
			line-height: 1.9;
		}
		.po-card-meta b {
			color: #fff;
		}
		.po-dialog-meta {
			margin-bottom: 12px;
			font-size: 13px;
			
			color: #4b5563;
		}
	    .po-dialog-group {
      	  margin-bottom: 18px;
	    }

		.po-item-table {
			width: 100%;
			table-layout: fixed;
		}

		.po-item-table th,
		.po-item-table td {
			vertical-align: middle;
		}

		.po-group-row td {
			background: #f3f4f6;
			font-weight: 500;
			color: #1f2937;
			padding: 10px 8px !important;
		}

		.po-group-row a {
			color: black
			text-decoration: none;
		}

		.po-group-row a:hover {
			text-decoration: underline;
		}

		.po-group-row span {
			margin-left: 10px;
			font-size: 12px;
			
			color: #6b7280;
		}
		.dt-cell__content {
			overflow: visible !important;
			text-overflow: clip !important;
			white-space: nowrap !important;
		}

		.dt-cell {
			overflow: visible !important;
		}

	</style>`);
}

function po_read_checked(report) {
	var dt = report.datatable;
	if (!dt || !report.data) return;

	var selected = {};

	$(dt.wrapper).find(".dt-scrollable .dt-row").each(function () {
		var $row = $(this);

		var is_checked =
			$row.hasClass("dt-row--highlight") ||
			$row.hasClass("dt-row--checked") ||
			$row.find("input[type='checkbox']:checked").length > 0;

		if (!is_checked) return;

		var row_idx = parseInt($row.attr("data-row-index"), 10);

		if (isNaN(row_idx)) {
			row_idx = parseInt($row.find("[data-row-index]").first().attr("data-row-index"), 10);
		}

		var rd = report.data[row_idx] || report.data[row_idx - 1];

		if (rd && rd.name) {
			selected[rd.name] = rd;
		}
	});

	report._po_selected = selected;
	po_update_button(report);
}

function po_update_button(report) {
	var count = Object.keys(report._po_selected || {}).length;

	if (!report._dp_btn) return;

	report._dp_btn
		.text(__("Detail View") + " (" + count + ")")
		.toggleClass("active", count > 0);
}

function po_fetch_and_render(report) {
	var po_names = Object.keys(report._po_selected || {});

	console.log("po_fetch_and_render called");
	console.log("po_names:", po_names);

	if (!po_names.length) {
		console.warn("No PO selected.");
		frappe.show_alert({
			message: __("Please select at least one Purchase Order."),
			indicator: "orange",
		});
		return;
	}

	frappe.call({
		method: "gh_raisoni_reports.gh_raisoni_reports.report.purchase_order_report_new.purchase_order_report_new.get_po_item_details",
		args: {
			po_names: po_names,
		},
		freeze: true,
		freeze_message: __("Loading item details..."),
		callback: function (r) {
			console.log("SERVER RESPONSE:", r);
			console.log("ITEM DETAILS:", r.message);

			var items = r.message || [];
			// po_render_panel(report, items, po_names);
			po_open_detail_tab(items, po_names);
		},
		error: function (err) {
			console.error("FRAPPE CALL ERROR:", err);
			frappe.msgprint(__("Could not load Purchase Order Item details."));
		},
	});
}


function po_make_item_table(items) {
	if (!items.length) {
		return '<div style="padding:12px;color:#6b7280;">No Purchase Order Item rows found.</div>';
	}

	var by_po = {};

	items.forEach(function (it) {
		var po_id = it.parent || "-";

		if (!by_po[po_id]) {
			by_po[po_id] = [];
		}

		by_po[po_id].push(it);
	});

	var rows = "";

	Object.keys(by_po).forEach(function (po_id) {
		var po_items = by_po[po_id];

		rows += '' +
			'<tr class="po-group-row" data-po="' + po_esc(po_id) + '">' +
				'<td colspan="5">' +
					'<a href="/app/purchase-order/' + encodeURIComponent(po_id) + '" target="_blank">' +
						po_esc(po_id) +
					'</a>' +
					'<span>' + po_items.length + ' item' + (po_items.length !== 1 ? 's' : '') + '</span>' +
				'</td>' +
			'</tr>';

		rows += po_items.map(function (it) {
			return '' +
				'<tr>' +
					'<td>' + po_esc(it.item_name || "-") + '</td>' +
					'<td style="text-align:right;">' + po_fmt_num(it.qty) + '</td>' +
					'<td>' + po_esc(it.uom || "-") + '</td>' +
					'<td style="text-align:right;">Rs. ' + po_fmt_money(it.rate) + '</td>' +
					'<td style="text-align:right;">Rs. ' + po_fmt_money(it.amount) + '</td>' +
				'</tr>';
		}).join("");
	});

	return '' +
		'<table class="table table-bordered po-item-table" style="margin:0;">' +
			'<thead>' +
				'<tr>' +
					'<th>Item Name</th>' +
					'<th style="text-align:right;">Quantity</th>' +
					'<th>UOM</th>' +
					'<th style="text-align:right;">Rate</th>' +
					'<th style="text-align:right;">Total Amount</th>' +
				'</tr>' +
			'</thead>' +
			'<tbody>' + rows + '</tbody>' +
		'</table>';
}
function po_make_item_cards(items) {
	if (!items.length) {
		return '<div style="color:#c9c9c3;font-size:13px;padding:10px 0;">No Purchase Order Item rows found.</div>';
	}

	return '<div class="po-cards">' + items.map(function (it) {
		return '' +
			'<div class="po-card">' +
				'<div class="po-card-name">' + po_esc(it.item_name || "-") + '</div>' +
				'<div class="po-card-meta">' +
					'<b>Quantity:</b> ' + po_fmt_num(it.qty) + '<br>' +
					'<b>UOM:</b> ' + po_esc(it.uom || "-") + '<br>' +
					'<b>Rate:</b> Rs. ' + po_fmt_money(it.rate) + '<br>' +
					'<b>Total Amount:</b> Rs. ' + po_fmt_money(it.amount) +
				'</div>' +
			'</div>';
	}).join("") + '</div>';
}

function po_esc(value) {
	return String(value == null ? "" : value)
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;")
		.replace(/'/g, "&#039;");
}

function po_fmt_money(value) {
	return flt(value || 0).toLocaleString("en-IN", {
		minimumFractionDigits: 2,
		maximumFractionDigits: 2,
	});
}

function po_fmt_num(value) {
	return flt(value || 0).toLocaleString("en-IN");
}

//EXCEL
function po_export_detail_excel(items) {
	if (!items.length) {
		frappe.show_alert({
			message: __("No item details to export."),
			indicator: "orange",
		});
		return;
	}

	var rows = [
		["PO ID", "Material Request ID","Item Name", "Quantity", "UOM", "Rate", "Total Amount"]
	];

	items.forEach(function (it) {
		rows.push([
			it.parent || "",
			it.material_request || "",
			it.item_name || "",
			it.qty || 0,
			it.uom || "",
			it.rate || 0,
			it.amount || 0,
		]);
	});

	var csv = rows.map(function (row) {
		return row.map(function (cell) {
			return '"' + String(cell == null ? "" : cell).replace(/"/g, '""') + '"';
		}).join(",");
	}).join("\n");

	var blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
	var url = URL.createObjectURL(blob);
	var a = document.createElement("a");

	a.href = url;
	a.download = "purchase_order_item_details.csv";
	document.body.appendChild(a);
	a.click();
	document.body.removeChild(a);
	URL.revokeObjectURL(url);
}

function po_export_detail_pdf() {
	var panel = document.getElementById("po-detail-panel");

	if (!panel) {
		frappe.show_alert({
			message: __("No item details to export."),
			indicator: "orange",
		});
		return;
	}

	var print_window = window.open("", "_blank");

	print_window.document.write(
		"<html><head><title>Purchase Order Item Details</title>" +
		"<style>" +
			"body{font-family:Arial,sans-serif;padding:20px;}" +
			"table{width:100%;border-collapse:collapse;}" +
			"th,td{border:1px solid #ddd;padding:8px;font-size:12px;}" +
			"th{background:#f3f4f6;text-align:left;}" +
			".po-dp-hdr button{display:none;}" +
			".po-group-row td{background:#f3f4f6;font-weight:bold;}" +
		"</style>" +
		"</head><body>" +
		panel.innerHTML +
		"</body></html>"
	);

	print_window.document.close();
	print_window.focus();
	print_window.print();
}


function po_open_detail_tab(items, po_names) {
	var meta =
		po_names.length + " PO" + (po_names.length > 1 ? "s" : "") +
		", " + items.length + " item" + (items.length !== 1 ? "s" : "");
    
	var html =
		'<!doctype html>' +
		'<html>' +
		'<head>' +
			'<title>Purchase Order Item Details</title>' +
			'<style>' +
				'body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;margin:0;color:#1f272e;background:#fff;font-size:14px;}' +
				'.page{padding:16px 24px;}' +
				'.amount-cell{color:#111827;}' +
				'.report-card{border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;background:#fff;}' +
				'.report-header{padding:14px 16px 10px;border-bottom:1px solid #eef0f2;}' +
				'.title{font-size:18px;font-weight:700;margin-bottom:4px;color:#0f172a;}' +
				'.meta{font-size:13px;color:#64748b;font-weight:600;}' +
				'.filter-row{display:grid;grid-template-columns:190px 260px 1fr auto auto;gap:10px;align-items:center;padding:10px 12px;background:#fff;}' +
				'.filter-row input{height:28px;border:0;background:#f3f4f6;border-radius:7px;padding:4px 10px;font-size:13px;outline:none;color:#111827;}' +
				'.filter-row input:focus{background:#fff;box-shadow:0 0 0 2px #d1d5db;}' +
				'.filter-row button{height:28px;border:1px solid #d1d5db;background:#fff;border-radius:6px;padding:3px 12px;font-size:13px;font-weight:600;cursor:pointer;color:#111827;}' +
				'.filter-row button:hover{background:#f3f4f6;}' +
				'.table-wrap{overflow:auto;max-height:calc(100vh - 135px);border-top:1px solid #eef0f2;}' +
				'table{width:100%;border-collapse:collapse;table-layout:fixed;}' +
				'th,td{border-right:1px solid #e5e7eb;border-bottom:1px solid #e5e7eb;padding:8px;font-size:13px;vertical-align:middle;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}' +
				'th{background:#f3f4f6;color:#111827;text-align:left;font-weight:600;position:sticky;top:0;z-index:2;}' +
				'td:last-child,th:last-child{border-right:0;}' +
				'.text-right{text-align:right;}' +
				'.po-group-row td{background:#f3f4f6;font-weight:500;color:#111827;}' +
				'.doc-link{color:#111827;text-decoration:none;}' +
				'.doc-link:hover{text-decoration:underline;color:#black;}' +
				
				'.empty{padding:16px;color:#6b7280;font-weight:600;}' +
				'.count-pill{position:fixed;left:50%;bottom:12px;transform:translateX(-50%);background:#4b5563;color:#fff;border-radius:6px;padding:6px 14px;font-size:13px;opacity:.92;}' +
				'@media print{' +
					'@page{size:landscape;margin:10mm;}' +
					'.filter-row,.count-pill,.no-print{display:none!important;}' +
					'body{background:#fff!important;}' +
					'.filter-row,.count-pill{display:none!important;}' +
					'.page{padding:0!important;}' +
					'.report-card{border:0!important;border-radius:0!important;overflow:visible!important;}' +
					'.table-wrap{max-height:none!important;overflow:visible!important;border-top:1px solid #eef0f2;}' +
					'table{width:100%!important;table-layout:auto!important;}' +
					'th{position:static!important;}' +
					'th,td{white-space:normal!important;overflow:visible!important;text-overflow:clip!important;font-size:11px!important;padding:6px!important;}' +
					'tr.hidden-print{display:none!important;}' +
					'a{color:#000!important;text-decoration:none!important;}' +
				'}' +
			'</style>' +
		'</head>' +
		'<body>' +
			'<div class="page">' +
				'<div class="report-card">' +
					'<div class="report-header">' +
						'<div class="title">Purchase Order Item Details</div>' +
						'<div class="meta">' + po_esc(meta) + '</div>' +
					'</div>' +

					'<div class="filter-row">' +
						'<input id="filter-po" placeholder="PO ID" oninput="filterDetailTable()">' +
						'<input id="filter-item" placeholder="Item Name" oninput="filterDetailTable()">' +
						'<div></div>' +
						'<button class="no-print" onclick="window.print()">PDF</button>' +
                        '<button class="no-print" onclick="downloadExcel()">Excel</button>' +
					'</div>' +

					'<div class="table-wrap">' +
						po_make_item_table_for_new_tab(items) +
					'</div>' +
				'</div>' +
			'</div>' +

			'<div class="count-pill" id="row-count"></div>' +

			'<script>' +
				'function getValue(id){return (document.getElementById(id).value||"").toLowerCase().trim();}' +

				'function updateCount(){' +
					'var rows=document.querySelectorAll("tbody tr.po-item-row");' +
					'var visible=0;' +
					'rows.forEach(function(row){if(row.style.display!=="none") visible++;});' +
					'document.getElementById("row-count").textContent=visible+" rows selected";' +
				'}' +

				'function filterDetailTable(){' +
					'var po=getValue("filter-po");' +
					'var item=getValue("filter-item");' +
					'var groups=document.querySelectorAll("tr.po-group-row");' +

					'groups.forEach(function(group){' +
						'var poId=(group.getAttribute("data-po")||"").toLowerCase();' +
						'var next=group.nextElementSibling;' +
						'var visibleCount=0;' +

						'while(next && !next.classList.contains("po-group-row")){' +
							'var itemName=(next.getAttribute("data-item")||"").toLowerCase();' +
							'var show=true;' +
							'if(po && poId.indexOf(po)===-1) show=false;' +
							'if(item && itemName.indexOf(item)===-1) show=false;' +
							'next.style.display=show ? "" : "none";' +
							'next.classList.toggle("hidden-print", !show);' +
							'if(show) visibleCount++;' +
							'next=next.nextElementSibling;' +
						'}' +

						'group.style.display=visibleCount ? "" : "none";' +
						'group.classList.toggle("hidden-print", !visibleCount);' +
					'});' +

					'updateCount();' +
				'}' +

				'var detailItems = ' + JSON.stringify(items).replace(/</g, "\\u003c") + ';' +

				'function downloadExcel(){' +
					'var rows = [[' +
						'"PO ID","Date","Company","Supplier","Required By","PO Grand Total","PO Net Total","PO Total Qty","Status","Item No.","Material Request ID","Item Name","Quantity","UOM","Rate","Item Amount"' +
					']];' +

					'detailItems.forEach(function(it){' +
						'rows.push([' +
							'it.po_id || it.parent || "",' +
							'it.date || "",' +
							'it.company || "",' +
							'it.supplier || "",' +
							'it.required_by || "",' +
							'it.grand_total || 0,' +
							'it.net_total || 0,' +
							'it.total_qty || 0,' +
							'it.workflow_state || "",' +
							'it.idx || "",' +
							'it.material_request || "",' +
							'it.item_name || "",' +
							'it.qty || 0,' +
							'it.uom || "",' +
							'it.rate || 0,' +
							'it.amount || 0' +
						']);' +
					'});' +

					'var csv = rows.map(function(row){' +
						'return row.map(function(cell){' +
							'return "\\"" + String(cell == null ? "" : cell).replace(/"/g, "\\"\\"") + "\\"";' +
						'}).join(",");' +
					'}).join("\\n");' +

					'var blob = new Blob([csv], {type:"text/csv;charset=utf-8;"});' +
					'var a = document.createElement("a");' +
					'a.href = URL.createObjectURL(blob);' +
					'a.download = "purchase_order_with_item_details.csv";' +
					'document.body.appendChild(a);' +
					'a.click();' +
					'document.body.removeChild(a);' +
				'}' +

				'updateCount();' +
			'</script>' +
		'</body>' +
		'</html>';

	var new_tab = window.open("", "_blank");

	if (!new_tab) {
		frappe.msgprint(__("Please allow pop-ups for this site to open Detail View in a new tab."));
		return;
	}

	new_tab.document.open();
	new_tab.document.write(html);
	new_tab.document.close();
}

function po_make_item_table_for_new_tab(items) {
	if (!items.length) {
		return '<div class="empty">No Purchase Order Item rows found.</div>';
	}

	var by_po = {};

	items.forEach(function (it) {
		var po_id = it.parent || "-";

		if (!by_po[po_id]) {
			by_po[po_id] = [];
		}

		by_po[po_id].push(it);
	});

	var rows = "";

	Object.keys(by_po).forEach(function (po_id) {
		var po_items = by_po[po_id];

		rows += '' +
			'<tr class="po-group-row" data-po="' + po_esc(po_id) + '">' +
				'<td colspan="8">' +
					'<a class="doc-link" href="/app/purchase-order/' + encodeURIComponent(po_id) + '" target="_blank">' +
						po_esc(po_id) +
					'</a>' +
					
				'</td>' +
			'</tr>';

		rows += po_items.map(function (it, index) {
			var material_request = it.material_request || "";
			var item_name = it.item_name || "";
			var item_group = it.item_group || "";
			var qty = po_fmt_num(it.qty);
			var uom = it.uom || "";
			var rate = po_fmt_money(it.rate);
			var amount = po_fmt_money(it.amount);

			return '' +
				'<tr class="po-item-row" data-po="' + po_esc(po_id) + '" data-item="' + po_esc(item_name) + '">' +

					'<td class="text-right">' + (index + 1) + '</td>' +
					'<td title="' + po_esc(material_request) + '">' +
						(material_request
							? '<a class="doc-link" href="/app/material-request/' + encodeURIComponent(material_request) + '" target="_blank">' + po_esc(material_request) + '</a>'
							: '-') +
					'</td>' +
					'<td title="' + po_esc(item_name) + '">' +
						(item_name
							? '<a class="doc-link" href="/app/item/' + encodeURIComponent(it.item_code || item_name) + '" target="_blank">' + po_esc(item_name) + '</a>'
							: '-') +
					'</td>' +

					'<td title="' + po_esc(item_group) + '">' +
						(item_group
							? '<a class="doc-link" href="/app/item-group/' + encodeURIComponent(item_group) + '" target="_blank">' + po_esc(item_group) + '</a>'
							: '-') +
					'</td>' +
					'<td class="text-right">' + po_esc(qty) + '</td>' +
					'<td>' + po_esc(uom || "-") + '</td>' +
					'<td class="text-right">Rs. ' + po_esc(rate) + '</td>' +
					'<td class="text-right amount-cell">Rs. ' + po_esc(amount) + '</td>' +
				'</tr>';
		}).join("");
	});

	return '' +
		'<table>' +
			'<thead>' +
				'<tr>' +
					'<th style="width:55px;" class="text-right">No.</th>' +
					'<th style="width:190px;">Material Request ID</th>' +
					'<th style="width:100px;">Item Name</th>' +
					'<th style="width:110px;">Item Group</th>' +
					'<th style="width:110px;" class="text-right">Quantity</th>' +
					'<th style="width:100px;">UOM</th>' +
					'<th style="width:130px;" class="text-right">Rate</th>' +
					'<th style="width:150px;" class="text-right amount-cell">Total Amount</th>' +
				'</tr>' +
			'</thead>' +
			'<tbody>' + rows + '</tbody>' +
		'</table>';
}


function downloadDetailExcel(items) {
	var rows = [
		[
			"PO ID",
			"Date",
			"Company",
			"Supplier",
			"Required By",
			"PO Grand Total",
			"PO Net Total",
			"PO Total Qty",
			"Status",
			"Item No.",
			"Material Request ID",
			"Item Name",
			"Item Group",
			"Quantity",
			"UOM",
			"Rate",
			"Item Amount"
		]
	];

	items.forEach(function (it) {
		rows.push([
			it.po_id || it.parent || "",
			it.date || "",
			it.company || "",
			it.supplier || "",
			it.required_by || "",
			it.grand_total || 0,
			it.net_total || 0,
			it.total_qty || 0,
			it.workflow_state || "",
			it.idx || "",
			it.material_request || "",
			it.item_name || "",
			it.item_group || "",
			it.qty || 0,
			it.uom || "",
			it.rate || 0,
			it.amount || 0
		]);
	});

	var csv = rows.map(function (row) {
		return row.map(function (cell) {
			return '"' + String(cell == null ? "" : cell).replace(/"/g, '""') + '"';
		}).join(",");
	}).join("\n");

	var blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
	var a = document.createElement("a");
	a.href = URL.createObjectURL(blob);
	a.download = "purchase_order_with_item_details.csv";
	document.body.appendChild(a);
	a.click();
	document.body.removeChild(a);
}


function downloadDetailExcel(items) {
	var rows = [
		[
			"PO ID",
			"Date",
			"Company",
			"Supplier",
			"Required By",
			"PO Grand Total",
			"PO Net Total",
			"PO Total Qty",
			"Status",
			"Item No.",
			"Material Request ID",
			"Item Name",
			"Item Group",
			"Quantity",
			"UOM",
			"Rate",
			"Item Amount"
		]
	];

	items.forEach(function (it) {
		rows.push([
			it.po_id || it.parent || "",
			it.date || "",
			it.company || "",
			it.supplier || "",
			it.required_by || "",
			it.grand_total || 0,
			it.net_total || 0,
			it.total_qty || 0,
			it.workflow_state || "",
			it.idx || "",
			it.material_request || "",
			it.item_name || "",
			it.item_group || "",
			it.qty || 0,
			it.uom || "",
			it.rate || 0,
			it.amount || 0
		]);
	});

	var csv = rows.map(function (row) {
		return row.map(function (cell) {
			return '"' + String(cell == null ? "" : cell).replace(/"/g, '""') + '"';
		}).join(",");
	}).join("\n");

	var blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
	var a = document.createElement("a");
	a.href = URL.createObjectURL(blob);
	a.download = "purchase_order_with_item_details.csv";
	document.body.appendChild(a);
	a.click();
	document.body.removeChild(a);
}