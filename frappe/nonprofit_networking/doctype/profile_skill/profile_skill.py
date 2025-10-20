# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe.model.document import Document


class ProfileSkill(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        is_primary: DF.Check
        proficiency_level: DF.Literal["Beginner", "Intermediate", "Advanced", "Expert"]
        skill: DF.Link
        years_experience: DF.Int
    # end: auto-generated types

    def validate(self):
        """Validate skill data"""
        if self.years_experience and self.years_experience < 0:
            frappe.throw("Years of experience cannot be negative")
        
        if self.proficiency_level == "Expert" and self.years_experience and self.years_experience < 5:
            frappe.msgprint("Expert level typically requires 5+ years of experience")