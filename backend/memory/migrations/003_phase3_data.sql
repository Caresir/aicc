-- AICC Migration 003 — Phase 3 Data: Cairnvillage enrichment + fba_manager agent
-- Run after: 002_sharon_traylor_intake.sql

-- ── REGISTER FBA_MANAGER AGENT ────────────────────────────────────────────────
-- The FBAAgent self-registers on init, but this ensures the row exists for FK constraints
INSERT INTO agents (name, display_name, description)
VALUES (
    'fba_manager',
    'FBA Manager',
    'Amazon FBA brand approvals, distributor management, wholesale strategy'
)
ON CONFLICT (name) DO NOTHING;

-- ── ENRICH CAIRNVILLAGE LISTING ───────────────────────────────────────────────
UPDATE listings SET
    listing_type  = 'sale',
    status        = 'on_hold',
    city          = 'Houston',
    state         = 'TX',
    zip           = '77084',
    notes         = 'Probate listing — on hold pending title clearance due to sibling estate dispute. Client: Nadine. Already loaded in Lone Wolf Transactions. Do not market or show until hold is lifted. Contact Jennifer before any action on this file.'
WHERE address = '4707 Cairnvillage St';

-- ── RENAME DOCUSIGN COLUMN (if it exists) ─────────────────────────────────────
-- Rename legacy column — we use Lone Wolf Transactions, not DocuSign
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'transactions' AND column_name = 'docusign_envelope_id'
    ) THEN
        ALTER TABLE transactions RENAME COLUMN docusign_envelope_id TO legacy_docusign_id;
    END IF;
END $$;

-- ── ADD MEETS TABLE (GymnastDiva meet schedule) ───────────────────────────────
-- The content director stores meets in agent_memory, but a dedicated table
-- gives us proper querying and Google Calendar sync later
CREATE TABLE IF NOT EXISTS meets (
    id         UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    date       DATE        NOT NULL,
    name       TEXT        NOT NULL,
    location   TEXT        NOT NULL,
    discipline TEXT        NOT NULL DEFAULT 'gymnastics',
    notes      TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_meets_date ON meets(date ASC);

-- ── REGISTER CONTENT_DIRECTOR AGENT (safety net) ─────────────────────────────
INSERT INTO agents (name, display_name, description)
VALUES (
    'content_director',
    'Content Director',
    'GymnastDiva content, captions, hashtags, platform scheduling'
)
ON CONFLICT (name) DO NOTHING;
