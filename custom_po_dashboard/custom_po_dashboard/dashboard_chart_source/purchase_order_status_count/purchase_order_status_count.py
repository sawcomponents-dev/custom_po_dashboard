# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from frappe.utils.dashboard import cache_source

COLOR_MAP = {
	# User Specified:
	"To Approve": "#fff1e7",       # Light Orange/Peach
	"To Check": "#edf6fd",         # Very Light Blue
	"Waiting for PO Confirmation": "#e4f5e9", # Very Light Green (Assuming this matches "Waiting ...")
	"To Order": "#f8d7da",         # Light Red
	"To Bill": "#fff1e7",          # Light Orange/Peach (Same as To Approve)

	# Deduced from Chart Image (assigning distinct light colors):
	"To Receive": "#cfe2ff",       # Light Blue/Indigo
	"To Receive and Bill": "#d1ecf1", # Light Cyan/Teal (Assuming this matches "To Recei ...")

	# Add other potential standard workflow states (optional, but good practice):
	"Draft": "#fdfdfe",            # Very Light Grey / Off-white
	"Pending": "#fff3cd",          # Light Yellow
	"Approved": "#d4edda",         # Light Green (Different from Waiting Confirmation)
	"Cancelled": "#e2e3e5",        # Light Grey
	# Add any other possible statuses/states returned by your specific workflow
}
# Define a default color for any state/status not explicitly mapped
DEFAULT_COLOR = "#f8f9fa" # Very light grey / almost white



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
			AND workflow_state not in ('Expect Delivery', 'PO Rejected', 'Rejected')
			GROUP BY workflow_state
		""", as_dict=True)

	expected_delivery = frappe.db.sql(f"""
			SELECT status as workflow_state, COUNT(*) AS count
			FROM `tabPurchase Order`
			WHERE company = '{company}'
			AND workflow_state = 'Expect Delivery'
			AND status not in ('Completed', 'Cancelled', 'Closed')
			GROUP BY status
		""", as_dict=True)

	data.extend(expected_delivery)

	if not data:
		return []

	for d in data:
		# Get the state/status string. Use .strip() just in case of leading/trailing whitespace
		state_or_status = d.workflow_state.strip()
		labels.append(_(state_or_status))
		datapoints.append(d.count) # No need for _() on counts (they are numbers)


		# Append the corresponding color, using the default if not found
		colors.append(COLOR_MAP.get(state_or_status, DEFAULT_COLOR))


	return {
		"labels": labels,
		"datasets": [{"name": _("Documents Count"), "values": datapoints}],
		"type": "bar",
		"colors": colors, # Add the colors list here
	}
