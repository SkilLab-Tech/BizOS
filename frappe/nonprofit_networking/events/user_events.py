# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _


def after_user_insert(doc, method):
    """Run after user is inserted"""
    # Create profile for new user
    create_profile_for_user(doc)


def on_user_update(doc, method):
    """Run when user is updated"""
    # Update corresponding profile
    update_profile_for_user(doc)


def create_profile_for_user(user_doc):
    """Create profile for new user"""
    try:
        # Check if profile already exists
        if frappe.db.exists("Profile", {"user": user_doc.name}):
            return
        
        # Create profile
        profile = frappe.get_doc({
            "doctype": "Profile",
            "user": user_doc.name,
            "full_name": user_doc.full_name,
            "email": user_doc.email,
            "phone": user_doc.phone,
            "profile_image": user_doc.user_image,
            "profile_type": "Individual",
            "availability_status": "Available"
        })
        
        profile.insert(ignore_permissions=True)
        
    except Exception as e:
        frappe.log_error(f"Error creating profile for user {user_doc.name}: {str(e)}")


def update_profile_for_user(user_doc):
    """Update profile when user is updated"""
    try:
        profile = frappe.get_doc("Profile", {"user": user_doc.name})
        
        # Update profile fields
        profile.full_name = user_doc.full_name
        profile.email = user_doc.email
        profile.phone = user_doc.phone
        profile.profile_image = user_doc.user_image
        
        profile.save(ignore_permissions=True)
        
    except Exception as e:
        frappe.log_error(f"Error updating profile for user {user_doc.name}: {str(e)}")