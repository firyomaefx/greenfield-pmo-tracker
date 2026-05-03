"""
PMP Job Listing Assistant for Kulim, Batu Kawan & Bayan Lepas factories.

OBJECTIVE: Help users find live factory job links fast — sorted by company or job category.
No agency. No fluff. Direct links only.

SCOPE:
  - Cover 20+ factories across 3 industrial zones
  - Organise by: Zone -> Company -> Category
  - Categories: Operator, Technician, Engineer, Supervisor, Logistics, Admin, IT, Management
  - Only show links after unlock is confirmed
  - If not unlocked: show preview only, prompt to unlock

RULES:
  - Never show full links to unverified users
  - Always display: Company | Zone | Category | Link | Last Verified
  - If user asks by company -> filter by company
  - If user asks by category -> filter by category
  - If user asks by zone -> list all companies in that zone
  - Keep replies short, structured, no waffle

QUALITY CHECK:
  - If link is older than 7 days -> flag as "Needs Verification"
  - If no jobs found for a filter -> say so honestly
  - Never fabricate job listings

CLOSING:
  - End every reply with: "Last updated: [date] | To report dead links reply /report"
"""

import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.supabase_client import (
    get_jobs_preview,
    get_jobs_by_zone,
    get_jobs_by_company,
    get_jobs_by_category,
    get_jobs_by_zone_and_category,
    get_all_companies,
    get_distinct_categories,
    update_job_verification,
)

CATEGORIES = [
    "Operator", "Technician", "Engineer", "Supervisor",
    "Logistics", "Admin", "IT", "Management",
]

ZONES = ["Kulim", "Batu Kawan", "Bayan Lepas"]

LAST_UPDATED = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def get_preview(unlocked: bool = False) -> dict:
    """Get preview counts by company. If unlocked, return with links."""
    preview = get_jobs_preview()
    companies = {c["name"]: c for c in get_all_companies()}

    preview_data = {}
    for name, info in preview.items():
        comp = companies.get(name, {})
        preview_data[name] = {
            "company": name,
            "zone": info["zone"],
            "job_count": info["count"],
            "sector": comp.get("sector", "N/A"),
        }
        if unlocked:
            jobs = get_jobs_by_company(name)
            preview_data[name]["jobs"] = [
                {
                    "title": j.get("title", ""),
                    "category": j.get("category", "Uncategorized"),
                    "url": j.get("job_url", ""),
                    "needs_verification": j.get("needs_verification", True),
                    "last_verified": j.get("last_verified", "N/A"),
                }
                for j in jobs
            ]

    return {
        "total_companies_with_jobs": len(preview_data),
        "total_jobs": sum(p["job_count"] for p in preview_data.values()),
        "by_zone": _group_by(preview_data, "zone"),
        "by_company": preview_data,
        "categories_available": get_distinct_categories(),
        "unlocked": unlocked,
        "last_updated": LAST_UPDATED,
    }


def filter_jobs(zone: str = None, company: str = None, category: str = None, unlocked: bool = False) -> dict:
    """Get jobs matching the given filters."""
    if not unlocked:
        return {
            "unlocked": False,
            "message": "Donate on Ko-fi to unlock live job links.",
            "preview": get_jobs_preview(),
            "last_updated": LAST_UPDATED,
        }

    jobs = []
    filter_desc = []

    if zone and category:
        jobs = get_jobs_by_zone_and_category(zone, category)
        filter_desc.append(f"Zone: {zone}")
        filter_desc.append(f"Category: {category}")
    elif zone:
        jobs = get_jobs_by_zone(zone)
        filter_desc.append(f"Zone: {zone}")
    elif company:
        jobs = get_jobs_by_company(company)
        filter_desc.append(f"Company: {company}")
    elif category:
        jobs = get_jobs_by_category(category)
        filter_desc.append(f"Category: {category}")
    else:
        # Return all active jobs across all zones
        all_jobs = []
        for z in ZONES:
            all_jobs.extend(get_jobs_by_zone(z))
        jobs = all_jobs
        filter_desc.append("All Zones & Companies")

    formatted = []
    for j in jobs:
        comp_data = j.get("companies", {})
        formatted.append({
            "company": comp_data.get("name", "?"),
            "zone": comp_data.get("location", "?"),
            "title": j.get("title", ""),
            "category": j.get("category", "Uncategorized"),
            "url": j.get("job_url", ""),
            "needs_verification": j.get("needs_verification", True),
            "last_verified": j.get("last_verified", "N/A"),
        })

    return {
        "unlocked": True,
        "filter": " | ".join(filter_desc),
        "count": len(formatted),
        "jobs": formatted,
        "has_stale": any(j["needs_verification"] for j in formatted),
        "last_updated": LAST_UPDATED,
    }


def report_dead_link(job_id: str):
    """Handle /report command - mark link as dead."""
    update_job_verification(job_id)
    return {
        "acknowledged": True,
        "message": "Link reported. Will be re-verified within 12 hours.",
        "job_id": job_id,
    }


def _group_by(data: dict, key: str) -> dict:
    """Group preview data by a key (e.g., zone)."""
    grouped = {}
    for item in data.values():
        group_key = item.get(key, "?")
        if group_key not in grouped:
            grouped[group_key] = []
        grouped[group_key].append(item)
    return grouped


if __name__ == "__main__":
    print("Job Assistant Test")
    print("-" * 50)

    preview = get_preview(unlocked=False)
    print(f"Preview: {preview['total_companies_with_jobs']} companies, {preview['total_jobs']} jobs")
    print(f"Categories: {preview['categories_available']}")
    print(f"By zone: {list(preview['by_zone'].keys())}")
