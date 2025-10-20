# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from frappe.model.document import Document


class Skill(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		category: DF.Literal["", "Technical", "Management", "Communication", "Design", "Marketing", "Finance", "Operations", "Sales", "Leadership", "Other"]
		description: DF.SmallText | None
		skill_name: DF.Data
	# end: auto-generated types

	pass
