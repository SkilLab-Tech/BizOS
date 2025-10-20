# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data, filters)
	return columns, data, None, chart


def get_columns():
	return [
		{
			"fieldname": "member",
			"label": _("Member"),
			"fieldtype": "Link",
			"options": "Member Profile",
			"width": 200,
		},
		{
			"fieldname": "email",
			"label": _("Email"),
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"fieldname": "member_type",
			"label": _("Type"),
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"fieldname": "total_connections",
			"label": _("Connections"),
			"fieldtype": "Int",
			"width": 110,
		},
		{
			"fieldname": "pending_requests",
			"label": _("Pending"),
			"fieldtype": "Int",
			"width": 90,
		},
		{
			"fieldname": "total_meetings",
			"label": _("Meetings"),
			"fieldtype": "Int",
			"width": 90,
		},
		{
			"fieldname": "upcoming_meetings",
			"label": _("Upcoming"),
			"fieldtype": "Int",
			"width": 90,
		},
		{
			"fieldname": "interests_count",
			"label": _("Interests"),
			"fieldtype": "Int",
			"width": 90,
		},
		{
			"fieldname": "skills_count",
			"label": _("Skills"),
			"fieldtype": "Int",
			"width": 80,
		},
		{
			"fieldname": "join_date",
			"label": _("Join Date"),
			"fieldtype": "Date",
			"width": 100,
		},
	]


def get_data(filters):
	from frappe.utils import today

	conditions = []
	values = {}

	if filters.get("member_type"):
		conditions.append("mp.member_type = %(member_type)s")
		values["member_type"] = filters.get("member_type")

	if filters.get("status"):
		conditions.append("mp.status = %(status)s")
		values["status"] = filters.get("status")
	else:
		conditions.append("mp.status = 'Active'")

	where_clause = " AND ".join(conditions) if conditions else "1=1"

	data = frappe.db.sql(
		f"""
		SELECT
			mp.name as member,
			mp.email,
			mp.member_type,
			mp.join_date,
			(
				SELECT COUNT(*)
				FROM `tabNetworking Connection` nc
				WHERE nc.status = 'Accepted'
				AND (nc.from_member = mp.name OR nc.to_member = mp.name)
			) as total_connections,
			(
				SELECT COUNT(*)
				FROM `tabNetworking Connection` nc
				WHERE nc.status = 'Pending'
				AND nc.to_member = mp.name
			) as pending_requests,
			(
				SELECT COUNT(*)
				FROM `tabNetworking Meeting` nm
				WHERE nm.status IN ('Completed', 'Confirmed')
				AND (nm.participant_1 = mp.name OR nm.participant_2 = mp.name)
			) as total_meetings,
			(
				SELECT COUNT(*)
				FROM `tabNetworking Meeting` nm
				WHERE nm.status IN ('Scheduled', 'Confirmed')
				AND nm.meeting_date >= %(today)s
				AND (nm.participant_1 = mp.name OR nm.participant_2 = mp.name)
			) as upcoming_meetings,
			(
				SELECT COUNT(*)
				FROM `tabMember Interest` mi
				WHERE mi.parent = mp.name
			) as interests_count,
			(
				SELECT COUNT(*)
				FROM `tabMember Skill` ms
				WHERE ms.parent = mp.name
			) as skills_count
		FROM
			`tabMember Profile` mp
		WHERE
			{where_clause}
		ORDER BY
			total_connections DESC
	""",
		{"today": today(), **values},
		as_dict=1,
	)

	return data


def get_chart_data(data, filters):
	if not data:
		return None

	# Count members by type
	member_types = {}
	for row in data:
		member_type = row.get("member_type") or "Unspecified"
		member_types[member_type] = member_types.get(member_type, 0) + 1

	return {
		"data": {
			"labels": list(member_types.keys()),
			"datasets": [{"name": _("Members"), "values": list(member_types.values())}],
		},
		"type": "donut",
		"height": 300,
	}
