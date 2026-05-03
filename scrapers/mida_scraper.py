"""MIDA (Malaysian Investment Development Authority) press release scraper."""
from typing import List, Dict
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper

MIDA_PRESS_URL = "https://www.mida.gov.my/media-release/"

class MIDAScraper(BaseScraper):
    def __init__(self):
        super().__init__("MIDA")

    def scrape(self) -> List[Dict]:
        results = []
        html = self.fetch(MIDA_PRESS_URL)
        if not html:
            return results

        soup = BeautifulSoup(html, "lxml")
        articles = soup.select("article, .post, .news-item, .media-release-item")[:15]

        for article in articles:
            title_el = article.select_one("h2, h3, .title, a")
            link_el = article.select_one("a[href]")
            date_el = article.select_one("time, .date, .published")

            title = title_el.get_text(strip=True) if title_el else ""
            link = link_el.get("href", "") if link_el else ""
            if link and link.startswith("/"):
                link = f"https://www.mida.gov.my{link}"
            date_str = date_el.get_text(strip=True) if date_el else ""

            if title:
                results.append({
                    "source": "MIDA",
                    "title": title,
                    "body": title,
                    "source_url": link,
                    "published_at": date_str,
                    "raw_text": title.lower(),
                    "detected_by": "mida"
                })

        return results
