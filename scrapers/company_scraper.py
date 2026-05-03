"""Direct company press release pages scraper."""
from typing import List, Dict
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper

COMPANY_PRESS_PAGES = {
    "AIXTRON": "https://www.aixtron.com/en/news",
    "AMD": "https://www.amd.com/en/newsroom.html",
    "UMediC": "https://www.umedic.com.my/news-events/",
    "AT&S": "https://ats.net/newsroom/",
}

class CompanyScraper(BaseScraper):
    def __init__(self):
        super().__init__("Company")

    def scrape(self) -> List[Dict]:
        results = []
        for company, url in COMPANY_PRESS_PAGES.items():
            html = self.fetch(url)
            if not html:
                continue

            soup = BeautifulSoup(html, "lxml")
            articles = soup.select("article, .post, .news-item, .press-item, .teaser, .card")[:10]

            for article in articles:
                title_el = article.select_one("h2, h3, .title, .headline, a")
                link_el = article.select_one("a[href]")
                date_el = article.select_one("time, .date, .published, .meta")

                title = title_el.get_text(strip=True) if title_el else ""
                link = link_el.get("href", "") if link_el else ""
                if link and link.startswith("/"):
                    base = url.split("/en/")[0] if "/en/" in url else url.split(".com")[0] + ".com"
                    link = f"{base}{link}"
                date_str = date_el.get_text(strip=True) if date_el else ""

                if title and any(kw in title.lower() for kw in ["malaysia", "penang", "kulim", "batu kawan", "bayan lepas", "expansion", "new plant", "factory", "facility"]):
                    results.append({
                        "source": company,
                        "title": title,
                        "body": title,
                        "source_url": link,
                        "published_at": date_str,
                        "raw_text": title.lower(),
                        "detected_by": "company_page"
                    })

        return results
