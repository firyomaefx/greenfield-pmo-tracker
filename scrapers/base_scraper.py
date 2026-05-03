"""Base scraper with rate limiting, user-agent rotation, and error handling."""
import time
import random
import requests
from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from datetime import datetime

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
]

class BaseScraper(ABC):
    def __init__(self, name: str, min_delay: float = 2.0, max_delay: float = 5.0):
        self.name = name
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request = 0.0
        self.session = requests.Session()

    def _random_delay(self):
        elapsed = time.time() - self.last_request
        if elapsed < self.min_delay:
            sleep_time = random.uniform(self.min_delay - elapsed, self.max_delay)
            time.sleep(sleep_time)
        self.last_request = time.time()

    def _headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ms;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "DNT": "1",
        }

    def fetch(self, url: str, timeout: int = 30) -> Optional[str]:
        self._random_delay()
        try:
            resp = self.session.get(url, headers=self._headers(), timeout=timeout, allow_redirects=True)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            print(f"[{self.name}] Fetch error for {url}: {str(e)[:100]}")
            return None

    @abstractmethod
    def scrape(self) -> List[Dict]:
        pass
