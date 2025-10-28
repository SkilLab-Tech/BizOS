# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, today


class JobApplication(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        additional_skills: DF.Text | None
        application_date: DF.Date | None
        availability_date: DF.Date | None
        cover_letter: DF.Attach | None
        expected_salary: DF.Data | None
        interview_date: DF.Datetime | None
        interview_notes: DF.Text | None
        interview_scheduled: DF.Check
        job_posting: DF.Link
        motivation: DF.Text | None
        profile: DF.Link
        relevant_experience: DF.Text | None
        resume: DF.Attach | None
        reviewer_notes: DF.Text | None
        status: DF.Literal["Applied", "Under Review", "Shortlisted", "Interviewed", "Rejected", "Accepted", "Withdrawn"]
    # end: auto-generated types

    def autoname(self):
        """Set name based on job posting and profile"""
        if self.job_posting and self.profile:
            self.name = f"{self.job_posting}-{self.profile}-{now().strftime('%Y%m%d%H%M%S')}"

    def validate(self):
        """Validate job application data"""
        self.validate_duplicate_application()
        self.set_defaults()

    def validate_duplicate_application(self):
        """Validate that profile hasn't already applied for this job"""
        if self.job_posting and self.profile:
            existing = frappe.db.exists("Job Application", {
                "job_posting": self.job_posting,
                "profile": self.profile,
                "name": ("!=", self.name)
            })
            
            if existing:
                frappe.throw(_("You have already applied for this job"))

    def set_defaults(self):
        """Set default values"""
        if not self.application_date:
            self.application_date = today()

    def after_insert(self):
        """Run after inserting"""
        self.send_application_notification()

    def send_application_notification(self):
        """Send notification about job application"""
        job_doc = frappe.get_doc("Job Posting", self.job_posting)
        profile_doc = frappe.get_doc("Profile", self.profile)
        
        # Notify the organization
        org_doc = frappe.get_doc("Organization", job_doc.organization)
        
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"New job application for {job_doc.title}",
            "email_content": f"{profile_doc.full_name} has applied for the position of {job_doc.title}.",
            "for_user": org_doc.contact_person,
            "document_type": "Job Application",
            "document_name": self.name
        }).insert(ignore_permissions=True)
        
        # Notify the applicant
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"Application submitted for {job_doc.title}",
            "email_content": f"Your application for {job_doc.title} at {org_doc.organization_name} has been submitted successfully.",
            "for_user": profile_doc.user,
            "document_type": "Job Application",
            "document_name": self.name
        }).insert(ignore_permissions=True)

    def update_status(self, new_status, notes=None):
        """Update application status"""
        self.status = new_status
        if notes:
            self.reviewer_notes = notes
        self.save()
        
        # Send notification
        self.send_status_notification(new_status)

    def send_status_notification(self, status):
        """Send notification about status change"""
        job_doc = frappe.get_doc("Job Posting", self.job_posting)
        profile_doc = frappe.get_doc("Profile", self.profile)
        
        status_messages = {
            "Under Review": "is under review",
            "Shortlisted": "has been shortlisted",
            "Interviewed": "interview has been completed",
            "Rejected": "has been rejected",
            "Accepted": "has been accepted",
            "Withdrawn": "has been withdrawn"
        }
        
        message = status_messages.get(status, status)
        
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"Application status update: {job_doc.title}",
            "email_content": f"Your application for {job_doc.title} {message}.",
            "for_user": profile_doc.user,
            "document_type": "Job Application",
            "document_name": self.name
        }).insert(ignore_permissions=True)

    def schedule_interview(self, interview_date, notes=None):
        """Schedule an interview"""
        self.interview_scheduled = 1
        self.interview_date = interview_date
        if notes:
            self.interview_notes = notes
        self.status = "Shortlisted"
        self.save()
        
        # Send notification
        self.send_interview_notification()

    def send_interview_notification(self):
        """Send interview notification"""
        job_doc = frappe.get_doc("Job Posting", self.job_posting)
        profile_doc = frappe.get_doc("Profile", self.profile)
        
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"Interview scheduled for {job_doc.title}",
            "email_content": f"An interview has been scheduled for your application to {job_doc.title} on {self.interview_date}.",
            "for_user": profile_doc.user,
            "document_type": "Job Application",
            "document_name": self.name
        }).insert(ignore_permissions=True)

    def get_application_summary(self):
        """Get application summary"""
        return {
            "application_id": self.name,
            "job_title": frappe.get_value("Job Posting", self.job_posting, "title"),
            "organization": frappe.get_value("Job Posting", self.job_posting, "organization"),
            "applicant": frappe.get_value("Profile", self.profile, "full_name"),
            "status": self.status,
            "application_date": self.application_date,
            "interview_scheduled": self.interview_scheduled,
            "interview_date": self.interview_date
        }


@frappe.whitelist()
def get_applications_for_job(job_posting, status=None):
    """Get applications for a specific job"""
    filters = {"job_posting": job_posting}
    if status:
        filters["status"] = status
    
    applications = frappe.get_all(
        "Job Application",
        filters=filters,
        fields=["name", "profile", "status", "application_date", "interview_scheduled", "interview_date"],
        order_by="application_date desc"
    )
    
    return applications


@frappe.whitelist()
def get_applications_by_profile(profile, status=None):
    """Get applications by a specific profile"""
    filters = {"profile": profile}
    if status:
        filters["status"] = status
    
    applications = frappe.get_all(
        "Job Application",
        filters=filters,
        fields=["name", "job_posting", "status", "application_date", "interview_scheduled", "interview_date"],
        order_by="application_date desc"
    )
    
    return applications


@frappe.whitelist()
def withdraw_application(application):
    """Withdraw a job application"""
    application_doc = frappe.get_doc("Job Application", application)
    application_doc.status = "Withdrawn"
    application_doc.save()
    
    # Send notification
    application_doc.send_status_notification("Withdrawn")
    
    return application_doc