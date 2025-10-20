from __future__ import annotations

import frappe
from frappe.model.document import Document


class MemberProfile(Document):
    def validate(self):
        if not self.full_name:
            # derive from user if possible
            if self.user:
                user = frappe.get_doc("User", self.user)
                self.full_name = user.full_name or user.first_name or user.username
        if self.full_name:
            self.full_name = self.full_name.strip()

    def on_update(self):
        # ensure naming follows full_name if autoname uses it
        pass
