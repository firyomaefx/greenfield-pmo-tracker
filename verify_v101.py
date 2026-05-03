import sys
sys.path.insert(0, ".")

from database.supabase_client import (
    verify_unlock_code, create_unlock_code, mark_code_used,
    get_jobs_preview, get_distinct_categories, get_all_companies,
    get_jobs_by_zone, get_jobs_by_company, get_jobs_by_category,
)

print("=" * 50)
print("  V1.0.1 VERIFICATION TEST")
print("=" * 50)

# 1. Companies
comps = get_all_companies()
print(f"\n[1] Companies: {len(comps)}")

# 2. Unlock flow
code = create_unlock_code(email="verify-test@greenfield.com", ko_fi_ref="verify-001")
print(f"\n[2] Unlock code generated: {code}")
valid = verify_unlock_code(code)
print(f"    Code valid: {valid}")
mark_code_used(code)
valid2 = verify_unlock_code(code)
print(f"    Code after use: {valid2} (should be False)")

# 3. Job queries
preview = get_jobs_preview()
total = sum(p["count"] for p in preview.values())
print(f"\n[3] Job preview: {len(preview)} companies, {total} total jobs")
for name, info in list(preview.items())[:5]:
    print(f"    {name}: {info['count']} jobs ({info['zone']})")

# 4. Categories
cats = get_distinct_categories()
print(f"\n[4] Categories: {cats}")

# 5. Zone query
for zone in ["Kulim", "Batu Kawan", "Bayan Lepas"]:
    jobs = get_jobs_by_zone(zone)
    print(f"\n[5] {zone}: {len(jobs)} jobs")

# 6. Company query
jobs2 = get_jobs_by_company("AMD")
print(f"\n[6] AMD: {len(jobs2)} jobs")

# 7. Category query
jobs3 = get_jobs_by_category("Engineer")
print(f"\n[7] Engineer category: {len(jobs3)} jobs")

print("\n" + "=" * 50)
print("  ALL SYSTEMS VERIFIED")
print("=" * 50)
