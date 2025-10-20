# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

"""
AI-Powered Matchmaking API

This module provides advanced matchmaking algorithms for connecting members
based on their interests, skills, goals, and compatibility.
"""

import frappe
from frappe import _


@frappe.whitelist()
def find_matches_for_member(member, criteria=None, limit=10):
	"""
	Find potential matches for a member using AI-powered algorithm

	Args:
		member: Member Profile name
		criteria: Additional filtering criteria (JSON string)
		limit: Maximum number of matches to return

	Returns:
		List of matched members with scores and reasons
	"""
	import json

	if criteria and isinstance(criteria, str):
		criteria = json.loads(criteria)
	else:
		criteria = {}

	member_profile = frappe.get_doc("Member Profile", member)
	matches = member_profile.find_matches(limit=int(limit))

	# Apply additional criteria
	if criteria:
		matches = apply_match_filters(matches, criteria)

	return {
		"total": len(matches),
		"matches": matches,
		"member": member,
		"timestamp": frappe.utils.now(),
	}


def apply_match_filters(matches, criteria):
	"""Apply additional filtering criteria to matches"""
	filtered = matches

	# Filter by minimum score
	if "min_score" in criteria:
		filtered = [m for m in filtered if m["score"] >= criteria["min_score"]]

	# Filter by connection type preference
	if "connection_type" in criteria:
		# This would filter based on member preferences
		pass

	# Filter by location
	if "location" in criteria:
		location = criteria["location"]
		filtered = [
			m
			for m in filtered
			if m["profile"].location and location.lower() in m["profile"].location.lower()
		]

	# Filter by industry
	if "industry" in criteria:
		industry = criteria["industry"]
		filtered = [
			m
			for m in filtered
			if m["profile"].industry and industry.lower() in m["profile"].industry.lower()
		]

	return filtered


@frappe.whitelist()
def get_member_statistics(member):
	"""
	Get networking statistics for a member

	Args:
		member: Member Profile name

	Returns:
		Dictionary with statistics
	"""
	from frappe.utils import today, add_months

	stats = {}

	# Connection stats
	stats["connections"] = frappe.db.count(
		"Networking Connection",
		{"status": "Accepted"},
		or_filters=[{"from_member": member}, {"to_member": member}],
	)

	stats["pending_connections"] = frappe.db.count(
		"Networking Connection", {"to_member": member, "status": "Pending"}
	)

	# Meeting stats
	stats["meetings"] = frappe.db.count(
		"Networking Meeting",
		{"status": ["in", ["Completed", "Confirmed"]]},
		or_filters=[{"participant_1": member}, {"participant_2": member}],
	)

	stats["upcoming_meetings"] = frappe.db.count(
		"Networking Meeting",
		{
			"status": ["in", ["Scheduled", "Confirmed"]],
			"meeting_date": [">=", today()],
		},
		or_filters=[{"participant_1": member}, {"participant_2": member}],
	)

	# Profile stats
	member_profile = frappe.get_doc("Member Profile", member)
	stats["interests"] = len(member_profile.interests)
	stats["skills"] = len(member_profile.skills)
	stats["organizations"] = len(member_profile.organizations)
	stats["alumni_groups"] = len(member_profile.alumni_groups)

	# Matchmaking stats
	stats["match_requests"] = frappe.db.count("Matchmaking Request", {"member": member})

	# Activity in last 30 days
	last_month = add_months(today(), -1)
	stats["recent_connections"] = frappe.db.count(
		"Networking Connection",
		{"status": "Accepted", "accepted_date": [">=", last_month]},
		or_filters=[{"from_member": member}, {"to_member": member}],
	)

	stats["recent_meetings"] = frappe.db.count(
		"Networking Meeting",
		{"status": "Completed", "meeting_date": [">=", last_month]},
		or_filters=[{"participant_1": member}, {"participant_2": member}],
	)

	return stats


@frappe.whitelist()
def suggest_connections(member, limit=5):
	"""
	Suggest new connections based on mutual connections and interests

	Args:
		member: Member Profile name
		limit: Maximum suggestions

	Returns:
		List of suggested connections
	"""
	# Get existing connections
	existing_connections = get_connected_members(member)

	# Get member profile
	member_profile = frappe.get_doc("Member Profile", member)

	# Find matches excluding existing connections
	all_matches = member_profile.find_matches(limit=50)

	suggestions = []
	for match in all_matches:
		if match["member"] not in existing_connections:
			# Calculate mutual connections
			mutual = count_mutual_connections(member, match["member"])

			suggestions.append(
				{
					"member": match["member"],
					"profile": match["profile"],
					"match_score": match["score"],
					"mutual_connections": mutual,
					"reason": get_connection_suggestion_reason(
						member_profile, match["profile"], mutual
					),
				}
			)

			if len(suggestions) >= int(limit):
				break

	return suggestions


