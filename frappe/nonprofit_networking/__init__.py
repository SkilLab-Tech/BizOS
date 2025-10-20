# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from . import __version__ as app_version

app_name = "nonprofit_networking"
app_title = "Nonprofit Networking"
app_publisher = "Frappe Technologies"
app_description = "AI-powered networking and matchmaking platform for nonprofits and their communities"
app_license = "MIT"
app_logo_url = "/assets/nonprofit_networking/images/logo.svg"
develop_version = "1.0.0"
app_home = "/app/build"

app_email = "developers@frappe.io"

# Website
app_include_js = [
    "nonprofit_networking.bundle.js"
]

app_include_css = [
    "nonprofit_networking.bundle.css"
]

# DocType JS
doctype_js = {
    "Profile": "public/js/nonprofit_networking/profile.js",
    "Organization": "public/js/nonprofit_networking/organization.js",
    "Meeting Request": "public/js/nonprofit_networking/meeting_request.js",
    "Meeting": "public/js/nonprofit_networking/meeting.js",
    "Mentorship": "public/js/nonprofit_networking/mentorship.js",
    "Job Posting": "public/js/nonprofit_networking/job_posting.js",
    "Match": "public/js/nonprofit_networking/match.js"
}

# Fixtures
fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                [
                    "User-profile_type",
                    "User-availability_status",
                    "User-bio",
                    "User-linkedin_profile",
                    "User-twitter_profile",
                    "User-github_profile",
                    "User-portfolio_website"
                ]
            ]
        ]
    }
]

# Hooks
before_install = "nonprofit_networking.setup.before_install"
after_install = "nonprofit_networking.setup.after_install"
after_migrate = "nonprofit_networking.setup.after_migrate"

# Permissions
permission_query_conditions = {
    "Profile": "nonprofit_networking.permissions.get_profile_permission_query_conditions",
    "Organization": "nonprofit_networking.permissions.get_organization_permission_query_conditions",
    "Meeting Request": "nonprofit_networking.permissions.get_meeting_request_permission_query_conditions",
    "Meeting": "nonprofit_networking.permissions.get_meeting_permission_query_conditions",
    "Mentorship": "nonprofit_networking.permissions.get_mentorship_permission_query_conditions",
    "Job Posting": "nonprofit_networking.permissions.get_job_posting_permission_query_conditions",
    "Match": "nonprofit_networking.permissions.get_match_permission_query_conditions"
}

# DocType Events
doc_events = {
    "User": {
        "after_insert": "nonprofit_networking.events.user_events.after_user_insert",
        "on_update": "nonprofit_networking.events.user_events.on_user_update"
    },
    "Contact": {
        "after_insert": "nonprofit_networking.events.contact_events.after_contact_insert",
        "on_update": "nonprofit_networking.events.contact_events.on_contact_update"
    }
}

# Scheduled Events
scheduler_events = {
    "daily": [
        "nonprofit_networking.tasks.daily_tasks.run_daily_matchmaking",
        "nonprofit_networking.tasks.daily_tasks.send_meeting_reminders"
    ],
    "hourly": [
        "nonprofit_networking.tasks.hourly_tasks.process_pending_meeting_requests"
    ]
}

# Website Context
website_context = {
    "favicon": "/assets/nonprofit_networking/images/favicon.ico",
    "splash_image": "/assets/nonprofit_networking/images/splash.png"
}