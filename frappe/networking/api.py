from __future__ import annotations

from typing import Any, Optional

import frappe
from frappe import _

from .matching import generate_matches_for_member


def _get_or_create_profile_for(user: str) -> str:
    existing = frappe.get_all("Member Profile", filters={"user": user}, pluck="name", limit=1)
    if existing:
        return existing[0]
    doc = frappe.new_doc("Member Profile")
    doc.user = user
    doc.enabled = 1
    doc.accepts_intros = 1
    doc.insert(ignore_permissions=True)
    return doc.name


@frappe.whitelist()
def get_my_profile() -> dict[str, Any]:
    user = frappe.session.user
    name = _get_or_create_profile_for(user)
    doc = frappe.get_doc("Member Profile", name)
    return doc.as_dict()


@frappe.whitelist()
def search_members(q: Optional[str] = None, limit: int = 20) -> list[dict[str, Any]]:
    q = (q or "").strip().lower()
    filters = {"enabled": 1}
    fields = [
        "name",
        "full_name",
        "headline",
        "location",
        "organization",
        "can_mentor",
        "wants_mentor",
        "is_hiring",
        "open_to_work",
    ]
    results = frappe.get_all("Member Profile", filters=filters, fields=fields, limit=int(limit))
    if not q:
        return results
    out: list[dict[str, Any]] = []
    for r in results:
        blob = " ".join(
            [
                str(r.get("full_name") or ""),
                str(r.get("headline") or ""),
                str(r.get("location") or ""),
                str(r.get("organization") or ""),
            ]
        ).lower()
        if q in blob:
            out.append(r)
    return out


@frappe.whitelist()
def generate_my_matches(limit: int = 5) -> list[str]:
    user = frappe.session.user
    profile = _get_or_create_profile_for(user)
    return generate_matches_for_member(profile, limit=int(limit))


@frappe.whitelist()
def respond_to_match(match: str, action: str) -> None:
    doc = frappe.get_doc("Match", match)
    action = (action or "").lower()
    if action == "accept":
        doc.status = "Accepted"
    elif action == "reject":
        doc.status = "Rejected"
    else:
        frappe.throw(_("Invalid action"))
    doc.save(ignore_permissions=True)


@frappe.whitelist()
def schedule_meeting(
    match: str,
    start: str,
    duration_minutes: int = 30,
    location: Optional[str] = None,
    video_link: Optional[str] = None,
) -> str:
    m = frappe.get_doc("Match", match)
    if m.status != "Accepted":
        m.status = "Accepted"
        m.save(ignore_permissions=True)

    meeting = frappe.new_doc("Meeting")
    meeting.member_a = m.member_a
    meeting.member_b = m.member_b
    meeting.start = frappe.utils.get_datetime(start)
    meeting.duration_minutes = int(duration_minutes)
    meeting.location = location
    meeting.video_link = video_link
    meeting.status = "Scheduled"
    meeting.insert(ignore_permissions=True)

    m.meeting = meeting.name
    m.status = "Scheduled"
    m.save(ignore_permissions=True)
    return meeting.name
