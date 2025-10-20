# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, add_days, get_datetime
from nonprofit_networking.ai.matchmaking import calculate_match_score


class MeetingRequest(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        additional_notes: DF.Text | None
        confirmed_date: DF.Date | None
        confirmed_location: DF.Data | None
        confirmed_meeting_link: DF.Data | None
        confirmed_time: DF.Time | None
        duration: DF.Literal["15 minutes", "30 minutes", "45 minutes", "1 hour", "1.5 hours", "2 hours"]
        from_profile: DF.Link
        is_ai_suggested: DF.Check
        location: DF.Data | None
        match_score: DF.Percent
        meeting_link: DF.Data | None
        meeting_purpose: DF.Literal["Networking", "Mentorship", "Job Discussion", "Project Collaboration", "General Discussion", "Other"]
        meeting_type: DF.Literal["In-Person", "Video Call", "Phone Call"]
        message: DF.Text | None
        priority: DF.Literal["Low", "Medium", "High"]
        proposed_date: DF.Date | None
        proposed_time: DF.Time | None
        response: DF.Literal["Pending", "Accepted", "Rejected", "Counter Proposal"]
        response_date: DF.Datetime | None
        response_message: DF.Text | None
        status: DF.Literal["Pending", "Accepted", "Rejected", "Cancelled", "Completed"]
        to_profile: DF.Link
    # end: auto-generated types

    def autoname(self):
        """Set name based on profiles and purpose"""
        if self.from_profile and self.to_profile and self.meeting_purpose:
            self.name = f"{self.from_profile}-{self.to_profile}-{self.meeting_purpose}-{now().strftime('%Y%m%d%H%M%S')}"

    def validate(self):
        """Validate meeting request"""
        self.validate_profiles()
        self.validate_dates()
        self.calculate_match_score()
        self.set_defaults()

    def validate_profiles(self):
        """Validate that profiles are different"""
        if self.from_profile == self.to_profile:
            frappe.throw(_("Cannot send meeting request to yourself"))

    def validate_dates(self):
        """Validate proposed date and time"""
        if self.proposed_date and self.proposed_date < frappe.utils.today():
            frappe.throw(_("Proposed date cannot be in the past"))

    def calculate_match_score(self):
        """Calculate AI match score between profiles"""
        if self.from_profile and self.to_profile:
            self.match_score = calculate_match_score(self.from_profile, self.to_profile)

    def set_defaults(self):
        """Set default values"""
        if not self.proposed_date:
            self.proposed_date = add_days(frappe.utils.today(), 7)

    def before_save(self):
        """Run before saving"""
        if self.status == "Accepted" and not self.response_date:
            self.response_date = now()
            self.response = "Accepted"

    def after_insert(self):
        """Run after inserting"""
        self.send_notification()

    def send_notification(self):
        """Send notification to the recipient"""
        to_profile_doc = frappe.get_doc("Profile", self.to_profile)
        from_profile_doc = frappe.get_doc("Profile", self.from_profile)
        
        # Create notification
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"New meeting request from {from_profile_doc.full_name}",
            "email_content": f"You have received a meeting request from {from_profile_doc.full_name} for {self.meeting_purpose}.",
            "for_user": to_profile_doc.user,
            "document_type": "Meeting Request",
            "document_name": self.name
        }).insert(ignore_permissions=True)

    def accept_request(self, response_message=None, confirmed_date=None, confirmed_time=None, confirmed_location=None, confirmed_meeting_link=None):
        """Accept the meeting request"""
        self.status = "Accepted"
        self.response = "Accepted"
        self.response_message = response_message
        self.response_date = now()
        
        if confirmed_date:
            self.confirmed_date = confirmed_date
        if confirmed_time:
            self.confirmed_time = confirmed_time
        if confirmed_location:
            self.confirmed_location = confirmed_location
        if confirmed_meeting_link:
            self.confirmed_meeting_link = confirmed_meeting_link
        
        self.save()
        
        # Create meeting record
        self.create_meeting()
        
        # Send notification to requester
        self.send_acceptance_notification()

    def reject_request(self, response_message=None):
        """Reject the meeting request"""
        self.status = "Rejected"
        self.response = "Rejected"
        self.response_message = response_message
        self.response_date = now()
        self.save()
        
        # Send notification to requester
        self.send_rejection_notification()

    def create_meeting(self):
        """Create meeting record from accepted request"""
        meeting = frappe.get_doc({
            "doctype": "Meeting",
            "from_profile": self.from_profile,
            "to_profile": self.to_profile,
            "meeting_purpose": self.meeting_purpose,
            "meeting_type": self.meeting_type,
            "scheduled_date": self.confirmed_date or self.proposed_date,
            "scheduled_time": self.confirmed_time or self.proposed_time,
            "duration": self.duration,
            "location": self.confirmed_location or self.location,
            "meeting_link": self.confirmed_meeting_link or self.meeting_link,
            "status": "Scheduled",
            "meeting_request": self.name
        })
        meeting.insert(ignore_permissions=True)
        return meeting

    def send_acceptance_notification(self):
        """Send acceptance notification to requester"""
        from_profile_doc = frappe.get_doc("Profile", self.from_profile)
        to_profile_doc = frappe.get_doc("Profile", self.to_profile)
        
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"Meeting request accepted by {to_profile_doc.full_name}",
            "email_content": f"Your meeting request with {to_profile_doc.full_name} has been accepted.",
            "for_user": from_profile_doc.user,
            "document_type": "Meeting Request",
            "document_name": self.name
        }).insert(ignore_permissions=True)

    def send_rejection_notification(self):
        """Send rejection notification to requester"""
        from_profile_doc = frappe.get_doc("Profile", self.from_profile)
        to_profile_doc = frappe.get_doc("Profile", self.to_profile)
        
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"Meeting request declined by {to_profile_doc.full_name}",
            "email_content": f"Your meeting request with {to_profile_doc.full_name} has been declined.",
            "for_user": from_profile_doc.user,
            "document_type": "Meeting Request",
            "document_name": self.name
        }).insert(ignore_permissions=True)


