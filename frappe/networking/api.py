from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import frappe


@frappe.whitelist(methods=["GET"])
def search_profiles(q: str = "", community: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """Search member profiles by text and filters.

    Args:
        q: Free text query across name, headline, bio.
        community: Optional community name to scope results.
        limit: Max results to return.
    """
    filters: Dict[str, Any] = {}
    if community:
        filters["community"] = community
    # Only return safe, public-facing fields
    fields = [
        "name",
        "display_name",
        "headline",
        "industry",
        "city",
        "country",
        "is_open_to_mentoring",
        "is_seeking_mentor",
        "is_hiring",
        "is_open_to_roles",
    ]
    or_filters = []
    if q:
        like = f"%{q}%"
        or_filters = [
            ["Member Profile", "display_name", "like", like],
            ["Member Profile", "headline", "like", like],
            ["Member Profile", "bio", "like", like],
            ["Member Profile", "industry", "like", like],
            ["Member Profile", "city", "like", like],
        ]
    return frappe.get_list(
        "Member Profile",
        filters=filters,
        fields=fields,
        or_filters=or_filters,
        limit_page_length=limit,
        order_by="modified desc",
        ignore_permissions=True,
    )


@frappe.whitelist(methods=["POST"])
def run_matchmaking(community: str, dry_run: int = 0) -> Dict[str, Any]:
    """Trigger matchmaking for a community.

    Returns the created Match Run document (or a preview in dry_run).
    """
    from .matching import compute_matches

    if not community:
        frappe.throw("community is required")

    if int(dry_run):
        preview = compute_matches(community, persist=False)
        return {"preview": preview}

    match_run = frappe.get_doc({
        "doctype": "Match Run",
        "community": community,
        "status": "Queued",
    }).insert(ignore_permissions=True)

    frappe.enqueue(
        method="frappe.networking.matching.compute_matches",
        queue="default",
        job_name=f"compute-matches-{community}-{match_run.name}",
        timeout=900,
        community=community,
        match_run_name=match_run.name,
        persist=True,
    )
    return {"match_run": match_run.name}


@frappe.whitelist(methods=["POST"])
def accept_match(suggestion: str) -> Dict[str, Any]:
    """Accept a match suggestion and mark as accepted."""
    doc = frappe.get_doc("Match Suggestion", suggestion)
    if doc.status not in {"Suggested", "Proposed"}:
        frappe.throw("Only Suggested/Proposed matches can be accepted")
    doc.status = "Accepted"
    doc.save(ignore_permissions=True)
    return {"ok": True}


@frappe.whitelist(methods=["POST"])
def create_event_from_suggestion(
    suggestion: str, starts_on: str, ends_on: Optional[str] = None, add_video_conferencing: int = 0
) -> Dict[str, Any]:
    """Create an Event for a match suggestion and link it back.

    Args:
        suggestion: Match Suggestion name
        starts_on: ISO datetime string
        ends_on: Optional ISO datetime string
        add_video_conferencing: 1 to request Google Meet via integration
    """
    s = frappe.get_doc("Match Suggestion", suggestion)
    participants = [s.member_profile_a_user, s.member_profile_b_user]
    subject = f"Networking: {s.member_profile_a_name} <> {s.member_profile_b_name}"

    event = frappe.get_doc(
        {
            "doctype": "Event",
            "subject": subject,
            "event_category": "Meeting",
            "event_type": "Private",
            "starts_on": starts_on,
            "ends_on": ends_on,
            "send_reminder": 1,
            "add_video_conferencing": int(add_video_conferencing),
            "event_participants": [
                {"reference_doctype": "User", "reference_docname": p} for p in participants if p
            ],
        }
    ).insert(ignore_permissions=True)

    s.status = "Scheduled"
    s.event = event.name
    s.save(ignore_permissions=True)

    return {"event": event.name}
