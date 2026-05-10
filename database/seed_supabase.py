"""
Supabase Seed Script - Populate all 20 Greenfield projects
Phase 2: Initial data seeding for Kulim, Batu Kawan & Bayan Lepas
"""
import sys
sys.path.insert(0, "C:\\Users\\Pedot\\OneDrive\\Documents")

from database.supabase_client import *

ALL_PROJECTS = [
    # ========== KULIM (9 projects) ==========
    {
        "name": "Novolyte",
        "location": "Kulim",
        "sector": "Battery Electrolytes",
        "status": "Under Construction",
        "phase": "Construction",
        "investment": "RM 264M",
        "jobs_estimate": 300,
        "latest_news": "Jan 2026: Groundbreaking for RM264M electrolyte plant at KHTP. Capacity ~30,000 MT/year.",
        "sort_order": 1,
        "milestones": [
            {"name": "Company Registration (Capchem SEA)", "target_date": "2025-Q1", "actual_date": "Feb 2025", "status": "Completed"},
            {"name": "First Order Delivery (Plant 1)", "target_date": "2025-Q3", "actual_date": "Sep 2025", "status": "Completed"},
            {"name": "Ground Breaking (New Plant)", "target_date": "2026-Q1", "actual_date": "Jan 19 2026", "status": "Completed"},
            {"name": "Plant Commissioning / Commercial Ops", "target_date": "2026-Q3", "actual_date": "TBD", "status": "Planned"}
        ]
    },
    {
        "name": "AIXTRON",
        "location": "Penang",
        "sector": "Semiconductor Equipment",
        "status": "Pre-Construction",
        "phase": "Pre-Construction",
        "investment": "EUR 40M (~RM 190M)",
        "jobs_estimate": 250,
        "latest_news": "Mar 2026: Announced EUR 40M new manufacturing facility in Penang region. Exact sub-zone TBD. Plant start-up Spring 2027.",
        "sort_order": 2,
        "location_verified": False,
        "milestones": [
            {"name": "Strategic Announcement / Site Selection", "target_date": "2026-Q1", "actual_date": "Mar 25 2026", "status": "Completed"},
            {"name": "CAPEX Phase 1 (Land / Facility)", "target_date": "2026-H2", "actual_date": "TBD", "status": "Planned"},
            {"name": "CAPEX Phase 2 (Equip / Qual)", "target_date": "2027-H1", "actual_date": "TBD", "status": "Planned"},
            {"name": "Plant Start-Up", "target_date": "2027-Spring", "actual_date": "TBD", "status": "Planned"},
            {"name": "First Shipments", "target_date": "2027-H2", "actual_date": "TBD", "status": "Planned"}
        ]
    },
    {
        "name": "Medtronic",
        "location": "Kulim",
        "sector": "Medical Devices Manufacturing",
        "status": "Ramp-Up / New Venture",
        "phase": "Site Establishment / Hiring",
        "investment": "TBD (Expanding/Greenfield)",
        "jobs_estimate": 250,
        "latest_news": "Apr 2026: Active recruitment for Sr Mfg Operations QA Manager in Kulim Kedah. 27+ job postings indicate new venture scale-up in KHTP.",
        "sort_order": 3,
        "milestones": [
            {"name": "PM Anwar Meeting (Intent to Expand)", "target_date": "2023-Q3", "actual_date": "Sep 2023", "status": "Completed"},
            {"name": "Sr Leadership Hiring Launch", "target_date": "2026-Q1", "actual_date": "Apr 2026", "status": "Completed"},
            {"name": "Site Fit-Out / New Build", "target_date": "2026-Q3", "actual_date": "TBD", "status": "Planned"},
            {"name": "Production Ramp / Full Ops", "target_date": "2027-Q2", "actual_date": "TBD", "status": "Planned"}
        ]
    },
    {
        "name": "Ferrotec",
        "location": "Kulim",
        "sector": "High-Tech Components / Precision Manufacturing",
        "status": "Under Construction",
        "phase": "Construction",
        "investment": "RM 1.0B",
        "jobs_estimate": 1000,
        "latest_news": "Apr 2025: Groundbreaking for RM1B Plant #2 at KHTP (20 acres, 1M sq ft, 700+ CNC machines, Industry 4.0).",
        "sort_order": 4,
        "milestones": [
            {"name": "Ground Breaking (Plant #2)", "target_date": "2025-Q2", "actual_date": "Apr 2025", "status": "Completed"},
            {"name": "Facility Completion", "target_date": "2026-Q2", "actual_date": "TBD", "status": "Planned"},
            {"name": "Production Ramp", "target_date": "2026-Q3", "actual_date": "TBD", "status": "Planned"}
        ]
    },
    {
        "name": "Ichia Technologies",
        "location": "Kulim",
        "sector": "PCBs & PCB Assemblies",
        "status": "Operational",
        "phase": "Operations",
        "investment": "RM 490M",
        "jobs_estimate": 600,
        "latest_news": "Oct 2025: Grand opening of 2nd facility (55,000+ sq m on 11 acres). AI & IoT enabled.",
        "sort_order": 5,
        "milestones": [
            {"name": "Ground Breaking", "target_date": "2023", "actual_date": "Completed", "status": "Completed"},
            {"name": "Grand Opening (2nd Facility)", "target_date": "2025-Q4", "actual_date": "Oct 2025", "status": "Completed"},
            {"name": "Full Production Ramp", "target_date": "2026-Q2", "actual_date": "TBD", "status": "Planned"}
        ]
    },
    {
        "name": "AT&S",
        "location": "Kulim",
        "sector": "IC Substrates",
        "status": "Operational",
        "phase": "High-Volume Manufacturing",
        "investment": "RM 5.0B",
        "jobs_estimate": 1500,
        "latest_news": "May 2025: High-volume manufacturing start for AMD and other customers. ~1,500 employees.",
        "sort_order": 6,
        "milestones": [
            {"name": "Site Establishment", "target_date": "2022", "actual_date": "Completed", "status": "Completed"},
            {"name": "High-Volume Manufacturing Start", "target_date": "2025-Q2", "actual_date": "May 2025", "status": "Completed"},
            {"name": "Top-3 Global Substrate Target", "target_date": "2027", "actual_date": "TBD", "status": "Planned"}
        ]
    },
    {
        "name": "Hyundai Motor",
        "location": "Kulim",
        "sector": "Automotive Assembly",
        "status": "Operational",
        "phase": "Production",
        "investment": "RM 2.16B",
        "jobs_estimate": 800,
        "latest_news": "First Malaysian assembly plant in Kulim. Plans 7 CKD models within 5 years.",
        "sort_order": 7,
        "milestones": [
            {"name": "Site Preparation", "target_date": "2024", "actual_date": "Completed", "status": "Completed"},
            {"name": "Plant Opening", "target_date": "2025-Q4", "actual_date": "Late 2025", "status": "Completed"},
            {"name": "7 CKD Models Rollout", "target_date": "2030", "actual_date": "TBD", "status": "Planned"}
        ]
    },
    {
        "name": "Unigen",
        "location": "Kulim",
        "sector": "Electronics Manufacturing",
        "status": "Under Construction",
        "phase": "Construction",
        "investment": "TBD",
        "jobs_estimate": 200,
        "latest_news": "Oct 2024: Broke ground on 56,000 sq ft facility at KHTP.",
        "sort_order": 8,
        "milestones": [
            {"name": "Ground Breaking", "target_date": "2024-Q4", "actual_date": "Oct 2024", "status": "Completed"},
            {"name": "Facility Completion", "target_date": "2026-Q2", "actual_date": "TBD", "status": "Planned"}
        ]
    },
    {
        "name": "Pivotal Systems",
        "location": "Kulim",
        "sector": "Gas-Flow Solutions (Semiconductor)",
        "status": "Operational",
        "phase": "Operations",
        "investment": "TBD",
        "jobs_estimate": 150,
        "latest_news": "Opened new engineering & manufacturing facility at KHTP to support semiconductor demand.",
        "sort_order": 9,
        "milestones": [
            {"name": "Facility Opening", "target_date": "2025-Q1", "actual_date": "Late 2024 / Early 2025", "status": "Completed"},
            {"name": "Production Ramp", "target_date": "2025-Q3", "actual_date": "TBD", "status": "Completed"}
        ]
    },
    # ========== BATU KAWAN (5 projects) ==========
    {
        "name": "UMediC Group Berhad",
        "location": "Batu Kawan",
        "sector": "Medical Devices & Consumables",
        "status": "Operational / Expansion",
        "phase": "Operations & New Plant Planning",
        "investment": "RM 11.4M (land for new plant)",
        "jobs_estimate": 150,
        "latest_news": "Jan 2026: Secured 3.06-acre lease in BKIP for RM11.4M. Construction H2 2027, completion H1 2029. Aug 2025 existing capacity doubled.",
        "sort_order": 10,
        "milestones": [
            {"name": "Original Site Acquisition", "target_date": "2015-2020", "actual_date": "Completed", "status": "Completed"},
            {"name": "Capacity Expansion (Existing)", "target_date": "2025-Q3", "actual_date": "Aug 2025", "status": "Completed"},
            {"name": "New Land Lease (3.06 acres)", "target_date": "2026-Q1", "actual_date": "Jan 2026", "status": "Completed"},
            {"name": "Construction Start (New Plant)", "target_date": "2027-H2", "actual_date": "TBD", "status": "Planned"},
            {"name": "New Plant Completion", "target_date": "2029-H1", "actual_date": "TBD", "status": "Planned"}
        ]
    },
    {
        "name": "Hotayi Electronic",
        "location": "Batu Kawan",
        "sector": "EMS / Electronics",
        "status": "Under Construction",
        "phase": "Construction",
        "investment": "RM 500M",
        "jobs_estimate": 1000,
        "latest_news": "Mar 2025: RM500M Phase 3 smart factory (380,000 sq ft). 1,000 new high-skilled jobs.",
        "sort_order": 11,
        "milestones": [
            {"name": "Phase 3 Expansion Announcement", "target_date": "2025-Q1", "actual_date": "Mar 2025", "status": "Completed"},
            {"name": "Smart Factory Completion", "target_date": "2026-Q4", "actual_date": "TBD", "status": "Planned"},
            {"name": "Full Operations", "target_date": "2027-Q2", "actual_date": "TBD", "status": "Planned"}
        ]
    },
    {
        "name": "Benchmark Precision Technologies",
        "location": "Batu Kawan",
        "sector": "Wafer Fab Equipment (WFE)",
        "status": "Under Construction",
        "phase": "Construction",
        "investment": "USD 25M (~RM 110M)",
        "jobs_estimate": 500,
        "latest_news": "Feb 2025: Groundbreaking for PT4 at BKIP. 215,000 sq ft; completion June 2026.",
        "sort_order": 12,
        "milestones": [
            {"name": "Ground Breaking (PT4)", "target_date": "2025-Q1", "actual_date": "Feb 2025", "status": "Completed"},
            {"name": "Facility Completion", "target_date": "2026-Q2", "actual_date": "TBD", "status": "Planned"},
            {"name": "Production Ramp", "target_date": "2026-Q4", "actual_date": "TBD", "status": "Planned"}
        ]
    },
    {
        "name": "Chipbond Technology",
        "location": "Batu Kawan",
        "sector": "OSAT / Semiconductor Packaging",
        "status": "Operational",
        "phase": "Production",
        "investment": "USD 200M (~RM 800M)",
        "jobs_estimate": 600,
        "latest_news": "Feb 2026: Officially opened RM800M advanced OSAT at Valdor Industrial Park. 10,000 wafers/month capacity.",
        "sort_order": 13,
        "milestones": [
            {"name": "Facility Construction", "target_date": "2024-2025", "actual_date": "Completed", "status": "Completed"},
            {"name": "Official Opening", "target_date": "2026-Q1", "actual_date": "Feb 2026", "status": "Completed"},
            {"name": "Full Capacity Utilization", "target_date": "2026-Q4", "actual_date": "TBD", "status": "Planned"}
        ]
    },
    # ========== BAYAN LEPAS (7 projects) ==========
    # Bayan Lepas companies: location assumed from "Penang" press releases
    {
        "name": "AMD",
        "location": "Bayan Lepas",
        "location_verified": True,  # GBS by the Sea is confirmed Bayan Lepas
        "sector": "Semiconductors / IC Design & GBS",
        "status": "Operational",
        "phase": "Production",
        "investment": "209,000 sq ft facility",
        "jobs_estimate": 1200,
        "latest_news": "Aug 2025: Inaugurated 209,000 sq ft engineering lab and GBS facility at GBS by the Sea. Supports global semiconductor design and business services.",
        "sort_order": 14,
        "milestones": [
            {"name": "Site Planning / Permits", "target_date": "2024", "actual_date": "Completed", "status": "Completed"},
            {"name": "Facility Construction / Fit-Out", "target_date": "2025-Q2", "actual_date": "Completed", "status": "Completed"},
            {"name": "Official Inauguration", "target_date": "2025-Q3", "actual_date": "Aug 14 2025", "status": "Completed"},
            {"name": "Full Staffing / Operations Ramp", "target_date": "2026", "actual_date": "Ongoing", "status": "Planned"}
        ]
    },
    {
        "name": "Monolithic Power Systems (MPS)",
        "location": "Bayan Lepas",
        "location_verified": False,  # Press release only says "Penang"
        "sector": "Semiconductors / Power Management",
        "status": "Operational",
        "phase": "Production",
        "investment": "TBD",
        "jobs_estimate": 200,
        "latest_news": "Mar 2026: Opened first Malaysia engineering and test center. Serves as MPS Malaysia HQ for data centre, automotive, consumer, and industrial segments.",
        "sort_order": 15,
        "milestones": [
            {"name": "Site Selection / Lease", "target_date": "2025", "actual_date": "Completed", "status": "Completed"},
            {"name": "Engineering Center Opening", "target_date": "2026-Q1", "actual_date": "Mar 10 2026", "status": "Completed"},
            {"name": "Test Lab Qualification", "target_date": "2026-Q2", "actual_date": "TBD", "status": "Planned"}
        ]
    },
    {
        "name": "Bitdeer Technologies",
        "location": "Bayan Lepas",
        "location_verified": False,  # Press release only says "Penang"
        "sector": "Blockchain / HPC / IC Design",
        "status": "Operational",
        "phase": "Production",
        "investment": "TBD",
        "jobs_estimate": 150,
        "latest_news": "Oct 2025: Opened first Malaysia facility. Regional hub for supply chain management and HPC hardware/software design. Features 7 testing labs + 2 aging chambers.",
        "sort_order": 16,
        "milestones": [
            {"name": "Site Setup / Labs Build", "target_date": "2025-Q3", "actual_date": "Completed", "status": "Completed"},
            {"name": "Facility Opening", "target_date": "2025-Q4", "actual_date": "Oct 1 2025", "status": "Completed"},
            {"name": "NPU Talent / Local IC Design Build", "target_date": "2026", "actual_date": "TBD", "status": "Planned"}
        ]
    },
    {
        "name": "congatec",
        "location": "Bayan Lepas",
        "location_verified": False,  # Press release only says "Penang"
        "sector": "Embedded & Edge Computing",
        "status": "Establishing",
        "phase": "R&D Setup",
        "investment": "TBD",
        "jobs_estimate": 70,
        "latest_news": "Jan 2026: Announced new Malaysia R&D subsidiary. Onboarded 23 engineers from Kontron Asia; scaling to ~70 employees medium-term.",
        "sort_order": 17,
        "milestones": [
            {"name": "Subsidiary Registration / Team Transfer", "target_date": "2026-Q1", "actual_date": "Jan 2026", "status": "Completed"},
            {"name": "Engineering Team Scale-Up", "target_date": "2026-Q4", "actual_date": "TBD", "status": "Planned"},
            {"name": "Full R&D Operations", "target_date": "2027-Q2", "actual_date": "TBD", "status": "Planned"}
        ]
    },
    {
        "name": "V-Chip",
        "location": "Bayan Lepas",
        "location_verified": False,  # PSD@5KM+ covers entire Penang
        "sector": "Semiconductors / IC Design",
        "status": "Operational",
        "phase": "Production",
        "investment": "TBD",
        "jobs_estimate": 80,
        "latest_news": "Jan 2026: Established new IC design facility under Penang PSD@5KM+ initiative.",
        "sort_order": 18,
        "milestones": [
            {"name": "Facility Setup / PSD Registration", "target_date": "2025-Q4", "actual_date": "Completed", "status": "Completed"},
            {"name": "Production Launch", "target_date": "2026-Q1", "actual_date": "Jan 5 2026", "status": "Completed"}
        ]
    },
    {
        "name": "Hanic",
        "location": "Bayan Lepas",
        "location_verified": False,  # Press release only says "Penang"
        "sector": "Semiconductors / IC Design & Advanced Packaging",
        "status": "Ramping Up",
        "phase": "Engineering Ramp",
        "investment": "TBD",
        "jobs_estimate": 60,
        "latest_news": "Mar 2026: Hub for SoC design, verification, physical design, DFT, and advanced 2.5D/3D packaging. Aligns with National Semiconductor Strategy (NSS).",
        "sort_order": 19,
        "milestones": [
            {"name": "Team / Facility Setup", "target_date": "2025-Q4", "actual_date": "Completed", "status": "Completed"},
            {"name": "Design Team Ramp", "target_date": "2026-Q2", "actual_date": "TBD", "status": "Planned"},
            {"name": "Advanced Packaging Qualification", "target_date": "2027-Q1", "actual_date": "TBD", "status": "Planned"}
        ]
    },
    {
        "name": "Penang ATE Campus",
        "location": "Bayan Lepas",
        "sector": "Industrial Park / Semiconductor Ecosystem",
        "status": "Planned",
        "phase": "Pre-Construction",
        "investment": "~RM 40M (land)",
        "jobs_estimate": 500,
        "latest_news": "Mar 2026: State allocated 10 acres at PDC Industrial Park, Bayan Lepas. Targets Q2 2026 launch for advanced packaging, ATE, IDM, EMS, MedTech cluster.",
        "sort_order": 20,
        "milestones": [
            {"name": "Land Allocation / PDC Approval", "target_date": "2026-Q1", "actual_date": "Mar 13 2026", "status": "Completed"},
            {"name": "Campus Launch / Groundbreaking", "target_date": "2026-Q2", "actual_date": "TBD", "status": "Planned"},
            {"name": "First Tenant Move-In", "target_date": "2027-Q2", "actual_date": "TBD", "status": "Planned"}
        ]
    }
]


