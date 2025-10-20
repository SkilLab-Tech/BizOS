# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today


class MentorshipMilestone(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        completion_date: DF.Date | None
        description: DF.Text | None
        notes: DF.Text | None
        status: DF.Literal["Pending", "In Progress", "Completed", "Cancelled"]
        target_date: DF.Date | None
        title: DF.Data | None
    # end: auto-generated types

    def validate(self):
        """Validate milestone data"""
        if self.status == "Completed" and not self.completion_date:
            self.completion_date = today()
        
        if self.target_date and self.completion_date:
            if self.completion_date < self.target_date:
                frappe.msgprint(_("Completion date is before target date"))