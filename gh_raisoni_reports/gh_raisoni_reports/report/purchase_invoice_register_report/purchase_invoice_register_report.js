frappe.query_reports["Purchase Invoice Register Report"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			width: "80",
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
			only_select: true,
			options: "Supplier",
		},
		{
			fieldname: "supplier_group",
			label: __("Supplier Group"),
			fieldtype: "Link",
			only_select: true,
			options: "Supplier Group",
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			only_select: true,
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "mode_of_payment",
			label: __("Mode of Payment"),
			fieldtype: "Link",
			only_select: true,
			options: "Mode of Payment",
		},
		{
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "Link",
			only_select: true,
			options: "Cost Center",
		},
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			only_select: true,
			options: "Warehouse",
		},
		{
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "Link",
			only_select: true,
			options: "Item Group",
		},
	],

	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		// invoice rows and the Grand Total row in bold; item rows stay plain
		if (data && (data.is_invoice || data.is_total) && value !== undefined && value !== null && value !== "") {
			return "<b>" + value + "</b>";
		}

		return value;
	},

	onload: function (report) {
		$(report.page.wrapper).addClass("pir-report-page");
		(report.filters || []).forEach(function (flt_field) {
			if (flt_field.df && flt_field.df.fieldtype === "Link") flt_field.df.only_select = true;
		});

		pir_add_styles();
	},
};

if (window.erpnext && erpnext.utils && erpnext.utils.add_dimensions) {
	erpnext.utils.add_dimensions("Purchase Invoice Register Report", 7);
}

function pir_add_styles() {
	if ($("#pir-rpt-style").length) return;

	$("head").append(`<style id="pir-rpt-style">
		.dt-cell__content {
			overflow: visible !important;
			text-overflow: clip !important;
			white-space: nowrap !important;
		}
		.dt-cell {
			overflow: visible !important;
		}
		.pir-report-page .layout-main,
		.pir-report-page .page-body,
		.pir-report-page .layout-main-section-wrapper,
		.pir-report-page .layout-main-section {
			overflow: visible !important;
		}
		.pir-report-page .layout-main-section {
			min-height: 520px;
		}
	</style>`);
}
