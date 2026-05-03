"""Bursa Malaysia company announcement scraper for listed companies."""
import feedparser
from typing import List, Dict
from scrapers.base_scraper import BaseScraper

BURSA_RSS = "https://www.bursamalaysia.com/market_information/announcements/company_announcement"

TRACKED_LISTED_COMPANIES = [
    "UMediC", "UMC", "umedic",
]

class BursaScraper(BaseScraper):
    def __init__(self):
        super().__init__("Bursa")

    def scrape(self) -> List[Dict]:
        results = []
        html = self.fetch(BURSA_RSS)
        if not html:
            return results

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")

        rows = soup.select("table tr, .announcement-row, .data-row")[:30]
        for row in rows:
            cells = row.select("td, .cell")
            if len(cells) < 2:
                continue

            title = cells[0].get_text(strip=True) if cells else ""
            date_str = cells[1].get_text(strip=True) if len(cells) > 1 else ""
            link_el = row.select_one("a[href]")
            link = link_el.get("href", "") if link_el else ""

            for company in TRACKED_LISTED_COMPANIES:
                if company.lower() in title.lower():
                    results.append({
                        "source": "Bursa Malaysia",
                        "title": title,
                        "body": f"Bursa announcement: {title}",
                        "source_url": link,
                        "published_at": date_str,
                        "raw_text": title.lower(),
                        "detected_by": "bursa"
                    })
                    break

        return results
