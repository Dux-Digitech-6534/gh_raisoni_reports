frappe.query_reports["Purchase Receipt Report New"] = {
	filters: [
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
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nDraft\nTo Bill\nCompleted\nCancelled\nReturn Issued\nReturn",
		},
	],

	get_datatable_options: function (options) {
		options.checkboxColumn = true;
		return options;
	},

	onload: function (report) {
		report._pr_selected = {};
		report._pr_poll_timer = null;

		pr_add_styles();

		report._detail_btn = report.page
			.add_inner_button(__("Detail View") + " (0)", function () {
				pr_read_checked(report);
				pr_fetch_and_open_tab(report);
			})
			.addClass("pr-detail-btn");

		report._pr_poll_timer = setInterval(function () {
			if (!report.datatable) return;
			pr_read_checked(report);
		}, 700);
	},

	after_datatable_render: function (report) {
		setTimeout(function () {
			pr_read_checked(report);
		}, 500);
	},
};

function pr_add_styles() {
	if ($("#pr-rpt-style").length) return;

	$("head").append(`<style id="pr-rpt-style">
		.pr-detail-btn {
			font-weight: 700 !important;
			border-radius: 8px !important;
			border: 1px solid #d1d5db !important;
			background: #fff !important;
			color: #1f2937 !important;
		}
		.pr-detail-btn.active {
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
	</style>`);
}

function pr_read_checked(report) {
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

	report._pr_selected = selected;
	pr_update_button(report);
}

function pr_update_button(report) {
	var count = Object.keys(report._pr_selected || {}).length;

	if (!report._detail_btn) return;

	report._detail_btn
		.text(__("Detail View") + " (" + count + ")")
		.toggleClass("active", count > 0);
}

function pr_fetch_and_open_tab(report) {
	var receipt_names = Object.keys(report._pr_selected || {});

	if (!receipt_names.length) {
		frappe.show_alert({
			message: __("Please select at least one Purchase Receipt."),
			indicator: "orange",
		});
		return;
	}

	frappe.call({
		method: "gh_raisoni_reports.gh_raisoni_reports.report.purchase_receipt_report_new.purchase_receipt_report_new.get_receipt_item_details",
		args: {
			receipt_names: receipt_names,
		},
		freeze: true,
		freeze_message: __("Loading item details..."),
		callback: function (r) {
			var items = r.message || [];
			pr_open_detail_tab(items, receipt_names);
		},
		error: function (err) {
			console.error("Purchase Receipt Detail Error:", err);
			frappe.msgprint(__("Could not load Purchase Receipt Item details."));
		},
	});
}