def get_connected_members(member):
	"""Get list of members already connected"""
	connections = frappe.db.sql(
		"""
		SELECT
			CASE
				WHEN from_member = %s THEN to_member
				ELSE from_member
			END as connected_member
		FROM
			`tabNetworking Connection`
		WHERE
			status = 'Accepted'
			AND (from_member = %s OR to_member = %s)
	""",
		(member, member, member),
		as_dict=False,
	)

	return [conn[0] for conn in connections]


def count_mutual_connections(member1, member2):
	"""Count mutual connections between two members"""
	member1_connections = set(get_connected_members(member1))
	member2_connections = set(get_connected_members(member2))

	mutual = member1_connections & member2_connections
	return len(mutual)


def get_connection_suggestion_reason(profile1, profile2, mutual_count):
	"""Generate reason for connection suggestion"""
	reasons = []

	if mutual_count > 0:
		reasons.append(f"{mutual_count} mutual connection{'s' if mutual_count > 1 else ''}")

	# Check interests
	interests1 = {row.interest for row in profile1.interests}
	interests2 = {row.interest for row in profile2.interests}
	common_interests = interests1 & interests2
	if common_interests:
		reasons.append(f"Share {len(common_interests)} interest{'s' if len(common_interests) > 1 else ''}")

	# Check industry
	if profile1.industry and profile2.industry and profile1.industry == profile2.industry:
		reasons.append(f"Both in {profile1.industry}")

	return ", ".join(reasons) if reasons else "Potential networking match"


@frappe.whitelist()
def get_trending_interests():
	"""Get trending interests based on member activity"""
	trending = frappe.db.sql(
		"""
		SELECT
			mi.interest,
			COUNT(*) as member_count,
			i.category
		FROM
			`tabMember Interest` mi
		INNER JOIN
			`tabMember Profile` mp ON mi.parent = mp.name
		LEFT JOIN
			`tabInterest` i ON mi.interest = i.name
		WHERE
			mp.status = 'Active'
		GROUP BY
			mi.interest
		ORDER BY
			member_count DESC
		LIMIT 20
	""",
		as_dict=True,
	)

	return trending


@frappe.whitelist()
def get_trending_skills():
	"""Get trending skills based on member activity"""
	trending = frappe.db.sql(
		"""
		SELECT
			ms.skill,
			COUNT(*) as member_count,
			s.category,
			AVG(ms.years_of_experience) as avg_experience
		FROM
			`tabMember Skill` ms
		INNER JOIN
			`tabMember Profile` mp ON ms.parent = mp.name
		LEFT JOIN
			`tabSkill` s ON ms.skill = s.name
		WHERE
			mp.status = 'Active'
		GROUP BY
			ms.skill
		ORDER BY
			member_count DESC
		LIMIT 20
	""",
		as_dict=True,
	)

	return trending


@frappe.whitelist()
def get_networking_recommendations(member):
	"""
	Get personalized networking recommendations for a member

	Returns various recommendations including:
	- People to connect with
	- Events to attend
	- Groups to join
	- Skills to develop
	"""
	recommendations = {
		"connections": suggest_connections(member, limit=5),
		"match_score_threshold": 70,
		"active_connections": frappe.db.count(
			"Networking Connection",
			{"status": "Accepted"},
			or_filters=[{"from_member": member}, {"to_member": member}],
		),
	}

	# Get member profile
	member_profile = frappe.get_doc("Member Profile", member)

	# Recommend alumni groups
	if member_profile.organizations:
		org_names = [org.organization for org in member_profile.organizations]
		recommendations["alumni_groups"] = frappe.get_all(
			"Alumni Group",
			filters={"organization": ["in", org_names], "status": "Active"},
			fields=["name", "group_name", "group_type", "total_members"],
			limit=5,
		)

	# Recommend skills to learn based on interests
	if member_profile.interests:
		recommendations["suggested_skills"] = get_skills_for_interests(
			[interest.interest for interest in member_profile.interests]
		)

	return recommendations


def get_skills_for_interests(interests):
	"""Suggest skills based on interests"""
	# This is a simple implementation - can be enhanced with ML
	skill_mapping = {
		"Technology": ["Python", "JavaScript", "Cloud Computing", "Data Science"],
		"Business": ["Strategy", "Project Management", "Financial Analysis"],
		"Arts & Culture": ["Design", "Creative Writing", "Photography"],
	}

	suggested = set()
	for interest_name in interests:
		interest = frappe.db.get_value("Interest", interest_name, "category")
		if interest and interest in skill_mapping:
			suggested.update(skill_mapping[interest])

	return list(suggested)[:5]
