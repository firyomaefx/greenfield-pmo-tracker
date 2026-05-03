"""Main scraper orchestrator - runs all scrapers, deduplicates, and updates Supabase."""
import os
import sys
import time
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.rss_scraper import RSSScraper
from scrapers.mida_scraper import MIDAScraper
from scrapers.penang_scraper import PenangScraper
from scrapers.bursa_scraper import BursaScraper
from scrapers.job_scraper import JobScraper
from scrapers.company_scraper import CompanyScraper
from scrapers.nlp_processor import classify_news_item
from utils.deduplicator import deduplicate
from database.supabase_client import (
    get_all_companies, get_company_by_name, upsert_company_by_name,
    insert_news_item, insert_job, log_scrape_run, deactivate_old_jobs
)

SCRAPERS = [
    ("rss", RSSScraper()),
    ("mida", MIDAScraper()),
    ("penang", PenangScraper()),
    ("bursa", BursaScraper()),
    ("jobs_search", JobScraper()),
    ("company_pages", CompanyScraper()),
]


def run_all_scrapers() -> List[Dict]:
    """Run all scrapers and collect results."""
    all_items = []
    for name, scraper in SCRAPERS:
        t0 = time.time()
        try:
            items = scraper.scrape()
            elapsed = time.time() - t0
            all_items.extend(items)
            log_scrape_run(source=name, status="success",
                          items_found=len(items), duration_seconds=round(elapsed, 2))
            print(f"  [{name}] {len(items)} items in {elapsed:.1f}s")
        except Exception as e:
            elapsed = time.time() - t0
            log_scrape_run(source=name, status="failed", errors=str(e),
                          duration_seconds=round(elapsed, 2))
            print(f"  [{name}] FAILED: {e}")
    return all_items


def process_and_store(items: List[Dict]):
    """Deduplicate, classify, and store items."""
    print(f"\n  Processing {len(items)} raw items...")
    unique = deduplicate(items)

    existing_companies = {c["name"].lower(): c for c in get_all_companies()}
    new_news = 0
    new_jobs = 0

    for item in unique:
        item = classify_news_item(item)

        # Determine company_id
        extracted_name = item.get("extracted_company", "")
        company_id = None

        if extracted_name and extracted_name.lower() in existing_companies:
            company_id = existing_companies[extracted_name.lower()]["id"]
        elif extracted_name:
            # New auto-detected company
            new_comp = upsert_company_by_name({
                "name": extracted_name,
                "location": item.get("extracted_location") or "Penang",
                "sector": "TBD",
                "status": "Discovered",
                "phase": "Verification Pending",
                "is_auto_detected": True,
                "needs_review": True,
                "latest_news": item.get("title", "")[:300],
                "source_url": item.get("source_url", "")
            })
            if new_comp:
                company_id = new_comp["id"]
                existing_companies[extracted_name.lower()] = new_comp
                print(f"  [NEW COMPANY] {extracted_name} ({item.get('extracted_location','?')})")

        if company_id:
            if item.get("detected_by") in ["rss", "mida", "penang", "bursa", "company_page"]:
                result = insert_news_item({
                    "company_id": company_id,
                    "title": item["title"],
                    "body": item.get("body", ""),
                    "source": item["source"],
                    "source_url": item.get("source_url", ""),
                    "published_at": item.get("published_at", ""),
                    "detected_by": item.get("detected_by", "scraper")
                })
                if result:
                    new_news += 1
            elif item.get("detected_by") == "jobs":
                result = insert_job({
                    "company_id": company_id,
                    "title": item["title"],
                    "job_url": item.get("source_url", ""),
                    "source": item["source"],
                    "location": item.get("extracted_location", ""),
                    "posted_at": item.get("published_at", datetime.now().isoformat())
                })
                if result:
                    new_jobs += 1

    print(f"  New news items: {new_news}, New job listings: {new_jobs}")


if __name__ == "__main__":
    print("=" * 60)
    print(f"  GREENFIELD DATA PIPELINE - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    print("\n  [PHASE 1] Running scrapers...")
    all_items = run_all_scrapers()

    print(f"\n  [PHASE 2] Processing {len(all_items)} items...")
    process_and_store(all_items)

    print("\n  [CLEANUP] Removing old job listings...")
    deactivate_old_jobs()

    print("\n  [DONE] Pipeline complete at", datetime.now().strftime("%H:%M:%S"))
