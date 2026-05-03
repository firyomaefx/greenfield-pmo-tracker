"""Deduplication engine for scraped news items."""
from typing import List, Dict
import hashlib
from datetime import datetime

def hash_item(item: Dict) -> str:
    """Create a content-based hash for deduplication."""
    key = f"{item.get('title','')}|{item.get('source','')}|{item.get('source_url','')}"
    return hashlib.md5(key.encode()).hexdigest()[:16]

def deduplicate(items: List[Dict], known_hashes: set = None) -> List[Dict]:
    """Remove duplicate items by content hash."""
    if known_hashes is None:
        known_hashes = set()

    unique = []
    for item in items:
        h = hash_item(item)
        if h not in known_hashes:
            known_hashes.add(h)
            unique.append(item)
    return unique
