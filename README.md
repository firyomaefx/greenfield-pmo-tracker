# 🏭 Greenfield Factory Project Tracker

**PMP Portfolio Dashboard — Kulim, Batu Kawan & Bayan Lepas (2025–2028)**

[![Scrape Pipeline](https://github.com/firyomaefx/greenfield-factory-tracker/actions/workflows/scrape.yml/badge.svg)](https://github.com/firyomaefx/greenfield-factory-tracker/actions/workflows/scrape.yml)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live-brightgreen)](https://greenfield-pmo-tracker.streamlit.app)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support-orange)](https://ko-fi.com/greenfieldtrackerbypedot)

---

## 👁️ Live Dashboard

| Deployment | URL |
|------------|-----|
| **Streamlit Cloud** | [greenfield-pmo-tracker.streamlit.app](https://greenfield-pmo-tracker.streamlit.app) |
| **Supabase DB** | [qoncvdcyypwhogrqzesm.supabase.co](https://qoncvdcyypwhogrqzesm.supabase.co) |
| **Ko-fi Donation** | [ko-fi.com/greenfieldtrackerbypedot](https://ko-fi.com/greenfieldtrackerbypedot) |

---

## 🚀 Quick Start

### Method A: Standalone HTML (No Installation)
Double-click `Greenfield_Dashboard.html` — opens in any browser. All 20 projects, filters, milestones, risk register, and action items. **Apple-inspired "Amazing Green" UI theme.**

### Method B: Streamlit Cloud
Visit: [https://greenfield-pmo-tracker.streamlit.app](https://greenfield-pmo-tracker.streamlit.app)

### Method C: Local Streamlit (Supabase-backed)
```bash
git clone https://github.com/firyomaefx/greenfield-factory-tracker.git
cd greenfield-factory-tracker
pip install -r requirements.txt
streamlit run dashboard.py
```

---

## 📊 Tracked Projects (20 Companies)

| Location | Color | Companies | Count |
|----------|-------|-----------|-------|
| **Kulim** | 🟢 Emerald | Novolyte, AIXTRON, Medtronic, Ferrotec, Ichia Technologies, AT&S, Hyundai Motor, Unigen, Pivotal Systems | 9 |
| **Batu Kawan** | 🔵 Sapphire | UMediC Group Berhad, Hotayi Electronic, Benchmark Precision Technologies, Chipbond Technology | 4 |
| **Bayan Lepas** | 🟠 Amber | AMD, Monolithic Power Systems (MPS), Bitdeer Technologies, congatec, V-Chip, Hanic, Penang ATE Campus | 7 |

---

## 🎨 Amazing Green UI Theme

Apple-inspired design system with forest and emerald tones:

| Element | Style |
|---------|-------|
| **Typography** | -apple-system, SF Pro Display, SF Pro Text, Inter |
| **Background** | `#f0faf5` (mint white) |
| **Header** | `linear-gradient(135deg, #0d2b1d, #1a5c32, #1a8a4a)` |
| **Cards** | Frosted glass (`backdrop-filter: blur(20px)`) |
| **KPI Values** | `#0d2b1d` (deep forest), weight 800 |
| **Dark Mode** | Auto-detected via `prefers-color-scheme: dark` |
| **Badges** | Gradient emerald / sapphire / amber with subtle glow |

---

## 🗄️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│              .github/workflows/scrape.yml (Every 12h)     │
│                                                           │
│  RSS Scraper ─► Web Scraper ─► Bursa ─► Job Scraper    │
│       │                                 │                 │
│       └──────── NLP Processor ──────────┘                │
│                     │                                     │
│              Supabase Database                             │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│                  Streamlit Cloud                           │
│                                                           │
│  dashboard.py ─► Supabase Client ─► Amazing Green UI     │
│                                                           │
│  • KPI Dashboard           • Auto-detect new companies   │
│  • Milestone tables        • Location filters            │
│  • Risk register           • Ko-fi donation unlock       │
│  • Job links (unlocked)    • Dark mode auto-switch        │
└──────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
greenfield-factory-tracker/
├── dashboard.py                        # Streamlit app (Supabase + Ko-fi)
├── Greenfield_Dashboard.html           # Standalone HTML (Amazing Green)
├── tracker.md                          # PMP milestone log
├── README.md                           # This file
├── VERSION                             # Semantic version
├── requirements.txt                    # 13 Python packages
├── .env.example                        # Config template
│
├── database/
│   ├── schema.sql                      # 6 tables + RLS policies
│   ├── supabase_client.py              # Full CRUD wrapper (20+ functions)
│   └── seed_supabase.py                # 20-project data seeder
│
├── scrapers/
│   ├── base_scraper.py                 # Rate-limited HTTP client
│   ├── rss_scraper.py                  # 3 Malaysian RSS feeds
│   ├── mida_scraper.py                 # MIDA.gov.my
│   ├── penang_scraper.py               # InvestPenang.gov.my
│   ├── bursa_scraper.py                # Bursa Malaysia
│   ├── job_scraper.py                  # Job postings aggregator
│   ├── company_scraper.py              # 4 direct company press pages
│   ├── nlp_processor.py                # Auto-detect new companies
│   └── run_all.py                      # Main orchestrator
│
├── utils/
│   ├── unlock_manager.py               # Ko-fi → unlock code system
│   └── deduplicator.py                 # Content-based dedup
│
└── .github/workflows/
    ├── scrape.yml                       # 12h CI/CD pipeline
    └── release.yml                      # Release management workflow
```

---

## ☕ Donation & Job Links

Support the tracker and unlock **live job listings** from all 20+ tracked factories:

1. Donate at [ko-fi.com/greenfieldtrackerbypedot](https://ko-fi.com/greenfieldtrackerbypedot)
2. Receive an **unlock code** via email
3. Enter the code in the dashboard → job links become visible **permanently**
4. Job listings are scraped automatically and refreshed every 12 hours

---

## ⚙️ CI/CD Pipelines

| Workflow | Trigger | What It Does |
|----------|---------|--------------|
| `scrape.yml` | Every 12h + manual | Runs all 6 scrapers, deduplicates, stores to Supabase |
| `release.yml` | Manual + version input | Tags release, generates changelog, creates GitHub Release |

---

## 🔑 Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_ANON_KEY` | Yes | Public read access |
| `SUPABASE_SERVICE_KEY` | For seeding/scraper | Full read/write access (never commit) |
| `KOFI_URL` | No | Donation page link |

---

## 📦 Dependencies

```
streamlit>=1.40.0        # Web framework
pandas>=2.2.0            # Data processing
supabase>=2.3.0          # Database client
feedparser>=6.0.11       # RSS parsing
beautifulsoup4>=4.12.0   # HTML scraping
lxml>=5.0.0              # XML/HTML parser
httpx>=0.27.0            # HTTP client
requests>=2.32.0         # HTTP requests
streamlit-autorefresh    # Auto-refresh
reportlab>=4.0.0         # PDF export
yagmail>=0.15.293        # Email alerts
python-dotenv>=1.0.0     # Environment config
python-dateutil>=2.8.2   # Date parsing
```

---

## 📝 Release History

| Version | Date | Highlights |
|---------|------|------------|
| **v1.0.0** | 2026-05 | Initial release — 20 projects, Amazing Green theme, Supabase, Ko-fi, scrapers, CI/CD |

---

## 👤 Author

**firyomaefx** — PMP Professional  
GitHub: [@firyomaefx](https://github.com/firyomaefx)  
Ko-fi: [greenfieldtrackerbypedot](https://ko-fi.com/greenfieldtrackerbypedot)

---

<p align="center">
  <sub>Amazing Green Theme — Engineered for professional portfolio management.</sub>
</p>
