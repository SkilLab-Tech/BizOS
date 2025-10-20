# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from frappe.model.document import Document


class MatchmakingResult(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		connection_sent: DF.Check
		match_reason: DF.SmallText | None
		match_score: DF.Int
		matched_member: DF.Link
		matched_member_name: DF.Data | None
	# end: auto-generated types

	pass
