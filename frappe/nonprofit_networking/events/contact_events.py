# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _


def after_contact_insert(doc, method):
    """Run after contact is inserted"""
    # Create profile if contact has user
    if doc.user:
        create_profile_for_contact(doc)


def on_contact_update(doc, method):
    """Run when contact is updated"""
    # Update profile if contact has user
    if doc.user:
        update_profile_for_contact(doc)


def create_profile_for_contact(contact_doc):
    """Create profile for contact with user"""
    try:
        # Check if profile already exists
        if frappe.db.exists("Profile", {"user": contact_doc.user}):
            return
        
        # Create profile
        profile = frappe.get_doc({
            "doctype": "Profile",
            "user": contact_doc.user,
            "full_name": contact_doc.full_name,
            "email": contact_doc.email_id,
            "phone": contact_doc.phone,
            "profile_image": contact_doc.image,
            "profile_type": "Individual",
            "availability_status": "Available"
        })
        
        profile.insert(ignore_permissions=True)
        
    except Exception as e:
        frappe.log_error(f"Error creating profile for contact {contact_doc.name}: {str(e)}")


def update_profile_for_contact(contact_doc):
    """Update profile when contact is updated"""
    try:
        profile = frappe.get_doc("Profile", {"user": contact_doc.user})
        
        # Update profile fields
        profile.full_name = contact_doc.full_name
        profile.email = contact_doc.email_id
        profile.phone = contact_doc.phone
        profile.profile_image = contact_doc.image
        
        profile.save(ignore_permissions=True)
        
    except Exception as e:
        frappe.log_error(f"Error updating profile for contact {contact_doc.name}: {str(e)}")