"""RSS scraper for Malaysian business news feeds."""
import feedparser
from datetime import datetime
from typing import List, Dict
from scrapers.base_scraper import BaseScraper

RSS_FEEDS = {
    "The Star Business": "https://www.thestar.com.my/rss/business",
    "NST Business": "https://www.nst.com.my/business/rss.xml",
    "Free Malaysia Today Business": "https://www.freemalaysiatoday.com/category/business/feed/",
}

LOCATION_KEYWORDS = [
    "Kulim", "Kulim Hi-Tech", "KHTP",
    "Batu Kawan", "BKIP", "Valdor",
    "Bayan Lepas", "Bayan Lepas FIZ", "Penang",
]

TRIGGER_KEYWORDS = [
    "factory", "plant", "manufacturing", "investment", "expansion",
    "groundbreaking", "ground breaking", "inaugurat", "opens facility",
    "new facility", "semiconductor", "medical device", "industrial park",
]

class RSSScraper(BaseScraper):
    def __init__(self):
        super().__init__("RSS")

    def scrape(self) -> List[Dict]:
        results = []
        for source_name, feed_url in RSS_FEEDS.items():
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:20]:
                    title = entry.get("title", "")
                    summary = entry.get("summary", "")
                    link = entry.get("link", "")
                    published = entry.get("published", datetime.now().isoformat())
                    full_text = (title + " " + summary).lower()
                    if any(kw.lower() in full_text for kw in LOCATION_KEYWORDS) or \
                       any(kw.lower() in full_text for kw in TRIGGER_KEYWORDS):
                        results.append({
                            "source": source_name,
                            "title": title,
                            "body": summary[:500] if summary else "",
                            "source_url": link,
                            "published_at": published,
                            "raw_text": full_text,
                            "detected_by": "rss"
                        })
            except Exception as e:
                print(f"[RSS] Error fetching {source_name}: {e}")
        return results
