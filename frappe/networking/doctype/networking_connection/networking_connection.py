# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, today


class NetworkingConnection(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		accepted_date: DF.Date | None
		connection_note: DF.Text | None
		connection_type: DF.Literal["", "Networking", "Mentorship", "Collaboration", "Recruiting", "Alumni", "Partnership"]
		created_date: DF.Date | None
		from_member: DF.Link
		from_member_name: DF.Data | None
		interaction_count: DF.Int
		last_interaction_date: DF.Datetime | None
		meeting_count: DF.Int
		status: DF.Literal["Pending", "Accepted", "Rejected", "Blocked"]
		tags: DF.SmallText | None
		to_member: DF.Link
		to_member_name: DF.Data | None
	# end: auto-generated types

	def validate(self):
		"""Validate connection request"""
		self.validate_members_different()
		self.validate_duplicate_connection()
		self.update_accepted_date()

	def validate_members_different(self):
		"""Ensure from and to members are different"""
		if self.from_member == self.to_member:
			frappe.throw(_("Cannot create a connection with yourself"))

	def validate_duplicate_connection(self):
		"""Check for duplicate connections"""
		if self.is_new():
			# Check for existing connection in either direction
			exists = frappe.db.exists(
				"Networking Connection",
				{
					"name": ["!=", self.name],
					"status": ["in", ["Pending", "Accepted"]],
				},
				[
					["from_member", "=", self.from_member],
					["to_member", "=", self.to_member],
				],
			) or frappe.db.exists(
				"Networking Connection",
				{
					"name": ["!=", self.name],
					"status": ["in", ["Pending", "Accepted"]],
				},
				[
					["from_member", "=", self.to_member],
					["to_member", "=", self.from_member],
				],
			)

			if exists:
				frappe.throw(_("A connection already exists between these members"))

	def update_accepted_date(self):
		"""Set accepted date when status changes to accepted"""
		if self.status == "Accepted" and not self.accepted_date:
			self.accepted_date = today()

	def after_insert(self):
		"""Send notification after connection request"""
		self.send_connection_notification()

	def on_update(self):
		"""Handle status changes"""
		if self.has_value_changed("status"):
			if self.status == "Accepted":
				self.send_acceptance_notification()
			elif self.status == "Rejected":
				self.send_rejection_notification()

	def send_connection_notification(self):
		"""Send email notification to the recipient"""
		to_member = frappe.get_doc("Member Profile", self.to_member)
		from_member = frappe.get_doc("Member Profile", self.from_member)

		if to_member.email_notifications and to_member.email:
			frappe.sendmail(
				recipients=to_member.email,
				subject=_("New Connection Request from {0}").format(from_member.full_name),
				message=_(
					"<p>Hello {0},</p>"
					"<p>{1} has sent you a connection request.</p>"
					"<p><strong>Connection Type:</strong> {2}</p>"
					"<p><strong>Note:</strong> {3}</p>"
					"<p>Please log in to accept or reject this request.</p>"
				).format(
					to_member.full_name,
					from_member.full_name,
					self.connection_type or "General Networking",
					self.connection_note or "No additional note",
				),
				reference_doctype=self.doctype,
				reference_name=self.name,
			)

	def send_acceptance_notification(self):
		"""Send email notification when connection is accepted"""
		from_member = frappe.get_doc("Member Profile", self.from_member)
		to_member = frappe.get_doc("Member Profile", self.to_member)

		if from_member.email_notifications and from_member.email:
			frappe.sendmail(
				recipients=from_member.email,
				subject=_("{0} Accepted Your Connection Request").format(to_member.full_name),
				message=_(
					"<p>Hello {0},</p>"
					"<p>{1} has accepted your connection request!</p>"
					"<p>You can now start networking and scheduling meetings.</p>"
				).format(from_member.full_name, to_member.full_name),
				reference_doctype=self.doctype,
				reference_name=self.name,
			)

	def send_rejection_notification(self):
		"""Send email notification when connection is rejected"""
		from_member = frappe.get_doc("Member Profile", self.from_member)
		to_member = frappe.get_doc("Member Profile", self.to_member)

		if from_member.email_notifications and from_member.email:
			frappe.sendmail(
				recipients=from_member.email,
				subject=_("Connection Request Update"),
				message=_(
					"<p>Hello {0},</p>"
					"<p>Your connection request to {1} was not accepted at this time.</p>"
					"<p>You may try connecting again in the future.</p>"
				).format(from_member.full_name, to_member.full_name),
				reference_doctype=self.doctype,
				reference_name=self.name,
			)

	def log_interaction(self):
		"""Log an interaction between connected members"""
		if self.status == "Accepted":
			self.interaction_count = (self.interaction_count or 0) + 1
			self.last_interaction_date = now()
			self.save(ignore_permissions=True)


@frappe.whitelist()
def accept_connection(connection_name):
	"""Accept a connection request"""
	doc = frappe.get_doc("Networking Connection", connection_name)
	doc.check_permission("write")

	if doc.status != "Pending":
		frappe.throw(_("Only pending connections can be accepted"))

	doc.status = "Accepted"
	doc.save()

	return doc


@frappe.whitelist()
def reject_connection(connection_name):
	"""Reject a connection request"""
	doc = frappe.get_doc("Networking Connection", connection_name)
	doc.check_permission("write")

	if doc.status != "Pending":
		frappe.throw(_("Only pending connections can be rejected"))

	doc.status = "Rejected"
	doc.save()

	return doc


@frappe.whitelist()
def get_my_connections(member_profile, status=None):
	"""Get all connections for a member"""
	filters = [
		["from_member", "=", member_profile],
		["to_member", "=", member_profile],
	]

	if status:
		filters.append(["status", "=", status])

	connections = frappe.get_all(
		"Networking Connection",
		or_filters=[
			{"from_member": member_profile},
			{"to_member": member_profile},
		],
		filters={"status": status} if status else {},
		fields=[
			"name",
			"from_member",
			"from_member_name",
			"to_member",
			"to_member_name",
			"status",
			"connection_type",
			"created_date",
			"accepted_date",
			"interaction_count",
			"last_interaction_date",
		],
		order_by="modified desc",
	)

	return connections


@frappe.whitelist()
def get_connection_status(from_member, to_member):
	"""Check if a connection exists between two members"""
	connection = frappe.db.get_value(
		"Networking Connection",
		{
			"status": ["in", ["Pending", "Accepted"]],
		},
		["name", "status"],
		as_dict=True,
		or_filters=[
			[
				["from_member", "=", from_member],
				["to_member", "=", to_member],
			],
			[
				["from_member", "=", to_member],
				["to_member", "=", from_member],
			],
		],
	)

	return connection if connection else None
