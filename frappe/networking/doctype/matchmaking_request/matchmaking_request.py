# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now


class MatchmakingRequest(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.networking.doctype.matchmaking_result.matchmaking_result import MatchmakingResult
		from frappe.types import DF

		matching_criteria: DF.SmallText | None
		matches: DF.Table[MatchmakingResult]
		max_matches: DF.Int
		member: DF.Link
		member_name: DF.Data | None
		min_match_score: DF.Int
		notes: DF.Text | None
		preferred_connection_type: DF.Literal["", "Networking", "Mentorship", "Collaboration", "Recruiting", "Alumni", "Partnership"]
		processed_date: DF.Datetime | None
		request_date: DF.Date | None
		status: DF.Literal["Pending", "Processing", "Completed", "Failed"]
		total_matches_found: DF.Int
	# end: auto-generated types

	def after_insert(self):
		"""Process matchmaking after insert"""
		self.process_matchmaking()

	def process_matchmaking(self):
		"""Run AI matchmaking algorithm"""
		try:
			self.status = "Processing"
			self.save(ignore_permissions=True)
			frappe.db.commit()

			# Get member profile
			member_profile = frappe.get_doc("Member Profile", self.member)

			# Find matches
			matches = member_profile.find_matches(limit=self.max_matches or 10)

			# Clear existing matches
			self.matches = []

			# Add new matches
			for match in matches:
				if match["score"] >= (self.min_match_score or 70):
					self.append(
						"matches",
						{
							"matched_member": match["member"],
							"match_score": match["score"],
							"match_reason": self.get_match_reason(member_profile, match["profile"]),
						},
					)

			self.total_matches_found = len(self.matches)
			self.processed_date = now()
			self.status = "Completed"
			self.save(ignore_permissions=True)

			# Send notification
			self.send_completion_notification()

		except Exception as e:
			frappe.log_error(f"Matchmaking failed: {str(e)}", "Matchmaking Error")
			self.status = "Failed"
			self.notes = f"Error: {str(e)}"
			self.save(ignore_permissions=True)

	def get_match_reason(self, member_profile, matched_profile):
		"""Generate explanation for why members match"""
		reasons = []

		# Check interests
		my_interests = {row.interest for row in member_profile.interests}
		their_interests = {row.interest for row in matched_profile.interests}
		common_interests = my_interests & their_interests
		if common_interests:
			reasons.append(f"Common interests: {', '.join(list(common_interests)[:3])}")

		# Check skills
		my_skills = {row.skill for row in member_profile.skills}
		their_skills = {row.skill for row in matched_profile.skills}
		common_skills = my_skills & their_skills
		if common_skills:
			reasons.append(f"Common skills: {', '.join(list(common_skills)[:3])}")

		# Check mentor/mentee
		if member_profile.looking_for_mentor and matched_profile.willing_to_mentor:
			reasons.append("Mentor opportunity")
		if member_profile.willing_to_mentor and matched_profile.looking_for_mentor:
			reasons.append("Mentee opportunity")

		# Check hiring
		if member_profile.seeking_opportunities and matched_profile.open_to_hiring:
			reasons.append("Job opportunity")
		if member_profile.open_to_hiring and matched_profile.seeking_opportunities:
			reasons.append("Candidate available")

		return "; ".join(reasons) if reasons else "General compatibility"

	def send_completion_notification(self):
		"""Send email when matchmaking is complete"""
		member_profile = frappe.get_doc("Member Profile", self.member)

		if member_profile.email_notifications and member_profile.email:
			frappe.sendmail(
				recipients=member_profile.email,
				subject=_("Your Matchmaking Results are Ready"),
				message=_(
					"<p>Hello {0},</p>"
					"<p>Your matchmaking request has been processed.</p>"
					"<p><strong>Total Matches Found:</strong> {1}</p>"
					"<p>Please log in to view your matches and connect with potential networking partners.</p>"
				).format(member_profile.full_name, self.total_matches_found),
				reference_doctype=self.doctype,
				reference_name=self.name,
			)


@frappe.whitelist()
def create_matchmaking_request(member, max_matches=10, min_match_score=70):
	"""API to create a matchmaking request"""
	doc = frappe.get_doc(
		{
			"doctype": "Matchmaking Request",
			"member": member,
			"max_matches": max_matches,
			"min_match_score": min_match_score,
		}
	)
	doc.insert()

	return doc
