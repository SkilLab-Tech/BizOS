# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe.model.document import Document


class ProfileLanguage(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        is_primary: DF.Check
        language: DF.Link
        proficiency_level: DF.Literal["Beginner", "Intermediate", "Advanced", "Native"]
    # end: auto-generated types

    pass