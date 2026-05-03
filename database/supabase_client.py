"""
Supabase Client Wrapper for Greenfield Factory Tracker
Phase 2 & 4: Database read/write + donation unlock management
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import uuid
import random
import string
from datetime import datetime

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qoncvdcyypwhogrqzesm.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "sb_publishable_omF5no32CBvoK2nBqgjCRg_3VlDj4lp")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# Client instances
anon_client: Client = None
service_client: Client = None

def get_anon_client() -> Client:
    """Get public (anon) Supabase client for read operations."""
    global anon_client
    if anon_client is None:
        anon_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    return anon_client

def get_service_client() -> Client:
    """Get service-role client for write operations (requires service key)."""
    global service_client
    if not SUPABASE_SERVICE_KEY:
        return get_anon_client()  # fallback
    if service_client is None:
        service_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return service_client

# ==================== COMPANIES ====================

def get_all_companies():
    """Fetch all companies from Supabase."""
    client = get_anon_client()
    resp = client.table("companies").select("*").order("sort_order").execute()
    return resp.data or []

def get_company_by_name(name: str):
    """Look up company by name."""
    client = get_anon_client()
    resp = client.table("companies").select("*").eq("name", name).execute()
    data = resp.data
    return data[0] if data else None

def insert_company(data: dict):
    """Insert a new company record."""
    client = get_service_client()
    resp = client.table("companies").insert(data).execute()
    return resp.data[0] if resp.data else None

def update_company(company_id: str, data: dict):
    """Update an existing company."""
    client = get_service_client()
    resp = client.table("companies").update(data).eq("id", company_id).execute()
    return resp.data[0] if resp.data else None

def upsert_company_by_name(data: dict):
    """Insert company if not exists, update if exists (match by name)."""
    existing = get_company_by_name(data.get("name", ""))
    if existing:
        return update_company(existing["id"], data)
    else:
        return insert_company(data)

# ==================== MILESTONES ====================

def get_milestones_for_company(company_id: str):
    """Get milestones for a specific company."""
    client = get_anon_client()
    resp = client.table("milestones").select("*").eq("company_id", company_id).order("sort_order").execute()
    return resp.data or []

def insert_milestone(data: dict):
    """Insert a milestone record."""
    client = get_service_client()
    resp = client.table("milestones").insert(data).execute()
    return resp.data[0] if resp.data else None

def delete_milestones_for_company(company_id: str):
    """Remove all milestones for a company (for re-seeding)."""
    client = get_service_client()
    client.table("milestones").delete().eq("company_id", company_id).execute()

def seed_milestones_for_company(company_id: str, milestones: list):
    """Replace all milestones for a company."""
    delete_milestones_for_company(company_id)
    for i, m in enumerate(milestones):
        m["company_id"] = company_id
        m["sort_order"] = i
        insert_milestone(m)

# ==================== NEWS ====================

def get_news_for_company(company_id: str, limit: int = 10):
    """Get recent news items for a company."""
    client = get_anon_client()
    resp = client.table("news_items").select("*").eq("company_id", company_id).order("created_at", desc=True).limit(limit).execute()
    return resp.data or []

def get_all_recent_news(limit: int = 30):
    """Get most recent news across all companies."""
    client = get_anon_client()
    resp = client.table("news_items").select("*, companies(name, location)").order("created_at", desc=True).limit(limit).execute()
    return resp.data or []

def insert_news_item(data: dict):
    """Insert a news item, return if it's new (not duplicate)."""
    client = get_service_client()
    # Check for duplicate (same title + company)
    existing = client.table("news_items").select("id").eq("company_id", data.get("company_id")).eq("title", data.get("title")).execute()
    if existing.data:
        return None  # duplicate, skip
    
    resp = client.table("news_items").insert(data).execute()
    return resp.data[0] if resp.data else None

# ==================== JOBS ====================

def get_jobs_for_company(company_id: str):
    """Get active job listings for a company."""
    client = get_service_client()  # service role bypasses RLS on jobs
    resp = client.table("jobs").select("*").eq("company_id", company_id).eq("is_active", True).order("created_at", desc=True).execute()
    return resp.data or []

def get_all_jobs(limit: int = 100):
    """Get all active job listings."""
    client = get_service_client()
    resp = client.table("jobs").select("*, companies(name, location)").eq("is_active", True).order("created_at", desc=True).limit(limit).execute()
    return resp.data or []

def insert_job(data: dict):
    """Insert a job listing."""
    client = get_service_client()
    # Check for duplicate URL
    existing = client.table("jobs").select("id").eq("job_url", data.get("job_url")).execute()
    if existing.data:
        return None  # duplicate
    
    resp = client.table("jobs").insert(data).execute()
    return resp.data[0] if resp.data else None

def deactivate_old_jobs():
    """Mark jobs older than 30 days as inactive."""
    client = get_service_client()
    client.table("jobs").update({"is_active": False}).lt("created_at", "now() - interval '30 days'").eq("is_active", True).execute()

