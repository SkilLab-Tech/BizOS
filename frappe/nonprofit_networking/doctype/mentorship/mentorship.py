# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, add_days, get_datetime


class Mentorship(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from nonprofit_networking.doctype.mentorship_milestone.mentorship_milestone import MentorshipMilestone

        achievements: DF.Text | None
        completed_meetings: DF.Int
        current_phase: DF.Literal["Initial", "Planning", "Active Mentoring", "Review", "Completion"]
        description: DF.Text | None
        end_date: DF.Date | None
        expectations: DF.Text | None
        frequency: DF.Literal["Weekly", "Bi-weekly", "Monthly", "Quarterly", "As Needed"]
        goals: DF.Text | None
        meeting_duration: DF.Literal["30 minutes", "45 minutes", "1 hour", "1.5 hours", "2 hours"]
        mentee: DF.Link
        mentee_commitments: DF.Text | None
        mentee_feedback: DF.Text | None
        mentor: DF.Link
        mentor_commitments: DF.Text | None
        mentor_feedback: DF.Text | None
        mentorship_area: DF.Link | None
        mentorship_type: DF.Literal["Career Guidance", "Skill Development", "Leadership Development", "Industry Insights", "Project Guidance", "General Mentoring"]
        milestones: DF.Table[MentorshipMilestone]
        overall_rating: DF.Literal["1", "2", "3", "4", "5"]
        recommendations: DF.Text | None
        start_date: DF.Date | None
        status: DF.Literal["Pending", "Active", "Paused", "Completed", "Cancelled"]
        total_meetings: DF.Int
        upcoming_meetings: DF.Int
    # end: auto-generated types

    def autoname(self):
        """Set name based on mentor, mentee and type"""
        if self.mentor and self.mentee and self.mentorship_type:
            self.name = f"{self.mentor}-{self.mentee}-{self.mentorship_type}-{now().strftime('%Y%m%d%H%M%S')}"

    def validate(self):
        """Validate mentorship data"""
        self.validate_profiles()
        self.validate_dates()
        self.update_meeting_counts()

    def validate_profiles(self):
        """Validate that mentor and mentee are different"""
        if self.mentor == self.mentee:
            frappe.throw(_("Mentor and mentee cannot be the same person"))
        
        # Check if mentor can actually mentor
        mentor_doc = frappe.get_doc("Profile", self.mentor)
        if not mentor_doc.can_mentor:
            frappe.throw(_("Selected mentor is not available for mentoring"))
        
        # Check if mentee is seeking mentorship
        mentee_doc = frappe.get_doc("Profile", self.mentee)
        if not mentee_doc.seeking_mentor:
            frappe.throw(_("Selected mentee is not seeking mentorship"))

    def validate_dates(self):
        """Validate start and end dates"""
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                frappe.throw(_("End date must be after start date"))

    def update_meeting_counts(self):
        """Update meeting counts"""
        # Count total meetings
        self.total_meetings = frappe.db.count("Meeting", {
            "from_profile": self.mentor,
            "to_profile": self.mentee,
            "meeting_purpose": "Mentorship"
        }) + frappe.db.count("Meeting", {
            "from_profile": self.mentee,
            "to_profile": self.mentor,
            "meeting_purpose": "Mentorship"
        })
        
        # Count completed meetings
        self.completed_meetings = frappe.db.count("Meeting", {
            "from_profile": self.mentor,
            "to_profile": self.mentee,
            "meeting_purpose": "Mentorship",
            "status": "Completed"
        }) + frappe.db.count("Meeting", {
            "from_profile": self.mentee,
            "to_profile": self.mentor,
            "meeting_purpose": "Mentorship",
            "status": "Completed"
        })
        
        # Count upcoming meetings
        self.upcoming_meetings = frappe.db.count("Meeting", {
            "from_profile": self.mentor,
            "to_profile": self.mentee,
            "meeting_purpose": "Mentorship",
            "status": "Scheduled"
        }) + frappe.db.count("Meeting", {
            "from_profile": self.mentee,
            "to_profile": self.mentor,
            "meeting_purpose": "Mentorship",
            "status": "Scheduled"
        })

    def before_save(self):
        """Run before saving"""
        if self.status == "Active" and not self.start_date:
            self.start_date = frappe.utils.today()
        
        if self.status == "Completed" and not self.end_date:
            self.end_date = frappe.utils.today()

    def after_insert(self):
        """Run after inserting"""
        self.send_mentorship_notification()

    def send_mentorship_notification(self):
        """Send notification about mentorship"""
        mentor_doc = frappe.get_doc("Profile", self.mentor)
        mentee_doc = frappe.get_doc("Profile", self.mentee)
        
        # Notify mentee
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"Mentorship request from {mentor_doc.full_name}",
            "email_content": f"You have received a mentorship request from {mentor_doc.full_name} for {self.mentorship_type}.",
            "for_user": mentee_doc.user,
            "document_type": "Mentorship",
            "document_name": self.name
        }).insert(ignore_permissions=True)
        
        # Notify mentor
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"Mentorship request sent to {mentee_doc.full_name}",
            "email_content": f"You have sent a mentorship request to {mentee_doc.full_name} for {self.mentorship_type}.",
            "for_user": mentor_doc.user,
            "document_type": "Mentorship",
            "document_name": self.name
        }).insert(ignore_permissions=True)

    def accept_mentorship(self):
        """Accept the mentorship"""
        self.status = "Active"
        self.start_date = frappe.utils.today()
        self.save()
        
        # Send notification
        self.send_mentorship_status_notification("accepted")

    def complete_mentorship(self, achievements=None, mentor_feedback=None, mentee_feedback=None, overall_rating=None):
        """Complete the mentorship"""
        self.status = "Completed"
        self.end_date = frappe.utils.today()
        self.current_phase = "Completion"
        
        if achievements:
            self.achievements = achievements
        if mentor_feedback:
            self.mentor_feedback = mentor_feedback
        if mentee_feedback:
            self.mentee_feedback = mentee_feedback
        if overall_rating:
            self.overall_rating = overall_rating
        
        self.save()
        
        # Send notification
        self.send_mentorship_status_notification("completed")

    def pause_mentorship(self, reason=None):
        """Pause the mentorship"""
        self.status = "Paused"
        if reason:
            self.description = f"{self.description or ''}\n\nPaused: {reason}"
        self.save()
        
        # Send notification
        self.send_mentorship_status_notification("paused")

    def resume_mentorship(self):
        """Resume the mentorship"""
        self.status = "Active"
        self.save()
        
        # Send notification
        self.send_mentorship_status_notification("resumed")

    def cancel_mentorship(self, reason=None):
        """Cancel the mentorship"""
        self.status = "Cancelled"
        if reason:
            self.description = f"{self.description or ''}\n\nCancelled: {reason}"
        self.save()
        
        # Send notification
        self.send_mentorship_status_notification("cancelled")

    def send_mentorship_status_notification(self, action):
        """Send notification about mentorship status change"""
        mentor_doc = frappe.get_doc("Profile", self.mentor)
        mentee_doc = frappe.get_doc("Profile", self.mentee)
        
        action_messages = {
            "accepted": "has been accepted",
            "completed": "has been completed",
            "paused": "has been paused",
            "resumed": "has been resumed",
            "cancelled": "has been cancelled"
        }
        
        message = action_messages.get(action, action)
        
        for profile_doc, other_profile in [(mentor_doc, mentee_doc), (mentee_doc, mentor_doc)]:
            frappe.get_doc({
                "doctype": "Notification Log",
                "subject": f"Mentorship {action} with {other_profile.full_name}",
                "email_content": f"Your mentorship with {other_profile.full_name} {message}.",
                "for_user": profile_doc.user,
                "document_type": "Mentorship",
                "document_name": self.name
            }).insert(ignore_permissions=True)

    def add_milestone(self, title, description, target_date=None, status="Pending"):
        """Add a milestone to the mentorship"""
        milestone = frappe.get_doc({
            "doctype": "Mentorship Milestone",
            "parent": self.name,
            "parenttype": "Mentorship",
            "title": title,
            "description": description,
            "target_date": target_date,
            "status": status
        })
        milestone.insert(ignore_permissions=True)
        return milestone

    def get_mentorship_summary(self):
        """Get mentorship summary"""
        return {
            "mentorship_id": self.name,
            "mentor": frappe.get_value("Profile", self.mentor, "full_name"),
            "mentee": frappe.get_value("Profile", self.mentee, "full_name"),
            "type": self.mentorship_type,
            "status": self.status,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "total_meetings": self.total_meetings,
            "completed_meetings": self.completed_meetings,
            "upcoming_meetings": self.upcoming_meetings,
            "current_phase": self.current_phase,
            "overall_rating": self.overall_rating
        }


