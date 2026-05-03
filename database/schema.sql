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

-- Add missing columns to existing jobs table (v1.0.2 fix)
ALTER TABLE public.jobs ADD COLUMN IF NOT EXISTS category TEXT DEFAULT 'Uncategorized';
ALTER TABLE public.jobs ADD COLUMN IF NOT EXISTS last_verified TIMESTAMPTZ DEFAULT NOW();

-- ============================================================
-- Public RPC Functions (v1.0.2)
-- SECURITY DEFINER bypasses RLS for anon access via rpc()
-- ============================================================

-- 1. Verify donation unlock code without service key
CREATE OR REPLACE FUNCTION verify_donation_code(code_input TEXT)
RETURNS TABLE(code TEXT, is_valid BOOLEAN, email TEXT)
LANGUAGE plpgsql SECURITY DEFINER SET search_path = ''
AS $$
BEGIN
  RETURN QUERY
  SELECT dc.code, NOT COALESCE(dc.is_used, false) AS is_valid, dc.email
  FROM donation_codes dc
  WHERE dc.code = UPPER(TRIM(code_input));
END;
$$;
GRANT EXECUTE ON FUNCTION verify_donation_code TO anon, authenticated;

-- 2. Mark unlock code as consumed
CREATE OR REPLACE FUNCTION consume_donation_code(code_input TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql SECURITY DEFINER SET search_path = ''
AS $$
BEGIN
  UPDATE donation_codes SET is_used = true, used_at = NOW()
  WHERE code = UPPER(TRIM(code_input)) AND is_used = false;
  RETURN FOUND;
END;
$$;
GRANT EXECUTE ON FUNCTION consume_donation_code TO anon, authenticated;

-- 3. Public job listing access (bypasses jobs RLS)
CREATE OR REPLACE FUNCTION get_public_jobs(
  zone_filter TEXT DEFAULT NULL,
  category_filter TEXT DEFAULT NULL,
  company_name_filter TEXT DEFAULT NULL
)
RETURNS TABLE(
  id UUID, company_name TEXT, company_location TEXT,
  title TEXT, job_url TEXT, source TEXT,
  location TEXT, category TEXT, posted_at TEXT,
  last_verified TIMESTAMPTZ, is_active BOOLEAN, created_at TIMESTAMPTZ
)
LANGUAGE plpgsql SECURITY DEFINER SET search_path = ''
AS $$
BEGIN
  RETURN QUERY
  SELECT j.id, c.name, c.location,
    j.title, j.job_url, j.source, j.location, j.category,
    j.posted_at, j.last_verified, j.is_active, j.created_at
  FROM jobs j JOIN companies c ON j.company_id = c.id
  WHERE j.is_active = true
    AND (zone_filter IS NULL OR c.location = zone_filter)
    AND (category_filter IS NULL OR j.category = category_filter)
    AND (company_name_filter IS NULL OR c.name = company_name_filter)
  ORDER BY j.created_at DESC;
END;
$$;
GRANT EXECUTE ON FUNCTION get_public_jobs TO anon, authenticated;

-- 4. Distinct active categories (bypasses jobs RLS)
CREATE OR REPLACE FUNCTION get_public_categories()
RETURNS TABLE(category TEXT)
LANGUAGE plpgsql SECURITY DEFINER SET search_path = ''
AS $$
BEGIN
  RETURN QUERY
  SELECT DISTINCT j.category FROM jobs j
  WHERE j.is_active = true AND j.category != 'Uncategorized'
  ORDER BY j.category;
END;
$$;
GRANT EXECUTE ON FUNCTION get_public_categories TO anon, authenticated;