# ==================== JOB ASSISTANT QUERIES (Phase 2 + v1.0.1 RPC) ====================

def _rpc(func_name: str, params: dict = None):
    """Call Supabase RPC function via anon client (SECURITY DEFINER bypasses RLS)."""
    client = get_anon_client()
    resp = client.rpc(func_name, params or {}).execute()
    return resp.data or []

def get_jobs_preview():
    """Get preview counts by company (no links) — v1.0.1: uses RPC."""
    rows = _rpc("get_public_jobs")
    preview = {}
    for row in rows:
        name = row.get("company_name", "Unknown")
        if name not in preview:
            preview[name] = {"count": 0, "zone": row.get("company_location", "?")}
        preview[name]["count"] += 1
    return preview

def get_jobs_by_zone(zone: str):
    """Get all active jobs in a zone with link verification status."""
    rows = _rpc("get_public_jobs", {"zone_filter": zone})
    return _enrich_jobs(rows)

def get_jobs_by_company(company_name: str):
    """Get all active jobs for a company."""
    rows = _rpc("get_public_jobs", {"company_name_filter": company_name})
    return _enrich_jobs(rows)

def get_jobs_by_category(category: str):
    """Get all active jobs in a category across zones."""
    rows = _rpc("get_public_jobs", {"category_filter": category})
    return _enrich_jobs(rows)

def get_jobs_by_zone_and_category(zone: str, category: str):
    """Get active jobs in a zone filtered by category."""
    rows = _rpc("get_public_jobs", {"zone_filter": zone, "category_filter": category})
    return _enrich_jobs(rows)

def _enrich_jobs(jobs: list) -> list:
    """Add verification status flag to each job."""
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    for job in jobs:
        verified_at = job.get("last_verified")
        if verified_at:
            if isinstance(verified_at, str):
                verified_at = datetime.fromisoformat(verified_at.replace("Z", "+00:00"))
            job["needs_verification"] = (now - verified_at) > timedelta(days=7)
        else:
            job["needs_verification"] = True
    return jobs

def get_distinct_categories():
    """Get list of available categories that have active jobs — v1.0.1: uses RPC."""
    rows = _rpc("get_public_categories")
    return [r["category"] for r in rows if r.get("category")]

def update_job_verification(job_id: str):
    """Update the last_verified timestamp for a job — service role required."""
    sc = get_service_client()
    sc.table("jobs").update({"last_verified": "now()"}).eq("id", job_id).execute()

# ==================== DONATION / UNLOCK SYSTEM ====================

def generate_unlock_code(length: int = 8) -> str:
    """Generate a random unlock code."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

def create_unlock_code(email: str = "", ko_fi_ref: str = "") -> str:
    """Create a new unlock code and store in DB."""
    code = generate_unlock_code()
    client = get_service_client()
    data = {
        "code": code,
        "email": email,
        "ko_fi_reference": ko_fi_ref
    }
    client.table("donation_codes").insert(data).execute()
    return code

def verify_unlock_code(code: str) -> bool:
    """v1.0.1: Verify via SECURITY DEFINER RPC (no service key needed)."""
    rows = _rpc("verify_donation_code", {"code_input": code.upper().strip()})
    return len(rows) > 0 and rows[0].get("is_valid", False)

def mark_code_used(code: str) -> bool:
    """v1.0.2: Mark via SECURITY DEFINER RPC (no service key needed)."""
    result = _rpc("consume_donation_code", {"code_input": code.upper().strip()})
    return bool(result)

def get_unlock_code_by_email(email: str):
    """Find unlock codes by donor email."""
    sc = get_service_client()
    resp = sc.table("donation_codes").select("*").eq("email", email).order("created_at", desc=True).execute()
    return resp.data or []

# ==================== SCRAPE LOGS ====================

def log_scrape_run(source: str, status: str, items_found: int = 0, items_new: int = 0, errors: str = None, duration: float = None):
    """Record scraper execution in logs."""
    client = get_service_client()
    data = {
        "source": source,
        "status": status,
        "items_found": items_found,
        "items_new": items_new,
        "errors": errors,
        "duration_seconds": duration
    }
    client.table("scrape_logs").insert(data).execute()

def get_last_successful_scrape(source: str):
    """v1.0.5: Get timestamp of last successful scrape for a source."""
    client = get_anon_client()
    resp = client.table("scrape_logs").select("run_at").eq("source", source).eq("status", "success").order("run_at", desc=True).limit(1).execute()
    rows = resp.data or []
    return rows[0].get("run_at") if rows else None

# ==================== TESTS ====================

if __name__ == "__main__":
    print("Supabase Client Test")
    print(f"URL: {SUPABASE_URL}")
    
    # Test connection
    try:
        companies = get_all_companies()
        print(f"Companies in DB: {len(companies)}")
    except Exception as e:
        print(f"Connection error: {e}")
        print("Run seed_supabase.py first to populate data.")
    
    # Test unlock code flow
    code = create_unlock_code(email="test@example.com")
    print(f"Generated code: {code}")
    print(f"Valid: {verify_unlock_code(code)}")
