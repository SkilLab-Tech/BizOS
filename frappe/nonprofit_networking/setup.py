# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.utils import cint


def before_install():
    """Run before installing the app"""
    pass


def after_install():
    """Run after installing the app"""
    create_custom_fields()
    create_default_roles()
    create_default_workspace()
    setup_website_theme()


def after_migrate():
    """Run after migrating the app"""
    pass


def create_custom_fields():
    """Create custom fields for User doctype"""
    custom_fields = [
        {
            "dt": "User",
            "fieldname": "profile_type",
            "fieldtype": "Select",
            "label": "Profile Type",
            "options": "Individual\nOrganization\nBoth",
            "default": "Individual",
            "insert_after": "last_name"
        },
        {
            "dt": "User",
            "fieldname": "availability_status",
            "fieldtype": "Select",
            "label": "Availability Status",
            "options": "Available\nBusy\nAway\nDo Not Disturb",
            "default": "Available",
            "insert_after": "profile_type"
        },
        {
            "dt": "User",
            "fieldname": "bio",
            "fieldtype": "Text",
            "label": "Bio",
            "insert_after": "availability_status"
        },
        {
            "dt": "User",
            "fieldname": "linkedin_profile",
            "fieldtype": "Data",
            "label": "LinkedIn Profile",
            "options": "URL",
            "insert_after": "bio"
        },
        {
            "dt": "User",
            "fieldname": "twitter_profile",
            "fieldtype": "Data",
            "label": "Twitter Profile",
            "options": "URL",
            "insert_after": "linkedin_profile"
        },
        {
            "dt": "User",
            "fieldname": "github_profile",
            "fieldtype": "Data",
            "label": "GitHub Profile",
            "options": "URL",
            "insert_after": "twitter_profile"
        },
        {
            "dt": "User",
            "fieldname": "portfolio_website",
            "fieldtype": "Data",
            "label": "Portfolio Website",
            "options": "URL",
            "insert_after": "github_profile"
        }
    ]
    
    for field in custom_fields:
        if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
            frappe.get_doc({
                "doctype": "Custom Field",
                **field
            }).insert(ignore_permissions=True)


def create_default_roles():
    """Create default roles for the networking module"""
    roles = [
        {
            "role_name": "Networking User",
            "desk_access": 1,
            "is_custom": 1,
            "restrict_to_domain": None
        },
        {
            "role_name": "Networking Manager",
            "desk_access": 1,
            "is_custom": 1,
            "restrict_to_domain": None
        },
        {
            "role_name": "Organization Admin",
            "desk_access": 1,
            "is_custom": 1,
            "restrict_to_domain": None
        }
    ]
    
    for role_data in roles:
        if not frappe.db.exists("Role", role_data["role_name"]):
            frappe.get_doc({
                "doctype": "Role",
                **role_data
            }).insert(ignore_permissions=True)


def create_default_workspace():
    """Create default workspace for networking module"""
    if not frappe.db.exists("Workspace", "Nonprofit Networking"):
        workspace = frappe.get_doc({
            "doctype": "Workspace",
            "title": "Nonprofit Networking",
            "module": "Nonprofit Networking",
            "is_default": 0,
            "public": 1,
            "content": """[
                {
                    "type": "card",
                    "label": "My Profile",
                    "link_type": "DocType",
                    "link_to": "Profile",
                    "icon": "fa fa-user",
                    "color": "#1f2937"
                },
                {
                    "type": "card",
                    "label": "Find People",
                    "link_type": "DocType",
                    "link_to": "Profile",
                    "icon": "fa fa-search",
                    "color": "#059669"
                },
                {
                    "type": "card",
                    "label": "My Meetings",
                    "link_type": "DocType",
                    "link_to": "Meeting",
                    "icon": "fa fa-calendar",
                    "color": "#dc2626"
                },
                {
                    "type": "card",
                    "label": "Mentorship",
                    "link_type": "DocType",
                    "link_to": "Mentorship",
                    "icon": "fa fa-graduation-cap",
                    "color": "#7c3aed"
                },
                {
                    "type": "card",
                    "label": "Job Postings",
                    "link_type": "DocType",
                    "link_to": "Job Posting",
                    "icon": "fa fa-briefcase",
                    "color": "#ea580c"
                },
                {
                    "type": "card",
                    "label": "Organizations",
                    "link_type": "DocType",
                    "link_to": "Organization",
                    "icon": "fa fa-building",
                    "color": "#0891b2"
                }
            ]"""
        })
        workspace.insert(ignore_permissions=True)


def setup_website_theme():
    """Setup website theme for networking module"""
    if not frappe.db.exists("Website Theme", "Nonprofit Networking"):
        theme = frappe.get_doc({
            "doctype": "Website Theme",
            "theme": "Nonprofit Networking",
            "module": "Nonprofit Networking",
            "custom": 1,
            "primary_color": "#059669",
            "secondary_color": "#1f2937",
            "accent_color": "#7c3aed"
        })
        theme.insert(ignore_permissions=True)