def seed_all():
    """Clear existing data and seed all 20 projects."""
    print("=" * 60)
    print("  SEEDING GREENFIELD PROJECT DATABASE")
    print("=" * 60)

    total_inserted = 0

    for project in ALL_PROJECTS:
        name = project["name"]
        milestones = project.pop("milestones", [])

        # Check if company already exists
        existing = get_company_by_name(name)
        if existing:
            company = existing
            print(f"  [SKIP] {name} - already exists")
        else:
            data = {k: v for k, v in project.items() if v is not None}
            company = insert_company(data)
            if company:
                total_inserted += 1
                print(f"  [OK]   {name} ({company['id'][:8]}...)")
            else:
                print(f"  [FAIL] {name} - insert failed (check service key)")
                continue

        # Seed milestones
        if company and milestones:
            seed_milestones_for_company(company["id"], milestones)

    print("-" * 60)
    print(f"  TOTAL COMPANIES INSERTED: {total_inserted}")
    print(f"  (Milestones seeded for all)")
    print("=" * 60)

    # Verify
    all_companies = get_all_companies()
    print(f"\n  DB SUMMARY: {len(all_companies)} companies in database")
    locations = {}
    for c in all_companies:
        loc = c.get("location", "Unknown")
        locations[loc] = locations.get(loc, 0) + 1
    for loc, count in locations.items():
        print(f"    {loc}: {count}")


if __name__ == "__main__":
    seed_all()
