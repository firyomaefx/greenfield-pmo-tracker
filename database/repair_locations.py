"""
v1.1.1: Direct DB repair — fixes location data without re-seeding.
Updates AIXTRON to Penang, sets verification flags on all 20 companies.
"""
import sys
sys.path.insert(0, "C:\\Users\\Pedot\\OneDrive\\Documents")

from database.supabase_client import get_service_client, get_all_companies

LOCATION_AUDIT = {
    # All 20 companies — verified True/False based on research
    "Novolyte": {"verified": True,  "confirmed": "Kulim"},
    "AIXTRON":  {"verified": False, "confirmed": "Penang"},     # FIX: was Kulim
    "Medtronic": {"verified": True,  "confirmed": "Kulim"},
    "Ferrotec": {"verified": True,  "confirmed": "Kulim"},
    "Ichia Technologies": {"verified": True,  "confirmed": "Kulim"},
    "AT&S": {"verified": True,  "confirmed": "Kulim"},
    "Hyundai Motor": {"verified": True,  "confirmed": "Kulim"},
    "Unigen": {"verified": True,  "confirmed": "Kulim"},
    "Pivotal Systems": {"verified": True,  "confirmed": "Kulim"},
    "UMediC Group Berhad": {"verified": True,  "confirmed": "Batu Kawan"},
    "Hotayi Electronic": {"verified": True,  "confirmed": "Batu Kawan"},
    "Benchmark Precision Technologies": {"verified": True,  "confirmed": "Batu Kawan"},
    "Chipbond Technology": {"verified": True,  "confirmed": "Batu Kawan"},
    "AMD": {"verified": True,  "confirmed": "Bayan Lepas"},
    "Monolithic Power Systems (MPS)": {"verified": False, "confirmed": None},  # unknown sub-zone
    "Bitdeer Technologies": {"verified": False, "confirmed": None},
    "congatec": {"verified": False, "confirmed": None},
    "V-Chip": {"verified": False, "confirmed": None},
    "Hanic": {"verified": False, "confirmed": None},
    "Penang ATE Campus": {"verified": True,  "confirmed": "Bayan Lepas"},
}

client = get_service_client()

print("=" * 60)
print("  LOCATION REPAIR v1.1.1")
print("=" * 60)

companies = get_all_companies()
fixes = 0

for c in companies:
    name = c.get("name", "")
    audit = LOCATION_AUDIT.get(name)
    if not audit:
        continue

    cid = c["id"]
    current_loc = c.get("location", "")
    current_verified = c.get("location_verified", True)

    updates = {}

    # Fix wrong location
    if audit["confirmed"] and current_loc != audit["confirmed"]:
        updates["location"] = audit["confirmed"]
        print(f"  FIX: {name}: {current_loc} -> {audit['confirmed']}")

    # Set verification flag
    if current_verified != audit["verified"]:
        updates["location_verified"] = audit["verified"]
        status = "VERIFIED" if audit["verified"] else "UNVERIFIED"
        print(f"  FLAG: {name}: location_verified = {status}")

    if updates:
        client.table("companies").update(updates).eq("id", cid).execute()
        fixes += 1

print(f"\n  Total fixes applied: {fixes}")
print(f"  Done. Streamlit should now show AIXTRON as Penang.")

# Also fix the CHECK constraint to allow 'Penang'
print("\n  Fixing CHECK constraint...")
try:
    client.sql("ALTER TABLE public.companies DROP CONSTRAINT IF EXISTS companies_location_check").execute()
    client.sql(
        "ALTER TABLE public.companies ADD CONSTRAINT companies_location_check "
        "CHECK (location IN ('Kulim', 'Batu Kawan', 'Bayan Lepas', 'Penang'))"
    ).execute()
    print("  CHECK constraint updated: Penang zone allowed.")
except Exception as e:
    print(f"  Could not update constraint via SQL: {e}")
    print("  Run this in Supabase SQL Editor:")
    print("  ALTER TABLE public.companies DROP CONSTRAINT IF EXISTS companies_location_check;")
    print("  ALTER TABLE public.companies ADD CONSTRAINT companies_location_check CHECK (location IN ('Kulim', 'Batu Kawan', 'Bayan Lepas', 'Penang'));")
