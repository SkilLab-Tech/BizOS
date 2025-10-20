# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from frappe.model.document import Document


class MemberSkill(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		proficiency_level: DF.Literal["", "Beginner", "Intermediate", "Advanced", "Expert"]
		skill: DF.Link
		years_of_experience: DF.Int
	# end: auto-generated types

	pass
