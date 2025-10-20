from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

import math
import frappe


@dataclass
class CandidateProfile:
    name: str
    user: str
    community: str
    display_name: str
    headline: str
    industry: str
    city: str
    country: str
    timezone: str
    is_open_to_mentoring: int
    is_seeking_mentor: int
    is_hiring: int
    is_open_to_roles: int
    match_frequency: str
    match_enabled: int
    interests: Set[str]
    last_matched_on: Optional[str]


def _get_profile_interests(profile_names: Sequence[str]) -> Dict[str, Set[str]]:
    if not profile_names:
        return {}
    rows = frappe.get_all(
        "Profile Interest",
        filters={"parenttype": "Member Profile", "parent": ["in", list(profile_names)]},
        fields=["parent", "interest"],
        limit_page_length=10000,
    )
    result: Dict[str, Set[str]] = {p: set() for p in profile_names}
    for r in rows:
        result.setdefault(r.parent, set()).add(r.interest)
    return result


def _load_candidates(community: str) -> List[CandidateProfile]:
    profiles = frappe.get_all(
        "Member Profile",
        filters={"community": community, "match_enabled": 1},
        fields=[
            "name",
            "user",
            "community",
            "display_name",
            "headline",
            "industry",
            "city",
            "country",
            "timezone",
            "is_open_to_mentoring",
            "is_seeking_mentor",
            "is_hiring",
            "is_open_to_roles",
            "match_frequency",
            "match_enabled",
            "last_matched_on",
        ],
        limit_page_length=10000,
    )
    interests = _get_profile_interests([p.name for p in profiles])

    out: List[CandidateProfile] = []
    for p in profiles:
        out.append(
            CandidateProfile(
                name=p.name,
                user=p.user,
                community=p.community,
                display_name=p.display_name or "",
                headline=p.headline or "",
                industry=p.industry or "",
                city=p.city or "",
                country=p.country or "",
                timezone=p.timezone or "",
                is_open_to_mentoring=int(p.is_open_to_mentoring or 0),
                is_seeking_mentor=int(p.is_seeking_mentor or 0),
                is_hiring=int(p.is_hiring or 0),
                is_open_to_roles=int(p.is_open_to_roles or 0),
                match_frequency=p.match_frequency or "Weekly",
                match_enabled=int(p.match_enabled or 1),
                interests=interests.get(p.name, set()),
                last_matched_on=p.last_matched_on,
            )
        )
    return out


def _compatibility_score(a: CandidateProfile, b: CandidateProfile) -> float:
    score = 0.0

    # Interest overlap (Jaccard)
    if a.interests or b.interests:
        jaccard = 0.0
        inter = a.interests & b.interests
        union = a.interests | b.interests
        if union:
            jaccard = len(inter) / len(union)
        score += 0.5 * jaccard

    # Mentor/mentee alignment
    mentor_pair = (a.is_open_to_mentoring and b.is_seeking_mentor) or (
        b.is_open_to_mentoring and a.is_seeking_mentor
    )
    if mentor_pair:
        score += 0.25

    # Hiring alignment
    hiring_pair = (a.is_hiring and b.is_open_to_roles) or (b.is_hiring and a.is_open_to_roles)
    if hiring_pair:
        score += 0.2

    # Location/timezone proximity (simple check)
    if a.country and a.country == b.country:
        score += 0.05
    if a.timezone and b.timezone and a.timezone == b.timezone:
        score += 0.05

    return score


def _greedy_pairing(candidates: List[CandidateProfile]) -> List[Tuple[CandidateProfile, CandidateProfile, float]]:
    pairs: List[Tuple[str, str, float]] = []
    for i in range(len(candidates)):
        for j in range(i + 1, len(candidates)):
            a = candidates[i]
            b = candidates[j]
            if a.user == b.user:
                continue
            s = _compatibility_score(a, b)
            if s > 0:
                pairs.append((a.name, b.name, s))

    # Sort by score descending
    pairs.sort(key=lambda t: t[2], reverse=True)

    used: Set[str] = set()
    chosen: List[Tuple[CandidateProfile, CandidateProfile, float]] = []
    by_name = {c.name: c for c in candidates}
    for a_name, b_name, s in pairs:
        if a_name in used or b_name in used:
            continue
        chosen.append((by_name[a_name], by_name[b_name], s))
        used.add(a_name)
        used.add(b_name)
    return chosen


def compute_matches(
    community: str,
    match_run_name: Optional[str] = None,
    persist: bool = True,
) -> List[Dict[str, Any]]:
    """Compute matches for a community.

    If persist is True, creates a Match Run and Match Suggestion documents.
    Returns a list of suggestions (dicts) in all cases.
    """
    candidates = _load_candidates(community)
    if not candidates:
        return []

    pairings = _greedy_pairing(candidates)

    suggestions: List[Dict[str, Any]] = []
    for a, b, score in pairings:
        suggestions.append(
            {
                "member_profile_a": a.name,
                "member_profile_b": b.name,
                "member_profile_a_user": a.user,
                "member_profile_b_user": b.user,
                "member_profile_a_name": a.display_name or a.user,
                "member_profile_b_name": b.display_name or b.user,
                "score": round(score, 4),
                "status": "Suggested",
                "community": community,
                "match_run": match_run_name,
            }
        )

    if not persist:
        return suggestions

    # Persist suggestions under a Match Run
    match_run = None
    if match_run_name:
        match_run = frappe.get_doc("Match Run", match_run_name)
        match_run.status = "Running"
        match_run.started_on = frappe.utils.now_datetime()
        match_run.save(ignore_permissions=True)
    else:
        match_run = frappe.get_doc({
            "doctype": "Match Run",
            "community": community,
            "status": "Running",
            "started_on": frappe.utils.now_datetime(),
        })
        match_run.insert(ignore_permissions=True)

    for s in suggestions:
        doc = frappe.get_doc({"doctype": "Match Suggestion", **s})
        doc.insert(ignore_permissions=True)

    # Update last_matched_on for member profiles included in suggestions
    for s in suggestions:
        frappe.db.set_value("Member Profile", s["member_profile_a"], "last_matched_on", frappe.utils.now_datetime())
        frappe.db.set_value("Member Profile", s["member_profile_b"], "last_matched_on", frappe.utils.now_datetime())

    match_run.status = "Completed"
    match_run.pair_count = len(suggestions)
    match_run.completed_on = frappe.utils.now_datetime()
    match_run.save(ignore_permissions=True)

    return suggestions