function pr_open_detail_tab(items, receipt_names) {
	var meta =
		receipt_names.length + " Receipt" + (receipt_names.length > 1 ? "s" : "") +
		", " + items.length + " item" + (items.length !== 1 ? "s" : "");

	var html =
		'<!doctype html>' +
		'<html>' +
		'<head>' +
			'<title>Purchase Receipt Item Details</title>' +
			'<style>' +
				'body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;margin:0;color:#1f272e;background:#fff;font-size:14px;}' +
				'.page{padding:16px 24px;}' +
				'.report-card{border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;background:#fff;}' +
				'.report-header{padding:14px 16px 10px;border-bottom:1px solid #eef0f2;}' +
				'.title{font-size:18px;font-weight:700;margin-bottom:4px;color:#0f172a;}' +
				'.meta{font-size:13px;color:#64748b;font-weight:600;}' +
				'.filter-row{display:grid;grid-template-columns:190px 260px 1fr auto auto;gap:10px;align-items:center;padding:10px 12px;background:#fff;}' +
				'.filter-row input{height:28px;border:0;background:#f3f4f6;border-radius:7px;padding:4px 10px;font-size:13px;outline:none;color:#111827;}' +
				'.filter-row input:focus{background:#fff;box-shadow:0 0 0 2px #d1d5db;}' +
				'.filter-row button{height:28px;border:1px solid #d1d5db;background:#fff;border-radius:6px;padding:3px 12px;font-size:13px;font-weight:600;cursor:pointer;color:#111827;}' +
				'.filter-row button:hover{background:#f8fafc;}' +
				'.table-wrap{overflow:auto;max-height:calc(100vh - 135px);border-top:1px solid #eef0f2;}' +
				'table{width:100%;border-collapse:collapse;table-layout:fixed;}' +
				'th,td{border-right:1px solid #e5e7eb;border-bottom:1px solid #e5e7eb;padding:8px 8px;font-size:13px;vertical-align:middle;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}' +
				'th{background:#f3f4f6;color:#111827;text-align:left;font-weight:600;position:sticky;top:0;z-index:2;}' +
				'td:last-child,th:last-child{border-right:0;}' +
				'.text-right{text-align:right;}' +
				'.doc-link{color:#111827;text-decoration:none;font-weight:500;}' +
				'.doc-link:hover{text-decoration:underline;color:#2563eb;}' +
				'.muted{color:#6b7280;}' +
				'.item-img{width:54px;height:42px;border:1px solid #e5e7eb;background:#f3f4f6;border-radius:6px;display:flex;align-items:center;justify-content:center;overflow:hidden;color:#9ca3af;font-size:10px;}' +
				'.item-img img{width:100%;height:100%;object-fit:cover;}' +
				'.empty{padding:16px;color:#6b7280;font-weight:600;}' +
				'.count-pill{position:fixed;left:50%;bottom:12px;transform:translateX(-50%);background:#4b5563;color:#fff;border-radius:6px;padding:6px 14px;font-size:13px;opacity:.92;}' +
				'@media print{' +
					'.filter-row,.count-pill{display:none!important;}' +
					'.page{padding:0;}' +
					'.report-card{border:0;border-radius:0;}' +
					'.table-wrap{max-height:none;overflow:visible;}' +
					'th{position:static;}' +
					'tr.hidden-print{display:none!important;}' +
				'}' +
			'</style>' +
		'</head>' +
		'<body>' +
			'<div class="page">' +
				'<div class="report-card">' +
					'<div class="report-header">' +
						'<div class="title">Purchase Receipt Item Details</div>' +
						'<div class="meta">' + pr_esc(meta) + '</div>' +
					'</div>' +

					'<div class="filter-row">' +
						'<input id="filter-receipt" placeholder="Receipt ID" oninput="filterDetailTable()">' +
						'<input id="filter-item" placeholder="Item Name" oninput="filterDetailTable()">' +
						'<div></div>' +
						'<button onclick="window.print()">PDF / Print</button>' +
						'<button onclick="downloadExcel()">Excel</button>' +
					'</div>' +

					'<div class="table-wrap">' +
						pr_make_item_table_for_new_tab(items) +
					'</div>' +
				'</div>' +
			'</div>' +

			'<div class="count-pill" id="row-count"></div>' +

			'<script>' +
				'function getValue(id){return (document.getElementById(id).value||"").toLowerCase().trim();}' +

				'function updateCount(){' +
					'var rows=document.querySelectorAll("tbody tr");' +
					'var visible=0;' +
					'rows.forEach(function(row){if(row.style.display!=="none") visible++;});' +
					'document.getElementById("row-count").textContent=visible+" rows selected";' +
				'}' +

				'function filterDetailTable(){' +
					'var receipt=getValue("filter-receipt");' +
					'var item=getValue("filter-item");' +
					'var rows=document.querySelectorAll("tbody tr");' +
					'rows.forEach(function(row){' +
						'var show=true;' +
						'if(receipt && (row.getAttribute("data-receipt")||"").toLowerCase().indexOf(receipt)===-1) show=false;' +
						'if(item && (row.getAttribute("data-item")||"").toLowerCase().indexOf(item)===-1) show=false;' +
						'row.style.display=show ? "" : "none";' +
						'row.classList.toggle("hidden-print", !show);' +
					'});' +
					'updateCount();' +
				'}' +

				'function downloadExcel(){' +
					'var table=document.querySelector("table").cloneNode(true);' +
					'Array.from(table.querySelectorAll("tbody tr")).forEach(function(row){' +
						'if(row.style.display==="none" || row.classList.contains("hidden-print")) row.remove();' +
					'});' +
					'Array.from(table.querySelectorAll("img")).forEach(function(img){img.parentNode.innerHTML=img.getAttribute("src") || "";});' +
					'var html="<!doctype html><html><head><meta charset=\\"utf-8\\"></head><body>"+table.outerHTML+"</body></html>";' +
					'var blob=new Blob([html],{type:"application/vnd.ms-excel"});' +
					'var a=document.createElement("a");' +
					'a.href=URL.createObjectURL(blob);' +
					'a.download="purchase_receipt_item_details.xls";' +
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

function pr_make_item_table_for_new_tab(items) {
	if (!items.length) {
		return '<div class="empty">No Purchase Receipt Item rows found.</div>';
	}

	var rows = items.map(function (it, index) {
		var receipt_id = it.receipt_id || "";
		var purchase_order = it.purchase_order || "";
		var material_request = it.material_request || "";
		var item_name = it.item_name || "";
		var qty = pr_fmt_num(it.qty);
		var uom = it.uom || "";
		var rate = pr_fmt_money(it.rate);
		var amount = pr_fmt_money(it.amount);

		var image_html = it.item_image
			? '<div class="item-img"><img src="' + pr_esc(it.item_image) + '" alt=""></div>'
			: '<div class="item-img">No Image</div>';

		return '' +
			'<tr ' +
				'data-receipt="' + pr_esc(receipt_id) + '" ' +
				'data-item="' + pr_esc(item_name) + '"' +
			'>' +
				'<td class="text-right">' + (index + 1) + '</td>' +
				'<td>' +
					'<a class="doc-link" href="/app/purchase-receipt/' + encodeURIComponent(receipt_id) + '" target="_blank">' +
						pr_esc(receipt_id || "-") +
					'</a>' +
				'</td>' +
				'<td>' + pr_make_link("purchase-order", purchase_order) + '</td>' +
				'<td>' + pr_make_link("material-request", material_request) + '</td>' +
				'<td>' + pr_esc(item_name || "-") + '</td>' +
				'<td class="text-right">' + pr_esc(qty) + '</td>' +
				'<td>' + pr_esc(uom || "-") + '</td>' +
				'<td class="text-right">Rs. ' + pr_esc(rate) + '</td>' +
				'<td class="text-right">Rs. ' + pr_esc(amount) + '</td>' +
				'<td>' + image_html + '</td>' +
			'</tr>';
	}).join("");

	return '' +
		'<table>' +
			'<thead>' +
				'<tr>' +
					'<th style="width:55px;" class="text-right">No.</th>' +
					'<th style="width:190px;">Purchase Receipt No.</th>' +
					'<th style="width:190px;">Purchase Order</th>' +
					'<th style="width:190px;">Material Request</th>' +
					'<th>Item Name</th>' +
					'<th style="width:110px;" class="text-right">Quantity</th>' +
					'<th style="width:100px;">UOM</th>' +
					'<th style="width:130px;" class="text-right">Rate</th>' +
					'<th style="width:150px;" class="text-right">Total Amount</th>' +
					'<th style="width:90px;">Image</th>' +
				'</tr>' +
			'</thead>' +
			'<tbody>' + rows + '</tbody>' +
		'</table>';
}

function pr_make_link(route, value) {
	if (!value) {
		return '<span class="muted">-</span>';
	}

	return '<a class="doc-link" href="/app/' + route + '/' + encodeURIComponent(value) + '" target="_blank">' +
		pr_esc(value) +
	'</a>';
}

function pr_esc(value) {
	return String(value == null ? "" : value)
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;")
		.replace(/'/g, "&#039;");
}

function pr_fmt_money(value) {
	return flt(value || 0).toLocaleString("en-IN", {
		minimumFractionDigits: 2,
		maximumFractionDigits: 2,
	});
}

function pr_fmt_num(value) {
	return flt(value || 0).toLocaleString("en-IN");
}