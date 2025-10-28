# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe.model.document import Document


class ProfileInterest(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        interest: DF.Link
        interest_level: DF.Literal["Low", "Medium", "High"]
        is_primary: DF.Check
    # end: auto-generated types

    pass