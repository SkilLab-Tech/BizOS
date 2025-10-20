# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe.model.document import Document


class ProfileAvailability(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        day_of_week: DF.Literal["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        end_time: DF.Time
        is_available: DF.Check
        start_time: DF.Time
    # end: auto-generated types

    def validate(self):
        """Validate availability data"""
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                frappe.throw("Start time must be before end time")