# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.utils import now, add_days
import json
from typing import List, Dict, Any


def calculate_match_score(profile1: str, profile2: str) -> float:
    """Calculate AI match score between two profiles"""
    try:
        profile1_doc = frappe.get_doc("Profile", profile1)
        profile2_doc = frappe.get_doc("Profile", profile2)
        
        score = 0.0
        total_weight = 0.0
        
        # Skills matching (40% weight)
        if profile1_doc.skills and profile2_doc.skills:
            skills_score = calculate_skills_match(profile1_doc.skills, profile2_doc.skills)
            score += skills_score * 0.4
            total_weight += 0.4
        
        # Interests matching (30% weight)
        if profile1_doc.interests and profile2_doc.interests:
            interests_score = calculate_interests_match(profile1_doc.interests, profile2_doc.interests)
            score += interests_score * 0.3
            total_weight += 0.3
        
        # Industry matching (15% weight)
        if profile1_doc.industry and profile2_doc.industry:
            industry_score = 1.0 if profile1_doc.industry == profile2_doc.industry else 0.0
            score += industry_score * 0.15
            total_weight += 0.15
        
        # Location matching (10% weight)
        if profile1_doc.location and profile2_doc.location:
            location_score = calculate_location_match(profile1_doc.location, profile2_doc.location)
            score += location_score * 0.1
            total_weight += 0.1
        
        # Networking preferences (5% weight)
        networking_score = calculate_networking_match(profile1_doc, profile2_doc)
        score += networking_score * 0.05
        total_weight += 0.05
        
        # Normalize score
        if total_weight > 0:
            final_score = (score / total_weight) * 100
        else:
            final_score = 0.0
        
        return min(final_score, 100.0)
        
    except Exception as e:
        frappe.log_error(f"Error calculating match score: {str(e)}")
        return 0.0


def calculate_skills_match(skills1: List, skills2: List) -> float:
    """Calculate skills matching score"""
    if not skills1 or not skills2:
        return 0.0
    
    skills1_list = [skill.skill for skill in skills1 if skill.skill]
    skills2_list = [skill.skill for skill in skills2 if skill.skill]
    
    if not skills1_list or not skills2_list:
        return 0.0
    
    # Calculate Jaccard similarity
    set1 = set(skills1_list)
    set2 = set(skills2_list)
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    if union == 0:
        return 0.0
    
    return intersection / union


def calculate_interests_match(interests1: List, interests2: List) -> float:
    """Calculate interests matching score"""
    if not interests1 or not interests2:
        return 0.0
    
    interests1_list = [interest.interest for interest in interests1 if interest.interest]
    interests2_list = [interest.interest for interest in interests2 if interest.interest]
    
    if not interests1_list or not interests2_list:
        return 0.0
    
    # Calculate weighted similarity based on interest levels
    score = 0.0
    total_weight = 0.0
    
    for interest1 in interests1:
        for interest2 in interests2:
            if interest1.interest == interest2.interest:
                # Weight by interest levels
                weight1 = get_interest_weight(interest1.interest_level)
                weight2 = get_interest_weight(interest2.interest_level)
                score += (weight1 + weight2) / 2
                total_weight += 1.0
    
    if total_weight == 0:
        return 0.0
    
    return score / total_weight


def get_interest_weight(level: str) -> float:
    """Get weight for interest level"""
    weights = {
        "Low": 0.3,
        "Medium": 0.6,
        "High": 1.0
    }
    return weights.get(level, 0.5)


def calculate_location_match(location1: str, location2: str) -> float:
    """Calculate location matching score"""
    if not location1 or not location2:
        return 0.0
    
    # Simple string matching for now
    # In production, this could use geocoding APIs
    location1_lower = location1.lower().strip()
    location2_lower = location2.lower().strip()
    
    if location1_lower == location2_lower:
        return 1.0
    
    # Check if cities match
    city1 = location1_lower.split(',')[0].strip()
    city2 = location2_lower.split(',')[0].strip()
    
    if city1 == city2:
        return 0.8
    
    # Check if countries match
    if ',' in location1 and ',' in location2:
        country1 = location1_lower.split(',')[-1].strip()
        country2 = location2_lower.split(',')[-1].strip()
        
        if country1 == country2:
            return 0.5
    
    return 0.0


def calculate_networking_match(profile1, profile2) -> float:
    """Calculate networking preferences match"""
    score = 0.0
    
    # Mentor-mentee matching
    if profile1.seeking_mentor and profile2.can_mentor:
        score += 0.5
    if profile2.seeking_mentor and profile1.can_mentor:
        score += 0.5
    
    # Job opportunities
    if profile1.open_to_jobs and profile2.open_to_jobs:
        score += 0.3
    
    # Project collaborations
    if profile1.open_to_projects and profile2.open_to_projects:
        score += 0.2
    
    return min(score, 1.0)


