-- AICC Core Schema Migration 001
-- Run against: local Supabase Postgres (aicc database)
-- Created: 2026-06-26

-- ── EXTENSIONS ────────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ── AGENTS ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO agents (name, display_name, description) VALUES
    ('ceo', 'CEO Agent', 'Daily priorities, business performance, strategic decisions'),
    ('project_manager', 'Project Manager', 'Task assignment, progress tracking, deadline alerts'),
    ('real_estate', 'Real Estate Assistant', 'Leads, CRM, emails, texts, transaction tracking'),
    ('content_director', 'Content Director', 'GymnastDiva content, captions, hashtags, scheduling'),
    ('marketing', 'Marketing Agent', 'Social media, ad copy, email campaigns, branding'),
    ('research', 'Research Agent', 'Prospect research, market analysis, competitor intel'),
    ('sales', 'Sales Agent', 'Proposals, follow-ups, pipeline for AI Agency clients'),
    ('finance', 'Finance Assistant', 'Revenue tracking, invoice generation, expense log'),
    ('document', 'Document Assistant', 'Contract review, paperwork, file organization'),
    ('customer_support', 'Customer Support', 'Client communications, follow-up sequences'),
    ('seo', 'SEO Agent', 'Content optimization, keyword research, Google profile'),
    ('analytics', 'Analytics Agent', 'KPI dashboards, engagement reports, trend detection')
ON CONFLICT (name) DO NOTHING;

-- ── AGENT MEMORY ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS agent_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name TEXT NOT NULL REFERENCES agents(name),
    memory_type TEXT NOT NULL,  -- 'preference', 'context', 'decision', 'fact'
    key TEXT NOT NULL,
    value JSONB NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    UNIQUE(agent_name, memory_type, key)
);

-- ── CONVERSATIONS ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name TEXT NOT NULL REFERENCES agents(name),
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── TASKS ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'todo' CHECK (status IN ('todo', 'doing', 'done', 'blocked')),
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    business_unit TEXT CHECK (business_unit IN ('real_estate', 'gymnastics', 'agency', 'fba', 'digital', 'admin')),
    assigned_agent TEXT REFERENCES agents(name),
    due_date TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── LEADS (Real Estate) ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    source TEXT,       -- 'referral', 'har_mls', 'kw_command', 'social', 'direct'
    referrer TEXT,     -- e.g. "Shay Mims"
    status TEXT DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'qualified', 'active', 'under_contract', 'closed', 'lost')),
    lead_type TEXT CHECK (lead_type IN ('buyer', 'seller', 'land', 'investor', 'renter')),
    budget_min NUMERIC,
    budget_max NUMERIC,
    desired_areas TEXT[],
    notes TEXT,
    last_contact_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed Sharon Traylor as active lead
INSERT INTO leads (first_name, last_name, source, referrer, status, lead_type, notes)
VALUES ('Sharon', 'Traylor', 'referral', 'Shay Mims', 'active', 'land', 'Land buyer referred by Shay Mims. Currently in follow-up.')
ON CONFLICT DO NOTHING;

-- ── LISTINGS ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT DEFAULT 'TX',
    zip TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'pending', 'under_contract', 'sold', 'on_hold', 'withdrawn')),
    listing_type TEXT CHECK (listing_type IN ('sale', 'lease', 'land')),
    price NUMERIC,
    bedrooms INTEGER,
    bathrooms NUMERIC,
    sqft INTEGER,
    mls_number TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed active listing
INSERT INTO listings (address, city, zip, status, notes)
VALUES ('4707 Cairnvillage St', 'Houston', '77084', 'on_hold', 'Probate listing — on hold pending resolution.')
ON CONFLICT DO NOTHING;

-- ── CONTENT QUEUE (GymnastDiva) ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS content_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform TEXT NOT NULL CHECK (platform IN ('instagram', 'tiktok', 'youtube_shorts', 'facebook', 'all')),
    content_type TEXT NOT NULL,  -- 'highlight', 'skills', 'meet_recap', 'motivation', 'lesson_promo'
    athlete_name TEXT DEFAULT 'Nastia',
    title TEXT,
    caption TEXT,
    hashtags TEXT[],
    media_url TEXT,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'review', 'approved', 'scheduled', 'published', 'archived')),
    scheduled_for TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── TRANSACTIONS (Real Estate) ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id),
    listing_id UUID REFERENCES listings(id),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'offer_submitted', 'under_contract', 'inspection', 'closing', 'closed', 'fallen_through')),
    contract_price NUMERIC,
    closing_date DATE,
    commission_rate NUMERIC DEFAULT 0.03,
    docusign_envelope_id TEXT,
    lone_wolf_id TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── INDEXES ───────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_conversations_agent ON conversations(agent_name, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status, priority);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_content_queue_status ON content_queue(status, scheduled_for);
CREATE INDEX IF NOT EXISTS idx_agent_memory_lookup ON agent_memory(agent_name, memory_type, key);

-- ── UPDATED_AT TRIGGER ────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_agents_updated_at BEFORE UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_agent_memory_updated_at BEFORE UPDATE ON agent_memory FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_tasks_updated_at BEFORE UPDATE ON tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_leads_updated_at BEFORE UPDATE ON leads FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_listings_updated_at BEFORE UPDATE ON listings FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_content_queue_updated_at BEFORE UPDATE ON content_queue FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_transactions_updated_at BEFORE UPDATE ON transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at();