@frappe.whitelist()
def create_mentorship_request(mentor, mentee, mentorship_type, description=None, goals=None, expectations=None):
    """Create a mentorship request"""
    # Check if mentorship already exists
    existing = frappe.db.exists("Mentorship", {
        "mentor": mentor,
        "mentee": mentee,
        "status": ["in", ["Pending", "Active"]]
    })
    
    if existing:
        frappe.throw(_("A mentorship relationship already exists between these profiles"))
    
    mentorship = frappe.get_doc({
        "doctype": "Mentorship",
        "mentor": mentor,
        "mentee": mentee,
        "mentorship_type": mentorship_type,
        "description": description,
        "goals": goals,
        "expectations": expectations,
        "status": "Pending"
    })
    
    mentorship.insert(ignore_permissions=True)
    return mentorship


@frappe.whitelist()
def get_mentorship_opportunities(profile):
    """Get mentorship opportunities for a profile"""
    profile_doc = frappe.get_doc("Profile", profile)
    
    if profile_doc.seeking_mentor:
        # Find potential mentors
        mentors = frappe.get_all(
            "Profile",
            filters={
                "can_mentor": 1,
                "name": ("!=", profile),
                "profile_visibility": "Public"
            },
            fields=["name", "full_name", "bio", "job_title", "current_organization", "skills", "interests"]
        )
        return {"type": "mentors", "opportunities": mentors}
    
    elif profile_doc.can_mentor:
        # Find potential mentees
        mentees = frappe.get_all(
            "Profile",
            filters={
                "seeking_mentor": 1,
                "name": ("!=", profile),
                "profile_visibility": "Public"
            },
            fields=["name", "full_name", "bio", "job_title", "current_organization", "skills", "interests"]
        )
        return {"type": "mentees", "opportunities": mentees}
    
    return {"type": "none", "opportunities": []}


