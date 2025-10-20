# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe.model.document import Document


class NetworkingOrganization(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		active_members: DF.Int
		address_line_1: DF.Data | None
		address_line_2: DF.Data | None
		allow_public_membership: DF.Check
		city: DF.Data | None
		country: DF.Link | None
		description: DF.TextEditor | None
		email: DF.Data | None
		focus_areas: DF.SmallText | None
		founded_date: DF.Date | None
		logo: DF.AttachImage | None
		membership_fee: DF.Currency
		mission_statement: DF.Text | None
		organization_name: DF.Data
		organization_type: DF.Literal["", "Nonprofit", "Charity", "Foundation", "Community Group", "Professional Association", "Educational Institution", "Other"]
		phone: DF.Data | None
		postal_code: DF.Data | None
		requires_approval: DF.Check
		state: DF.Data | None
		status: DF.Literal["Active", "Inactive", "Pending"]
		total_events: DF.Int
		total_members: DF.Int
		website: DF.Data | None
	# end: auto-generated types

	def on_update(self):
		"""Update statistics"""
		self.update_member_count()

	def update_member_count(self):
		"""Update member count"""
		total = frappe.db.count(
			"Member Organization", {"organization": self.name, "parenttype": "Member Profile"}
		)
		active = frappe.db.count(
			"Member Organization",
			{"organization": self.name, "is_current": 1, "parenttype": "Member Profile"},
		)

		if total != self.total_members or active != self.active_members:
			self.db_set("total_members", total, update_modified=False)
			self.db_set("active_members", active, update_modified=False)


@frappe.whitelist()
def get_organization_members(organization):
	"""Get all members of an organization"""
	members = frappe.db.sql(
		"""
		SELECT
			mp.name, mp.full_name, mp.email, mp.current_position,
			mo.role, mo.from_date, mo.to_date, mo.is_current
		FROM
			`tabMember Profile` mp
		INNER JOIN
			`tabMember Organization` mo ON mo.parent = mp.name
		WHERE
			mo.organization = %s
			AND mp.status = 'Active'
		ORDER BY
			mo.is_current DESC, mp.full_name
	""",
		(organization,),
		as_dict=True,
	)

	return members
