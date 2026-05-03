## Greenfield PMO Tracker v1.0.1 — Patch Release

### Critical Fixes
- **Donation unlock now works on Streamlit Cloud** — Verify and consume codes via SECURITY DEFINER RPC (no service key needed)
- **Job links now accessible** — All 5 job query functions switched from service client to anon client calling RPC functions
- **Scraper schedule corrected** — 12h → 6h cron interval

### Technical Details
Four new Supabase SQL functions:
- `verify_donation_code()` — Check unlock codes without service key
- `consume_donation_code()` — Mark codes as used without service key
- `get_public_jobs()` — Full job listing access bypassing RLS
- `get_public_categories()` — Active categories list bypassing RLS

All functions use SECURITY DEFINER with search_path='' for safety.

### Manual Step Required After Deploy
Run the 4 CREATE FUNCTION blocks from database/schema.sql in Supabase SQL Editor.

### Files Changed (4)
- database/schema.sql — 4 new RPC functions appended
- database/supabase_client.py — 8 query rewrites (service→anon+RPC)
- .github/workflows/scrape.yml — cron: 12h → 6h
- VERSION — 1.0.0 → 1.0.1
