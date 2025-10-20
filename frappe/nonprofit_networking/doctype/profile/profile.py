# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, cint, cstr
from frappe.contacts.address_and_contact import set_link_title


class Profile(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from nonprofit_networking.doctype.profile_availability.profile_availability import ProfileAvailability
        from nonprofit_networking.doctype.profile_interest.profile_interest import ProfileInterest
        from nonprofit_networking.doctype.profile_language.profile_language import ProfileLanguage
        from nonprofit_networking.doctype.profile_looking_for.profile_looking_for import ProfileLookingFor
        from nonprofit_networking.doctype.profile_skill.profile_skill import ProfileSkill

        allow_direct_messages: DF.Check
        availability_schedule: DF.Table[ProfileAvailability]
        availability_status: DF.Literal["Available", "Busy", "Away", "Do Not Disturb"]
        bio: DF.Text | None
        can_mentor: DF.Check
        current_organization: DF.Link | None
        education_level: DF.Literal["High School", "Associate Degree", "Bachelor's Degree", "Master's Degree", "Doctorate", "Professional Degree", "Other"]
        email: DF.Data | None
        email_verified: DF.Check
        experience_years: DF.Int
        full_name: DF.Data | None
        github_profile: DF.Data | None
        industry: DF.Link | None
        interests: DF.Table[ProfileInterest]
        job_title: DF.Data | None
        languages: DF.Table[ProfileLanguage]
        last_active: DF.Datetime | None
        linkedin_profile: DF.Data | None
        location: DF.Data | None
        looking_for: DF.Table[ProfileLookingFor]
        open_to_jobs: DF.Check
        open_to_projects: DF.Check
        phone: DF.Data | None
        portfolio_website: DF.Data | None
        preferred_contact_method: DF.Literal["Email", "Phone", "LinkedIn", "Twitter", "Other"]
        preferred_meeting_type: DF.Literal["In-Person", "Video Call", "Phone Call", "Any"]
        profile_completed: DF.Check
        profile_image: DF.AttachImage | None
        profile_type: DF.Literal["Individual", "Organization", "Both"]
        profile_visibility: DF.Literal["Public", "Connections Only", "Private"]
        seeking_mentor: DF.Check
        show_contact_info: DF.Check
        show_social_profiles: DF.Check
        skills: DF.Table[ProfileSkill]
        timezone: DF.Data | None
        twitter_profile: DF.Data | None
        user: DF.Link
    # end: auto-generated types

    def autoname(self):
        """Set name based on user email"""
        if self.user:
            user_email = frappe.db.get_value("User", self.user, "email")
            self.name = user_email

    def validate(self):
        """Validate profile data"""
        self.set_user_details()
        self.validate_skills()
        self.validate_interests()
        self.validate_availability()
        self.calculate_profile_completion()
        self.update_last_active()

    def before_save(self):
        """Run before saving"""
        self.set_full_name()

    def set_user_details(self):
        """Set user details from User doctype"""
        if self.user:
            user_doc = frappe.get_doc("User", self.user)
            self.email = user_doc.email
            self.full_name = user_doc.full_name
            self.phone = user_doc.phone
            self.profile_image = user_doc.user_image

    def set_full_name(self):
        """Set full name from user data"""
        if self.user:
            user_doc = frappe.get_doc("User", self.user)
            self.full_name = user_doc.full_name

    def validate_skills(self):
        """Validate skills data"""
        if self.skills:
            skill_names = [skill.skill for skill in self.skills if skill.skill]
            if len(skill_names) != len(set(skill_names)):
                frappe.throw(_("Duplicate skills are not allowed"))

    def validate_interests(self):
        """Validate interests data"""
        if self.interests:
            interest_names = [interest.interest for interest in self.interests if interest.interest]
            if len(interest_names) != len(set(interest_names)):
                frappe.throw(_("Duplicate interests are not allowed"))

    def validate_availability(self):
        """Validate availability schedule"""
        if self.availability_schedule:
            for schedule in self.availability_schedule:
                if schedule.start_time and schedule.end_time:
                    if schedule.start_time >= schedule.end_time:
                        frappe.throw(_("Start time must be before end time for availability schedule"))

    def calculate_profile_completion(self):
        """Calculate profile completion percentage"""
        required_fields = [
            'bio', 'job_title', 'industry', 'skills', 'interests',
            'location', 'preferred_meeting_type'
        ]
        
        completed_fields = 0
        for field in required_fields:
            if self.get(field):
                completed_fields += 1
        
        completion_percentage = (completed_fields / len(required_fields)) * 100
        self.profile_completed = completion_percentage >= 80

    def update_last_active(self):
        """Update last active timestamp"""
        self.last_active = now()

    def get_matching_profiles(self, limit=10):
        """Get profiles that match this profile's interests and skills"""
        if not self.interests or not self.skills:
            return []

        # Get matching interests
        interest_matches = []
        for interest in self.interests:
            interest_matches.extend(
                frappe.get_all(
                    "Profile Interest",
                    filters={"interest": interest.interest, "parent": ("!=", self.name)},
                    fields=["parent"]
                )
            )

        # Get matching skills
        skill_matches = []
        for skill in self.skills:
            skill_matches.extend(
                frappe.get_all(
                    "Profile Skill",
                    filters={"skill": skill.skill, "parent": ("!=", self.name)},
                    fields=["parent"]
                )
            )

        # Combine and rank matches
        all_matches = interest_matches + skill_matches
        match_counts = {}
        for match in all_matches:
            parent = match.parent
            match_counts[parent] = match_counts.get(parent, 0) + 1

        # Sort by match count and return top matches
        sorted_matches = sorted(match_counts.items(), key=lambda x: x[1], reverse=True)
        return [match[0] for match in sorted_matches[:limit]]

    def get_mentorship_opportunities(self):
        """Get mentorship opportunities based on profile"""
        if self.seeking_mentor:
            # Find potential mentors
            mentors = frappe.get_all(
                "Profile",
                filters={
                    "can_mentor": 1,
                    "name": ("!=", self.name),
                    "profile_visibility": "Public"
                },
                fields=["name", "full_name", "bio", "skills", "interests"]
            )
            return mentors
        elif self.can_mentor:
            # Find potential mentees
            mentees = frappe.get_all(
                "Profile",
                filters={
                    "seeking_mentor": 1,
                    "name": ("!=", self.name),
                    "profile_visibility": "Public"
                },
                fields=["name", "full_name", "bio", "skills", "interests"]
            )
            return mentees
        return []

    def get_job_opportunities(self):
        """Get job opportunities based on profile"""
        if not self.open_to_jobs:
            return []

        # Find job postings that match skills and interests
        job_postings = frappe.get_all(
            "Job Posting",
            filters={
                "status": "Open",
                "profile_visibility": "Public"
            },
            fields=["name", "title", "organization", "description", "required_skills"]
        )

        # Filter by matching skills
        matching_jobs = []
        if self.skills:
            profile_skills = [skill.skill for skill in self.skills]
            for job in job_postings:
                if job.required_skills:
                    job_skills = [skill.strip() for skill in job.required_skills.split(",")]
                    if any(skill in profile_skills for skill in job_skills):
                        matching_jobs.append(job)

        return matching_jobs

    def get_networking_stats(self):
        """Get networking statistics for this profile"""
        stats = {
            "total_meetings": frappe.db.count("Meeting", {"profile": self.name}),
            "total_mentorships": frappe.db.count("Mentorship", {"mentor": self.name}) + 
                               frappe.db.count("Mentorship", {"mentee": self.name}),
            "total_connections": frappe.db.count("Profile Connection", {"profile": self.name}),
            "profile_views": frappe.db.get_value("Profile", self.name, "profile_views") or 0
        }
        return stats


@frappe.whitelist()
def get_profile_by_user(user_id):
    """Get profile by user ID"""
    profile = frappe.get_value("Profile", {"user": user_id}, "name")
    if profile:
        return frappe.get_doc("Profile", profile)
    return None


@frappe.whitelist()
def create_profile_from_user(user_id):
    """Create profile from user"""
    if frappe.db.exists("Profile", {"user": user_id}):
        frappe.throw(_("Profile already exists for this user"))
    
    user_doc = frappe.get_doc("User", user_id)
    profile = frappe.get_doc({
        "doctype": "Profile",
        "user": user_id,
        "full_name": user_doc.full_name,
        "email": user_doc.email,
        "phone": user_doc.phone,
        "profile_image": user_doc.user_image
    })
    profile.insert(ignore_permissions=True)
    return profile


@frappe.whitelist()
def search_profiles(filters=None, limit=20):
    """Search profiles with filters"""
    if not filters:
        filters = {}
    
    # Build search query
    query_filters = {"profile_visibility": "Public"}
    
    if filters.get("profile_type"):
        query_filters["profile_type"] = filters["profile_type"]
    
    if filters.get("industry"):
        query_filters["industry"] = filters["industry"]
    
    if filters.get("location"):
        query_filters["location"] = ["like", f"%{filters['location']}%"]
    
    if filters.get("can_mentor"):
        query_filters["can_mentor"] = 1
    
    if filters.get("seeking_mentor"):
        query_filters["seeking_mentor"] = 1
    
    if filters.get("open_to_jobs"):
        query_filters["open_to_jobs"] = 1
    
    profiles = frappe.get_all(
        "Profile",
        filters=query_filters,
        fields=["name", "full_name", "bio", "job_title", "current_organization", 
                "location", "profile_image", "can_mentor", "seeking_mentor", 
                "open_to_jobs", "skills", "interests"],
        limit=limit
    )
    
    return profiles


@frappe.whitelist()
def get_profile_recommendations(profile_name):
    """Get AI-powered profile recommendations"""
    profile = frappe.get_doc("Profile", profile_name)
    return profile.get_matching_profiles()


@frappe.whitelist()
def update_profile_activity(profile_name):
    """Update profile activity timestamp"""
    frappe.db.set_value("Profile", profile_name, "last_active", now())
    frappe.db.commit()