# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _
from frappe.utils.dashboard import cache_source

# Color map for different workflow states and statuses
COLOR_MAP = {
    # User Specified / Workflow States:
    "To Approve": "#fff1e7",  # Light Orange/Peach
    "To Check": "#edf6fd",  # Very Light Blue
    "Waiting for PO Confirmation": "#e4f5e9",  # Very Light Green
    "To Order": "#fff0f0",  # Light Red
    "Approved": "#d4edda",  # Light Green (Different from Waiting Confirmation)
    "Draft": "#fdfdfe",  # Very Light Grey / Off-white
    "Cancelled": "#e2e3e5",  # Light Grey
    # Statuses (when workflow_state='Expect Delivery'):
    "To Bill": "#fff1e7",  # Light Orange/Peach (Same as To Approve)
    "To Receive": "#cfe2ff",  # Light Blue/Indigo
    "To Receive and Bill": "#d1ecf1",  # Light Cyan/Teal
    "Pending": "#fff3cd",  # Light Yellow (Often a status)
}

# Define a default color for any state/status not explicitly mapped
DEFAULT_COLOR = "#f8f9fa"  # Very light grey / almost white

@frappe.whitelist()
@cache_source
def get(
    chart_name=None, 
    chart=None, 
    no_cache=None, 
    filters=None, 
    from_date=None,  # Add date filters if needed
    to_date=None,    # Add date filters if needed
    timespan=None, 
    time_interval=None, 
    heatmap_year=None,
):
    # Parse filters
    filters_dict = frappe.parse_json(filters) if filters else {}
    company = filters_dict.get("company") or frappe.defaults.get_user_default("company")
    
    if not company:
        frappe.throw(_("Company not specified in filters or user defaults."))
    
    sql_args = {"company": company}
    
    # Fetch workflow states excluding specific ones
    data = frappe.db.sql("""
        SELECT workflow_state, COUNT(*) AS count
        FROM `tabPurchase Order`
        WHERE company = %(company)s
        AND workflow_state NOT IN ('Expect Delivery', 'PO Rejected', 'Rejected')
        GROUP BY workflow_state
    """, values=sql_args, as_dict=True)
    
    # Fetch statuses for 'Expect Delivery' workflow state
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
            "datasets": [],
            "type": "bar"
        }
    
    # Create separate datasets for each bar to achieve individual colors
    labels = []
    datasets = []
    
    for d in data:
        state_or_status = (d.workflow_state or "").strip()
        if not state_or_status:
            continue
        
        # Get the color for this state/status
        color = COLOR_MAP.get(state_or_status, DEFAULT_COLOR)
        
        # Create a dataset for this single bar
        dataset = {
            "name": _(state_or_status),
            "values": [d.count],  # Single value for this bar
            "chartType": "bar"
        }
        
        # Add to our collections
        datasets.append(dataset)
        
    # Use labels appropriately
    status_names = [_(d.get("name")) for d in datasets]
    
    return {
        "labels": ["Status Count"],  # Single X-axis label since we're using separate datasets
        "datasets": datasets,
        "type": "bar",
        "colors": [COLOR_MAP.get(d.get("name").replace("_", " "), DEFAULT_COLOR) for d in datasets],
        "barOptions": {
            "stacked": 0,  # Make sure bars aren't stacked
            "spaceRatio": 0.2  # Space between bars
        }
    }
