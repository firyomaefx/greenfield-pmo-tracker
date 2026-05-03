"""Brave Search API job scraper for 20+ tracked factory companies.

Searches Kulim, Batu Kawan & Bayan Lepas via Brave Search API.
API key stored ONLY in GitHub/Streamlit secrets — never in source code.
Free tier: 2,000 queries/month. v1.0.5 adds cooldown: skip if last run < 24h ago.
"""

import os
import json
import re
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import requests as req_lib
from scrapers.base_scraper import BaseScraper

TRACKED_COMPANIES = [
    "Novolyte", "AIXTRON", "UMediC", "Medtronic", "AMD",
    "Monolithic Power Systems", "Bitdeer", "congatec",
    "V-Chip", "Hanic", "Ferrotec", "Ichia", "AT&S",
    "Hyundai", "Unigen", "Pivotal", "Hotayi", "Benchmark", "Chipbond"
]

ZONES = ["Kulim", "Batu Kawan", "Bayan Lepas"]
COOLDOWN_HOURS = 24  # v1.0.5: skip API call if last successful scrape was within this window

CATEGORY_RULES = [
    (r"\b(operator|assembler|production|packer|general worker|production operator|machine operator|qc inspector)\b", "Operator"),
    (r"\b(technician|technician)\b", "Technician"),
    (r"\b(engineer|engineering|design engineer|process engineer|qa engineer|r&d)\b", "Engineer"),
    (r"\b(supervisor|team lead|shift lead|line leader|foreman|foreperson)\b", "Supervisor"),
    (r"\b(logistics|warehouse|forklift|driver|shipping|receiving|inventory|storekeeper|dispatch)\b", "Logistics"),
    (r"\b(admin|hr|human resource|receptionist|clerk|office|accountant|finance|payroll)\b", "Admin"),
    (r"\b(it |software|developer|programmer|network|system admin|sap|erp|data analyst|cyber)\b", "IT"),
    (r"\b(manager|director|head of|president|vp|senior manager|general manager|plant manager|factory manager)\b", "Management"),
]

def classify_category(text: str) -> str:
    """Auto-classify job title/description into a category."""
    text_lower = text.lower()
    for pattern, category in CATEGORY_RULES:
        if re.search(pattern, text_lower):
            return category
    return "Uncategorized"

class BraveJobScraper(BaseScraper):
    def __init__(self):
        super().__init__("BraveJobs", min_delay=1.0, max_delay=2.0)
        self.api_key = os.getenv("BRAVE_API_KEY", "")
        self.api_url = "https://api.search.brave.com/res/v1/web/search"
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key,
        }

    def search(self, query: str, count: int = 20) -> List[Dict]:
        """Call Brave Search API for a single query."""
        params = {
            "q": query,
            "count": count,
            "search_lang": "en",
            "freshness": "pw",  # past week only
        }
        try:
            resp = self.session.get(
                self.api_url, headers=self.headers, params=params, timeout=30
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("web", {}).get("results", [])
        except Exception as e:
            print(f"[BraveJobs] API error for '{query[:60]}': {str(e)[:100]}")
            return []

    def should_run(self) -> bool:
        """v1.0.5: Check scrape_logs. Skip if last successful run was within cooldown window."""
        try:
            from database.supabase_client import get_last_successful_scrape
            last_ts = get_last_successful_scrape("brave_jobs")
            if last_ts:
                # Parse timestamp (could be ISO string)
                if isinstance(last_ts, str):
                    last_ts = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
                elapsed = datetime.now(timezone.utc) - last_ts.replace(tzinfo=timezone.utc)
                skip = elapsed < timedelta(hours=COOLDOWN_HOURS)
                if skip:
                    print(f"[BraveJobs] Skipping — last successful scrape was {elapsed.seconds // 60} min ago")
                return not skip
        except Exception:
            pass  # Can't check logs → run anyway
        return True

    def scrape(self) -> List[Dict]:
        """Search all 3 zones, match results to tracked companies.
        v1.0.5: Returns empty list if should_run() is False (cooldown active)."""
        if not self.should_run():
            return []

        results = []

        for zone in ZONES:
            query = f"jobs hiring {zone} factory Malaysia"
            items = self.search(query)

            for item in items:
                title = item.get("title", "")
                description = item.get("description", "")
                url = item.get("url", "")
                full_text = (title + " " + description).lower()

                matched_company = None
                for company in TRACKED_COMPANIES:
                    # Match full company name or key part
                    company_lower = company.lower()
                    # Check with flexible matching
                    parts = company_lower.split()
                    if company_lower in full_text:
                        matched_company = company
                        break
                    elif len(parts) > 1 and parts[0] in full_text:
                        matched_company = company
                        break

                if matched_company:
                    category = classify_category(title + " " + description)
                    results.append({
                        "source": "Brave Search",
                        "title": title,
                        "body": description[:500] if description else "",
                        "source_url": url,
                        "published_at": "",
                        "raw_text": full_text,
                        "detected_by": "brave_jobs",
                        "company": matched_company,
                        "zone": zone,
                        "category": category,
                    })

        return results
