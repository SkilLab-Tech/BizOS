# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "name",
			"label": _("Connection ID"),
			"fieldtype": "Link",
			"options": "Networking Connection",
			"width": 150,
		},
		{
			"fieldname": "from_member_name",
			"label": _("From Member"),
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"fieldname": "to_member_name",
			"label": _("To Member"),
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"fieldname": "connection_type",
			"label": _("Type"),
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"fieldname": "created_date",
			"label": _("Created Date"),
			"fieldtype": "Date",
			"width": 110,
		},
		{
			"fieldname": "accepted_date",
			"label": _("Accepted Date"),
			"fieldtype": "Date",
			"width": 110,
		},
		{
			"fieldname": "interaction_count",
			"label": _("Interactions"),
			"fieldtype": "Int",
			"width": 100,
		},
		{
			"fieldname": "meeting_count",
			"label": _("Meetings"),
			"fieldtype": "Int",
			"width": 90,
		},
		{
			"fieldname": "last_interaction_date",
			"label": _("Last Interaction"),
			"fieldtype": "Datetime",
			"width": 150,
		},
	]


def get_data(filters):
	conditions = []
	values = {}

	if filters.get("member"):
		conditions.append("(nc.from_member = %(member)s OR nc.to_member = %(member)s)")
		values["member"] = filters.get("member")

	if filters.get("status"):
		conditions.append("nc.status = %(status)s")
		values["status"] = filters.get("status")

	if filters.get("connection_type"):
		conditions.append("nc.connection_type = %(connection_type)s")
		values["connection_type"] = filters.get("connection_type")

	if filters.get("from_date"):
		conditions.append("nc.created_date >= %(from_date)s")
		values["from_date"] = filters.get("from_date")

	if filters.get("to_date"):
		conditions.append("nc.created_date <= %(to_date)s")
		values["to_date"] = filters.get("to_date")

	where_clause = " AND ".join(conditions) if conditions else "1=1"

	data = frappe.db.sql(
		f"""
		SELECT
			nc.name,
			nc.from_member_name,
			nc.to_member_name,
			nc.status,
			nc.connection_type,
			nc.created_date,
			nc.accepted_date,
			nc.interaction_count,
			nc.meeting_count,
			nc.last_interaction_date
		FROM
			`tabNetworking Connection` nc
		WHERE
			{where_clause}
		ORDER BY
			nc.created_date DESC
	""",
		values,
		as_dict=1,
	)

	return data
