# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from frappe.utils.dashboard import cache_source

COLOR_MAP = {
	# User Specified / Workflow States:
	"To Approve": "#fff1e7",       # Light Orange/Peach
	"To Check": "#edf6fd",         # Very Light Blue
	"Waiting for PO Confirmation": "#e4f5e9", # Very Light Green
	"To Order": "#fff0f0",         # Light Red
	"Approved": "#d4edda",         # Light Green (Different from Waiting Confirmation)
	"Draft": "#fdfdfe",            # Very Light Grey / Off-white
	"Cancelled": "#e2e3e5",        # Light Grey
	# Add other actual workflow states if needed

	# Statuses (when workflow_state='Expect Delivery'):
	"To Bill": "#fff1e7",          # Light Orange/Peach (Same as To Approve)
	"To Receive": "#cfe2ff",       # Light Blue/Indigo
	"To Receive and Bill": "#d1ecf1", # Light Cyan/Teal
	"Pending": "#fff3cd",          # Light Yellow (Often a status)

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
	from_date=None, # Add date filters if needed
	to_date=None,   # Add date filters if needed
	timespan=None,
	time_interval=None,
	heatmap_year=None,
):
	labels, datapoints, colors = [], [], [] # Initialize colors list
	filters_dict = frappe.parse_json(filters) if filters else {}
	company = filters_dict.get("company") or frappe.defaults.get_user_default("company")

	if not company:
	    frappe.throw(_("Company not specified in filters or user defaults."))


	sql_args = {"company": company}

	data = frappe.db.sql("""
	    SELECT workflow_state, COUNT(*) AS count
	    FROM `tabPurchase Order`
	    WHERE company = %(company)s
	    AND workflow_state NOT IN ('Expect Delivery', 'PO Rejected', 'Rejected')
	    GROUP BY workflow_state
	""", values=sql_args, as_dict=True)

	expected_delivery = frappe.db.sql("""
	    SELECT status as workflow_state, COUNT(*) AS count
	    FROM `tabPurchase Order`
	    WHERE company = %(company)s
	    AND workflow_state = 'Expect Delivery'
	    AND status NOT IN ('Completed', 'Cancelled', 'Closed')
	    GROUP BY status
	""", values=sql_args, as_dict=True)

	# Combine results
	data.extend(expected_delivery)

	if not data:
		# Return empty structure expected by charts
		return {
			"labels": [],
			"datasets": [{"name": _("Documents Count"), "values": []}],
			"type": "bar",
			"colors": [],
		}

	for d in data:
		# Get the state/status string. Use .strip() for safety.
		state_or_status = (d.workflow_state or "").strip() # Handle potential None values before strip
		if not state_or_status: # Skip if state/status is empty/None
			continue

		labels.append(_(state_or_status))
		datapoints.append(d.count)

		# Append the corresponding color, using the default if not found
		colors.append(COLOR_MAP.get(state_or_status, DEFAULT_COLOR))

	return {
		"labels": labels,
		"datasets": [{"name": _("Documents Count"), "values": datapoints}],
		"type": "bar",
		"colors": colors, # Add the colors list here
	}
