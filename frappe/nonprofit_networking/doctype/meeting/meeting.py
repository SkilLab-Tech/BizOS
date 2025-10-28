# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, add_days, get_datetime


class Meeting(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        agenda: DF.Text | None
        duration: DF.Literal["15 minutes", "30 minutes", "45 minutes", "1 hour", "1.5 hours", "2 hours"]
        feedback_notes: DF.Text | None
        follow_up_notes: DF.Text | None
        follow_up_required: DF.Check
        from_profile: DF.Link
        location: DF.Data | None
        meeting_documents: DF.Attach | None
        meeting_link: DF.Data | None
        meeting_purpose: DF.Literal["Networking", "Mentorship", "Job Discussion", "Project Collaboration", "General Discussion", "Other"]
        meeting_recording: DF.Attach | None
        meeting_request: DF.Link | None
        notes: DF.Text | None
        outcomes: DF.Text | None
        rating: DF.Literal["1", "2", "3", "4", "5"]
        scheduled_date: DF.Date
        scheduled_time: DF.Time
        status: DF.Literal["Scheduled", "In Progress", "Completed", "Cancelled", "No Show"]
        to_profile: DF.Link
    # end: auto-generated types

    def autoname(self):
        """Set name based on profiles and date"""
        if self.from_profile and self.to_profile and self.scheduled_date:
            date_str = self.scheduled_date.strftime('%Y%m%d')
            self.name = f"{self.from_profile}-{self.to_profile}-{date_str}-{now().strftime('%H%M%S')}"

    def validate(self):
        """Validate meeting data"""
        self.validate_profiles()
        self.validate_schedule()
        self.set_defaults()

    def validate_profiles(self):
        """Validate that profiles are different"""
        if self.from_profile == self.to_profile:
            frappe.throw(_("Cannot schedule meeting with yourself"))

    def validate_schedule(self):
        """Validate meeting schedule"""
        if self.scheduled_date and self.scheduled_date < frappe.utils.today():
            frappe.throw(_("Meeting date cannot be in the past"))

    def set_defaults(self):
        """Set default values"""
        if not self.status:
            self.status = "Scheduled"

    def before_save(self):
        """Run before saving"""
        if self.status == "Completed" and not self.rating:
            frappe.msgprint(_("Please provide a rating for the completed meeting"))

    def after_insert(self):
        """Run after inserting"""
        self.send_meeting_notification()

    def send_meeting_notification(self):
        """Send notification about the meeting"""
        to_profile_doc = frappe.get_doc("Profile", self.to_profile)
        from_profile_doc = frappe.get_doc("Profile", self.from_profile)
        
        # Create notification for both participants
        for profile_doc, other_profile in [(to_profile_doc, from_profile_doc), (from_profile_doc, to_profile_doc)]:
            frappe.get_doc({
                "doctype": "Notification Log",
                "subject": f"Meeting scheduled with {other_profile.full_name}",
                "email_content": f"You have a meeting scheduled with {other_profile.full_name} on {self.scheduled_date} at {self.scheduled_time}.",
                "for_user": profile_doc.user,
                "document_type": "Meeting",
                "document_name": self.name
            }).insert(ignore_permissions=True)

    def start_meeting(self):
        """Start the meeting"""
        self.status = "In Progress"
        self.save()
        
        # Send notification
        self.send_meeting_status_notification("started")

    def complete_meeting(self, notes=None, outcomes=None, rating=None, feedback_notes=None):
        """Complete the meeting"""
        self.status = "Completed"
        if notes:
            self.notes = notes
        if outcomes:
            self.outcomes = outcomes
        if rating:
            self.rating = rating
        if feedback_notes:
            self.feedback_notes = feedback_notes
        
        self.save()
        
        # Send notification
        self.send_meeting_status_notification("completed")
        
        # Create follow-up tasks if needed
        if self.follow_up_required:
            self.create_follow_up_tasks()

    def cancel_meeting(self, reason=None):
        """Cancel the meeting"""
        self.status = "Cancelled"
        if reason:
            self.notes = f"Cancellation reason: {reason}"
        self.save()
        
        # Send notification
        self.send_meeting_status_notification("cancelled")

    def send_meeting_status_notification(self, action):
        """Send notification about meeting status change"""
        to_profile_doc = frappe.get_doc("Profile", self.to_profile)
        from_profile_doc = frappe.get_doc("Profile", self.from_profile)
        
        action_messages = {
            "started": "has started",
            "completed": "has been completed",
            "cancelled": "has been cancelled"
        }
        
        message = action_messages.get(action, action)
        
        for profile_doc, other_profile in [(to_profile_doc, from_profile_doc), (from_profile_doc, to_profile_doc)]:
            frappe.get_doc({
                "doctype": "Notification Log",
                "subject": f"Meeting {action} with {other_profile.full_name}",
                "email_content": f"Your meeting with {other_profile.full_name} {message}.",
                "for_user": profile_doc.user,
                "document_type": "Meeting",
                "document_name": self.name
            }).insert(ignore_permissions=True)

    def create_follow_up_tasks(self):
        """Create follow-up tasks if required"""
        if not self.follow_up_notes:
            return
        
        # Create task for both participants
        for profile in [self.from_profile, self.to_profile]:
            profile_doc = frappe.get_doc("Profile", profile)
            
            frappe.get_doc({
                "doctype": "Task",
                "subject": f"Follow-up from meeting with {self.get_other_profile(profile)}",
                "description": self.follow_up_notes,
                "assigned_to": profile_doc.user,
                "priority": "Medium",
                "status": "Open"
            }).insert(ignore_permissions=True)

    def get_other_profile(self, current_profile):
        """Get the other profile in the meeting"""
        if current_profile == self.from_profile:
            return frappe.get_value("Profile", self.to_profile, "full_name")
        else:
            return frappe.get_value("Profile", self.from_profile, "full_name")

    def get_meeting_summary(self):
        """Get meeting summary"""
        return {
            "meeting_id": self.name,
            "participants": [
                frappe.get_value("Profile", self.from_profile, "full_name"),
                frappe.get_value("Profile", self.to_profile, "full_name")
            ],
            "purpose": self.meeting_purpose,
            "type": self.meeting_type,
            "scheduled_date": self.scheduled_date,
            "scheduled_time": self.scheduled_time,
            "duration": self.duration,
            "status": self.status,
            "location": self.location,
            "meeting_link": self.meeting_link,
            "rating": self.rating,
            "outcomes": self.outcomes
        }


@frappe.whitelist()
def get_upcoming_meetings(profile, limit=10):
    """Get upcoming meetings for a profile"""
    meetings = frappe.get_all(
        "Meeting",
        filters={
            "status": "Scheduled",
            "scheduled_date": [">=", frappe.utils.today()],
            "from_profile": profile
        },
        fields=["name", "to_profile", "meeting_purpose", "scheduled_date", "scheduled_time", "meeting_type", "location"],
        order_by="scheduled_date, scheduled_time",
        limit=limit
    )
    
    # Also get meetings where profile is the recipient
    meetings.extend(frappe.get_all(
        "Meeting",
        filters={
            "status": "Scheduled",
            "scheduled_date": [">=", frappe.utils.today()],
            "to_profile": profile
        },
        fields=["name", "from_profile as to_profile", "meeting_purpose", "scheduled_date", "scheduled_time", "meeting_type", "location"],
        order_by="scheduled_date, scheduled_time",
        limit=limit
    ))
    
    # Sort by date and time
    meetings.sort(key=lambda x: (x.scheduled_date, x.scheduled_time))
    
    return meetings[:limit]


@frappe.whitelist()
def get_meeting_history(profile, limit=20):
    """Get meeting history for a profile"""
    meetings = frappe.get_all(
        "Meeting",
        filters={
            "status": "Completed",
            "from_profile": profile
        },
        fields=["name", "to_profile", "meeting_purpose", "scheduled_date", "rating", "outcomes"],
        order_by="scheduled_date desc",
        limit=limit
    )
    
    # Also get meetings where profile is the recipient
    meetings.extend(frappe.get_all(
        "Meeting",
        filters={
            "status": "Completed",
            "to_profile": profile
        },
        fields=["name", "from_profile as to_profile", "meeting_purpose", "scheduled_date", "rating", "outcomes"],
        order_by="scheduled_date desc",
        limit=limit
    ))
    
    # Sort by date
    meetings.sort(key=lambda x: x.scheduled_date, reverse=True)
    
    return meetings[:limit]


@frappe.whitelist()
def reschedule_meeting(meeting, new_date, new_time, reason=None):
    """Reschedule a meeting"""
    meeting_doc = frappe.get_doc("Meeting", meeting)
    
    if meeting_doc.status != "Scheduled":
        frappe.throw(_("Only scheduled meetings can be rescheduled"))
    
    old_date = meeting_doc.scheduled_date
    old_time = meeting_doc.scheduled_time
    
    meeting_doc.scheduled_date = new_date
    meeting_doc.scheduled_time = new_time
    
    if reason:
        meeting_doc.notes = f"Rescheduled from {old_date} {old_time}. Reason: {reason}"
    
    meeting_doc.save()
    
    # Send notification
    meeting_doc.send_meeting_status_notification("rescheduled")
    
    return meeting_doc


@frappe.whitelist()
def get_meeting_analytics(profile):
    """Get meeting analytics for a profile"""
    try:
        # Get meeting statistics
        total_meetings = frappe.db.count("Meeting", {
            "from_profile": profile
        }) + frappe.db.count("Meeting", {
            "to_profile": profile
        })
        
        completed_meetings = frappe.db.count("Meeting", {
            "from_profile": profile,
            "status": "Completed"
        }) + frappe.db.count("Meeting", {
            "to_profile": profile,
            "status": "Completed"
        })
        
        cancelled_meetings = frappe.db.count("Meeting", {
            "from_profile": profile,
            "status": "Cancelled"
        }) + frappe.db.count("Meeting", {
            "to_profile": profile,
            "status": "Cancelled"
        })
        
        # Get average rating
        ratings = frappe.get_all(
            "Meeting",
            filters={
                "from_profile": profile,
                "status": "Completed",
                "rating": ("!=", "")
            },
            fields=["rating"]
        ) + frappe.get_all(
            "Meeting",
            filters={
                "to_profile": profile,
                "status": "Completed",
                "rating": ("!=", "")
            },
            fields=["rating"]
        )
        
        avg_rating = 0
        if ratings:
            avg_rating = sum(int(r.rating) for r in ratings) / len(ratings)
        
        # Get meeting purposes breakdown
        purposes = frappe.get_all(
            "Meeting",
            filters={
                "from_profile": profile,
                "status": "Completed"
            },
            fields=["meeting_purpose"]
        ) + frappe.get_all(
            "Meeting",
            filters={
                "to_profile": profile,
                "status": "Completed"
            },
            fields=["meeting_purpose"]
        )
        
        purpose_counts = {}
        for purpose in purposes:
            purpose_counts[purpose.meeting_purpose] = purpose_counts.get(purpose.meeting_purpose, 0) + 1
        
        return {
            "total_meetings": total_meetings,
            "completed_meetings": completed_meetings,
            "cancelled_meetings": cancelled_meetings,
            "completion_rate": (completed_meetings / total_meetings * 100) if total_meetings > 0 else 0,
            "average_rating": round(avg_rating, 1),
            "purpose_breakdown": purpose_counts
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting meeting analytics: {str(e)}")
        return {}