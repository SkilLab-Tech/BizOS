# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.utils import now, add_days, today
from nonprofit_networking.ai.matchmaking import run_daily_matchmaking


def run_daily_matchmaking():
    """Run daily AI matchmaking for all active profiles"""
    try:
        run_daily_matchmaking()
        frappe.log_error("Daily matchmaking completed successfully")
    except Exception as e:
        frappe.log_error(f"Error in daily matchmaking: {str(e)}")


def send_meeting_reminders():
    """Send meeting reminders for upcoming meetings"""
    try:
        # Get meetings scheduled for tomorrow
        tomorrow = add_days(today(), 1)
        
        meetings = frappe.get_all(
            "Meeting",
            filters={
                "scheduled_date": tomorrow,
                "status": "Scheduled"
            },
            fields=["name", "from_profile", "to_profile", "scheduled_time", "meeting_purpose"]
        )
        
        for meeting in meetings:
            # Send reminder to both participants
            for profile_field in ["from_profile", "to_profile"]:
                profile = meeting[profile_field]
                other_profile = meeting["from_profile"] if profile_field == "to_profile" else meeting["to_profile"]
                
                profile_doc = frappe.get_doc("Profile", profile)
                other_profile_doc = frappe.get_doc("Profile", other_profile)
                
                frappe.get_doc({
                    "doctype": "Notification Log",
                    "subject": f"Meeting reminder: {meeting['meeting_purpose']} with {other_profile_doc.full_name}",
                    "email_content": f"You have a meeting scheduled tomorrow at {meeting['scheduled_time']} with {other_profile_doc.full_name}.",
                    "for_user": profile_doc.user,
                    "document_type": "Meeting",
                    "document_name": meeting["name"]
                }).insert(ignore_permissions=True)
        
        frappe.log_error(f"Sent {len(meetings)} meeting reminders")
        
    except Exception as e:
        frappe.log_error(f"Error sending meeting reminders: {str(e)}")