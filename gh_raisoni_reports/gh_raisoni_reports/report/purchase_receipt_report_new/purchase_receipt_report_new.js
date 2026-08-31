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

	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname === "supplier" && data && data.supplier && data.supplier !== "-") {
			return pr_make_link("supplier", data.supplier);
		}

		if (column.fieldname === "purchase_order" && data && data.purchase_order && data.purchase_order !== "-") {
			return pr_make_multi_link("purchase-order", data.purchase_order);
		}

		if (column.fieldname === "material_request" && data && data.material_request && data.material_request !== "-") {
			return pr_make_multi_link("material-request", data.material_request);
		}

		if (column.fieldname === "purchase_invoice_details" && data && data.purchase_invoice_details && data.purchase_invoice_details !== "-") {
			return pr_make_multi_link("purchase-invoice", data.purchase_invoice_details);
		}

		return value;
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
	if (!dt || !report.data || !dt.rowmanager) return;

	var selected = {};
	var indexes = dt.rowmanager.getCheckedRows() || [];

	indexes.forEach(function (row_idx) {
		if (row_idx === undefined) return;

		var rd = report.data[row_idx];

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
	<title>Purchase Receipt Item Details</title>

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
			grid-template-columns: 190px 190px 260px 1fr auto auto;
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

		.amount-cell {
			color: #111827;
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

		.flat-print-export {
			display: none;
		}

		.flat-export-title {
			font-size: 14px;
			font-weight: 700;
			margin-bottom: 8px;
			color: #000;
			text-align: center;
		}

		.flat-export-filters {
			font-size: 10px;
			margin-bottom: 8px;
			font-weight: 600;
			color: #000;
			text-align: center;
		}

		.flat-export-filters .filter-line {
			display: flex;
			justify-content: center;
			gap: 45px;
			margin-bottom: 3px;
		}

		.col-no { width: 55px; }
		.col-receipt { width: 180px; }
		.col-supplier { width: 190px; }
		.col-pi { width: 190px; }
		.col-expense { width: 190px; }
		.col-item { width: 170px; }
		.col-group { width: 120px; }
		.col-qty { width: 100px; }
		.col-uom { width: 80px; }
		.col-rate { width: 120px; }
		.col-amount { width: 140px; }

		@media print {
			@page {
				size: A4 landscape;
				margin: 6mm;
			}

			html,
			body {
				width: auto !important;
				height: auto !important;
				background: #fff !important;
				margin: 0 !important;
				padding: 0 !important;
			}

			body.print-flat .filter-row,
			body.print-flat .count-pill,
			body.print-flat .no-print,
			body.print-flat .table-wrap,
			body.print-flat .report-header {
				display: none !important;
			}

			body.print-flat .page {
				padding: 0 !important;
			}

			body.print-flat .report-card {
				border: 0 !important;
				border-radius: 0 !important;
				overflow: visible !important;
			}

			body.print-flat .flat-print-export {
				display: block !important;
			}

			body.print-flat .flat-print-export table {
				width: 100% !important;
				table-layout: fixed !important;
				border-collapse: collapse !important;
			}

			body.print-flat .flat-print-export th,
			body.print-flat .flat-print-export td {
				border: 1px solid #d1d5db !important;
				white-space: normal !important;
				overflow: visible !important;
				text-overflow: clip !important;
				word-break: break-word !important;
				font-size: 5.5px !important;
				line-height: 1.2 !important;
				padding: 2px !important;
				color: #000 !important;
			}

			body.print-flat .flat-print-export th {
				background: #f3f4f6 !important;
				font-weight: 700 !important;
			}

			body.print-flat .flat-export-title {
				font-size: 13px !important;
				font-weight: 700 !important;
				margin-bottom: 5px !important;
				text-align: center !important;
			}

			body.print-flat .flat-export-filters {
				font-size: 8px !important;
				margin-bottom: 6px !important;
				font-weight: 600 !important;
				text-align: center !important;
			}

			body.print-flat .flat-export-filters .filter-line {
				display: flex !important;
				justify-content: center !important;
				gap: 35px !important;
				margin-bottom: 3px !important;
			}
		}
	</style>
</head>

<body>
	<div class="page">
		<div class="report-card">
			<div class="report-header">
				<div class="title">Purchase Receipt Item Details</div>
				<div class="meta">${pr_esc(meta)}</div>
			</div>

			<div class="filter-row no-print">
				<input id="filter-receipt" placeholder="Receipt ID" oninput="filterDetailTable()">
				<input id="filter-po" placeholder="PO ID" oninput="filterDetailTable()">
				<input id="filter-item" placeholder="Item / Supplier / Group" oninput="filterDetailTable()">
				<div></div>
				<button class="no-print" onclick="printFlatExport()">PDF / Print</button>
				<button class="no-print" onclick="downloadExcel()">Excel</button>
			</div>

			<div class="table-wrap">
				${pr_make_item_table_for_new_tab(items)}
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

		function exportInputValue(id) {
			var el = document.getElementById(id);
			return el ? (el.value || "").trim() : "";
		}

		function updateCount() {
			var rows = document.querySelectorAll("tbody tr.pr-item-row");
			var visible = 0;

			rows.forEach(function (row) {
				if (row.style.display !== "none") visible++;
			});

			document.getElementById("row-count").textContent = visible + " rows selected";
		}

		function filterDetailTable() {
			var receipt = getValue("filter-receipt");
			var po = getValue("filter-po");
			var item = getValue("filter-item");

			var rows = document.querySelectorAll("tbody tr.pr-item-row");

			rows.forEach(function (row) {
				var receiptText = (row.getAttribute("data-receipt") || "").toLowerCase();
				var poText = (row.getAttribute("data-po") || "").toLowerCase();
				var searchText = (row.getAttribute("data-search") || "").toLowerCase();

				var show = true;

				if (receipt && receiptText.indexOf(receipt) === -1) show = false;
				if (po && poText.indexOf(po) === -1) show = false;
				if (item && searchText.indexOf(item) === -1) show = false;

				row.style.display = show ? "" : "none";
				row.classList.toggle("hidden-print", !show);
			});

			updateCount();
		}

		function displayValue(value) {
			return value == null || value === "" ? "-" : String(value);
		}

		function numberValue(value) {
			var num = Number(value || 0);
			return num.toLocaleString("en-IN");
		}

		function moneyValue(value) {
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

		function itemMatchesExportFilters(it) {
			var receiptFilter = exportInputValue("filter-receipt").toLowerCase();
			var poFilter = exportInputValue("filter-po").toLowerCase();
			var itemFilter = exportInputValue("filter-item").toLowerCase();

			var receiptNo = String(it.receipt_id || it.purchase_receipt || it.parent || "").toLowerCase();
			var poNo = String(it.purchase_order || "").toLowerCase();

			var searchText = [
				it.receipt_id,
				it.purchase_receipt,
				it.parent,
				it.purchase_order,
				it.material_request,
				it.purchase_invoice_details,
				it.company,
				it.supplier,
				it.status,
				it.item_code,
				it.item_name,
				it.item_group
			].join(" ").toLowerCase();

			if (receiptFilter && receiptNo.indexOf(receiptFilter) === -1) return false;
			if (poFilter && poNo.indexOf(poFilter) === -1) return false;
			if (itemFilter && searchText.indexOf(itemFilter) === -1) return false;

			return true;
		}

		function buildFlatExportRows() {
			var rows = [];

			var detailFilter = exportInputValue("filter-item");
			var supplierValue = EXPORT_FILTERS.supplier || "";

			// Company center FIRST
			rows.push([EXPORT_FILTERS.company || "-"]);
			rows.push([]);

			// From Date and To Date together in center
			rows.push([
				"",
				"",
				"",
				"",
				"",
				"From Date : " + exportDate(EXPORT_FILTERS.from_date) + "     To Date : " + exportDate(EXPORT_FILTERS.to_date)
			]);

			// Main supplier filter only if selected
			if (supplierValue && String(supplierValue).trim() !== "") {
				rows.push(["Supplier : " + supplierValue]);
			}

			// Detail filter dynamic label: Supplier / Item Group / Item
			if (detailFilter && String(detailFilter).trim() !== "") {
				var detailLabel = getDetailFilterLabel(detailFilter);
				rows.push([detailLabel + " : " + detailFilter]);
			}

			// Status only if selected
			if (EXPORT_FILTERS.status && String(EXPORT_FILTERS.status).trim() !== "") {
				rows.push(["Status : " + EXPORT_FILTERS.status]);
			}

			// Purchase Receipt No only if typed
			if (exportInputValue("filter-receipt")) {
				rows.push(["Purchase Receipt No : " + exportInputValue("filter-receipt")]);
			}

			// Purchase Order ID only if typed
			if (exportInputValue("filter-po")) {
				rows.push(["Purchase Order ID : " + exportInputValue("filter-po")]);
			}

			rows.push([]);

			rows.push([
				"Date",
				"Purchase Receipt No.",
				"Purchase Order",
				"Material Request",
				"Purchase Invoice ID",
				"Company",
				"Supplier",
				"Grand Total",
				"Status",
				"Item Code",
				"Item Name",
				"Item Group",
				"Quantity",
				"UOM",
				"Rate",
				"Total Amount"
			]);

			EXPORT_ITEMS.forEach(function (it) {
				if (!itemMatchesExportFilters(it)) return;

				rows.push([
					exportDate(it.date || it.posting_date),
					displayValue(it.receipt_id || it.purchase_receipt || it.parent),
					displayValue(it.purchase_order),
					displayValue(it.material_request),
					displayValue(it.purchase_invoice_details),
					displayValue(it.company),
					displayValue(it.supplier),
					moneyValue(it.grand_total),
					displayValue(it.status),
					displayValue(it.item_code),
					displayValue(it.item_name || it.item_code),
					displayValue(it.item_group),
					numberValue(it.qty),
					displayValue(it.uom),
					moneyValue(it.rate),
					moneyValue(it.amount)
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

		function buildFlatPrintHtml() {
			var rows = buildFlatExportRows();
			var headerIndex = getHeaderIndex(rows);
			var html = "";

			var detailFilter = exportInputValue("filter-item");
			var supplierValue = EXPORT_FILTERS.supplier || "";

			html += '<div class="flat-export-title">' + htmlEsc(EXPORT_FILTERS.company || "-") + '</div>';

			html += '<div class="flat-export-filters">';

			html += '<div class="filter-line">';
			html += '<span><b>From Date:</b> ' + htmlEsc(exportDate(EXPORT_FILTERS.from_date)) + '</span>';
			html += '<span><b>To Date:</b> ' + htmlEsc(exportDate(EXPORT_FILTERS.to_date)) + '</span>';
			html += '</div>';

			if (supplierValue && String(supplierValue).trim() !== "") {
				html += '<div class="filter-line">';
				html += '<span><b>Supplier:</b> ' + htmlEsc(supplierValue) + '</span>';
				html += '</div>';
			}

			if (detailFilter && String(detailFilter).trim() !== "") {
				var detailLabel = getDetailFilterLabel(detailFilter);

				html += '<div class="filter-line">';
				html += '<span><b>' + htmlEsc(detailLabel) + ':</b> ' + htmlEsc(detailFilter) + '</span>';
				html += '</div>';
			}

			if (EXPORT_FILTERS.status && String(EXPORT_FILTERS.status).trim() !== "") {
				html += '<div class="filter-line">';
				html += '<span><b>Status:</b> ' + htmlEsc(EXPORT_FILTERS.status) + '</span>';
				html += '</div>';
			}

			if (exportInputValue("filter-receipt")) {
				html += '<div class="filter-line">';
				html += '<span><b>Purchase Receipt No:</b> ' + htmlEsc(exportInputValue("filter-receipt")) + '</span>';
				html += '</div>';
			}

			if (exportInputValue("filter-po")) {
				html += '<div class="filter-line">';
				html += '<span><b>Purchase Order ID:</b> ' + htmlEsc(exportInputValue("filter-po")) + '</span>';
				html += '</div>';
			}

			html += '</div>';

			html += '<table>';
			html += '<thead><tr>';

			rows[headerIndex].forEach(function (cell) {
				html += '<th>' + htmlEsc(cell) + '</th>';
			});

			html += '</tr></thead>';
			html += '<tbody>';

			for (var j = headerIndex + 1; j < rows.length; j++) {
				if (!rows[j].length) continue;

				html += '<tr>';

				rows[j].forEach(function (cell) {
					html += '<td>' + htmlEsc(cell) + '</td>';
				});

				html += '</tr>';
			}

			html += '</tbody></table>';

			return html;
		}

		function printFlatExport() {
			document.body.classList.add("print-flat");
			document.getElementById("flat-print-export").innerHTML = buildFlatPrintHtml();

			setTimeout(function () {
				window.print();
			}, 100);

			setTimeout(function () {
				document.body.classList.remove("print-flat");
			}, 1500);
		}

		function applyExcelTopCenterStyle(ws, rows) {
			var headerIndex = getHeaderIndex(rows);
			var merges = [];

			// Company full center: A to P
			merges.push({
				s: { r: 0, c: 0 },
				e: { r: 0, c: 15 }
			});

			// From Date and To Date together: F to I
			merges.push({
				s: { r: 2, c: 5 },
				e: { r: 2, c: 8 }
			});

			// Dynamic center rows after date row until before table header
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

			// From Date and To Date
			styleCell("F3", false);

			// Other dynamic filter rows
			for (var i = 4; i <= headerIndex; i++) {
				styleCell("A" + i, false);
			}

			// Table header bold and center
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

		function downloadExcel() {
			var rows = buildFlatExportRows();

			if (typeof XLSX !== "undefined") {
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
					{ wch: 14 },
					{ wch: 24 },
					{ wch: 24 },
					{ wch: 24 },
					{ wch: 26 },
					{ wch: 32 },
					{ wch: 30 },
					{ wch: 16 },
					{ wch: 14 },
					{ wch: 18 },
					{ wch: 32 },
					{ wch: 20 },
					{ wch: 12 },
					{ wch: 10 },
					{ wch: 14 },
					{ wch: 16 }
				];

				var wb = XLSX.utils.book_new();
				XLSX.utils.book_append_sheet(wb, ws, "Flat Export");
				XLSX.writeFile(wb, "purchase_receipt_parent_child_export.xlsx");
				return;
			}

			downloadCsv(rows);
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
			a.download = "purchase_receipt_parent_child_export.csv";
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

function pr_make_item_table_for_new_tab(items) {
	if (!items.length) {
		return '<div class="empty">No Purchase Receipt Item rows found.</div>';
	}

	var rows = items.map(function (it, index) {
		var receipt_id = it.receipt_id || it.parent || "";
		var supplier = it.supplier || "";
		var purchase_order = it.purchase_order || "";
		var purchase_invoice_details = it.purchase_invoice_details || "";
		var expense_head = it.expense_head || "";
		var item_code = it.item_code || "";
		var item_name = it.item_name || item_code || "";
		var item_group = it.item_group || "";
		var qty = pr_fmt_num(it.qty);
		var uom = it.uom || "";
		var rate = pr_fmt_money(it.rate);
		var amount = pr_fmt_money(it.amount);

		var search_text = [
			supplier,
			purchase_order,
			purchase_invoice_details,
			expense_head,
			item_code,
			item_name,
			item_group
		].join(" ");

		return '' +
			'<tr class="pr-item-row" data-receipt="' + pr_esc(receipt_id) + '" data-po="' + pr_esc(purchase_order) + '" data-search="' + pr_esc(search_text) + '">' +
				'<td class="text-right col-no">' + (index + 1) + '</td>' +
				'<td class="col-receipt">' + pr_make_link("purchase-receipt", receipt_id) + '</td>' +
				'<td class="col-supplier" title="' + pr_esc(supplier) + '">' + pr_make_link("supplier", supplier) + '</td>' +
				'<td class="col-pi">' + pr_make_multi_link("purchase-invoice", purchase_invoice_details) + '</td>' +
				'<td class="col-expense" title="' + pr_esc(expense_head) + '">' + pr_esc(expense_head || "-") + '</td>' +
				'<td class="col-item" title="' + pr_esc(item_name) + '">' +
					(item_name
						? '<a class="doc-link" href="/app/item/' + encodeURIComponent(item_code || item_name) + '" target="_blank">' + pr_esc(item_name) + '</a>'
						: '<span class="muted">-</span>') +
				'</td>' +
				'<td class="col-group" title="' + pr_esc(item_group) + '">' +
					(item_group
						? '<a class="doc-link" href="/app/item-group/' + encodeURIComponent(item_group) + '" target="_blank">' + pr_esc(item_group) + '</a>'
						: '<span class="muted">-</span>') +
				'</td>' +
				'<td class="text-right col-qty">' + pr_esc(qty) + '</td>' +
				'<td class="col-uom">' + pr_esc(uom || "-") + '</td>' +
				'<td class="text-right col-rate">Rs. ' + pr_esc(rate) + '</td>' +
				'<td class="text-right col-amount amount-cell">Rs. ' + pr_esc(amount) + '</td>' +
			'</tr>';
	}).join("");

	return '' +
		'<table>' +
			'<thead>' +
				'<tr>' +
					'<th class="text-right col-no">No.</th>' +
					'<th class="col-receipt">Purchase Receipt No.</th>' +
					'<th class="col-supplier">Supplier</th>' +
					'<th class="col-pi">Purchase Invoice ID</th>' +
					'<th class="col-expense">Expense Head</th>' +
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

function pr_make_link(route, value) {
	if (!value || value === "-") {
		return '<span class="muted">-</span>';
	}

	return '<a class="doc-link" href="/app/' + route + '/' + encodeURIComponent(value) + '" target="_blank">' +
		pr_esc(value) +
	'</a>';
}

function pr_make_multi_link(route, value) {
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
			pr_esc(v) +
		'</a>';
	}).join(", ");
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