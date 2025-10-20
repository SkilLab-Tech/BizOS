from __future__ import annotations

from typing import List

import frappe


def run_scheduled_matches() -> None:
    """Run scheduled matches for opted-in communities.

    Communities can opt-in via Community.allow_auto_matching = 1.
    """
    communities: List[str] = [
        c.name
        for c in frappe.get_all(
            "Community", filters={"allow_auto_matching": 1}, fields=["name"], limit=10000
        )
    ]
    for c in communities:
        frappe.enqueue(
            method="frappe.networking.matching.compute_matches",
            queue="default",
            job_name=f"scheduled-compute-matches-{c}",
            timeout=900,
            community=c,
            persist=True,
        )
