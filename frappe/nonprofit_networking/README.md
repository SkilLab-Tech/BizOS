# Nonprofit Networking Module

A comprehensive AI-powered networking and matchmaking platform for nonprofits and their communities, built on the Frappe framework.

## Overview

The Nonprofit Networking module provides a sophisticated platform for connecting individuals, organizations, and opportunities within the nonprofit sector. It combines traditional networking features with AI-powered matchmaking to facilitate meaningful connections, mentorship relationships, job opportunities, and collaborative projects.

## Key Features

### 🤖 AI-Powered Matchmaking
- Intelligent matching based on skills, interests, industry, and location
- Personalized meeting suggestions with high compatibility scores
- Automated daily matchmaking process
- Match analytics and recommendations

### 👥 Profile Management
- Comprehensive individual profiles with skills, interests, and availability
- Organization profiles for nonprofits and businesses
- Social media integration (LinkedIn, Twitter, GitHub)
- Privacy controls and visibility settings

### 🤝 Networking & Meetings
- Meeting request system with AI suggestions
- Calendar integration and scheduling
- Multiple meeting types (in-person, video, phone)
- Meeting analytics and feedback

### 🎓 Mentorship System
- Mentor-mentee matching and relationship management
- Milestone tracking and progress monitoring
- Structured mentorship programs
- Feedback and rating system

### 💼 Job & Project Opportunities
- Job posting and application system
- AI-powered job recommendations
- Project collaboration opportunities
- Application tracking and management

### 📊 Analytics & Reporting
- Individual networking statistics
- Organization performance metrics
- Meeting and mentorship analytics
- Custom reports and dashboards

## Installation

1. Install the module in your Frappe site:
```bash
bench get-app nonprofit_networking
bench install-app nonprofit_networking
```

2. Run database migrations:
```bash
bench migrate
```

3. Restart your site:
```bash
bench restart
```

## Configuration

### User Custom Fields
The module automatically adds custom fields to the User doctype:
- Profile Type (Individual/Organization/Both)
- Availability Status
- Bio
- Social Media Profiles
- Portfolio Website

### Roles and Permissions
The module creates the following roles:
- **Networking User**: Basic networking functionality
- **Networking Manager**: Advanced management capabilities
- **Organization Admin**: Organization-specific permissions

### Workspace
A dedicated workspace "Nonprofit Networking" is created with quick access to all major features.

## Usage

### For Individuals

1. **Create Your Profile**
   - Complete your profile with skills, interests, and goals
   - Set your availability and meeting preferences
   - Configure privacy settings

2. **Find Connections**
   - Use the AI-powered search to find relevant people
   - Browse suggested matches
   - Send meeting requests

3. **Mentorship**
   - Offer to mentor others or seek mentorship
   - Track mentorship progress and milestones
   - Provide feedback and ratings

4. **Job Opportunities**
   - Browse job postings
   - Apply for positions
   - Track application status

### For Organizations

1. **Organization Setup**
   - Create your organization profile
   - Add team members and administrators
   - Configure organization settings

2. **Job Postings**
   - Post job opportunities
   - Review applications
   - Manage the hiring process

3. **Member Management**
   - Invite members to join
   - Manage member permissions
   - Track organization activity

## API Reference

### Profile Management
```python
# Get profile by user
profile = frappe.get_doc("Profile", {"user": "user@example.com"})

# Search profiles
profiles = frappe.get_all("Profile", filters={"profile_visibility": "Public"})

# Get AI suggestions
suggestions = frappe.call("nonprofit_networking.ai.matchmaking.get_ai_suggestions", 
                         profile="profile_name", limit=5)
```

### Meeting Management
```python
# Send meeting request
meeting_request = frappe.call("nonprofit_networking.meeting_request.send_meeting_request",
                             from_profile="profile1", to_profile="profile2",
                             meeting_purpose="Networking", message="Let's connect!")

# Get upcoming meetings
meetings = frappe.call("nonprofit_networking.meeting.get_upcoming_meetings",
                      profile="profile_name", limit=10)
```

### Mentorship
```python
# Create mentorship request
mentorship = frappe.call("nonprofit_networking.mentorship.create_mentorship_request",
                        mentor="mentor_profile", mentee="mentee_profile",
                        mentorship_type="Career Guidance")

# Get mentorship opportunities
opportunities = frappe.call("nonprofit_networking.mentorship.get_mentorship_opportunities",
                           profile="profile_name")
```

### Job Management
```python
# Search jobs
jobs = frappe.call("nonprofit_networking.job_posting.search_jobs",
                  filters={"job_type": "Full-time", "location": "New York"})

# Apply for job
application = frappe.call("nonprofit_networking.job_posting.apply_for_job",
                         job_posting="job_name", profile="profile_name")
```

## Customization

### AI Matching Algorithm
The AI matching algorithm can be customized by modifying the `calculate_match_score` function in `ai/matchmaking.py`. You can adjust the weights for different matching criteria:

- Skills matching: 40%
- Interests matching: 30%
- Industry matching: 15%
- Location matching: 10%
- Networking preferences: 5%

### Custom Fields
Add custom fields to any doctype by creating them in the Frappe UI or through fixtures.

### Notifications
Customize notification templates by modifying the notification content in the respective doctype methods.

## Troubleshooting

### Common Issues

1. **Profile not created automatically**
   - Check if the user has the required custom fields
   - Verify the user events are properly configured

2. **AI matching not working**
   - Ensure the AI matchmaking module is properly installed
   - Check the scheduled tasks are running

3. **Permissions issues**
   - Verify the user has the correct role assigned
   - Check the permission query conditions

### Debug Mode
Enable debug mode to see detailed error messages:
```python
frappe.conf.developer_mode = 1
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This module is licensed under the MIT License. See the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## Changelog

### Version 1.0.0
- Initial release
- AI-powered matchmaking
- Profile management
- Meeting system
- Mentorship platform
- Job posting system
- Analytics and reporting