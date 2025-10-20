# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from frappe.model.document import Document


class MemberInterest(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		interest: DF.Link
		proficiency_level: DF.Literal["", "Casual", "Interested", "Passionate", "Expert"]
	# end: auto-generated types

	pass
