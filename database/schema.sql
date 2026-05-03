-- Supabase Schema: Greenfield Factory Project Tracker
-- Phase 2: Database Layer for Kulim, Batu Kawan & Bayan Lepas

-- Enable RLS
ALTER TABLE IF EXISTS companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS milestones ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS news_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS scrape_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS donation_codes ENABLE ROW LEVEL SECURITY;

-- Companies table (core entity)
CREATE TABLE IF NOT EXISTS companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  location TEXT NOT NULL CHECK (location IN ('Kulim', 'Batu Kawan', 'Bayan Lepas')),
  sector TEXT NOT NULL,
  status TEXT NOT NULL,
  phase TEXT,
  investment TEXT,
  jobs_estimate INTEGER,
  latest_news TEXT,
  source_url TEXT,
  is_auto_detected BOOLEAN DEFAULT false,
  needs_review BOOLEAN DEFAULT false,
  sort_order INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Milestones table
CREATE TABLE IF NOT EXISTS milestones (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  target_date TEXT,
  actual_date TEXT,
  status TEXT NOT NULL DEFAULT 'Planned' CHECK (status IN ('Completed', 'Planned', 'Delayed', 'In Progress')),
  notes TEXT,
  sort_order INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- News items table (scraped content)
CREATE TABLE IF NOT EXISTS news_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  body TEXT,
  source TEXT,
  source_url TEXT,
  published_at TEXT,
  detected_by TEXT DEFAULT 'scraper',
  is_read BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Job listings table (scraped from job sites)
-- Categories: Operator, Technician, Engineer, Supervisor, Logistics, Admin, IT, Management
CREATE TABLE IF NOT EXISTS jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  job_url TEXT NOT NULL,
  source TEXT DEFAULT 'Unknown',
  location TEXT,
  category TEXT DEFAULT 'Uncategorized' CHECK (category IN ('Operator', 'Technician', 'Engineer', 'Supervisor', 'Logistics', 'Admin', 'IT', 'Management', 'Uncategorized')),
  posted_at TEXT,
  last_verified TIMESTAMPTZ DEFAULT NOW(),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Scraper execution logs
CREATE TABLE IF NOT EXISTS scrape_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('success', 'failed', 'partial')),
  items_found INTEGER DEFAULT 0,
  items_new INTEGER DEFAULT 0,
  errors TEXT,
  duration_seconds REAL,
  run_at TIMESTAMPTZ DEFAULT NOW()
);

-- Donation unlock codes
CREATE TABLE IF NOT EXISTS donation_codes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT UNIQUE NOT NULL,
  email TEXT,
  ko_fi_reference TEXT,
  is_used BOOLEAN DEFAULT false,
  used_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_companies_location ON companies(location);
CREATE INDEX IF NOT EXISTS idx_companies_status ON companies(status);
CREATE INDEX IF NOT EXISTS idx_milestones_company ON milestones(company_id);
CREATE INDEX IF NOT EXISTS idx_news_items_company ON news_items(company_id);
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company_id);
CREATE INDEX IF NOT EXISTS idx_jobs_active ON jobs(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_donation_codes_unused ON donation_codes(code) WHERE is_used = false;

-- RLS Policies: Public read for companies, milestones, news
DROP POLICY IF EXISTS "Allow public read companies" ON companies;
CREATE POLICY "Allow public read companies" ON companies
  FOR SELECT USING (true);

DROP POLICY IF EXISTS "Allow public read milestones" ON milestones;
CREATE POLICY "Allow public read milestones" ON milestones
  FOR SELECT USING (true);

DROP POLICY IF EXISTS "Allow public read news" ON news_items;
CREATE POLICY "Allow public read news" ON news_items
  FOR SELECT USING (true);

-- RLS Policies: Jobs only visible via service_role or verified unlock
DROP POLICY IF EXISTS "Hide jobs by default" ON jobs;
CREATE POLICY "Hide jobs by default" ON jobs
  FOR SELECT USING (false);  -- blocked by default; service role bypasses RLS

-- RLS Policies: Donation codes only visible via service_role
DROP POLICY IF EXISTS "Hide donation_codes" ON donation_codes;
CREATE POLICY "Hide donation_codes" ON donation_codes
  FOR SELECT USING (false);

-- RLS Policies: Scrape logs only for service_role
DROP POLICY IF EXISTS "Hide scrape_logs" ON scrape_logs;
CREATE POLICY "Hide scrape_logs" ON scrape_logs
  FOR SELECT USING (false);

-- Trigger: auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_companies_updated ON companies;
CREATE TRIGGER trg_companies_updated
  BEFORE UPDATE ON companies
  FOR EACH ROW EXECUTE FUNCTION update_timestamp();

DROP TRIGGER IF EXISTS trg_milestones_updated ON milestones;
CREATE TRIGGER trg_milestones_updated
  BEFORE UPDATE ON milestones
  FOR EACH ROW EXECUTE FUNCTION update_timestamp();
