# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now


class Organization(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        active_members: DF.Int
        address: DF.Text | None
        allow_member_registration: DF.Check
        city: DF.Data | None
        contact_email: DF.Data | None
        contact_person: DF.Data | None
        contact_phone: DF.Data | None
        country: DF.Link | None
        description: DF.Text | None
        email: DF.Data | None
        facebook_profile: DF.Data | None
        founded_year: DF.Int
        industry: DF.Link | None
        instagram_profile: DF.Data | None
        is_verified: DF.Check
        linkedin_profile: DF.Data | None
        logo: DF.AttachImage | None
        mission_statement: DF.Text | None
        organization_name: DF.Data | None
        organization_size: DF.Literal["1-10", "11-50", "51-200", "201-500", "501-1000", "1000+"]
        organization_type: DF.Literal["Nonprofit", "For-Profit", "Government", "Educational Institution", "Community Organization", "Other"]
        phone: DF.Data | None
        postal_code: DF.Data | None
        public_profile: DF.Check
        require_approval: DF.Check
        state: DF.Data | None
        total_events: DF.Int
        total_members: DF.Int
        total_projects: DF.Int
        twitter_profile: DF.Data | None
        verification_date: DF.Date | None
        verification_documents: DF.Attach | None
        website: DF.Data | None
    # end: auto-generated types

    def autoname(self):
        """Set name based on organization name"""
        if self.organization_name:
            self.name = self.organization_name

    def validate(self):
        """Validate organization data"""
        self.validate_contact_info()
        self.validate_website_urls()
        self.update_statistics()

    def validate_contact_info(self):
        """Validate contact information"""
        if self.email and not self.contact_email:
            self.contact_email = self.email

    def validate_website_urls(self):
        """Validate website URLs"""
        url_fields = ['website', 'linkedin_profile', 'twitter_profile', 'facebook_profile', 'instagram_profile']
        
        for field in url_fields:
            url = self.get(field)
            if url and not url.startswith(('http://', 'https://')):
                self.set(field, f'https://{url}')

    def update_statistics(self):
        """Update organization statistics"""
        # Update member counts
        self.total_members = frappe.db.count("Organization Member", {"organization": self.name})
        self.active_members = frappe.db.count("Organization Member", {
            "organization": self.name,
            "status": "Active"
        })
        
        # Update project and event counts
        self.total_projects = frappe.db.count("Project", {"organization": self.name})
        self.total_events = frappe.db.count("Event", {"organization": self.name})

    def get_members(self, status=None):
        """Get organization members"""
        filters = {"organization": self.name}
        if status:
            filters["status"] = status
            
        return frappe.get_all(
            "Organization Member",
            filters=filters,
            fields=["name", "profile", "role", "status", "joined_date"],
            order_by="joined_date desc"
        )

    def add_member(self, profile, role="Member", status="Active"):
        """Add a member to the organization"""
        if frappe.db.exists("Organization Member", {
            "organization": self.name,
            "profile": profile
        }):
            frappe.throw(_("Profile is already a member of this organization"))
        
        member = frappe.get_doc({
            "doctype": "Organization Member",
            "organization": self.name,
            "profile": profile,
            "role": role,
            "status": status,
            "joined_date": now()
        })
        member.insert(ignore_permissions=True)
        return member

    def remove_member(self, profile):
        """Remove a member from the organization"""
        member = frappe.get_doc("Organization Member", {
            "organization": self.name,
            "profile": profile
        })
        member.status = "Inactive"
        member.save(ignore_permissions=True)

    def get_job_postings(self, status="Open"):
        """Get job postings for this organization"""
        return frappe.get_all(
            "Job Posting",
            filters={
                "organization": self.name,
                "status": status
            },
            fields=["name", "title", "description", "location", "employment_type", "created"]
        )

    def get_events(self, status="Published"):
        """Get events for this organization"""
        return frappe.get_all(
            "Event",
            filters={
                "organization": self.name,
                "status": status
            },
            fields=["name", "title", "description", "start_date", "end_date", "location"]
        )

    def get_projects(self, status="Active"):
        """Get projects for this organization"""
        return frappe.get_all(
            "Project",
            filters={
                "organization": self.name,
                "status": status
            },
            fields=["name", "title", "description", "start_date", "end_date", "status"]
        )


@frappe.whitelist()
def search_organizations(filters=None, limit=20):
    """Search organizations with filters"""
    if not filters:
        filters = {}
    
    query_filters = {"public_profile": 1}
    
    if filters.get("organization_type"):
        query_filters["organization_type"] = filters["organization_type"]
    
    if filters.get("industry"):
        query_filters["industry"] = filters["industry"]
    
    if filters.get("city"):
        query_filters["city"] = ["like", f"%{filters['city']}%"]
    
    if filters.get("country"):
        query_filters["country"] = filters["country"]
    
    if filters.get("is_verified"):
        query_filters["is_verified"] = 1
    
    organizations = frappe.get_all(
        "Organization",
        filters=query_filters,
        fields=["name", "organization_name", "description", "organization_type", 
                "industry", "city", "country", "logo", "website", "is_verified"],
        limit=limit
    )
    
    return organizations


@frappe.whitelist()
def join_organization(organization, profile, role="Member"):
    """Join an organization"""
    org_doc = frappe.get_doc("Organization", organization)
    
    if not org_doc.allow_member_registration:
        frappe.throw(_("This organization does not allow member registration"))
    
    if org_doc.require_approval:
        status = "Pending"
    else:
        status = "Active"
    
    return org_doc.add_member(profile, role, status)


@frappe.whitelist()
def leave_organization(organization, profile):
    """Leave an organization"""
    org_doc = frappe.get_doc("Organization", organization)
    return org_doc.remove_member(profile)