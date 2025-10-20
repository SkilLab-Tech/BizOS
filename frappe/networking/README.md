# Networking Module for Frappe Framework

## Overview

The Networking Module is a comprehensive solution for nonprofit organizations to manage member relationships, facilitate networking, and create meaningful connections through AI-powered matchmaking. Similar to Mighty Networks with Lunchclub.com's AI matching capabilities, this module serves as a CRM/ERP for people and organizations.

## Key Features

### 1. Member Profile Management
- **Comprehensive Profiles**: Rich member profiles with professional information, bio, skills, interests, and networking goals
- **Profile Visibility Controls**: Public, Members Only, or Private visibility settings
- **Multi-Organization Support**: Members can belong to multiple organizations and alumni groups
- **Skill & Interest Tracking**: Categorized skills with proficiency levels and interests with engagement levels

### 2. AI-Powered Matchmaking
- **Intelligent Algorithm**: Matches members based on:
  - Shared interests (40% weight)
  - Complementary skills (30% weight)
  - Mentor/mentee compatibility (20% weight)
  - Hiring/job seeking alignment (10% weight)
- **Match Score Threshold**: Configurable minimum match scores (default: 70%)
- **Automatic Matching**: Background processing of matchmaking requests
- **Detailed Match Reasons**: Explanation of why members are matched

### 3. Networking Connections
- **Connection Requests**: Send and manage connection requests
- **Connection Types**: Networking, Mentorship, Collaboration, Recruiting, Alumni, Partnership
- **Status Tracking**: Pending, Accepted, Rejected, Blocked statuses
- **Interaction History**: Track meetings and interactions with connections
- **Email Notifications**: Automatic notifications for connection requests and responses

### 4. Meeting Management
- **Flexible Scheduling**: Schedule virtual, in-person, or phone meetings
- **Meeting Details**: Agenda, location, video links, and notes
- **Status Tracking**: Scheduled, Confirmed, Completed, Cancelled, Rescheduled
- **Follow-up System**: Mark meetings requiring follow-up with due dates
- **Calendar Integration**: Ready for calendar sync (requires implementation)

### 5. Organization & Alumni Management
- **Networking Organizations**: Manage nonprofits, charities, foundations, and professional associations
- **Alumni Groups**: Create groups by graduation year, program, location, or interests
- **Member Statistics**: Track total and active members per organization
- **Public/Private Groups**: Control visibility and membership approval requirements

### 6. Advanced Analytics & Reporting
- **Member Connections Report**: Detailed connection analytics with interaction counts
- **Networking Activity Report**: Member engagement metrics and activity tracking
- **Trending Insights**: Discover trending interests and skills in your network
- **Personal Statistics**: Individual dashboard showing connections, meetings, and engagement

## Architecture & Design

### Technology Stack
- **Backend**: Python with Frappe Framework
- **Frontend**: JavaScript with Vue.js components
- **Database**: MariaDB with optimized indexing
- **API**: RESTful API with whitelist decorators

### Core DocTypes

1. **Member Profile**: Central profile management
2. **Interest & Skill**: Taxonomy for categorization
3. **Networking Connection**: Relationship tracking
4. **Networking Meeting**: Meeting management
5. **Matchmaking Request**: AI matching requests
6. **Networking Organization**: Organization management
7. **Alumni Group**: Alumni group management

### Design Patterns
- **Document-based Architecture**: Leverages Frappe's Document model
- **Child Tables**: Efficient many-to-many relationships
- **Validation Hooks**: Business logic in Python validate() methods
- **Event-driven Notifications**: Email notifications on document events
- **RESTful APIs**: Exposed via @frappe.whitelist() decorators

## API Endpoints

### Member Profile APIs
```python
# Get member profile
frappe.call('frappe.networking.doctype.member_profile.member_profile.get_member_profile', {
    email: 'user@example.com'
})

# Search members
frappe.call('frappe.networking.doctype.member_profile.member_profile.search_members', {
    query: 'python developer',
    filters: {member_type: 'Alumni'}
})

# Find matches
frappe.call('frappe.networking.doctype.member_profile.member_profile.find_matching_members', {
    member_profile: 'Jane Doe',
    limit: 10
})
```

### Matchmaking APIs
```python
# Get member statistics
frappe.call('frappe.networking.api.matchmaking.get_member_statistics', {
    member: 'Jane Doe'
})

# Get connection suggestions
frappe.call('frappe.networking.api.matchmaking.suggest_connections', {
    member: 'Jane Doe',
    limit: 5
})

# Get networking recommendations
frappe.call('frappe.networking.api.matchmaking.get_networking_recommendations', {
    member: 'Jane Doe'
})
```

