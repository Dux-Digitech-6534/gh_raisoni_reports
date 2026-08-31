frappe.query_reports["Purchase Order Report New"] = {
	filters: [
		{
			fieldname: "po_id",
			label: __("PO ID"),
			fieldtype: "Data",
		},
		{
			fieldname: "material_request",
			label: __("Material Request"),
			fieldtype: "Data",
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
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
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nDraft\nTo Receive and Bill\nTo Bill\nTo Receive\nCompleted\nCancelled\nClosed\nDelivered",
		},
	],

	get_datatable_options: function (options) {
		options.checkboxColumn = true;
		return options;
	},

	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname === "supplier" && data && data.supplier && data.supplier !== "-") {
			return po_make_link("supplier", data.supplier);
		}

		if (column.fieldname === "po_id" && data && data.po_id && data.po_id !== "-") {
			return po_make_link("purchase-order", data.po_id);
		}

		if (column.fieldname === "purchase_order" && data && data.purchase_order && data.purchase_order !== "-") {
			return po_make_multi_link("purchase-order", data.purchase_order);
		}

		if (column.fieldname === "material_request" && data && data.material_request && data.material_request !== "-") {
			return po_make_multi_link("material-request", data.material_request);
		}

		return value;
	},

	onload: function (report) {
		report._po_selected = {};
		report._po_poll_timer = null;

		po_add_styles();

		report._detail_btn = report.page
			.add_inner_button(__("Detail View") + " (0)", function () {
				po_read_checked(report);
				po_fetch_and_open_tab(report);
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
	</style>`);
}

function po_read_checked(report) {
	var dt = report.datatable;
	if (!dt || !report.data || !dt.rowmanager) return;

	var selected = {};
	var indexes = dt.rowmanager.getCheckedRows() || [];

	indexes.forEach(function (row_idx) {
		if (row_idx === undefined) return;

		var rd = report.data[row_idx];

		if (rd) {
			var po_name = rd.name || rd.po_id || rd.purchase_order;
			if (po_name) {
				selected[po_name] = rd;
			}
		}
	});

	report._po_selected = selected;
	po_update_button(report);
}

function po_update_button(report) {
	var count = Object.keys(report._po_selected || {}).length;

	if (!report._detail_btn) return;

	report._detail_btn
		.text(__("Detail View") + " (" + count + ")")
		.toggleClass("active", count > 0);
}

function po_fetch_and_open_tab(report) {
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

// function po_open_detail_tab(items, po_names) {
// 	var meta =
// 		po_names.length + " PO" + (po_names.length > 1 ? "s" : "") +
// 		", " + items.length + " item" + (items.length !== 1 ? "s" : "");

// 	var report_filters = frappe.query_report ? frappe.query_report.get_filter_values() : {};

// 	var export_items_json = JSON.stringify(items || [])
// 		.replace(/</g, "\\u003c")
// 		.replace(/>/g, "\\u003e")
// 		.replace(/&/g, "\\u0026");

// 	var export_filters_json = JSON.stringify(report_filters || {})
// 		.replace(/</g, "\\u003c")
// 		.replace(/>/g, "\\u003e")
// 		.replace(/&/g, "\\u0026");

// 	var html = `
// <!doctype html>
// <html>
// <head>
// 	<title>Purchase Order Item Details</title>
// 	<script src="https://cdn.jsdelivr.net/npm/xlsx/dist/xlsx.full.min.js"></script>

// 	<style>
// 		body {
// 			font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
// 			margin: 0;
// 			color: #1f272e;
// 			background: #fff;
// 			font-size: 14px;
// 		}

// 		.page {
// 			padding: 16px 24px;
// 		}

// 		.report-card {
// 			border: 1px solid #e5e7eb;
// 			border-radius: 8px;
// 			overflow: hidden;
// 			background: #fff;
// 		}

// 		.report-header {
// 			padding: 14px 16px 10px;
// 			border-bottom: 1px solid #eef0f2;
// 		}

// 		.title {
// 			font-size: 18px;
// 			font-weight: 700;
// 			margin-bottom: 4px;
// 			color: #0f172a;
// 		}

// 		.meta {
// 			font-size: 13px;
// 			color: #64748b;
// 			font-weight: 600;
// 		}

// 		.filter-row {
// 			display: grid;
// 			grid-template-columns: 180px 220px 280px 1fr auto auto;
// 			gap: 10px;
// 			align-items: center;
// 			padding: 10px 12px;
// 			background: #fff;
// 		}

// 		.filter-row input {
// 			height: 28px;
// 			border: 0;
// 			background: #f3f4f6;
// 			border-radius: 7px;
// 			padding: 4px 10px;
// 			font-size: 13px;
// 			outline: none;
// 			color: #111827;
// 		}

// 		.filter-row input:focus {
// 			background: #fff;
// 			box-shadow: 0 0 0 2px #d1d5db;
// 		}

// 		.filter-row button {
// 			height: 28px;
// 			border: 1px solid #d1d5db;
// 			background: #fff;
// 			border-radius: 6px;
// 			padding: 3px 12px;
// 			font-size: 13px;
// 			font-weight: 600;
// 			cursor: pointer;
// 			color: #111827;
// 		}

// 		.filter-row button:hover {
// 			background: #f8fafc;
// 		}

// 		.table-wrap {
// 			overflow: auto;
// 			max-height: calc(100vh - 135px);
// 			border-top: 1px solid #eef0f2;
// 		}

// 		table {
// 			width: 100%;
// 			border-collapse: collapse;
// 			table-layout: fixed;
// 		}

// 		th,
// 		td {
// 			border-right: 1px solid #e5e7eb;
// 			border-bottom: 1px solid #e5e7eb;
// 			padding: 8px;
// 			font-size: 13px;
// 			vertical-align: middle;
// 			white-space: nowrap;
// 			overflow: hidden;
// 			text-overflow: ellipsis;
// 		}

// 		th {
// 			background: #f3f4f6;
// 			color: #111827;
// 			text-align: left;
// 			font-weight: 600;
// 			position: sticky;
// 			top: 0;
// 			z-index: 2;
// 		}

// 		td:last-child,
// 		th:last-child {
// 			border-right: 0;
// 		}

// 		.text-right {
// 			text-align: right;
// 		}

// 		.doc-link {
// 			color: #111827;
// 			text-decoration: none;
// 			font-weight: 600;
// 		}

// 		.doc-link:hover {
// 			text-decoration: underline;
// 		}

// 		.muted {
// 			color: #6b7280;
// 		}

// 		.empty {
// 			padding: 16px;
// 			color: #6b7280;
// 			font-weight: 600;
// 		}

// 		.count-pill {
// 			position: fixed;
// 			left: 50%;
// 			bottom: 12px;
// 			transform: translateX(-50%);
// 			background: #4b5563;
// 			color: #fff;
// 			border-radius: 6px;
// 			padding: 6px 14px;
// 			font-size: 13px;
// 			opacity: .92;
// 		}

// 		.po-parent-row td {
// 			background: #f3f4f6;
// 			font-weight: 700;
// 			color: #111827;
// 		}

// 		.col-no { width: 55px; }
// 		.col-mr { width: 210px; }
// 		.col-supplier { width: 260px; }
// 		.col-item { width: 260px; }
// 		.col-group { width: 150px; }
// 		.col-qty { width: 100px; }
// 		.col-uom { width: 80px; }
// 		.col-rate { width: 130px; }
// 		.col-amount { width: 150px; }

// 		.flat-print-export {
// 			display: none;
// 		}

// 		@media print {
// 			@page {
// 				size: A3 landscape;
// 				margin: 5mm;
// 			}

// 			body.print-flat .report-header,
// 			body.print-flat .filter-row,
// 			body.print-flat .count-pill,
// 			body.print-flat .table-wrap,
// 			body.print-flat .no-print {
// 				display: none !important;
// 			}

// 			body.print-flat .flat-print-export {
// 				display: block !important;
// 			}

// 			body.print-flat .page {
// 				padding: 0 !important;
// 			}

// 			body.print-flat .report-card {
// 				border: 0 !important;
// 				border-radius: 0 !important;
// 				overflow: visible !important;
// 			}

// 			body.print-flat .flat-title {
// 				font-size: 13px !important;
// 				font-weight: 700 !important;
// 				margin-bottom: 5px !important;
// 				color: #000 !important;
// 			}

// 			body.print-flat .flat-filter-table {
// 				width: 45% !important;
// 				border-collapse: collapse !important;
// 				margin-bottom: 8px !important;
// 			}

// 			body.print-flat .flat-filter-table td {
// 				border: 1px solid #d1d5db !important;
// 				font-size: 7px !important;
// 				padding: 3px !important;
// 				white-space: normal !important;
// 				color: #000 !important;
// 			}

// 			body.print-flat .flat-data-table {
// 				width: 100% !important;
// 				border-collapse: collapse !important;
// 				table-layout: fixed !important;
// 			}

// 			body.print-flat .flat-data-table th,
// 			body.print-flat .flat-data-table td {
// 				border: 1px solid #d1d5db !important;
// 				font-size: 5px !important;
// 				line-height: 1.15 !important;
// 				padding: 2px !important;
// 				white-space: normal !important;
// 				word-break: break-word !important;
// 				overflow: visible !important;
// 				text-overflow: clip !important;
// 				color: #000 !important;
// 			}

// 			body.print-flat .flat-data-table th {
// 				background: #f3f4f6 !important;
// 				font-weight: 700 !important;
// 			}
// 		}
// 	</style>
// </head>

// <body>
// 	<div class="page">
// 		<div class="report-card">
// 			<div class="report-header">
// 				<div class="title">Purchase Order Item Details</div>
// 				<div class="meta">${po_esc(meta)}</div>
// 			</div>

// 			<div class="filter-row no-print">
// 				<input id="filter-po" placeholder="PO ID" oninput="filterDetailTable()">
// 				<input id="filter-mr" placeholder="Material Request ID" oninput="filterDetailTable()">
// 				<input id="filter-item" placeholder="Item / Supplier / Group" oninput="filterDetailTable()">
// 				<div></div>
// 				<button class="no-print" onclick="printFlatExport()">PDF / Print</button>
// 				<button class="no-print" onclick="downloadExcel()">Excel</button>
// 			</div>

// 			<div class="table-wrap">
// 				${po_make_item_table_for_new_tab(items)}
// 			</div>

// 			<div id="flat-print-export" class="flat-print-export"></div>
// 		</div>
// 	</div>

// 	<div class="count-pill no-print" id="row-count"></div>

// 	<script>
// 		var EXPORT_ITEMS = ${export_items_json};
// 		var EXPORT_FILTERS = ${export_filters_json};

// 		function htmlEsc(value) {
// 			return String(value == null ? "" : value)
// 				.replace(/&/g, "&amp;")
// 				.replace(/</g, "&lt;")
// 				.replace(/>/g, "&gt;")
// 				.replace(/"/g, "&quot;")
// 				.replace(/'/g, "&#039;");
// 		}

// 		function getValue(id) {
// 			var el = document.getElementById(id);
// 			return el ? (el.value || "").toLowerCase().trim() : "";
// 		}

// 		function inputValue(id) {
// 			var el = document.getElementById(id);
// 			return el ? (el.value || "").trim() : "";
// 		}

// 		function updateCount() {
// 			var rows = document.querySelectorAll("tbody tr.po-item-row");
// 			var visible = 0;

// 			rows.forEach(function (row) {
// 				if (row.style.display !== "none") visible++;
// 			});

// 			document.getElementById("row-count").textContent = visible + " rows selected";
// 		}

// 		function filterDetailTable() {
// 			var po = getValue("filter-po");
// 			var mr = getValue("filter-mr");
// 			var item = getValue("filter-item");

// 			var parents = document.querySelectorAll("tbody tr.po-parent-row");

// 			parents.forEach(function (parentRow) {
// 				var poId = parentRow.getAttribute("data-po") || "";
// 				var childRows = document.querySelectorAll('tbody tr.po-item-row[data-parent="' + poId + '"]');

// 				var parentVisible = false;

// 				childRows.forEach(function (row) {
// 					var poText = (row.getAttribute("data-po") || "").toLowerCase();
// 					var mrText = (row.getAttribute("data-mr") || "").toLowerCase();
// 					var searchText = (row.getAttribute("data-search") || "").toLowerCase();

// 					var show = true;

// 					if (po && poText.indexOf(po) === -1) show = false;
// 					if (mr && mrText.indexOf(mr) === -1) show = false;
// 					if (item && searchText.indexOf(item) === -1) show = false;

// 					row.style.display = show ? "" : "none";
// 					row.classList.toggle("hidden-print", !show);

// 					if (show) parentVisible = true;
// 				});

// 				parentRow.style.display = parentVisible ? "" : "none";
// 				parentRow.classList.toggle("hidden-print", !parentVisible);
// 			});

// 			updateCount();
// 		}

// 		function exportValue(value) {
// 			return value == null || value === "" ? "-" : String(value);
// 		}

// 		function exportNumber(value) {
// 			var num = Number(value || 0);
// 			return num.toLocaleString("en-IN");
// 		}

// 		function exportMoney(value) {
// 			var num = Number(value || 0);
// 			return num.toLocaleString("en-IN", {
// 				minimumFractionDigits: 2,
// 				maximumFractionDigits: 2
// 			});
// 		}

// 		function getFilterRows() {
// 			var rows = [];

// 			rows.push(["From Date", EXPORT_FILTERS.from_date || "-"]);
// 			rows.push(["To Date", EXPORT_FILTERS.to_date || "-"]);
// 			rows.push(["Company", EXPORT_FILTERS.company || "-"]);
// 			rows.push(["Supplier", EXPORT_FILTERS.supplier || "-"]);
// 			rows.push(["Status", EXPORT_FILTERS.status || "-"]);

// 			var poFilter = inputValue("filter-po");
// 			var mrFilter = inputValue("filter-mr");
// 			var itemFilter = inputValue("filter-item");

// 			if (poFilter) rows.push(["PO ID Filter", poFilter]);
// 			if (mrFilter) rows.push(["Material Request Filter", mrFilter]);
// 			if (itemFilter) rows.push(["Item / Supplier / Group Filter", itemFilter]);

// 			return rows;
// 		}

// 		function itemPassesFilter(it) {
// 			var poFilter = inputValue("filter-po").toLowerCase();
// 			var mrFilter = inputValue("filter-mr").toLowerCase();
// 			var itemFilter = inputValue("filter-item").toLowerCase();

// 			var poText = String(it.po_id || it.purchase_order || it.parent || "").toLowerCase();
// 			var mrText = String(it.material_request || "").toLowerCase();

// 			var searchText = [
// 				it.po_id,
// 				it.purchase_order,
// 				it.parent,
// 				it.material_request,
// 				it.company,
// 				it.supplier,
// 				it.status,
// 				it.item_code,
// 				it.item_name,
// 				it.item_group
// 			].join(" ").toLowerCase();

// 			if (poFilter && poText.indexOf(poFilter) === -1) return false;
// 			if (mrFilter && mrText.indexOf(mrFilter) === -1) return false;
// 			if (itemFilter && searchText.indexOf(itemFilter) === -1) return false;

// 			return true;
// 		}

// 		function buildFlatExportRows() {
// 			var rows = [];

// 			getFilterRows().forEach(function (r) {
// 				rows.push(r);
// 			});

// 			rows.push([]);

// 			rows.push([
// 				"PO ID",
// 				"Date",
// 				"Company",
// 				"Supplier",
// 				"Required By",
// 				"PO Grand Total",
// 				"PO Net Total",
// 				"PO Total Qty",
// 				"Status",
// 				"Item No.",
// 				"Material Request",
// 				"Item Code",
// 				"Item Name",
// 				"Item Group",
// 				"Quantity",
// 				"UOM",
// 				"Rate",
// 				"Item Amount"
// 			]);

// 			EXPORT_ITEMS.forEach(function (it, index) {
// 				if (!itemPassesFilter(it)) return;

// 				rows.push([
// 					exportValue(it.po_id || it.purchase_order || it.parent),
// 					exportValue(it.date || it.transaction_date || it.posting_date),
// 					exportValue(it.company),
// 					exportValue(it.supplier),
// 					exportValue(it.required_by || it.schedule_date),
// 					exportMoney(it.po_grand_total || it.grand_total),
// 					exportMoney(it.po_net_total || it.net_total),
// 					exportNumber(it.po_total_qty || it.total_qty),
// 					exportValue(it.status),
// 					exportValue(it.idx || index + 1),
// 					exportValue(it.material_request),
// 					exportValue(it.item_code),
// 					exportValue(it.item_name || it.item_code),
// 					exportValue(it.item_group),
// 					exportNumber(it.qty),
// 					exportValue(it.uom),
// 					exportMoney(it.rate),
// 					exportMoney(it.amount)
// 				]);
// 			});

// 			return rows;
// 		}

// 		function buildFlatPrintHtml() {
// 			var rows = buildFlatExportRows();
// 			var filterRows = getFilterRows();

// 			var headerIndex = 0;

// 			for (var i = 0; i < rows.length; i++) {
// 				if (rows[i].length > 2) {
// 					headerIndex = i;
// 					break;
// 				}
// 			}

// 			var html = "";

// 			html += '<div class="flat-title">Purchase Order Parent Child Export</div>';

// 			html += '<table class="flat-filter-table">';
// 			filterRows.forEach(function (r) {
// 				html += '<tr>';
// 				html += '<td><b>' + htmlEsc(r[0]) + '</b></td>';
// 				html += '<td>' + htmlEsc(r[1]) + '</td>';
// 				html += '</tr>';
// 			});
// 			html += '</table>';

// 			html += '<table class="flat-data-table">';
// 			html += '<thead><tr>';

// 			rows[headerIndex].forEach(function (cell) {
// 				html += '<th>' + htmlEsc(cell) + '</th>';
// 			});

// 			html += '</tr></thead>';
// 			html += '<tbody>';

// 			for (var j = headerIndex + 1; j < rows.length; j++) {
// 				html += '<tr>';

// 				rows[j].forEach(function (cell) {
// 					html += '<td>' + htmlEsc(cell) + '</td>';
// 				});

// 				html += '</tr>';
// 			}

// 			html += '</tbody></table>';

// 			return html;
// 		}

// 		function printFlatExport() {
// 			document.body.classList.add("print-flat");
// 			document.getElementById("flat-print-export").innerHTML = buildFlatPrintHtml();

// 			setTimeout(function () {
// 				window.print();
// 			}, 200);

// 			setTimeout(function () {
// 				document.body.classList.remove("print-flat");
// 			}, 1500);
// 		}

// 		function downloadExcel() {
// 			var rows = buildFlatExportRows();

// 			if (typeof XLSX === "undefined") {
// 				downloadCsv(rows);
// 				return;
// 			}

// 			var ws = XLSX.utils.aoa_to_sheet(rows);

// 			var headerIndex = 0;

// 			for (var i = 0; i < rows.length; i++) {
// 				if (rows[i].length > 2) {
// 					headerIndex = i;
// 					break;
// 				}
// 			}

// 			ws["!autofilter"] = {
// 				ref: XLSX.utils.encode_range({
// 					s: { r: headerIndex, c: 0 },
// 					e: { r: Math.max(rows.length - 1, headerIndex), c: 17 }
// 				})
// 			};

// 			ws["!cols"] = [
// 				{ wch: 24 },
// 				{ wch: 14 },
// 				{ wch: 28 },
// 				{ wch: 32 },
// 				{ wch: 14 },
// 				{ wch: 16 },
// 				{ wch: 16 },
// 				{ wch: 14 },
// 				{ wch: 14 },
// 				{ wch: 10 },
// 				{ wch: 24 },
// 				{ wch: 18 },
// 				{ wch: 28 },
// 				{ wch: 18 },
// 				{ wch: 12 },
// 				{ wch: 10 },
// 				{ wch: 14 },
// 				{ wch: 16 }
// 			];

// 			var wb = XLSX.utils.book_new();
// 			XLSX.utils.book_append_sheet(wb, ws, "Parent Child Export");
// 			XLSX.writeFile(wb, "purchase_order_parent_child_export.xlsx");
// 		}

// 		function csvCell(value) {
// 			var q = String.fromCharCode(34);
// 			return q + String(value == null ? "" : value).replace(/"/g, q + q) + q;
// 		}

// 		function downloadCsv(rows) {
// 			var csvRows = [];

// 			rows.forEach(function (row) {
// 				csvRows.push(row.map(csvCell).join(","));
// 			});

// 			var csv = "\\ufeff" + csvRows.join("\\n");
// 			var blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });

// 			var a = document.createElement("a");
// 			a.href = URL.createObjectURL(blob);
// 			a.download = "purchase_order_parent_child_export.csv";
// 			document.body.appendChild(a);
// 			a.click();
// 			document.body.removeChild(a);
// 		}

// 		updateCount();
// 	</script>
// </body>
// </html>
// `;

// 	var new_tab = window.open("", "_blank");

// 	if (!new_tab) {
// 		frappe.msgprint(__("Please allow pop-ups for this site to open Detail View in a new tab."));
// 		return;
// 	}

// 	new_tab.document.open();
// 	new_tab.document.write(html);
// 	new_tab.document.close();
// }

function po_open_detail_tab(items, po_names) {
	var meta =
		po_names.length + " PO" + (po_names.length > 1 ? "s" : "") +
		", " + items.length + " item" + (items.length !== 1 ? "s" : "");

	var report_filters = frappe.query_report ? frappe.query_report.get_filter_values() : {};

	var export_items_json = JSON.stringify(items || [])
		.replace(/</g, "\\u003c")
		.replace(/>/g, "\\u003e")
		.replace(/&/g, "\\u0026");

	var export_filters_json = JSON.stringify(report_filters || {})
		.replace(/</g, "\\u003c")
		.replace(/>/g, "\\u003e")
		.replace(/&/g, "\\u0026");

	var html = `
<!doctype html>
<html>
<head>
	<title>Purchase Order Item Details</title>
	<script src="https://cdn.jsdelivr.net/npm/xlsx-js-style/dist/xlsx.bundle.js"><\/script>

	<style>
		body {
			font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
			margin: 0;
			color: #1f272e;
			background: #fff;
			font-size: 14px;
		}

		.page {
			padding: 16px 24px;
		}

		.report-card {
			border: 1px solid #e5e7eb;
			border-radius: 8px;
			overflow: hidden;
			background: #fff;
		}

		.report-header {
			padding: 14px 16px 10px;
			border-bottom: 1px solid #eef0f2;
		}

		.title {
			font-size: 18px;
			font-weight: 700;
			margin-bottom: 4px;
			color: #0f172a;
		}

		.meta {
			font-size: 13px;
			color: #64748b;
			font-weight: 600;
		}

		.filter-row {
			display: grid;
			grid-template-columns: 180px 220px 280px 1fr auto auto;
			gap: 10px;
			align-items: center;
			padding: 10px 12px;
			background: #fff;
		}

		.filter-row input {
			height: 28px;
			border: 0;
			background: #f3f4f6;
			border-radius: 7px;
			padding: 4px 10px;
			font-size: 13px;
			outline: none;
			color: #111827;
		}

		.filter-row input:focus {
			background: #fff;
			box-shadow: 0 0 0 2px #d1d5db;
		}

		.filter-row button {
			height: 28px;
			border: 1px solid #d1d5db;
			background: #fff;
			border-radius: 6px;
			padding: 3px 12px;
			font-size: 13px;
			font-weight: 600;
			cursor: pointer;
			color: #111827;
		}

		.filter-row button:hover {
			background: #f8fafc;
		}

		.table-wrap {
			overflow: auto;
			max-height: calc(100vh - 135px);
			border-top: 1px solid #eef0f2;
		}

		table {
			width: 100%;
			border-collapse: collapse;
			table-layout: fixed;
		}

		th,
		td {
			border-right: 1px solid #e5e7eb;
			border-bottom: 1px solid #e5e7eb;
			padding: 8px;
			font-size: 13px;
			vertical-align: middle;
			white-space: nowrap;
			overflow: hidden;
			text-overflow: ellipsis;
		}

		th {
			background: #f3f4f6;
			color: #111827;
			text-align: left;
			font-weight: 600;
			position: sticky;
			top: 0;
			z-index: 2;
		}

		td:last-child,
		th:last-child {
			border-right: 0;
		}

		.text-right {
			text-align: right;
		}

		.doc-link {
			color: #111827;
			text-decoration: none;
			font-weight: 600;
		}

		.doc-link:hover {
			text-decoration: underline;
		}

		.muted {
			color: #6b7280;
		}

		.empty {
			padding: 16px;
			color: #6b7280;
			font-weight: 600;
		}

		.count-pill {
			position: fixed;
			left: 50%;
			bottom: 12px;
			transform: translateX(-50%);
			background: #4b5563;
			color: #fff;
			border-radius: 6px;
			padding: 6px 14px;
			font-size: 13px;
			opacity: .92;
		}

		.po-parent-row td {
			background: #f3f4f6;
			font-weight: 700;
			color: #111827;
		}

		.col-no { width: 55px; }
		.col-mr { width: 210px; }
		.col-supplier { width: 260px; }
		.col-item { width: 260px; }
		.col-group { width: 150px; }
		.col-qty { width: 100px; }
		.col-uom { width: 80px; }
		.col-rate { width: 130px; }
		.col-amount { width: 150px; }

		.flat-print-export {
			display: none;
		}

		@media print {
			@page {
				size: A3 landscape;
				margin: 5mm;
			}

			body.print-flat .report-header,
			body.print-flat .filter-row,
			body.print-flat .count-pill,
			body.print-flat .table-wrap,
			body.print-flat .no-print {
				display: none !important;
			}

			body.print-flat .flat-print-export {
				display: block !important;
			}

			body.print-flat .page {
				padding: 0 !important;
			}

			body.print-flat .report-card {
				border: 0 !important;
				border-radius: 0 !important;
				overflow: visible !important;
			}

			body.print-flat .flat-title {
				font-size: 13px !important;
				font-weight: 700 !important;
				margin-bottom: 5px !important;
				color: #000 !important;
			}

			body.print-flat .flat-filter-table {
				width: 45% !important;
				border-collapse: collapse !important;
				margin-bottom: 8px !important;
			}

			body.print-flat .flat-filter-table td {
				border: 1px solid #d1d5db !important;
				font-size: 7px !important;
				padding: 3px !important;
				white-space: normal !important;
				color: #000 !important;
			}

			body.print-flat .flat-data-table {
				width: 100% !important;
				border-collapse: collapse !important;
				table-layout: fixed !important;
			}

			body.print-flat .flat-data-table th,
			body.print-flat .flat-data-table td {
				border: 1px solid #d1d5db !important;
				font-size: 5px !important;
				line-height: 1.15 !important;
				padding: 2px !important;
				white-space: normal !important;
				word-break: break-word !important;
				overflow: visible !important;
				text-overflow: clip !important;
				color: #000 !important;
			}

			body.print-flat .flat-data-table th {
				background: #f3f4f6 !important;
				font-weight: 700 !important;
			}
		}
	</style>
</head>

<body>
	<div class="page">
		<div class="report-card">
			<div class="report-header">
				<div class="title">Purchase Order Item Details</div>
				<div class="meta">${po_esc(meta)}</div>
			</div>

			<div class="filter-row no-print">
				<input id="filter-po" placeholder="PO ID" oninput="filterDetailTable()">
				<input id="filter-mr" placeholder="Material Request ID" oninput="filterDetailTable()">
				<input id="filter-item" placeholder="Item / Supplier / Group" oninput="filterDetailTable()">
				<div></div>
				<button class="no-print" onclick="printFlatExport()">PDF / Print</button>
				<button class="no-print" onclick="downloadExcel()">Excel</button>
			</div>

			<div class="table-wrap">
				${po_make_item_table_for_new_tab(items)}
			</div>

			<div id="flat-print-export" class="flat-print-export"></div>
		</div>
	</div>

	<div class="count-pill no-print" id="row-count"></div>

	<script>
		var EXPORT_ITEMS = ${export_items_json};
		var EXPORT_FILTERS = ${export_filters_json};

		function htmlEsc(value) {
			return String(value == null ? "" : value)
				.replace(/&/g, "&amp;")
				.replace(/</g, "&lt;")
				.replace(/>/g, "&gt;")
				.replace(/"/g, "&quot;")
				.replace(/'/g, "&#039;");
		}

		function getValue(id) {
			var el = document.getElementById(id);
			return el ? (el.value || "").toLowerCase().trim() : "";
		}

		function inputValue(id) {
			var el = document.getElementById(id);
			return el ? (el.value || "").trim() : "";
		}

		function updateCount() {
			var rows = document.querySelectorAll("tbody tr.po-item-row");
			var visible = 0;

			rows.forEach(function (row) {
				if (row.style.display !== "none") visible++;
			});

			document.getElementById("row-count").textContent = visible + " rows selected";
		}

		function filterDetailTable() {
			var po = getValue("filter-po");
			var mr = getValue("filter-mr");
			var item = getValue("filter-item");

			var rows = document.querySelectorAll("tbody tr.po-item-row");

			rows.forEach(function (row) {
				var poText = (row.getAttribute("data-po") || "").toLowerCase();
				var mrText = (row.getAttribute("data-mr") || "").toLowerCase();
				var searchText = (row.getAttribute("data-search") || "").toLowerCase();

				var show = true;

				if (po && poText.indexOf(po) === -1) show = false;
				if (mr && mrText.indexOf(mr) === -1) show = false;
				if (item && searchText.indexOf(item) === -1) show = false;

				row.style.display = show ? "" : "none";
				row.classList.toggle("hidden-print", !show);
			});

			updateCount();
		}
		function exportValue(value) {
			return value == null || value === "" ? "-" : String(value);
		}

		function exportNumber(value) {
			var num = Number(value || 0);
			return num.toLocaleString("en-IN");
		}

		function exportMoney(value) {
			var num = Number(value || 0);
			return num.toLocaleString("en-IN", {
				minimumFractionDigits: 2,
				maximumFractionDigits: 2
			});
		}
   

		function exportDate(value) {
			if (!value) return "-";

			var s = String(value);

			if (s.indexOf(" ") !== -1) {
				s = s.split(" ")[0];
			}

			if (s.indexOf("-") !== -1) {
				var parts = s.split("-");
				if (parts.length === 3) {
					return parts[2] + "/" + parts[1] + "/" + parts[0];
				}
			}

			if (s.indexOf("/") !== -1) {
				return s;
			}

			return s;
		}


		function addFilterIfFilled(rows, label, value) {
			if (
				value !== undefined &&
				value !== null &&
				String(value).trim() !== "" &&
				String(value).trim() !== "-"
			) {
				rows.push([label, value]);
			}
		}

		function getFilterRows() {
			var rows = [];

			addFilterIfFilled(rows, "PO ID", EXPORT_FILTERS.po_id || EXPORT_FILTERS.name);
			addFilterIfFilled(rows, "Material Request", EXPORT_FILTERS.material_request);
			addFilterIfFilled(rows, "Company", EXPORT_FILTERS.company);
			addFilterIfFilled(rows, "From Date", exportDate(EXPORT_FILTERS.from_date));
			addFilterIfFilled(rows, "To Date", exportDate(EXPORT_FILTERS.to_date));
			addFilterIfFilled(rows, "Supplier", EXPORT_FILTERS.supplier);
			addFilterIfFilled(rows, "Status", EXPORT_FILTERS.status || EXPORT_FILTERS.workflow_state);

			addFilterIfFilled(rows, "Detail PO Filter", inputValue("filter-po"));
			addFilterIfFilled(rows, "Detail Material Request Filter", inputValue("filter-mr"));
			addFilterIfFilled(rows, "Detail Item / Supplier / Group Filter", inputValue("filter-item"));

			return rows;
		}

		function itemPassesFilter(it) {
			var poFilter = inputValue("filter-po").toLowerCase();
			var mrFilter = inputValue("filter-mr").toLowerCase();
			var itemFilter = inputValue("filter-item").toLowerCase();

			var poText = String(it.po_id || it.purchase_order || it.parent || "").toLowerCase();
			var mrText = String(it.material_request || "").toLowerCase();

			var searchText = [
				it.po_id,
				it.purchase_order,
				it.parent,
				it.material_request,
				it.company,
				it.supplier,
				it.workflow_state,
				it.status,
				it.item_code,
				it.item_name,
				it.item_group
			].join(" ").toLowerCase();

			if (poFilter && poText.indexOf(poFilter) === -1) return false;
			if (mrFilter && mrText.indexOf(mrFilter) === -1) return false;
			if (itemFilter && searchText.indexOf(itemFilter) === -1) return false;

			return true;
		}

		function buildFlatExportRows() {
			var rows = [];

			var companyValue = EXPORT_FILTERS.company || "-";
			var fromDateValue = exportDate(EXPORT_FILTERS.from_date);
			var toDateValue = exportDate(EXPORT_FILTERS.to_date);

			// Company center
			rows.push([companyValue]);
			rows.push([]);

			// From Date and To Date in center, same row
			rows.push([
				"",
				"",
				"",
				"",
				"",
				"From Date : " + fromDateValue + "     To Date : " + toDateValue
			]);

			// Only display filters that have values
			if (EXPORT_FILTERS.supplier && String(EXPORT_FILTERS.supplier).trim() !== "") {
				rows.push(["Supplier : " + EXPORT_FILTERS.supplier]);
			}

			if ((EXPORT_FILTERS.status || EXPORT_FILTERS.workflow_state) && String(EXPORT_FILTERS.status || EXPORT_FILTERS.workflow_state).trim() !== "") {
				rows.push(["Status : " + (EXPORT_FILTERS.status || EXPORT_FILTERS.workflow_state)]);
			}

			if ((EXPORT_FILTERS.po_id || EXPORT_FILTERS.name) && String(EXPORT_FILTERS.po_id || EXPORT_FILTERS.name).trim() !== "") {
				rows.push(["PO ID : " + (EXPORT_FILTERS.po_id || EXPORT_FILTERS.name)]);
			}

			if (EXPORT_FILTERS.material_request && String(EXPORT_FILTERS.material_request).trim() !== "") {
				rows.push(["Material Request : " + EXPORT_FILTERS.material_request]);
			}

			if (inputValue("filter-po")) {
				rows.push(["PO Filter : " + inputValue("filter-po")]);
			}

			if (inputValue("filter-mr")) {
				rows.push(["Material Request Filter : " + inputValue("filter-mr")]);
			}

			if (inputValue("filter-item")) {
				var detailValue = inputValue("filter-item");
				var detailLabel = getDetailFilterLabel(detailValue);

				rows.push([detailLabel + " : " + detailValue]);
			}

			rows.push([]);

			rows.push([
				"Date",
				"PO ID",
				"Company",
				"Supplier",
				"Required By",
				"PO Grand Total",
				"PO Net Total",
				"PO Total Qty",
				"Status",
				"Material Request",
				"Item Name",
				"Item Group",
				"Quantity",
				"UOM",
				"Rate",
				"Total Amount"
			]);

			EXPORT_ITEMS.forEach(function (it, index) {
				if (!itemPassesFilter(it)) return;

				rows.push([
					exportDate(it.date || it.transaction_date || it.posting_date),
					exportValue(it.po_id || it.purchase_order || it.parent),
					exportValue(it.company),
					exportValue(it.supplier),
					exportDate(it.required_by || it.schedule_date),
					exportMoney(it.grand_total),
					exportMoney(it.net_total),
					exportNumber(it.total_qty),
					exportValue(it.workflow_state || it.status),
					exportValue(it.material_request),
					exportValue(it.item_name || it.item_code),
					exportValue(it.item_group),
					exportNumber(it.qty),
					exportValue(it.uom),
					exportMoney(it.rate),
					exportMoney(it.amount)
				]);
			});

			return rows;
		}

		function getHeaderIndex(rows) {
			for (var i = 0; i < rows.length; i++) {
				if (rows[i].length > 10 && rows[i][0] === "Date") {
					return i;
				}
			}
			return 0;
		}
		function applyExcelTopCenterStyle(ws, rows) {
			var headerIndex = getHeaderIndex(rows);
			var merges = [];

			// Company full center: A to P
			merges.push({
				s: { r: 0, c: 0 },
				e: { r: 0, c: 15 }
			});

			// From Date + To Date together: F to I
			merges.push({
				s: { r: 2, c: 5 },
				e: { r: 2, c: 8 }
			});

			// All other filter rows center: A to P
			for (var r = 3; r < headerIndex - 1; r++) {
				merges.push({
					s: { r: r, c: 0 },
					e: { r: r, c: 15 }
				});
			}

			ws["!merges"] = merges;

			function styleCell(cellRef, isTitle) {
				if (!ws[cellRef]) return;

				ws[cellRef].s = {
					alignment: {
						horizontal: "center",
						vertical: "center"
					},
					font: {
						bold: true,
						sz: isTitle ? 14 : 11
					}
				};
			}

			// Company
			styleCell("A1", true);

			// From Date + To Date
			styleCell("F3", false);

			// Other filters
			for (var i = 4; i <= headerIndex; i++) {
				styleCell("A" + i, false);
			}

			// Table header center and bold
			for (var c = 0; c < 16; c++) {
				var cellRef = XLSX.utils.encode_cell({ r: headerIndex, c: c });

				if (ws[cellRef]) {
					ws[cellRef].s = {
						alignment: {
							horizontal: "center",
							vertical: "center"
						},
						font: {
							bold: true
						}
					};
				}
			}
		}
		function printFlatExport() {
			document.body.classList.add("print-flat");
			document.getElementById("flat-print-export").innerHTML = buildFlatPrintHtml();

			setTimeout(function () {
				window.print();
			}, 200);

			setTimeout(function () {
				document.body.classList.remove("print-flat");
			}, 1500);
		}

		function downloadExcel() {
			var rows = buildFlatExportRows();

			if (typeof XLSX === "undefined") {
				downloadCsv(rows);
				return;
			}

			var ws = XLSX.utils.aoa_to_sheet(rows);
			var headerIndex = getHeaderIndex(rows);

			applyExcelTopCenterStyle(ws, rows);

			ws["!autofilter"] = {
				ref: XLSX.utils.encode_range({
					s: { r: headerIndex, c: 0 },
					e: { r: Math.max(rows.length - 1, headerIndex), c: 15 }
				})
			};

			ws["!cols"] = [
			{ wch: 24 },
			{ wch: 14 },
			{ wch: 28 },
			{ wch: 32 },
			{ wch: 14 },
			{ wch: 16 },
			{ wch: 16 },
			{ wch: 14 },
			{ wch: 14 },
			{ wch: 24 },
			{ wch: 28 },
			{ wch: 18 },
			{ wch: 12 },
			{ wch: 10 },
			{ wch: 14 },
			{ wch: 16 }
		];

			var wb = XLSX.utils.book_new();
			XLSX.utils.book_append_sheet(wb, ws, "Parent Child Export");
			XLSX.writeFile(wb, "purchase_order_parent_child_export.xlsx");
		}

		function csvCell(value) {
			var q = String.fromCharCode(34);
			return q + String(value == null ? "" : value).replace(/"/g, q + q) + q;
		}

		function downloadCsv(rows) {
			var csvRows = [];

			rows.forEach(function (row) {
				csvRows.push(row.map(csvCell).join(","));
			});

			var csv = "\\ufeff" + csvRows.join("\\n");
			var blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });

			var a = document.createElement("a");
			a.href = URL.createObjectURL(blob);
			a.download = "purchase_order_parent_child_export.csv";
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
		}
          
        function getDetailFilterLabel(value) {
	if (!value) return "Detail Filter";

	var search = String(value).toLowerCase().trim();

	var isSupplier = false;
	var isGroup = false;
	var isItem = false;

	EXPORT_ITEMS.forEach(function (it) {
		var supplier = String(it.supplier || "").toLowerCase();
		var itemGroup = String(it.item_group || "").toLowerCase();
		var itemCode = String(it.item_code || "").toLowerCase();
		var itemName = String(it.item_name || "").toLowerCase();

		if (supplier && supplier.indexOf(search) !== -1) {
			isSupplier = true;
		}

		if (itemGroup && itemGroup.indexOf(search) !== -1) {
			isGroup = true;
		}

		if (
			(itemCode && itemCode.indexOf(search) !== -1) ||
			(itemName && itemName.indexOf(search) !== -1)
		) {
			isItem = true;
		}
	});

	if (isSupplier) return "Supplier";
	if (isGroup) return "Item Group";
	if (isItem) return "Item";

	return "Detail Filter";
}

		updateCount(); 


	<\/script>
</body>
</html>
`;

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

	var rows = items.map(function (it, index) {
		var po_id = it.po_id || it.purchase_order || it.parent || "";
		var material_request = it.material_request || "";
		var supplier = it.supplier || "";
		var item_code = it.item_code || "";
		var item_name = it.item_name || item_code || "";
		var item_group = it.item_group || "";
		var qty = po_fmt_num(it.qty);
		var uom = it.uom || "";
		var rate = po_fmt_money(it.rate);
		var amount = po_fmt_money(it.amount);

		var search_text = [
			po_id,
			material_request,
			supplier,
			item_code,
			item_name,
			item_group
		].join(" ");

		return '' +
			'<tr class="po-item-row" ' +
				'data-parent="' + po_esc(po_id) + '" ' +
				'data-po="' + po_esc(po_id) + '" ' +
				'data-mr="' + po_esc(material_request) + '" ' +
				'data-search="' + po_esc(search_text) + '">' +

				'<td class="text-right col-no">' + (index + 1) + '</td>' +
				'<td class="col-mr">' + po_make_multi_link("material-request", material_request) + '</td>' +
				'<td class="col-supplier" title="' + po_esc(supplier) + '">' + po_make_link("supplier", supplier) + '</td>' +
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
				'<td class="text-right col-amount">Rs. ' + po_esc(amount) + '</td>' +
			'</tr>';
	}).join("");

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
					'<th class="text-right col-amount">Total Amount</th>' +
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