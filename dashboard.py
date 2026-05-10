"""
Greenfield Factory Project Tracker - Streamlit Dashboard v1.0.0
PMP Portfolio Tracker: Kulim, Batu Kawan & Bayan Lepas
Data: Supabase | UI: Amazing Green Theme
"""
import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
SUPABASE_ANON_KEY = st.secrets.get("SUPABASE_ANON_KEY", os.getenv("SUPABASE_ANON_KEY", ""))

USE_SUPABASE = False
if SUPABASE_URL and SUPABASE_ANON_KEY:
    os.environ["SUPABASE_URL"] = SUPABASE_URL
    os.environ["SUPABASE_ANON_KEY"] = SUPABASE_ANON_KEY
    try:
        from database.supabase_client import (
            get_all_companies, get_milestones_for_company,
            get_news_for_company, get_jobs_for_company,
            verify_unlock_code, mark_code_used
        )
        comps = get_all_companies()
        if comps:
            USE_SUPABASE = True
    except Exception:
        pass

KOFI_URL = "https://ko-fi.com/greenfieldtrackerbypedot"

st.set_page_config(page_title="Greenfield Factory Tracker", page_icon="🏭", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* {
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Inter', 'Helvetica Neue', Arial, sans-serif;
}

body {
  background: #f5f6f7;
  color: #1a1a1a;
  line-height: 1.47059;
  letter-spacing: -0.022em;
}

/* Header */
.main-header {
  font-size: 2.4rem;
  font-weight: 800;
  background: linear-gradient(135deg, #0a1a11, #122b1e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.2rem;
  letter-spacing: -0.04em;
  line-height: 1.1;
}

.sub-header {
  font-size: 1rem;
  color: #6e6e73;
  font-weight: 400;
  margin-bottom: 2rem;
  letter-spacing: -0.01em;
}

/* KPI */
.kpi-box {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 18px;
  padding: 1.5rem 1.2rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
  text-align: center;
}

.kpi-box:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border-color: rgba(0, 0, 0, 0.12);
}

.kpi-box h3 {
  font-size: 2.8rem;
  font-weight: 800;
  color: #111111;
  margin-bottom: 0.2rem;
  letter-spacing: -0.04em;
  line-height: 1;
}

.kpi-box p {
  color: #6e6e73;
  font-size: 0.85rem;
  font-weight: 500;
  letter-spacing: -0.01em;
}

/* Location badges */
.location-badge-kulim {
  background: #1b3b2b;
  color: #d4e6d8;
  padding: 0.25rem 1rem;
  border-radius: 14px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.location-badge-batu {
  background: #162544;
  color: #c5d4f0;
  padding: 0.25rem 1rem;
  border-radius: 14px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.location-badge-bayan {
  background: #3d2a15;
  color: #f0dcc5;
  padding: 0.25rem 1rem;
  border-radius: 14px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.location-badge-penang {
  background: #4a1a2e;
  color: #f0d0e8;
  padding: 0.25rem 1rem;
  border-radius: 14px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

/* Cards */
.project-card {
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  transition: all 0.25s ease;
}

.project-card:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.07);
  transform: translateY(-2px);
}

.project-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: #111111;
  letter-spacing: -0.03em;
}

/* Donation */
.donation-box {
  background: linear-gradient(135deg, #0a1a11, #122b1e, #1b3b2b);
  color: #e8edea;
  padding: 2rem;
  border-radius: 20px;
  text-align: center;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.12);
}

.donation-box h4 {
  color: #e8edea;
  font-size: 1.4rem;
  font-weight: 700;
  margin-bottom: 0.8rem;
  letter-spacing: -0.03em;
}

.donation-box-btn {
  background: white;
  color: #111111;
  padding: 14px 32px;
  border-radius: 28px;
  font-weight: 700;
  font-size: 1rem;
  text-decoration: none;
  display: inline-block;
  transition: all 0.2s ease;
  letter-spacing: -0.01em;
}

.donation-box-btn:hover {
  background: #e5e5ea;
  transform: scale(1.03);
}

/* Tables */
table th {
  background: #1a1a1a !important;
  color: #f5f5f5 !important;
  font-weight: 600 !important;
  font-size: 0.85rem !important;
  padding: 0.8rem !important;
  letter-spacing: 0.02em;
}

table td {
  font-size: 0.85rem;
  padding: 0.7rem 0.8rem;
}

/* Risk table */
.risk-table th {
  background: #2a1010 !important;
  color: #f0d0d0 !important;
}

/* Buttons */
button, .stButton > button {
  background: #1a1a1a !important;
  color: #f5f5f5 !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  letter-spacing: -0.01em;
  transition: all 0.2s ease;
}

button:hover, .stButton > button:hover {
  background: #333333 !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

/* Footer */
.caption {
  text-align: center;
  color: #6e6e73;
  font-size: 0.8rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
  body {
    background: #0d0d0d;
    color: #cccccc;
  }
  .kpi-box {
    background: rgba(255, 255, 255, 0.04);
    border-color: rgba(255, 255, 255, 0.06);
  }
  .kpi-box h3 {
    color: #e0e0e0;
  }
  .project-card {
    background: rgba(255, 255, 255, 0.04);
    border-color: rgba(255, 255, 255, 0.06);
  }
  .project-title {
    color: #e0e0e0;
  }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">Greenfield Factory Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">PMP Portfolio Tracker — Kulim • Batu Kawan • Bayan Lepas • Penang (2025–2028)</div>', unsafe_allow_html=True)

if "jobs_unlocked" not in st.session_state:
    st.session_state.jobs_unlocked = False
if "donation_code_input" not in st.session_state:
    st.session_state.donation_code_input = ""

with st.sidebar:
    st.title("Controls")
    st.caption(f"Last refresh: {datetime.now().strftime('%H:%M')}")

    location_filter = st.multiselect(
        "Location",
        options=["Kulim", "Batu Kawan", "Bayan Lepas", "Penang"],
        default=["Kulim", "Batu Kawan", "Bayan Lepas", "Penang"]
    )

    if USE_SUPABASE:
        all_companies = get_all_companies()
    else:
        from database.seed_supabase import ALL_PROJECTS
        all_companies = ALL_PROJECTS
        st.warning("Supabase unavailable — using local data")

    kulim_companies = [c for c in all_companies if c.get("location") == "Kulim"]
    batu_companies  = [c for c in all_companies if c.get("location") == "Batu Kawan"]
    bayan_companies = [c for c in all_companies if c.get("location") == "Bayan Lepas"]
    penang_companies = [c for c in all_companies if c.get("location") == "Penang"]

    company_filter = st.multiselect(
        "Company",
        options=[c["name"] for c in all_companies],
        default=[c["name"] for c in all_companies]
    )

    st.divider()

    if not st.session_state.jobs_unlocked:
        st.markdown("### Unlock Job Links")
        code_input = st.text_input("Donation code", type="password", key="unlock_input")
        if code_input:
            admin_code = st.secrets.get("ADMIN_CODE", os.getenv("ADMIN_CODE", ""))
            if admin_code and code_input == admin_code:
                st.session_state.jobs_unlocked = True
                st.success("Admin access granted!")
                st.rerun()
            elif USE_SUPABASE:
                is_valid = verify_unlock_code(code_input)
                if is_valid:
                    mark_code_used(code_input)
                    st.session_state.jobs_unlocked = True
                    st.success("Unlocked! Refresh to see jobs.")
                    st.rerun()
                else:
                    st.error("Invalid or used code")
            else:
                st.info("Connect Supabase first")
    else:
        st.success("Job links unlocked!")

# KPI row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        f'<div class="kpi-box"><h3>{len(all_companies)}</h3><p>Active Projects</p></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="kpi-box"><h3>{len(kulim_companies)}</h3><p>Kulim Sites</p></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f'<div class="kpi-box"><h3>{len(batu_companies)}</h3><p>Batu Kawan Sites</p></div>',
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        f'<div class="kpi-box"><h3>{len(bayan_companies) + len(penang_companies)}</h3><p>Bayan Lepas + Penang Sites</p></div>',
        unsafe_allow_html=True,
    )

st.divider()

filtered = [
    c for c in all_companies
    if c.get("location") in location_filter and c.get("name") in company_filter
]

if not filtered:
    st.warning("No projects match your filter.")
else:
    cols_per_row = 2
    for i in range(0, len(filtered), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, proj in enumerate(filtered[i : i + cols_per_row]):
            with cols[j]:
                loc = proj.get("location", "Kulim")
                badge_class = {
                    "Kulim": "location-badge-kulim",
                    "Batu Kawan": "location-badge-batu",
                    "Bayan Lepas": "location-badge-bayan",
                    "Penang": "location-badge-penang",
                }.get(loc, "location-badge-kulim")

                st.markdown(
                    f'<div class="project-card">'
                    f'<div class="project-title">{proj["name"]}</div>'
                    f'<span class="{badge_class}">{loc}</span>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

                c1, c2 = st.columns(2)
                c1.metric("Sector", proj.get("sector", "N/A"))
                c2.metric("Phase", proj.get("phase", "N/A"))
                c3, c4 = st.columns(2)
                c3.metric("Investment", proj.get("investment", "TBD"))
                c4.metric("Est. Jobs", proj.get("jobs_estimate", "N/A"))

                if proj.get("latest_news"):
                    st.info(proj["latest_news"])

                milestones = []
                if USE_SUPABASE:
                    try:
                        milestones = get_milestones_for_company(proj["id"])
                    except Exception:
                        milestones = proj.get("milestones", [])
                else:
                    milestones = proj.get("milestones", [])

                if milestones:
                    with st.expander("Milestones"):
                        df = pd.DataFrame(
                            [
                                {
                                    "Milestone": m.get("name", m.get("milestone", "")),
                                    "Target": m.get("target_date", m.get("target", "")),
                                    "Actual": m.get("actual_date", m.get("actual", "")),
                                    "Status": m.get("status", "Planned"),
                                }
                                for m in milestones
                            ]
                        )
                        st.dataframe(df, hide_index=True, use_container_width=True)


# ---- PMP JOB LISTING ASSISTANT (Phase 2) ----
st.divider()
st.header("PMP Job Listing Assistant")
st.caption("Factory jobs across Kulim • Batu Kawan • Bayan Lepas")

if USE_SUPABASE:
    try:
        from assistants.job_assistant import get_preview, filter_jobs, CATEGORIES, ZONES, LAST_UPDATED
    except Exception:
        pass

if not st.session_state.jobs_unlocked:
    st.markdown(
        f"""
        <div class="donation-box" style="margin: 1.5rem 0;">
            <h4>Unlock Live Factory Job Links</h4>
            <p style="font-size:0.92rem;opacity:0.9;margin-bottom:1rem;">
                Your donation unlocks live job listings from <strong>all 20+ tracked factories</strong><br/>
                across Kulim, Batu Kawan &amp; Bayan Lepas — sorted by company or job category.
            </p>
            <a class="donation-box-btn" href="{KOFI_URL}" target="_blank">Donate on Ko-fi</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if USE_SUPABASE:
        try:
            preview = get_preview(unlocked=False)
            st.subheader("Job Preview by Zone")
            for zone in ZONES:
                zone_companies = preview.get("by_zone", {}).get(zone, [])
                if zone_companies:
                    with st.expander(f"{zone} ({sum(c['job_count'] for c in zone_companies)} open jobs)"):
                        for comp in zone_companies:
                            st.markdown(f"- **{comp['company']}** — {comp['job_count']} positions ({comp['sector']})")
        except Exception:
            st.info("Job data will appear once scrapers run (coming in CI/CD pipeline).")

else:
    # ===== UNLOCKED - Full Job Assistant =====
    job_col1, job_col2 = st.columns([3, 1])

    with job_col1:
        job_search_mode = st.radio(
            "Filter by", ["Zone + Category", "Company", "All Jobs"],
            horizontal=True, key="job_mode"
        )

        if job_search_mode == "Zone + Category":
            col_z, col_c = st.columns(2)
            with col_z:
                sel_zone = st.selectbox("Zone", ZONES, key="job_zone")
            with col_c:
                try:
                    cats = get_distinct_categories()
                except Exception:
                    cats = CATEGORIES
                sel_category = st.selectbox("Category", cats, key="job_cat")
            if st.button("Search Jobs", key="job_search_zone"):
                result = filter_jobs(zone=sel_zone, category=sel_category, unlocked=True)
        elif job_search_mode == "Company":
            all_names = [c["name"] for c in all_companies]
            sel_company = st.selectbox("Company", all_names, key="job_company_select")
            if st.button("Search Jobs", key="job_search_company"):
                result = filter_jobs(company=sel_company, unlocked=True)
        else:
            if st.button("Show All Active Jobs", key="job_search_all"):
                result = filter_jobs(unlocked=True)

    with job_col2:
        st.success("Job links active!")

    if "result" in locals() and isinstance(result, dict):
        if result.get("unlocked"):
            st.markdown(f"**{result['count']} jobs found** — {result.get('filter', 'All')}")
            if result.get("has_stale"):
                st.warning("Some links need verification (older than 7 days).")

            jobs_df_data = []
            for jj in result.get("jobs", []):
                status_icon = "⚠️" if jj.get("needs_verification") else "✅"
                jobs_df_data.append({
                    "Company": jj["company"],
                    "Zone": jj["zone"],
                    "Category": jj.get("category", ""),
                    "Title": jj["title"],
                    "Link": jj["url"],
                    "Verified": status_icon,
                })
            if jobs_df_data:
                st.dataframe(
                    pd.DataFrame(jobs_df_data),
                    column_config={"Link": st.column_config.LinkColumn("Link")},
                    hide_index=True, use_container_width=True
                )
            else:
                st.info("No active jobs match this filter — try a different category or zone.")

        st.caption(f"Last updated: {result.get('last_updated', LAST_UPDATED)} | To report dead links reply /report")

st.divider()
st.header("Risk Register")
risk_df = pd.DataFrame([
    {"ID": "R001", "Risk": "Supply chain delays", "Impact": "High", "Mitigation": "Dual sourcing"},
    {"ID": "R002", "Risk": "Regulatory changes", "Impact": "Medium", "Mitigation": "Liaison"},
    {"ID": "R003", "Risk": "Labor shortage", "Impact": "High", "Mitigation": "Training"},
    {"ID": "R004", "Risk": "CAPEX fluctuation", "Impact": "High", "Mitigation": "Phased"},
    {"ID": "R005", "Risk": "Concurrent site works", "Impact": "High", "Mitigation": "Logistics"},
    {"ID": "R006", "Risk": "EUR-RM volatility", "Impact": "Medium", "Mitigation": "Hedging"},
])
st.dataframe(risk_df, hide_index=True, use_container_width=True)

st.divider()
st.caption(
    "Greenfield PMO Tracker v1.0.0 | Amazing Green Theme | "
    "Kulim • Batu Kawan • Bayan Lepas | 2026"
)
