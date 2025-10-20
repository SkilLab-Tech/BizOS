# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from frappe.model.document import Document


class Interest(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		category: DF.Literal["", "Technology", "Business", "Arts & Culture", "Science", "Health & Wellness", "Education", "Social Impact", "Environment", "Sports & Recreation", "Other"]
		description: DF.SmallText | None
		interest_name: DF.Data
	# end: auto-generated types

	pass
