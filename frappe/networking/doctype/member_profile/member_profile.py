# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import append_number_if_name_exists
from frappe.utils import cstr, has_gravatar, now


class MemberProfile(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.networking.doctype.member_alumni_group.member_alumni_group import MemberAlumniGroup
		from frappe.networking.doctype.member_interest.member_interest import MemberInterest
		from frappe.networking.doctype.member_organization.member_organization import MemberOrganization
		from frappe.networking.doctype.member_skill.member_skill import MemberSkill
		from frappe.types import DF

		ai_matching_enabled: DF.Check
		allow_messages: DF.Check
		alumni_groups: DF.Table[MemberAlumniGroup]
		availability_notes: DF.SmallText | None
		available_for_networking: DF.Check
		bio: DF.TextEditor | None
		contact: DF.Link | None
		current_organization: DF.Data | None
		current_position: DF.Data | None
		email: DF.Data
		email_notifications: DF.Check
		expertise_level: DF.Literal["", "Beginner", "Intermediate", "Advanced", "Expert"]
		first_name: DF.Data
		full_name: DF.Data | None
		headline: DF.Data | None
		industry: DF.Data | None
		interests: DF.Table[MemberInterest]
		join_date: DF.Date | None
		last_matched_on: DF.Datetime | None
		last_name: DF.Data | None
		linkedin_profile: DF.Data | None
		location: DF.Data | None
		looking_for_mentor: DF.Check
		match_score_threshold: DF.Int
		matchmaking_preferences: DF.SmallText | None
		member_type: DF.Literal["", "Alumni", "Mentor", "Mentee", "Volunteer", "Staff", "Board Member", "Donor", "Partner"]
		middle_name: DF.Data | None
		mobile_no: DF.Data | None
		networking_goals: DF.SmallText | None
		open_to_hiring: DF.Check
		organizations: DF.Table[MemberOrganization]
		phone: DF.Data | None
		preferred_meeting_mode: DF.Literal["Virtual", "In-Person", "Both"]
		profile_image: DF.AttachImage | None
		profile_visibility: DF.Literal["Public", "Members Only", "Private"]
		seeking_opportunities: DF.Check
		skills: DF.Table[MemberSkill]
		status: DF.Literal["Active", "Inactive", "Pending Approval", "Suspended"]
		timezone: DF.Literal["", "UTC", "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles", "Europe/London", "Europe/Paris", "Asia/Tokyo", "Asia/Shanghai", "Asia/Kolkata", "Australia/Sydney"]
		user: DF.Link | None
		willing_to_mentor: DF.Check
		years_of_experience: DF.Int
	# end: auto-generated types

	def autoname(self):
		"""Generate unique name from full name"""
		self.name = self.full_name
		if frappe.db.exists("Member Profile", self.name):
			self.name = append_number_if_name_exists("Member Profile", self.name)

	def validate(self):
		"""Validate member profile"""
		self.set_full_name()
		self.set_user()
		self.set_profile_image()
		self.validate_email_unique()

	def set_full_name(self):
		"""Set full name from first, middle, last name"""
		parts = [
			cstr(self.first_name).strip(),
			cstr(self.middle_name).strip() if self.middle_name else "",
			cstr(self.last_name).strip() if self.last_name else "",
		]
		self.full_name = " ".join(filter(None, parts))

	def set_user(self):
		"""Link to user if exists"""
		if not self.user and self.email:
			user = frappe.db.get_value("User", {"email": self.email})
			if user:
				self.user = user

	def set_profile_image(self):
		"""Set profile image from gravatar if not set"""
		if self.email and not self.profile_image:
			gravatar_url = has_gravatar(self.email)
			if gravatar_url:
				self.profile_image = gravatar_url

	def validate_email_unique(self):
		"""Ensure email is unique"""
		if self.email:
			duplicate = frappe.db.exists(
				"Member Profile", {"email": self.email, "name": ["!=", self.name]}
			)
			if duplicate:
				frappe.throw(_("A member profile with this email already exists"))

	def get_matching_score(self, other_profile):
		"""
		Calculate matching score with another member profile
		Returns a score from 0-100 based on common interests, skills, and goals
		"""
		if not isinstance(other_profile, MemberProfile):
			other_profile = frappe.get_doc("Member Profile", other_profile)

		score = 0
		max_score = 0

		# Check interest overlap (40 points)
		max_score += 40
		my_interests = {row.interest for row in self.interests}
		other_interests = {row.interest for row in other_profile.interests}
		if my_interests and other_interests:
			common_interests = my_interests & other_interests
			score += (len(common_interests) / max(len(my_interests), len(other_interests))) * 40

		# Check skill overlap (30 points)
		max_score += 30
		my_skills = {row.skill for row in self.skills}
		other_skills = {row.skill for row in other_profile.skills}
		if my_skills and other_skills:
			common_skills = my_skills & other_skills
			score += (len(common_skills) / max(len(my_skills), len(other_skills))) * 30

		# Check mentor/mentee compatibility (20 points)
		max_score += 20
		if (self.looking_for_mentor and other_profile.willing_to_mentor) or \
		   (self.willing_to_mentor and other_profile.looking_for_mentor):
			score += 20

		# Check hiring compatibility (10 points)
		max_score += 10
		if (self.seeking_opportunities and other_profile.open_to_hiring) or \
		   (self.open_to_hiring and other_profile.seeking_opportunities):
			score += 10

		return int((score / max_score) * 100) if max_score > 0 else 0

	def find_matches(self, limit=10):
		"""Find matching member profiles based on AI matching algorithm"""
		if not self.ai_matching_enabled:
			return []

		# Get all active members except self
		all_members = frappe.get_all(
			"Member Profile",
			filters={
				"name": ["!=", self.name],
				"status": "Active",
				"available_for_networking": 1,
				"ai_matching_enabled": 1,
			},
			fields=["name"],
		)

		matches = []
		for member in all_members:
			member_doc = frappe.get_doc("Member Profile", member.name)
			score = self.get_matching_score(member_doc)

			if score >= (self.match_score_threshold or 70):
				matches.append({
					"member": member.name,
					"score": score,
					"profile": member_doc,
				})

		# Sort by score descending
		matches.sort(key=lambda x: x["score"], reverse=True)

		# Update last matched timestamp
		self.db_set("last_matched_on", now(), update_modified=False)

		return matches[:limit]


@frappe.whitelist()
def get_member_profile(email=None, user=None):
	"""Get member profile by email or user"""
	filters = {}
	if email:
		filters["email"] = email
	elif user:
		filters["user"] = user
	else:
		frappe.throw(_("Please provide email or user"))

	profile = frappe.db.get_value("Member Profile", filters, "name")
	if profile:
		return frappe.get_doc("Member Profile", profile)
	return None


@frappe.whitelist()
def find_matching_members(member_profile, limit=10):
	"""API endpoint to find matching members"""
	profile = frappe.get_doc("Member Profile", member_profile)
	profile.check_permission("read")

	matches = profile.find_matches(limit=int(limit))

	# Return formatted results
	results = []
	for match in matches:
		results.append({
			"name": match["member"],
			"full_name": match["profile"].full_name,
			"headline": match["profile"].headline,
			"current_position": match["profile"].current_position,
			"current_organization": match["profile"].current_organization,
			"profile_image": match["profile"].profile_image,
			"match_score": match["score"],
			"willing_to_mentor": match["profile"].willing_to_mentor,
			"open_to_hiring": match["profile"].open_to_hiring,
		})

	return results


@frappe.whitelist()
def search_members(query, filters=None):
	"""Search for members by name, skills, or interests"""
	import json

	if filters:
		filters = json.loads(filters) if isinstance(filters, str) else filters
	else:
		filters = {}

	filters.update({"status": "Active"})

	# Search in multiple fields
	or_filters = []
	if query:
		or_filters = [
			["full_name", "like", f"%{query}%"],
			["headline", "like", f"%{query}%"],
			["current_position", "like", f"%{query}%"],
			["current_organization", "like", f"%{query}%"],
			["industry", "like", f"%{query}%"],
		]

	members = frappe.get_all(
		"Member Profile",
		filters=filters,
		or_filters=or_filters if or_filters else None,
		fields=[
			"name",
			"full_name",
			"email",
			"headline",
			"current_position",
			"current_organization",
			"profile_image",
			"willing_to_mentor",
			"looking_for_mentor",
			"open_to_hiring",
			"seeking_opportunities",
		],
		limit=50,
		order_by="modified desc",
	)

	return members
