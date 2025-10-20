# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe.model.document import Document


class AlumniGroup(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		active_members: DF.Int
		allow_guest_access: DF.Check
		description: DF.TextEditor | None
		email: DF.Data | None
		established_date: DF.Date | None
		graduation_year: DF.Int
		group_logo: DF.AttachImage | None
		group_name: DF.Data
		group_type: DF.Literal["", "Alumni", "Graduation Year", "Program", "Location-based", "Interest-based", "Professional", "Other"]
		is_public: DF.Check
		location: DF.Data | None
		organization: DF.Link | None
		program_name: DF.Data | None
		requires_approval: DF.Check
		status: DF.Literal["Active", "Inactive"]
		total_members: DF.Int
		website: DF.Data | None
	# end: auto-generated types

	def on_update(self):
		"""Update statistics"""
		self.update_member_count()

	def update_member_count(self):
		"""Update member count"""
		total = frappe.db.count(
			"Member Alumni Group", {"alumni_group": self.name, "parenttype": "Member Profile"}
		)
		active = frappe.db.count(
			"Member Alumni Group",
			{"alumni_group": self.name, "status": "Active", "parenttype": "Member Profile"},
		)

		if total != self.total_members or active != self.active_members:
			self.db_set("total_members", total, update_modified=False)
			self.db_set("active_members", active, update_modified=False)


@frappe.whitelist()
def get_alumni_group_members(alumni_group):
	"""Get all members of an alumni group"""
	members = frappe.db.sql(
		"""
		SELECT
			mp.name, mp.full_name, mp.email, mp.current_position,
			mp.current_organization, mag.join_date, mag.status
		FROM
			`tabMember Profile` mp
		INNER JOIN
			`tabMember Alumni Group` mag ON mag.parent = mp.name
		WHERE
			mag.alumni_group = %s
			AND mp.status = 'Active'
		ORDER BY
			mag.join_date DESC, mp.full_name
	""",
		(alumni_group,),
		as_dict=True,
	)

	return members
