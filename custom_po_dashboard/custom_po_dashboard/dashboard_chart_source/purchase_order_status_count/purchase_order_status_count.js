frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Purchase Order Status Count"] = {
	method: "custom_po_dashboard.custom_po_dashboard.dashboard_chart_source.purchase_order_status_count.purchase_order_status_count.get",
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
	],
};