def get_ai_suggestions(profile: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get AI-suggested meeting requests for a profile"""
    try:
        profile_doc = frappe.get_doc("Profile", profile)
        
        # Get potential matches
        potential_matches = get_potential_matches(profile, limit * 3)
        
        suggestions = []
        for match in potential_matches:
            match_profile = frappe.get_doc("Profile", match["profile"])
            match_score = calculate_match_score(profile, match["profile"])
            
            # Determine meeting purpose
            purpose = determine_meeting_purpose(profile_doc, match_profile, match_score)
            
            # Generate personalized message
            message = generate_meeting_message(profile_doc, match_profile, purpose)
            
            # Determine meeting type
            meeting_type = determine_meeting_type(profile_doc, match_profile)
            
            suggestions.append({
                "profile": match["profile"],
                "profile_name": match_profile.full_name,
                "match_score": match_score,
                "purpose": purpose,
                "message": message,
                "meeting_type": meeting_type,
                "reason": get_match_reason(profile_doc, match_profile, match_score)
            })
        
        # Sort by match score and return top suggestions
        suggestions.sort(key=lambda x: x["match_score"], reverse=True)
        return suggestions[:limit]
        
    except Exception as e:
        frappe.log_error(f"Error getting AI suggestions: {str(e)}")
        return []


def get_potential_matches(profile: str, limit: int) -> List[Dict[str, Any]]:
    """Get potential matches for a profile"""
    profile_doc = frappe.get_doc("Profile", profile)
    
    # Build filters
    filters = {
        "name": ("!=", profile),
        "profile_visibility": "Public"
    }
    
    # Add skill-based filtering
    if profile_doc.skills:
        skill_names = [skill.skill for skill in profile_doc.skills if skill.skill]
        if skill_names:
            filters["skills"] = ["in", skill_names]
    
    # Add interest-based filtering
    if profile_doc.interests:
        interest_names = [interest.interest for interest in profile_doc.interests if interest.interest]
        if interest_names:
            filters["interests"] = ["in", interest_names]
    
    # Add industry filtering
    if profile_doc.industry:
        filters["industry"] = profile_doc.industry
    
    # Get matches
    matches = frappe.get_all(
        "Profile",
        filters=filters,
        fields=["name", "full_name", "bio", "job_title", "current_organization", "location"],
        limit=limit
    )
    
    return matches


def determine_meeting_purpose(profile1, profile2, match_score: float) -> str:
    """Determine the best meeting purpose based on profiles and match score"""
    purposes = []
    
    # Mentorship opportunities
    if profile1.seeking_mentor and profile2.can_mentor:
        purposes.append("Mentorship")
    if profile2.seeking_mentor and profile1.can_mentor:
        purposes.append("Mentorship")
    
    # Job opportunities
    if profile1.open_to_jobs and profile2.open_to_jobs:
        purposes.append("Job Discussion")
    
    # Project collaborations
    if profile1.open_to_projects and profile2.open_to_projects:
        purposes.append("Project Collaboration")
    
    # High match score suggests networking
    if match_score > 70:
        purposes.append("Networking")
    
    # Default to general discussion
    if not purposes:
        purposes.append("General Discussion")
    
    return purposes[0]


def generate_meeting_message(profile1, profile2, purpose: str) -> str:
    """Generate a personalized meeting message"""
    templates = {
        "Mentorship": f"Hi {profile2.full_name}, I noticed your expertise in {get_primary_skills(profile2)} and would love to learn from your experience. Would you be interested in a mentoring session?",
        "Job Discussion": f"Hi {profile2.full_name}, I see we have similar backgrounds in {get_primary_skills(profile1)}. I'd love to discuss career opportunities and share insights.",
        "Project Collaboration": f"Hi {profile2.full_name}, I'm working on projects related to {get_primary_interests(profile1)} and think we could collaborate effectively. Would you be interested in discussing potential partnerships?",
        "Networking": f"Hi {profile2.full_name}, I noticed we share interests in {get_primary_interests(profile1)} and thought it would be great to connect and share experiences.",
        "General Discussion": f"Hi {profile2.full_name}, I'd love to connect and learn more about your work in {profile2.job_title or 'your field'}. Would you be interested in a brief conversation?"
    }
    
    return templates.get(purpose, templates["General Discussion"])


def get_primary_skills(profile) -> str:
    """Get primary skills as a string"""
    if not profile.skills:
        return "your field"
    
    primary_skills = [skill.skill for skill in profile.skills if skill.is_primary]
    if not primary_skills:
        primary_skills = [skill.skill for skill in profile.skills[:2]]
    
    return ", ".join(primary_skills[:2])


def get_primary_interests(profile) -> str:
    """Get primary interests as a string"""
    if not profile.interests:
        return "similar areas"
    
    primary_interests = [interest.interest for interest in profile.interests if interest.is_primary]
    if not primary_interests:
        primary_interests = [interest.interest for interest in profile.interests[:2]]
    
    return ", ".join(primary_interests[:2])


def determine_meeting_type(profile1, profile2) -> str:
    """Determine the best meeting type based on profiles"""
    # Check preferences
    if profile1.preferred_meeting_type and profile1.preferred_meeting_type != "Any":
        return profile1.preferred_meeting_type
    
    if profile2.preferred_meeting_type and profile2.preferred_meeting_type != "Any":
        return profile2.preferred_meeting_type
    
    # Default to video call for remote networking
    return "Video Call"


def get_match_reason(profile1, profile2, match_score: float) -> str:
    """Get the reason for the match"""
    reasons = []
    
    # Skills match
    if profile1.skills and profile2.skills:
        common_skills = set([skill.skill for skill in profile1.skills]) & set([skill.skill for skill in profile2.skills])
        if common_skills:
            reasons.append(f"Shared skills: {', '.join(list(common_skills)[:2])}")
    
    # Interests match
    if profile1.interests and profile2.interests:
        common_interests = set([interest.interest for interest in profile1.interests]) & set([interest.interest for interest in profile2.interests])
        if common_interests:
            reasons.append(f"Shared interests: {', '.join(list(common_interests)[:2])}")
    
    # Industry match
    if profile1.industry and profile2.industry and profile1.industry == profile2.industry:
        reasons.append(f"Same industry: {profile1.industry}")
    
    # Location match
    if profile1.location and profile2.location and profile1.location.lower() == profile2.location.lower():
        reasons.append(f"Same location: {profile1.location}")
    
    # Mentorship opportunity
    if profile1.seeking_mentor and profile2.can_mentor:
        reasons.append("Mentorship opportunity")
    
    if not reasons:
        reasons.append("High compatibility score")
    
    return "; ".join(reasons[:3])


@frappe.whitelist()
def run_daily_matchmaking():
    """Run daily AI matchmaking for all active profiles"""
    try:
        # Get all active profiles
        profiles = frappe.get_all(
            "Profile",
            filters={"profile_visibility": "Public"},
            fields=["name", "user"]
        )
        
        suggestions_created = 0
        for profile in profiles:
            # Get AI suggestions
            suggestions = get_ai_suggestions(profile.name, limit=3)
            
            # Create draft meeting requests for high-scoring suggestions
            for suggestion in suggestions:
                if suggestion["match_score"] > 70:  # Only high-scoring matches
                    # Check if suggestion already exists
                    existing = frappe.db.exists("Meeting Request", {
                        "from_profile": profile.name,
                        "to_profile": suggestion["profile"],
                        "is_ai_suggested": 1,
                        "status": "Draft"
                    })
                    
                    if not existing:
                        frappe.get_doc({
                            "doctype": "Meeting Request",
                            "from_profile": profile.name,
                            "to_profile": suggestion["profile"],
                            "meeting_purpose": suggestion["purpose"],
                            "message": suggestion["message"],
                            "meeting_type": suggestion["meeting_type"],
                            "is_ai_suggested": 1,
                            "match_score": suggestion["match_score"],
                            "status": "Draft"
                        }).insert(ignore_permissions=True)
                        suggestions_created += 1
        
        frappe.log_error(f"Daily matchmaking completed. Created {suggestions_created} suggestions.")
        
    except Exception as e:
        frappe.log_error(f"Error in daily matchmaking: {str(e)}")


@frappe.whitelist()
def get_match_analytics(profile: str) -> Dict[str, Any]:
    """Get match analytics for a profile"""
    try:
        # Get match statistics
        total_requests = frappe.db.count("Meeting Request", {"from_profile": profile})
        accepted_requests = frappe.db.count("Meeting Request", {
            "from_profile": profile,
            "status": "Accepted"
        })
        ai_suggestions = frappe.db.count("Meeting Request", {
            "from_profile": profile,
            "is_ai_suggested": 1
        })
        
        # Get top matching profiles
        top_matches = frappe.get_all(
            "Profile",
            filters={"name": ("!=", profile), "profile_visibility": "Public"},
            fields=["name", "full_name", "bio", "job_title"],
            limit=5
        )
        
        # Calculate match scores for top matches
        for match in top_matches:
            match["match_score"] = calculate_match_score(profile, match["name"])
        
        # Sort by match score
        top_matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "total_requests": total_requests,
            "accepted_requests": accepted_requests,
            "acceptance_rate": (accepted_requests / total_requests * 100) if total_requests > 0 else 0,
            "ai_suggestions": ai_suggestions,
            "top_matches": top_matches
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting match analytics: {str(e)}")
        return {}