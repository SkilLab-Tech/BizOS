from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

import frappe


@dataclass
class MatchCandidate:
    profile_a: str
    profile_b: str
    score: float
    explanation: str


def _get_interests(profile_name: str) -> set[str]:
    rows = frappe.get_all(
        "Member Profile Interest",
        filters={"parent": profile_name, "parenttype": "Member Profile"},
        pluck="interest",
        order_by="idx asc",
    )
    return {i.strip().lower() for i in rows if i and isinstance(i, str)}


def _get_skills(profile_name: str) -> set[str]:
    rows = frappe.get_all(
        "Member Profile Skill",
        filters={"parent": profile_name, "parenttype": "Member Profile"},
        pluck="skill",
        order_by="idx asc",
    )
    return {i.strip().lower() for i in rows if i and isinstance(i, str)}


def _roles(profile_doc) -> tuple[bool, bool, bool, bool]:
    return (
        bool(profile_doc.can_mentor),
        bool(profile_doc.wants_mentor),
        bool(profile_doc.is_hiring),
        bool(profile_doc.open_to_work),
    )


def _role_compatibility(a, b) -> float:
    a_can_mentor, a_wants_mentor, a_is_hiring, a_open_to_work = _roles(a)
    b_can_mentor, b_wants_mentor, b_is_hiring, b_open_to_work = _roles(b)

    score = 0.0
    # Mentor-Mentee pairing
    if (a_can_mentor and b_wants_mentor) or (b_can_mentor and a_wants_mentor):
        score += 1.0
    # Hiring - Open to work pairing
    if (a_is_hiring and b_open_to_work) or (b_is_hiring and a_open_to_work):
        score += 1.0

    return min(score, 1.0)


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _weights_for(profile_name: str) -> tuple[float, float, float]:
    """Return weights for (interests, skills, roles). Defaults if preferences missing."""
    pref = frappe.get_all(
        "Matching Preference",
        filters={"member_profile": profile_name},
        fields=["interest_weight", "skill_weight", "role_weight"],
        limit=1,
    )
    if not pref:
        return 0.5, 0.3, 0.2
    p = pref[0]
    iw = float(p.get("interest_weight") or 0.5)
    sw = float(p.get("skill_weight") or 0.3)
    rw = float(p.get("role_weight") or 0.2)
    s = iw + sw + rw
    if s == 0:
        return 0.5, 0.3, 0.2
    return iw / s, sw / s, rw / s


def _explanation(inter_sim: float, skill_sim: float, role_score: float, overlap_i: set[str], overlap_s: set[str]) -> str:
    parts: list[str] = []
    if overlap_i:
        parts.append(f"Shared interests: {', '.join(sorted(overlap_i))}")
    if overlap_s:
        parts.append(f"Complementary skills: {', '.join(sorted(overlap_s))}")
    if role_score >= 1.0:
        parts.append("Strong role fit (mentor/mentee or hiring/opentowork)")
    elif role_score > 0:
        parts.append("Partial role fit")
    if not parts:
        return "General compatibility based on profile signals"
    return "; ".join(parts)


def score_pair(profile_a: str, profile_b: str) -> MatchCandidate | None:
    if profile_a == profile_b:
        return None

    a_doc = frappe.get_doc("Member Profile", profile_a)
    b_doc = frappe.get_doc("Member Profile", profile_b)

    a_interests = _get_interests(profile_a)
    b_interests = _get_interests(profile_b)
    a_skills = _get_skills(profile_a)
    b_skills = _get_skills(profile_b)

    inter_sim = _jaccard(a_interests, b_interests)
    skill_sim = _jaccard(a_skills, b_skills)
    role_score = _role_compatibility(a_doc, b_doc)

    wi_a, ws_a, wr_a = _weights_for(profile_a)
    wi_b, ws_b, wr_b = _weights_for(profile_b)
    wi, ws, wr = (wi_a + wi_b) / 2.0, (ws_a + ws_b) / 2.0, (wr_a + wr_b) / 2.0

    total = wi * inter_sim + ws * skill_sim + wr * role_score
    overlap_i = a_interests & b_interests
    overlap_s = a_skills & b_skills

    return MatchCandidate(
        profile_a=profile_a,
        profile_b=profile_b,
        score=round(float(total), 4),
        explanation=_explanation(inter_sim, skill_sim, role_score, overlap_i, overlap_s),
    )


def _canonical_pair(a: str, b: str) -> tuple[str, str]:
    return (a, b) if a < b else (b, a)


def upsert_match(candidate: MatchCandidate) -> str:
    a, b = _canonical_pair(candidate.profile_a, candidate.profile_b)
    existing = frappe.get_all(
        "Match",
        filters={"member_a": a, "member_b": b},
        pluck="name",
        limit=1,
    )
    if existing:
        name = existing[0]
        doc = frappe.get_doc("Match", name)
        doc.score = candidate.score
        doc.explanation = candidate.explanation
        doc.status = doc.status or "Proposed"
        doc.save(ignore_permissions=True)
        return name

    doc = frappe.new_doc("Match")
    doc.member_a = a
    doc.member_b = b
    doc.score = candidate.score
    doc.explanation = candidate.explanation
    doc.status = "Proposed"
    doc.created_by_job = 1
    doc.insert(ignore_permissions=True)
    return doc.name


def generate_matches_for_member(profile_name: str, limit: int = 10, min_score: float = 0.2) -> list[str]:
    profiles = frappe.get_all(
        "Member Profile",
        filters={"enabled": 1, "name": ("!=", profile_name)},
        pluck="name",
    )
    candidates: list[MatchCandidate] = []
    for other in profiles:
        cand = score_pair(profile_name, other)
        if not cand:
            continue
        if cand.score >= float(min_score):
            candidates.append(cand)

    candidates.sort(key=lambda c: c.score, reverse=True)
    top = candidates[: int(limit)]
    names: list[str] = []
    for cand in top:
        names.append(upsert_match(cand))
    return names


def run_periodic_matching() -> None:
    profiles = frappe.get_all(
        "Member Profile",
        filters={"enabled": 1, "accepts_intros": 1},
        pluck="name",
    )
    for p in profiles:
        try:
            pref = frappe.get_all(
                "Matching Preference",
                filters={"member_profile": p},
                fields=["max_matches_per_round"],
                limit=1,
            )
            k = int(pref[0]["max_matches_per_round"]) if pref and pref[0].get("max_matches_per_round") else 5
            generate_matches_for_member(p, limit=k)
        except Exception:
            frappe.log_error("Networking Matching Failure", frappe.get_traceback())
