"""NLP processor: auto-detect new companies and classify news relevance."""
from typing import List, Dict, Optional, Tuple
import re

LOCATION_PATTERNS = [
    (r"Kulim\s+Hi[-\s]?Tech\s+Park", "Kulim"),
    (r"\bKHTP\b", "Kulim"),
    (r"\bKulim\b", "Kulim"),
    (r"Batu\s+Kawan", "Batu Kawan"),
    (r"\bBKIP\b", "Batu Kawan"),
    (r"\bValdor\b", "Batu Kawan"),
    (r"Bayan\s+Lepas", "Bayan Lepas"),
    (r"Bayan\s+Lepas\s+FIZ", "Bayan Lepas"),
    (r"GBS\s+by\s+the\s+Sea", "Bayan Lepas"),
    (r"\bPenang\b", "Bayan Lepas"),
]

NEW_COMPANY_PATTERNS = [
    (r"(?:announces|announced|opens|inaugurates|breaks? ground)\s+(?:new\s+)?(?:plant|facility|factory|manufacturing|production)\s+(?:(?:in|at)\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,4})", "direct_announcement"),
    (r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})\s+(?:breaks ground|groundbreaking|opens new|inaugurates|announces\s+(?:new\s+)?(?:plant|facility))", "company_first"),
    (r"(?:investment\s+by|investment\s+from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})", "investment_by"),
    (r"(?:RM\s*[0-9,.]+(?:million|billion)\s+investment\s+(?:by|from))\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})", "investment_rm"),
]

SKIP_NAMES = {"Mida", "Penang", "Malaysia", "Kedah", "Federal", "State", "The Edge", "The Star", "NST", "FMT", "Bernama", "Reuters"}

def extract_location(text: str) -> Optional[str]:
    for pattern, location in LOCATION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return location
    return None

def extract_company_name(text: str) -> Optional[str]:
    for pattern, tag in NEW_COMPANY_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            if len(name) > 3 and name not in SKIP_NAMES and not name.startswith("The "):
                return name
    return None

def extract_investment_amount(text: str) -> Optional[str]:
    patterns = [
        r"RM\s*([0-9,.]+)\s*(million|billion)",
        r"RM([0-9,.]+)\s*([mM]|[bB])",
        r"(?:EUR|USD)\s*([0-9,.]+)\s*(million|billion)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            amount = match.group(1)
            unit = match.group(2).lower()
            prefix = ""
            if "RM" in pattern:
                prefix = "RM "
            elif "EUR" in pattern:
                prefix = "EUR "
            elif "USD" in pattern:
                prefix = "USD "
            return f"{prefix}{amount} {unit}"
    return None

def extract_jobs_number(text: str) -> Optional[int]:
    patterns = [
        r"([0-9,]+)\s*(?:new\s+)?(?:high[-\s]?value|high[-\s]?skilled|skilled)?\s*jobs",
        r"employ(?:s|ment|ees)?\s+(?:of\s+)?(?:over\s+)?([0-9,]+)",
        r"creating\s+(?:about\s+)?(?:over\s+)?([0-9,]+)\s+jobs",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1).replace(",", ""))
            except:
                pass
    return None

def classify_news_item(item: Dict) -> Dict:
    text = item.get("raw_text", "")
    text += " " + item.get("title", "")
    text += " " + item.get("body", "")

    item["extracted_location"] = extract_location(text)
    item["extracted_company"] = extract_company_name(text)
    item["extracted_investment"] = extract_investment_amount(text)
    item["extracted_jobs"] = extract_jobs_number(text)

    is_new = bool(item["extracted_company"])
    item["is_new_company"] = is_new
    item["needs_review"] = is_new

    return item
