"""Job posting scraper for tracked companies in Kulim, Batu Kawan, Bayan Lepas.

Searches publicly visible job portal pages for companies we track.
LinkedIn scraping is blocked by ToS; we use Google job snippets and 
publicly accessible career pages instead.
"""

from typing import List, Dict
import requests as req_lib
from scrapers.base_scraper import BaseScraper

TRACKED_COMPANIES = [
    "Novolyte", "AIXTRON", "UMediC", "Medtronic", "AMD",
    "Monolithic Power Systems", "Bitdeer", "congatec",
    "V-Chip", "Hanic", "Ferrotec", "Ichia", "AT&S",
    "Hyundai", "Unigen", "Pivotal", "Hotayi", "Benchmark", "Chipbond"
]

LOCATIONS = ["Kulim", "Batu Kawan", "Bayan Lepas", "Penang"]

class JobScraper(BaseScraper):
    def __init__(self):
        super().__init__("Job")

    def scrape(self) -> List[Dict]:
        """Search Google for publicly indexed job listings."""
        results = []
        for company in TRACKED_COMPANIES[:5]:  # Limit to avoid rate-limiting
            for loc in LOCATIONS[:2]:
                query = f"{company} jobs {loc}"
                url = f"https://www.google.com/search?q={requests.utils.quote(query)}&tbm=nws"
                try:
                    html = self.fetch(url)
                    if html:
                        from bs4 import BeautifulSoup
                        import requests as req_lib
                        soup = BeautifulSoup(html, "lxml")
                        for link in soup.select("a[href]"):
                            href = link.get("href", "")
                            if href.startswith("http") and "google" not in href:
                                results.append({
                                    "source": "Google Jobs",
                                    "title": f"{company} - {loc}",
                                    "body": link.get_text(strip=True),
                                    "source_url": href,
                                    "published_at": "",
                                    "raw_text": f"{company} {loc} job".lower(),
                                    "detected_by": "jobs"
                                })
                                break  # One result per company-location pair
                except Exception as e:
                    print(f"[Job] Error for {company} {loc}: {e}")

        return results
