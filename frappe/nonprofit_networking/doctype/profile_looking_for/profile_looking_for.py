# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe.model.document import Document


class ProfileLookingFor(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        looking_for: DF.Literal["Networking", "Mentorship", "Job Opportunities", "Project Collaborations", "Industry Insights", "Skill Development", "Partnerships", "Investment", "Volunteer Opportunities", "Other"]
        priority: DF.Literal["High", "Medium", "Low"]
    # end: auto-generated types

    pass