@frappe.whitelist()
def send_meeting_request(from_profile, to_profile, meeting_purpose, message, meeting_type="Video Call", proposed_date=None, proposed_time=None, duration="30 minutes"):
    """Send a meeting request"""
    # Check if there's already a pending request
    existing_request = frappe.db.exists("Meeting Request", {
        "from_profile": from_profile,
        "to_profile": to_profile,
        "status": "Pending"
    })
    
    if existing_request:
        frappe.throw(_("There is already a pending meeting request between these profiles"))
    
    meeting_request = frappe.get_doc({
        "doctype": "Meeting Request",
        "from_profile": from_profile,
        "to_profile": to_profile,
        "meeting_purpose": meeting_purpose,
        "message": message,
        "meeting_type": meeting_type,
        "proposed_date": proposed_date,
        "proposed_time": proposed_time,
        "duration": duration
    })
    
    meeting_request.insert(ignore_permissions=True)
    return meeting_request


@frappe.whitelist()
def respond_to_meeting_request(meeting_request, response, response_message=None, confirmed_date=None, confirmed_time=None, confirmed_location=None, confirmed_meeting_link=None):
    """Respond to a meeting request"""
    meeting_request_doc = frappe.get_doc("Meeting Request", meeting_request)
    
    if response == "Accepted":
        meeting_request_doc.accept_request(response_message, confirmed_date, confirmed_time, confirmed_location, confirmed_meeting_link)
    elif response == "Rejected":
        meeting_request_doc.reject_request(response_message)
    else:
        frappe.throw(_("Invalid response type"))
    
    return meeting_request_doc


@frappe.whitelist()
def get_ai_suggested_meetings(profile, limit=5):
    """Get AI-suggested meeting requests"""
    from nonprofit_networking.ai.matchmaking import get_ai_suggestions
    
    suggestions = get_ai_suggestions(profile, limit)
    
    # Create meeting requests for suggestions
    meeting_requests = []
    for suggestion in suggestions:
        meeting_request = frappe.get_doc({
            "doctype": "Meeting Request",
            "from_profile": profile,
            "to_profile": suggestion["profile"],
            "meeting_purpose": suggestion["purpose"],
            "message": suggestion["message"],
            "meeting_type": suggestion["meeting_type"],
            "is_ai_suggested": 1,
            "match_score": suggestion["match_score"],
            "status": "Draft"
        })
        meeting_requests.append(meeting_request)
    
    return meeting_requests