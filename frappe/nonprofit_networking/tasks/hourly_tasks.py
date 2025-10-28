# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.utils import now, add_hours


def process_pending_meeting_requests():
    """Process pending meeting requests and send follow-up notifications"""
    try:
        # Get meeting requests that are pending for more than 24 hours
        from frappe.utils import add_days
        cutoff_time = add_days(now(), -1)
        
        pending_requests = frappe.get_all(
            "Meeting Request",
            filters={
                "status": "Pending",
                "creation": ("<", cutoff_time)
            },
            fields=["name", "from_profile", "to_profile", "meeting_purpose"]
        )
        
        for request in pending_requests:
            # Send follow-up notification to recipient
            to_profile_doc = frappe.get_doc("Profile", request["to_profile"])
            from_profile_doc = frappe.get_doc("Profile", request["from_profile"])
            
            frappe.get_doc({
                "doctype": "Notification Log",
                "subject": f"Reminder: Meeting request from {from_profile_doc.full_name}",
                "email_content": f"You have a pending meeting request from {from_profile_doc.full_name} for {request['meeting_purpose']}. Please respond soon.",
                "for_user": to_profile_doc.user,
                "document_type": "Meeting Request",
                "document_name": request["name"]
            }).insert(ignore_permissions=True)
        
        frappe.log_error(f"Processed {len(pending_requests)} pending meeting requests")
        
    except Exception as e:
        frappe.log_error(f"Error processing pending meeting requests: {str(e)}")