@frappe.whitelist()
def get_mentorship_analytics(profile):
    """Get mentorship analytics for a profile"""
    try:
        # Get mentorship statistics
        as_mentor = frappe.db.count("Mentorship", {"mentor": profile})
        as_mentee = frappe.db.count("Mentorship", {"mentee": profile})
        
        active_mentorships = frappe.db.count("Mentorship", {
            "mentor": profile,
            "status": "Active"
        }) + frappe.db.count("Mentorship", {
            "mentee": profile,
            "status": "Active"
        })
        
        completed_mentorships = frappe.db.count("Mentorship", {
            "mentor": profile,
            "status": "Completed"
        }) + frappe.db.count("Mentorship", {
            "mentee": profile,
            "status": "Completed"
        })
        
        # Get average rating as mentor
        mentor_ratings = frappe.get_all(
            "Mentorship",
            filters={
                "mentor": profile,
                "status": "Completed",
                "overall_rating": ("!=", "")
            },
            fields=["overall_rating"]
        )
        
        avg_mentor_rating = 0
        if mentor_ratings:
            avg_mentor_rating = sum(int(r.overall_rating) for r in mentor_ratings) / len(mentor_ratings)
        
        # Get mentorship types breakdown
        types = frappe.get_all(
            "Mentorship",
            filters={
                "mentor": profile,
                "status": "Completed"
            },
            fields=["mentorship_type"]
        ) + frappe.get_all(
            "Mentorship",
            filters={
                "mentee": profile,
                "status": "Completed"
            },
            fields=["mentorship_type"]
        )
        
        type_counts = {}
        for mentorship_type in types:
            type_counts[mentorship_type.mentorship_type] = type_counts.get(mentorship_type.mentorship_type, 0) + 1
        
        return {
            "as_mentor": as_mentor,
            "as_mentee": as_mentee,
            "active_mentorships": active_mentorships,
            "completed_mentorships": completed_mentorships,
            "average_mentor_rating": round(avg_mentor_rating, 1),
            "type_breakdown": type_counts
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting mentorship analytics: {str(e)}")
        return {}