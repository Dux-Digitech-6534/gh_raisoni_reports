frappe.query_reports["Purchase Order Report New"] = {
	filters: [
		{
			fieldname: "name",
			label: __("PO ID"),
			fieldtype: "Link",
			options: "Purchase Order",
		},
		{
			fieldname: "material_request",
			label: __("Material Request"),
			fieldtype: "Link",
			options: "Material Request",
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

		if (column.fieldname === "name" && data && data.name) {
			return po_make_link("purchase-order", data.name);
		}

		if (column.fieldname === "supplier" && data && data.supplier && data.supplier !== "-") {
			return po_make_link("supplier", data.supplier);
		}

		if (column.fieldname === "material_request" && data && data.material_request && data.material_request !== "-") {
			return po_make_multi_link("material-request", data.material_request);
		}

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

			return '<span style="background:' + s.bg + ';color:' + s.color + ';padding:2px 10px;border-radius:12px;font-size:11px;font-weight:700;">' +
				po_esc(data.workflow_state) +
			'</span>';
		}

		return value;
	},

	onload: function (report) {
		report._po_selected = {};
		report._po_poll_timer = null;

		po_add_styles();

		report._dp_btn = report.page
			.add_inner_button(__("Detail View") + " (0)", function () {
				po_read_checked(report);
				po_fetch_and_render(report);
			})
			.addClass("po-detail-btn");

		report._po_poll_timer = setInterval(function () {
			if (!report.datatable) return;
			po_read_checked(report);
		}, 700);
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
		.dt-cell__content {
			overflow: visible !important;
			text-overflow: clip !important;
			white-space: nowrap !important;
		}
		.dt-cell {
			overflow: visible !important;
		}
		.doc-link {
			color: #111827;
			text-decoration: none;
		
		}
		.doc-link:hover {
			text-decoration: underline;
			
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

	if (!po_names.length) {
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
			var items = r.message || [];
			po_open_detail_tab(items, po_names);
		},
		error: function (err) {
			console.error("Purchase Order Detail Error:", err);
			frappe.msgprint(__("Could not load Purchase Order Item details."));
		},
	});
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
				'*{box-sizing:border-box;}' +
				'body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;margin:0;color:#1f272e;background:#fff;font-size:14px;}' +
				'.page{padding:16px 24px;}' +
				'.report-card{border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;background:#fff;}' +
				'.report-header{padding:14px 16px 10px;border-bottom:1px solid #eef0f2;}' +
				'.title{font-size:18px;font-weight:700;margin-bottom:4px;color:#0f172a;}' +
				'.meta{font-size:13px;color:#64748b;font-weight:600;}' +

				'.filter-row{display:grid;grid-template-columns:170px 210px 260px 1fr auto auto;gap:10px;align-items:center;padding:10px 12px;background:#fff;}' +
				'.filter-row input{height:30px;border:0;background:#f3f4f6;border-radius:7px;padding:4px 10px;font-size:13px;outline:none;color:#111827;}' +
				'.filter-row input:focus{background:#fff;box-shadow:0 0 0 2px #d1d5db;}' +
				'.filter-row button{height:30px;border:1px solid #d1d5db;background:#fff;border-radius:6px;padding:3px 12px;font-size:13px;font-weight:600;cursor:pointer;color:#111827;}' +
				'.filter-row button:hover{background:#f8fafc;}' +

				'.table-wrap{overflow:auto;max-height:calc(100vh - 135px);border-top:1px solid #eef0f2;}' +
				'table{width:100%;min-width:1080px;border-collapse:collapse;table-layout:fixed;}' +
				'th,td{border-right:1px solid #e5e7eb;border-bottom:1px solid #e5e7eb;padding:8px;font-size:13px;vertical-align:middle;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}' +
				'th{background:#f3f4f6;color:#111827;text-align:left;font-weight:600;position:sticky;top:0;z-index:2;}' +
				'td:last-child,th:last-child{border-right:0;}' +
				'.text-right{text-align:right;}' +
				'.amount-cell{color:#111827;}' +
				'.po-group-row td{background:#f3f4f6;font-weight:700;color:#111827;padding:10px 8px!important;}' +
				'.group-count{margin-left:10px;color:#6b7280;font-size:12px;font-weight:700;}' +
				'.doc-link{color:#111827;text-decoration:none;}' +
				'.doc-link:hover{text-decoration:underline;}' +
				'.muted{color:#6b7280;}' +
				'.empty{padding:16px;color:#6b7280;font-weight:600;}' +
				'.count-pill{position:fixed;left:50%;bottom:12px;transform:translateX(-50%);background:#4b5563;color:#fff;border-radius:6px;padding:6px 14px;font-size:13px;opacity:.92;}' +

				'.col-no{width:55px;}' +
				'.col-mr{width:190px;}' +
				'.col-supplier{width:190px;}' +
				'.col-item{width:190px;}' +
				'.col-group{width:130px;}' +
				'.col-qty{width:110px;}' +
				'.col-uom{width:90px;}' +
				'.col-rate{width:130px;}' +
				'.col-amount{width:150px;}' +

				'@media screen and (max-width:768px){' +
					'.page{padding:10px;}' +
					'.filter-row{grid-template-columns:1fr;}' +
					'.table-wrap{max-height:calc(100vh - 230px);}' +
				'}' +

				'@media print{' +
					'@page{size:A4 landscape;margin:6mm;}' +
					'html,body{width:auto!important;height:auto!important;background:#fff!important;margin:0!important;padding:0!important;}' +
					'body{-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important;}' +
					'.filter-row,.count-pill,.no-print{display:none!important;}' +
					'.page{padding:0!important;}' +
					'.report-card{border:0!important;border-radius:0!important;overflow:visible!important;}' +
					'.report-header{padding:0 0 6px 0!important;}' +
					'.title{font-size:13px!important;margin-bottom:2px!important;}' +
					'.meta{font-size:9px!important;}' +
					'.table-wrap{max-height:none!important;overflow:visible!important;border-top:1px solid #eef0f2!important;}' +
					'table{width:100%!important;min-width:0!important;table-layout:fixed!important;border-collapse:collapse!important;}' +
					'th{position:static!important;}' +
					'th,td{white-space:normal!important;overflow:visible!important;text-overflow:clip!important;word-break:break-word!important;font-size:7px!important;line-height:1.2!important;padding:2px!important;}' +
					'.po-group-row td{font-size:8px!important;padding:3px!important;}' +
					'.col-no{width:4%!important;}' +
					'.col-mr{width:16%!important;}' +
					'.col-supplier{width:16%!important;}' +
					'.col-item{width:20%!important;}' +
					'.col-group{width:12%!important;}' +
					'.col-qty{width:7%!important;}' +
					'.col-uom{width:5%!important;}' +
					'.col-rate{width:9%!important;}' +
					'.col-amount{width:11%!important;}' +
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

					'<div class="filter-row no-print">' +
						'<input id="filter-po" placeholder="PO ID" oninput="filterDetailTable()">' +
						'<input id="filter-mr" placeholder="Material Request ID" oninput="filterDetailTable()">' +
						'<input id="filter-item" placeholder="Item / Supplier / Group" oninput="filterDetailTable()">' +
						'<div></div>' +
						'<button class="no-print" onclick="window.print()">PDF / Print</button>' +
						'<button class="no-print" onclick="downloadExcel()">Excel</button>' +
					'</div>' +

					'<div class="table-wrap">' +
						po_make_item_table_for_new_tab(items) +
					'</div>' +
				'</div>' +
			'</div>' +

			'<div class="count-pill no-print" id="row-count"></div>' +

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
					'var mr=getValue("filter-mr");' +
					'var search=getValue("filter-item");' +
					'var groups=document.querySelectorAll("tr.po-group-row");' +

					'groups.forEach(function(group){' +
						'var poId=(group.getAttribute("data-po")||"").toLowerCase();' +
						'var next=group.nextElementSibling;' +
						'var visibleCount=0;' +

						'while(next && !next.classList.contains("po-group-row")){' +
							'var mrText=(next.getAttribute("data-mr")||"").toLowerCase();' +
							'var searchText=(next.getAttribute("data-search")||"").toLowerCase();' +
							'var show=true;' +
							'if(po && poId.indexOf(po)===-1) show=false;' +
							'if(mr && mrText.indexOf(mr)===-1) show=false;' +
							'if(search && searchText.indexOf(search)===-1) show=false;' +
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

				'function csvCell(value){var q=String.fromCharCode(34);return q+String(value==null?"":value).replace(/"/g,q+q)+q;}' +

				'function downloadExcel(){' +
					'var po=getValue("filter-po");' +
					'var mr=getValue("filter-mr");' +
					'var search=getValue("filter-item");' +
					'var rows=[[' +
						'"PO ID","Date","Company","Supplier","Required By","PO Grand Total","PO Net Total","PO Total Qty","Status","Item No.","Material Request ID","Item Code","Item Name","Item Group","Quantity","UOM","Rate","Item Amount"' +
					']];' +

					'detailItems.forEach(function(it){' +
						'var poId=String(it.po_id || it.parent || "");' +
						'var mrText=String(it.material_request || "").toLowerCase();' +
						'var searchText=[' +
							'it.supplier || "",' +
							'it.material_request || "",' +
							'it.item_code || "",' +
							'it.item_name || "",' +
							'it.item_group || ""' +
						'].join(" ").toLowerCase();' +

						'if(po && poId.toLowerCase().indexOf(po)===-1) return;' +
						'if(mr && mrText.indexOf(mr)===-1) return;' +
						'if(search && searchText.indexOf(search)===-1) return;' +

						'rows.push([' +
							'poId,' +
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
							'it.item_code || "",' +
							'it.item_name || "",' +
							'it.item_group || "",' +
							'it.qty || 0,' +
							'it.uom || "",' +
							'it.rate || 0,' +
							'it.amount || 0' +
						']);' +
					'});' +

					'var csv="\\ufeff"+rows.map(function(row){return row.map(csvCell).join(",");}).join("\\n");' +
					'var blob=new Blob([csv],{type:"text/csv;charset=utf-8;"});' +
					'var a=document.createElement("a");' +
					'a.href=URL.createObjectURL(blob);' +
					'a.download="purchase_order_item_details.csv";' +
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
		var po_id = it.po_id || it.parent || "-";

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
				'<td colspan="9">' +
					(po_id && po_id !== "-"
						? '<a class="doc-link" href="/app/purchase-order/' + encodeURIComponent(po_id) + '" target="_blank">' + po_esc(po_id) + '</a>'
						: '<span class="muted">-</span>') +
					'<span class="group-count">' + po_items.length + ' item' + (po_items.length !== 1 ? 's' : '') + '</span>' +
				'</td>' +
			'</tr>';

		rows += po_items.map(function (it, index) {
			var material_request = it.material_request || "";
			var supplier = it.supplier || "";
			var item_code = it.item_code || "";
			var item_name = it.item_name || item_code || "";
			var item_group = it.item_group || "";
			var qty = po_fmt_num(it.qty);
			var uom = it.uom || "";
			var rate = po_fmt_money(it.rate);
			var amount = po_fmt_money(it.amount);
			var search_text = [material_request, supplier, item_code, item_name, item_group].join(" ");

			return '' +
				'<tr class="po-item-row" data-po="' + po_esc(po_id) + '" data-mr="' + po_esc(material_request) + '" data-search="' + po_esc(search_text) + '">' +
					'<td class="text-right col-no">' + (index + 1) + '</td>' +
					'<td class="col-mr" title="' + po_esc(material_request) + '">' +
						po_make_multi_link("material-request", material_request) +
					'</td>' +
					'<td class="col-supplier" title="' + po_esc(supplier) + '">' +
						po_make_link("supplier", supplier) +
					'</td>' +
					'<td class="col-item" title="' + po_esc(item_name) + '">' +
						(item_name
							? '<a class="doc-link" href="/app/item/' + encodeURIComponent(item_code || item_name) + '" target="_blank">' + po_esc(item_name) + '</a>'
							: '<span class="muted">-</span>') +
					'</td>' +
					'<td class="col-group" title="' + po_esc(item_group) + '">' +
						(item_group
							? '<a class="doc-link" href="/app/item-group/' + encodeURIComponent(item_group) + '" target="_blank">' + po_esc(item_group) + '</a>'
							: '<span class="muted">-</span>') +
					'</td>' +
					'<td class="text-right col-qty">' + po_esc(qty) + '</td>' +
					'<td class="col-uom">' + po_esc(uom || "-") + '</td>' +
					'<td class="text-right col-rate">Rs. ' + po_esc(rate) + '</td>' +
					'<td class="text-right col-amount amount-cell">Rs. ' + po_esc(amount) + '</td>' +
				'</tr>';
		}).join("");
	});

	return '' +
		'<table>' +
			'<thead>' +
				'<tr>' +
					'<th class="text-right col-no">No.</th>' +
					'<th class="col-mr">Material Request ID</th>' +
					'<th class="col-supplier">Supplier</th>' +
					'<th class="col-item">Item Name</th>' +
					'<th class="col-group">Item Group</th>' +
					'<th class="text-right col-qty">Quantity</th>' +
					'<th class="col-uom">UOM</th>' +
					'<th class="text-right col-rate">Rate</th>' +
					'<th class="text-right col-amount amount-cell">Total Amount</th>' +
				'</tr>' +
			'</thead>' +
			'<tbody>' + rows + '</tbody>' +
		'</table>';
}

function po_make_link(route, value) {
	if (!value || value === "-") {
		return '<span class="muted">-</span>';
	}

	return '<a class="doc-link" href="/app/' + route + '/' + encodeURIComponent(value) + '" target="_blank">' +
		po_esc(value) +
	'</a>';
}

function po_make_multi_link(route, value) {
	if (!value || value === "-") {
		return '<span class="muted">-</span>';
	}

	var list = String(value).split(",").map(function (v) {
		return v.trim();
	}).filter(Boolean);

	if (!list.length) {
		return '<span class="muted">-</span>';
	}

	return list.map(function (v) {
		return '<a class="doc-link" href="/app/' + route + '/' + encodeURIComponent(v) + '" target="_blank">' +
			po_esc(v) +
		'</a>';
	}).join(", ");
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