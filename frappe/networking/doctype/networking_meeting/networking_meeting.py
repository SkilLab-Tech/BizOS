# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_to_date, get_datetime, now


class NetworkingMeeting(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		agenda: DF.Text | None
		connection: DF.Link | None
		duration_minutes: DF.Int
		follow_up_date: DF.Date | None
		follow_up_required: DF.Check
		meeting_date: DF.Date
		meeting_link: DF.Data | None
		meeting_location: DF.SmallText | None
		meeting_mode: DF.Literal["Virtual", "In-Person", "Phone"]
		meeting_time: DF.Time | None
		notes: DF.TextEditor | None
		outcome: DF.Literal["", "Successful", "Needs Follow-up", "No Show", "Cancelled"]
		participant_1: DF.Link
		participant_1_name: DF.Data | None
		participant_2: DF.Link
		participant_2_name: DF.Data | None
		status: DF.Literal["Scheduled", "Confirmed", "Completed", "Cancelled", "Rescheduled"]
		title: DF.Data
	# end: auto-generated types

	def validate(self):
		"""Validate meeting"""
		self.validate_participants_different()
		self.validate_meeting_datetime()

	def validate_participants_different(self):
		"""Ensure participants are different"""
		if self.participant_1 == self.participant_2:
			frappe.throw(_("Participants must be different members"))

	def validate_meeting_datetime(self):
		"""Validate meeting date is not in the past"""
		if self.meeting_date and self.meeting_time:
			meeting_datetime = get_datetime(f"{self.meeting_date} {self.meeting_time}")
			if meeting_datetime < get_datetime(now()):
				frappe.msgprint(_("Meeting is scheduled in the past"), alert=True)

	def after_insert(self):
		"""Send notifications after meeting creation"""
		self.send_meeting_invitations()
		self.update_connection_stats()

	def on_update(self):
		"""Handle status changes"""
		if self.has_value_changed("status"):
			if self.status == "Completed":
				self.update_connection_stats()
			elif self.status == "Cancelled":
				self.send_cancellation_notification()

	def send_meeting_invitations(self):
		"""Send meeting invitations to participants"""
		participant_1 = frappe.get_doc("Member Profile", self.participant_1)
		participant_2 = frappe.get_doc("Member Profile", self.participant_2)

		# Send to participant 1
		if participant_1.email_notifications and participant_1.email:
			self.send_invitation_email(participant_1, participant_2)

		# Send to participant 2
		if participant_2.email_notifications and participant_2.email:
			self.send_invitation_email(participant_2, participant_1)

	def send_invitation_email(self, recipient, other_participant):
		"""Send invitation email to a participant"""
		meeting_details = f"""
			<p><strong>Title:</strong> {self.title}</p>
			<p><strong>Date:</strong> {self.meeting_date}</p>
			<p><strong>Time:</strong> {self.meeting_time or 'TBD'}</p>
			<p><strong>Duration:</strong> {self.duration_minutes} minutes</p>
			<p><strong>Mode:</strong> {self.meeting_mode}</p>
		"""

		if self.meeting_mode == "Virtual" and self.meeting_link:
			meeting_details += f'<p><strong>Link:</strong> <a href="{self.meeting_link}">{self.meeting_link}</a></p>'
		elif self.meeting_mode == "In-Person" and self.meeting_location:
			meeting_details += f"<p><strong>Location:</strong> {self.meeting_location}</p>"

		if self.agenda:
			meeting_details += f"<p><strong>Agenda:</strong><br>{self.agenda}</p>"

		frappe.sendmail(
			recipients=recipient.email,
			subject=_("Meeting Invitation: {0}").format(self.title),
			message=_(
				"<p>Hello {0},</p>"
				"<p>You have a meeting scheduled with {1}.</p>"
				"{2}"
				"<p>Please confirm your availability.</p>"
			).format(recipient.full_name, other_participant.full_name, meeting_details),
			reference_doctype=self.doctype,
			reference_name=self.name,
		)

	def send_cancellation_notification(self):
		"""Send cancellation notification"""
		participant_1 = frappe.get_doc("Member Profile", self.participant_1)
		participant_2 = frappe.get_doc("Member Profile", self.participant_2)

		for participant in [participant_1, participant_2]:
			if participant.email_notifications and participant.email:
				frappe.sendmail(
					recipients=participant.email,
					subject=_("Meeting Cancelled: {0}").format(self.title),
					message=_(
						"<p>Hello {0},</p>"
						"<p>The meeting '{1}' scheduled for {2} has been cancelled.</p>"
					).format(participant.full_name, self.title, self.meeting_date),
					reference_doctype=self.doctype,
					reference_name=self.name,
				)

	def update_connection_stats(self):
		"""Update connection statistics"""
		if self.connection:
			connection = frappe.get_doc("Networking Connection", self.connection)
			connection.meeting_count = frappe.db.count(
				"Networking Meeting",
				{"connection": self.connection, "status": ["in", ["Completed", "Confirmed"]]},
			)
			connection.last_interaction_date = now()
			connection.save(ignore_permissions=True)


@frappe.whitelist()
def get_upcoming_meetings(member):
	"""Get upcoming meetings for a member"""
	from frappe.utils import today

	meetings = frappe.get_all(
		"Networking Meeting",
		filters=[
			["meeting_date", ">=", today()],
			["status", "in", ["Scheduled", "Confirmed"]],
		],
		or_filters=[{"participant_1": member}, {"participant_2": member}],
		fields=[
			"name",
			"title",
			"meeting_date",
			"meeting_time",
			"meeting_mode",
			"participant_1",
			"participant_1_name",
			"participant_2",
			"participant_2_name",
			"status",
		],
		order_by="meeting_date asc, meeting_time asc",
		limit=20,
	)

	return meetings


@frappe.whitelist()
def confirm_meeting(meeting_name):
	"""Confirm a meeting"""
	doc = frappe.get_doc("Networking Meeting", meeting_name)
	doc.check_permission("write")

	if doc.status == "Scheduled":
		doc.status = "Confirmed"
		doc.save()
		frappe.msgprint(_("Meeting confirmed successfully"))

	return doc
