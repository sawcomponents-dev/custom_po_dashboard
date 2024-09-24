# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from frappe.utils.dashboard import cache_source


@frappe.whitelist()
@cache_source
def get(
	chart_name=None,
	chart=None,
	no_cache=None,
	filters=None,
	from_date=None,
	to_date=None,
	timespan=None,
	time_interval=None,
	heatmap_year=None,
):
	labels, datapoints = [], []
	filters = frappe.parse_json(filters)
	if filters and filters.get("company"):
		company = filters.get("company")
	else:
		company =  frappe.defaults.get_user_default("company")

	data = frappe.db.sql(f"""
			SELECT workflow_state, COUNT(*) AS count
			FROM `tabPurchase Order`
			WHERE company = '{company}'
			GROUP BY workflow_state
		""", as_dict=True)

	if not data:
		return []

	for d in data:
		labels.append(_(d.workflow_state))
		datapoints.append(_(d.count))

	return {
		"labels": labels,
		"datasets": [{"name": _("Documents Count"), "values": datapoints}],
		"type": "bar",
	}