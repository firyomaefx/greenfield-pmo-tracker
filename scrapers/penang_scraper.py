"""InvestPenang press release scraper for new project announcements."""
from typing import List, Dict
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper

PENANG_PRESS_URL = "https://investpenang.gov.my/newsroom/"

class PenangScraper(BaseScraper):
    def __init__(self):
        super().__init__("Penang")

    def scrape(self) -> List[Dict]:
        results = []
        html = self.fetch(PENANG_PRESS_URL)
        if not html:
            return results

        soup = BeautifulSoup(html, "lxml")
        articles = soup.select("article, .post, .news-item, .card, .listing-item")[:15]

        for article in articles:
            title_el = article.select_one("h2, h3, .title, a")
            link_el = article.select_one("a[href]")
            date_el = article.select_one("time, .date, .published")

            title = title_el.get_text(strip=True) if title_el else ""
            link = link_el.get("href", "") if link_el else ""
            if link and link.startswith("/"):
                link = f"https://investpenang.gov.my{link}"
            date_str = date_el.get_text(strip=True) if date_el else ""

            if title:
                results.append({
                    "source": "InvestPenang",
                    "title": title,
                    "body": title,
                    "source_url": link,
                    "published_at": date_str,
                    "raw_text": title.lower(),
                    "detected_by": "penang"
                })

        return results
