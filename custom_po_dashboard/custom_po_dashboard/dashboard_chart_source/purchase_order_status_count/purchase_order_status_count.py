@frappe.whitelist()
@cache_source
def get(chart_name=None, chart=None, no_cache=None, filters=None, from_date=None, to_date=None, timespan=None, time_interval=None, heatmap_year=None):
    labels, datapoints, colors = [], [], []
    
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
    
    data.extend(expected_delivery)
    
    if not data:
        return {
            "labels": [],
            "datasets": [{"name": _("Documents Count"), "values": []}],
            "type": "bar"
        }
    
    for d in data:
        state_or_status = (d.workflow_state or "").strip()
        if not state_or_status:
            continue
            
        labels.append(_(state_or_status))
        datapoints.append(d.count)
        colors.append(COLOR_MAP.get(state_or_status, DEFAULT_COLOR))
    
    # Just return the colors directly in the main structure
    return {
        "labels": labels,
        "datasets": [{"name": _("Documents Count"), "values": datapoints}],
        "type": "bar",
        "colors": colors  # This is the key part
    }
