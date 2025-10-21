from __future__ import annotations

import frappe
from frappe.tests import IntegrationTestCase


class TestNetworking(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        # Create two users and profiles
        self.user_a = frappe.get_all("User", filters={"email": "a@example.com"}, pluck="name", limit=1)
        if self.user_a:
            self.user_a = self.user_a[0]
        else:
            u = frappe.get_doc({
                "doctype": "User",
                "email": "a@example.com",
                "first_name": "Alice",
                "send_welcome_email": 0,
                "user_type": "System User",
            }).insert()
            self.user_a = u.name

        self.user_b = frappe.get_all("User", filters={"email": "b@example.com"}, pluck="name", limit=1)
        if self.user_b:
            self.user_b = self.user_b[0]
        else:
            u = frappe.get_doc({
                "doctype": "User",
                "email": "b@example.com",
                "first_name": "Bob",
                "send_welcome_email": 0,
                "user_type": "System User",
            }).insert()
            self.user_b = u.name

        self.profile_a = frappe.get_doc({
            "doctype": "Member Profile",
            "user": self.user_a,
            "full_name": "Alice",
            "can_mentor": 1,
            "wants_mentor": 0,
            "is_hiring": 0,
            "open_to_work": 0,
            "interests": [{"interest": "ai"}, {"interest": "social impact"}],
            "skills": [{"skill": "python"}, {"skill": "ml"}],
        }).insert()

        self.profile_b = frappe.get_doc({
            "doctype": "Member Profile",
            "user": self.user_b,
            "full_name": "Bob",
            "can_mentor": 0,
            "wants_mentor": 1,
            "is_hiring": 0,
            "open_to_work": 1,
            "interests": [{"interest": "ai"}, {"interest": "education"}],
            "skills": [{"skill": "python"}, {"skill": "data"}],
        }).insert()

    def test_match_generation(self):
        from frappe.networking.matching import generate_matches_for_member

        names = generate_matches_for_member(self.profile_b.name, limit=5)
        self.assertTrue(names, "Should create at least one match")
        match = frappe.get_doc("Match", names[0])
        self.assertIn(match.member_a, {self.profile_a.name, self.profile_b.name})
        self.assertIn(match.member_b, {self.profile_a.name, self.profile_b.name})
        self.assertGreaterEqual(match.score, 0.2)
        self.assertTrue(match.explanation)

    def tearDown(self):
        for dt, name in [
            ("Member Profile", getattr(self.profile_a, "name", None)),
            ("Member Profile", getattr(self.profile_b, "name", None)),
        ]:
            if name and frappe.db.exists(dt, name):
                frappe.delete_doc(dt, name, ignore_permissions=True, force=True)
        for email in ["a@example.com", "b@example.com"]:
            if frappe.db.exists("User", email):
                frappe.delete_doc("User", email, ignore_permissions=True, force=True)