### Connection APIs
```python
# Accept connection
frappe.call('frappe.networking.doctype.networking_connection.networking_connection.accept_connection', {
    connection_name: 'CONN-00001'
})

# Get my connections
frappe.call('frappe.networking.doctype.networking_connection.networking_connection.get_my_connections', {
    member_profile: 'Jane Doe',
    status: 'Accepted'
})
```

## Installation & Setup

### Prerequisites
- Frappe Framework (version 14 or higher)
- MariaDB 10.3+
- Python 3.10+
- Node.js 18+

### Installation Steps

1. **Install the module** (if in a separate app):
```bash
bench get-app networking
bench --site [site-name] install-app networking
```

2. **Migrate the database**:
```bash
bench --site [site-name] migrate
```

3. **Build assets**:
```bash
bench build
```

4. **Create initial data**:
```bash
# Create sample interests
bench --site [site-name] console
>>> from frappe.networking.utils import create_sample_data
>>> create_sample_data()
```

### Configuration

1. **Create Role**: Create a "Networking User" role for members
2. **Set Permissions**: Configure permissions for DocTypes
3. **Email Settings**: Configure SMTP for notifications
4. **Customize Fields**: Add custom fields as needed

## Usage Guide

### For Administrators

1. **Setup Organizations**:
   - Go to Networking > Networking Organization
   - Create your nonprofit organization
   - Set up alumni groups

2. **Import Members**:
   - Go to Member Profile
   - Use Import feature to bulk import members
   - Map fields from your existing database

3. **Configure Interests & Skills**:
   - Create relevant interests for your community
   - Add skills taxonomy for your industry

### For Members

1. **Complete Your Profile**:
   - Fill in professional information
   - Add skills with proficiency levels
   - Select interests
   - Set networking goals

2. **Find Matches**:
   - Click "Find Matches" button
   - Review AI-suggested connections
   - Send connection requests

3. **Network & Meet**:
   - Accept connection requests
   - Schedule meetings with connections
   - Track interactions

## Customization

### Adding Custom Fields

```python
# Example: Add custom field to Member Profile
frappe.get_doc({
    'doctype': 'Custom Field',
    'dt': 'Member Profile',
    'fieldname': 'linkedin_url',
    'label': 'LinkedIn URL',
    'fieldtype': 'Data',
    'insert_after': 'email'
}).insert()
```

### Extending Matchmaking Algorithm

```python
# In member_profile.py
def get_matching_score(self, other_profile):
    """Override to customize matching algorithm"""
    score = super().get_matching_score(other_profile)
    
    # Add custom scoring logic
    if self.industry == other_profile.industry:
        score += 10
    
    return min(score, 100)
```

### Custom Reports

Create custom reports in `frappe/networking/report/` following the existing report patterns.

## Best Practices

1. **Data Quality**: Encourage members to complete profiles fully
2. **Privacy**: Respect member privacy settings
3. **Engagement**: Regular matchmaking runs to keep connections fresh
4. **Moderation**: Monitor connections for inappropriate behavior
5. **Analytics**: Review reports regularly to improve matching

## Security Considerations

- **Permission Levels**: Role-based access control on all DocTypes
- **Data Privacy**: Profile visibility controls honored in all queries
- **SQL Injection**: Parameterized queries throughout
- **XSS Prevention**: Input sanitization in Text Editor fields
- **Email Validation**: Proper validation of email addresses

## Performance Optimization

- **Indexes**: Key fields indexed for fast lookups
- **Query Optimization**: Efficient SQL queries with proper joins
- **Caching**: Consider Redis caching for frequently accessed data
- **Background Jobs**: Matchmaking runs in background
- **Pagination**: Lists paginated for large datasets

## Troubleshooting

### Common Issues

1. **Matching not working**:
   - Check if AI matching is enabled on profile
   - Verify minimum match score threshold
   - Ensure members have interests/skills set

2. **Email notifications not sending**:
   - Check SMTP settings
   - Verify email_notifications flag on profile
   - Check email queue: `bench --site [site] doctor`

3. **Slow queries**:
   - Run `bench mariadb` and analyze slow queries
   - Add indexes if needed
   - Consider archiving old data

## Roadmap

### Planned Features
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Mobile app support
- [ ] Video meeting integration (Zoom, Teams)
- [ ] Advanced ML-based matching
- [ ] Recommendation engine improvements
- [ ] Event management integration
- [ ] Donation tracking integration
- [ ] Newsletter integration
- [ ] Social feed/timeline
- [ ] Messaging system

## Support & Contributing

For issues and feature requests, please use the GitHub issue tracker.

## License

MIT License - See LICENSE file for details

## Credits

Developed following Frappe Framework best practices and design patterns.
Inspired by Mighty Networks and Lunchclub.com.

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-20  
**Frappe Version Compatibility**: v14+
