-- Dedup guard: a lead must only receive automated outreach from ONE system —
-- either the AICC-native follow_up_sequences / hourly reminder workflow, or a
-- KW Command SmartPlan (enrolled manually in agent.kw.com, outside this repo).
--
-- Precedent: Sharon Traylor ended up on both at once and had to be fixed by
-- hand (see REAL_ESTATE_ASSETS.md and backend/agents/sequences/sharon_traylor.py).
-- This column makes that a deliberate, visible choice instead of a manual patch.
--
-- Default is 'aicc' so existing behavior is unchanged for every current lead.
-- When Kareesa manually enrolls someone in a SmartPlan in KW Command, she (or
-- whoever manages the Leads page) flips this to 'smartplan', which stops the
-- AICC hourly reminder workflow from drafting further outreach for that lead.

ALTER TABLE leads ADD COLUMN IF NOT EXISTS sequence_track TEXT NOT NULL DEFAULT 'aicc'
    CHECK (sequence_track IN ('aicc', 'smartplan', 'none'));

COMMENT ON COLUMN leads.sequence_track IS
    'Which system owns automated follow-up for this lead. aicc = AICC-native '
    'sequence/reminder workflow drafts outreach. smartplan = enrolled in a KW '
    'Command SmartPlan (enrollment happens manually in agent.kw.com); AICC '
    'automation must skip these leads to avoid duplicate outreach. none = no '
    'automated outreach from either system.';
