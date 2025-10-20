# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _


def get_profile_permission_query_conditions(user):
    """Get permission query conditions for Profile doctype"""
    if not user:
        user = frappe.session.user
    
    # Allow users to see their own profile and public profiles
    return f"""
        (tabProfile.user = '{user}' OR tabProfile.profile_visibility = 'Public')
    """


def get_organization_permission_query_conditions(user):
    """Get permission query conditions for Organization doctype"""
    if not user:
        user = frappe.session.user
    
    # Allow users to see public organizations and organizations they're members of
    return f"""
        (tabOrganization.public_profile = 1 OR 
         tabOrganization.name IN (
             SELECT organization FROM `tabOrganization Member` 
             WHERE profile IN (
                 SELECT name FROM `tabProfile` WHERE user = '{user}'
             )
         ))
    """


def get_meeting_request_permission_query_conditions(user):
    """Get permission query conditions for Meeting Request doctype"""
    if not user:
        user = frappe.session.user
    
    # Allow users to see meeting requests they sent or received
    return f"""
        (tabMeeting Request.from_profile IN (
             SELECT name FROM `tabProfile` WHERE user = '{user}'
         ) OR 
         tabMeeting Request.to_profile IN (
             SELECT name FROM `tabProfile` WHERE user = '{user}'
         ))
    """


def get_meeting_permission_query_conditions(user):
    """Get permission query conditions for Meeting doctype"""
    if not user:
        user = frappe.session.user
    
    # Allow users to see meetings they're part of
    return f"""
        (tabMeeting.from_profile IN (
             SELECT name FROM `tabProfile` WHERE user = '{user}'
         ) OR 
         tabMeeting.to_profile IN (
             SELECT name FROM `tabProfile` WHERE user = '{user}'
         ))
    """


def get_mentorship_permission_query_conditions(user):
    """Get permission query conditions for Mentorship doctype"""
    if not user:
        user = frappe.session.user
    
    # Allow users to see mentorships they're part of
    return f"""
        (tabMentorship.mentor IN (
             SELECT name FROM `tabProfile` WHERE user = '{user}'
         ) OR 
         tabMentorship.mentee IN (
             SELECT name FROM `tabProfile` WHERE user = '{user}'
         ))
    """


def get_job_posting_permission_query_conditions(user):
    """Get permission query conditions for Job Posting doctype"""
    if not user:
        user = frappe.session.user
    
    # Allow users to see all job postings (they're public by nature)
    return "1=1"


def get_match_permission_query_conditions(user):
    """Get permission query conditions for Match doctype"""
    if not user:
        user = frappe.session.user
    
    # Allow users to see matches involving their profile
    return f"""
        (tabMatch.profile1 IN (
             SELECT name FROM `tabProfile` WHERE user = '{user}'
         ) OR 
         tabMatch.profile2 IN (
             SELECT name FROM `tabProfile` WHERE user = '{user}'
         ))
    """