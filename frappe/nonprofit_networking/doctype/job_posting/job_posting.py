# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, add_days, get_datetime


class JobPosting(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        application_deadline: DF.Date | None
        application_method: DF.Literal["Email", "Website", "LinkedIn", "Other"]
        application_url: DF.Data | None
        benefits: DF.Text | None
        contact_email: DF.Data | None
        currency: DF.Link | None
        description: DF.Text | None
        education_required: DF.Literal["High School", "Associate Degree", "Bachelor's Degree", "Master's Degree", "Doctorate", "No Requirement"]
        employment_type: DF.Literal["Permanent", "Temporary", "Project-based", "Seasonal"]
        experience_level: DF.Literal["Entry Level", "Mid Level", "Senior Level", "Executive Level"]
        featured: DF.Check
        job_type: DF.Literal["Full-time", "Part-time", "Contract", "Internship", "Volunteer", "Freelance"]
        languages_required: DF.SmallText | None
        location: DF.Data | None
        organization: DF.Link
        posted_date: DF.Date | None
        preferred_skills: DF.SmallText | None
        priority: DF.Literal["Low", "Medium", "High", "Urgent"]
        remote_work: DF.Literal["No", "Yes", "Hybrid"]
        requirements: DF.Text | None
        responsibilities: DF.Text | None
        salary_range: DF.Data | None
        status: DF.Literal["Draft", "Open", "Closed", "Filled", "Cancelled"]
        title: DF.Data | None
        total_applications: DF.Int
        view_count: DF.Int
    # end: auto-generated types

    def autoname(self):
        """Set name based on title and organization"""
        if self.title and self.organization:
            org_name = frappe.get_value("Organization", self.organization, "organization_name")
            self.name = f"{self.title}-{org_name}-{now().strftime('%Y%m%d%H%M%S')}"

    def validate(self):
        """Validate job posting data"""
        self.validate_dates()
        self.validate_application_info()
        self.update_statistics()

    def validate_dates(self):
        """Validate posted date and deadline"""
        if self.posted_date and self.application_deadline:
            if self.posted_date > self.application_deadline:
                frappe.throw(_("Application deadline cannot be before posted date"))

    def validate_application_info(self):
        """Validate application information"""
        if self.application_method == "Email" and not self.contact_email:
            frappe.throw(_("Contact email is required when application method is Email"))
        
        if self.application_method == "Website" and not self.application_url:
            frappe.throw(_("Application URL is required when application method is Website"))

    def update_statistics(self):
        """Update job posting statistics"""
        # Count applications
        self.total_applications = frappe.db.count("Job Application", {"job_posting": self.name})
        
        # Count views (this would be updated by a separate view tracking system)
        if not self.view_count:
            self.view_count = 0

    def before_save(self):
        """Run before saving"""
        if not self.posted_date:
            self.posted_date = frappe.utils.today()

    def after_insert(self):
        """Run after inserting"""
        if self.status == "Open":
            self.send_job_notification()

    def publish_job(self):
        """Publish the job posting"""
        self.status = "Open"
        self.posted_date = frappe.utils.today()
        self.save()
        
        # Send notification
        self.send_job_notification()

    def close_job(self, reason=None):
        """Close the job posting"""
        self.status = "Closed"
        if reason:
            self.description = f"{self.description or ''}\n\nClosed: {reason}"
        self.save()

    def fill_job(self):
        """Mark job as filled"""
        self.status = "Filled"
        self.save()

    def send_job_notification(self):
        """Send notification about new job posting"""
        # Get profiles that might be interested
        interested_profiles = self.get_interested_profiles()
        
        for profile in interested_profiles:
            profile_doc = frappe.get_doc("Profile", profile)
            
            frappe.get_doc({
                "doctype": "Notification Log",
                "subject": f"New job posting: {self.title} at {frappe.get_value('Organization', self.organization, 'organization_name')}",
                "email_content": f"A new job posting that matches your profile has been posted: {self.title}",
                "for_user": profile_doc.user,
                "document_type": "Job Posting",
                "document_name": self.name
            }).insert(ignore_permissions=True)

    def get_interested_profiles(self):
        """Get profiles that might be interested in this job"""
        # This would use the AI matching system to find relevant profiles
        # For now, return profiles that are open to jobs
        profiles = frappe.get_all(
            "Profile",
            filters={
                "open_to_jobs": 1,
                "profile_visibility": "Public"
            },
            fields=["name"]
        )
        
        return [profile.name for profile in profiles]

    def increment_view_count(self):
        """Increment view count"""
        self.view_count = (self.view_count or 0) + 1
        self.save(ignore_permissions=True)

    def get_job_summary(self):
        """Get job posting summary"""
        return {
            "job_id": self.name,
            "title": self.title,
            "organization": frappe.get_value("Organization", self.organization, "organization_name"),
            "job_type": self.job_type,
            "location": self.location,
            "remote_work": self.remote_work,
            "posted_date": self.posted_date,
            "application_deadline": self.application_deadline,
            "status": self.status,
            "total_applications": self.total_applications,
            "view_count": self.view_count
        }


@frappe.whitelist()
def search_jobs(filters=None, limit=20):
    """Search job postings with filters"""
    if not filters:
        filters = {}
    
    query_filters = {"status": "Open"}
    
    if filters.get("job_type"):
        query_filters["job_type"] = filters["job_type"]
    
    if filters.get("employment_type"):
        query_filters["employment_type"] = filters["employment_type"]
    
    if filters.get("location"):
        query_filters["location"] = ["like", f"%{filters['location']}%"]
    
    if filters.get("remote_work"):
        query_filters["remote_work"] = filters["remote_work"]
    
    if filters.get("experience_level"):
        query_filters["experience_level"] = filters["experience_level"]
    
    if filters.get("organization"):
        query_filters["organization"] = filters["organization"]
    
    if filters.get("featured"):
        query_filters["featured"] = 1
    
    jobs = frappe.get_all(
        "Job Posting",
        filters=query_filters,
        fields=["name", "title", "organization", "job_type", "location", "remote_work", 
                "posted_date", "application_deadline", "experience_level", "featured"],
        order_by="featured desc, posted_date desc",
        limit=limit
    )
    
    return jobs


@frappe.whitelist()
def get_job_recommendations(profile, limit=10):
    """Get AI-powered job recommendations for a profile"""
    try:
        profile_doc = frappe.get_doc("Profile", profile)
        
        if not profile_doc.open_to_jobs:
            return []
        
        # Get all open jobs
        jobs = frappe.get_all(
            "Job Posting",
            filters={"status": "Open"},
            fields=["name", "title", "organization", "description", "required_skills", 
                   "experience_level", "location", "job_type", "posted_date"]
        )
        
        # Score jobs based on profile match
        scored_jobs = []
        for job in jobs:
            score = calculate_job_match_score(profile_doc, job)
            if score > 50:  # Only include jobs with decent match
                job["match_score"] = score
                scored_jobs.append(job)
        
        # Sort by match score
        scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        
        return scored_jobs[:limit]
        
    except Exception as e:
        frappe.log_error(f"Error getting job recommendations: {str(e)}")
        return []


def calculate_job_match_score(profile, job):
    """Calculate match score between profile and job"""
    score = 0.0
    total_weight = 0.0
    
    # Skills matching (40% weight)
    if profile.skills and job.required_skills:
        skills_score = calculate_skills_job_match(profile.skills, job.required_skills)
        score += skills_score * 0.4
        total_weight += 0.4
    
    # Experience level matching (20% weight)
    if profile.experience_years and job.experience_level:
        experience_score = calculate_experience_match(profile.experience_years, job.experience_level)
        score += experience_score * 0.2
        total_weight += 0.2
    
    # Location matching (15% weight)
    if profile.location and job.location:
        location_score = calculate_location_match(profile.location, job.location)
        score += location_score * 0.15
        total_weight += 0.15
    
    # Industry matching (15% weight)
    if profile.industry and job.organization:
        org_industry = frappe.get_value("Organization", job.organization, "industry")
        if org_industry and profile.industry == org_industry:
            score += 1.0 * 0.15
        total_weight += 0.15
    
    # Job type preference (10% weight)
    # This would be based on profile preferences
    score += 0.5 * 0.1  # Default moderate score
    total_weight += 0.1
    
    # Normalize score
    if total_weight > 0:
        final_score = (score / total_weight) * 100
    else:
        final_score = 0.0
    
    return min(final_score, 100.0)


def calculate_skills_job_match(profile_skills, job_skills):
    """Calculate skills match between profile and job"""
    if not profile_skills or not job_skills:
        return 0.0
    
    profile_skill_names = [skill.skill for skill in profile_skills if skill.skill]
    job_skill_names = [skill.strip() for skill in job_skills.split(",") if skill.strip()]
    
    if not profile_skill_names or not job_skill_names:
        return 0.0
    
    # Calculate Jaccard similarity
    set1 = set(profile_skill_names)
    set2 = set(job_skill_names)
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    if union == 0:
        return 0.0
    
    return intersection / union


def calculate_experience_match(profile_experience, job_level):
    """Calculate experience level match"""
    if not profile_experience or not job_level:
        return 0.0
    
    level_requirements = {
        "Entry Level": (0, 2),
        "Mid Level": (2, 5),
        "Senior Level": (5, 10),
        "Executive Level": (10, 20)
    }
    
    if job_level not in level_requirements:
        return 0.5
    
    min_exp, max_exp = level_requirements[job_level]
    
    if min_exp <= profile_experience <= max_exp:
        return 1.0
    elif profile_experience < min_exp:
        return 0.3  # Underqualified
    else:
        return 0.8  # Overqualified but still good


@frappe.whitelist()
def apply_for_job(job_posting, profile, cover_letter=None, resume=None):
    """Apply for a job"""
    # Check if already applied
    existing = frappe.db.exists("Job Application", {
        "job_posting": job_posting,
        "profile": profile
    })
    
    if existing:
        frappe.throw(_("You have already applied for this job"))
    
    # Create application
    application = frappe.get_doc({
        "doctype": "Job Application",
        "job_posting": job_posting,
        "profile": profile,
        "cover_letter": cover_letter,
        "resume": resume,
        "status": "Applied"
    })
    
    application.insert(ignore_permissions=True)
    
    # Update job statistics
    job_doc = frappe.get_doc("Job Posting", job_posting)
    job_doc.update_statistics()
    job_doc.save(ignore_permissions=True)
    
    return application


@frappe.whitelist()
def get_job_analytics(organization):
    """Get job posting analytics for an organization"""
    try:
        # Get job statistics
        total_jobs = frappe.db.count("Job Posting", {"organization": organization})
        open_jobs = frappe.db.count("Job Posting", {
            "organization": organization,
            "status": "Open"
        })
        filled_jobs = frappe.db.count("Job Posting", {
            "organization": organization,
            "status": "Filled"
        })
        
        # Get total applications
        total_applications = frappe.db.count("Job Application", {
            "job_posting": ["in", frappe.get_all("Job Posting", {"organization": organization}, pluck="name")]
        })
        
        # Get job types breakdown
        job_types = frappe.get_all(
            "Job Posting",
            filters={"organization": organization},
            fields=["job_type"]
        )
        
        type_counts = {}
        for job_type in job_types:
            type_counts[job_type.job_type] = type_counts.get(job_type.job_type, 0) + 1
        
        return {
            "total_jobs": total_jobs,
            "open_jobs": open_jobs,
            "filled_jobs": filled_jobs,
            "total_applications": total_applications,
            "job_types_breakdown": type_counts
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting job analytics: {str(e)}")
        return {}