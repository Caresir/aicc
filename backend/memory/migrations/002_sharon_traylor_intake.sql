-- AICC Migration 002 — Sharon Traylor Intake + Follow-Up Sequence Schema
-- Run after: 001_core_schema.sql
-- Created: 2026-06-26

-- ── EXTEND LEADS TABLE ────────────────────────────────────────────────────────
ALTER TABLE leads
    ADD COLUMN IF NOT EXISTS co_purchasers   JSONB DEFAULT '[]',
    ADD COLUMN IF NOT EXISTS property_criteria JSONB DEFAULT '{}';

-- ── FOLLOW-UP SEQUENCES TABLE ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS follow_up_sequences (
    id           UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id      UUID        NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    step         INTEGER     NOT NULL,
    channel      TEXT        NOT NULL CHECK (channel IN ('text', 'email', 'call', 'note')),
    subject      TEXT,
    content      TEXT        NOT NULL,
    scheduled_at TIMESTAMPTZ NOT NULL,
    status       TEXT        DEFAULT 'pending'
                             CHECK (status IN ('pending', 'sent', 'skipped', 'failed')),
    sent_at      TIMESTAMPTZ,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (lead_id, step)
);

CREATE INDEX IF NOT EXISTS idx_followup_lead_step
    ON follow_up_sequences (lead_id, step);
CREATE INDEX IF NOT EXISTS idx_followup_scheduled
    ON follow_up_sequences (scheduled_at)
    WHERE status = 'pending';

-- ── UPDATE SHARON TRAYLOR'S LEAD RECORD ──────────────────────────────────────
UPDATE leads SET
    status             = 'new',
    lead_type          = 'land',
    notes              = 'Land buyer referred by Shay Mims. Interested in purchasing acreage in Texas with co-purchasers. Acreage range, county preferences, purpose, and financing TBD at intake call. Welcome sequence queued.',
    co_purchasers      = '[{"name": "TBD", "notes": "Co-purchaser details to be gathered during intake call"}]',
    property_criteria  = '{"type": "land", "acreage_min": null, "acreage_max": null, "counties_preferred": [], "purpose": "TBD — personal/homesite/agricultural/investment", "water_needed": true, "road_access": true, "utilities_notes": "TBD at intake", "mineral_rights_preference": "TBD"}'
WHERE first_name = 'Sharon' AND last_name = 'Traylor';

-- ── SEED SHARON'S FOLLOW-UP SEQUENCE ─────────────────────────────────────────
-- Uses a CTE to get her lead ID safely

WITH sharon AS (
    SELECT id FROM leads
    WHERE first_name = 'Sharon' AND last_name = 'Traylor'
    LIMIT 1
)

INSERT INTO follow_up_sequences (lead_id, step, channel, subject, content, scheduled_at, status)
SELECT
    sharon.id,
    steps.step,
    steps.channel,
    steps.subject,
    steps.content,
    steps.scheduled_at,
    'pending'
FROM sharon, (VALUES

-- ── STEP 1 — Day 0 — Welcome Text ────────────────────────────────────────────
(
    1,
    'text',
    NULL,
    $$Hi Sharon! This is Kareesa Gonzales with Keller Williams Preferred. Shay Mims mentioned you're searching for land in Texas — so excited to help! Sending you an email now with a few questions to get started.$$,
    NOW()
),

-- ── STEP 2 — Day 0 — Welcome Email ───────────────────────────────────────────
(
    2,
    'email',
    'Your Texas Land Search Starts Here, Sharon',
    $$Hi Sharon,

It was so wonderful to hear about you through Shay Mims — anyone in Shay's circle is someone I'm truly excited to work with!

I'm Kareesa Gonzales, your dedicated real estate agent with Keller Williams Preferred in Pearland, TX. Helping buyers find their perfect piece of Texas land is one of my favorite parts of this work, and I'd love to make your search as smooth and successful as possible.

To make sure I'm finding the right properties for you and your co-purchasers, I have a few quick discovery questions:

ABOUT YOUR SEARCH:
1. What regions or counties of Texas are you most interested in? (Hill Country, East Texas, Brazos Valley, Southeast TX — or open to anywhere?)
2. What's your ideal acreage range? (Under 10 acres, 10–50, 50–100, 100+?)
3. What's the primary purpose for the land? (Personal homesite, hunting/recreation, agriculture, investment, or a combination?)
4. Are utilities important — do you need existing electricity, a water well, or septic already in place?
5. Do you have a target purchase timeline in mind?
6. Will this be a financed purchase or cash? (I can connect you with Texas land financing specialists if helpful.)

ABOUT YOUR CO-PURCHASERS:
7. Will everyone be viewing properties together, or will we need to coordinate remote walkthroughs?
8. Is there a point person for communication, or should I keep all co-purchasers in the loop?

Once I have your answers, I'll pull a curated list of available properties that match your vision and set up a time to walk through your options together — no obligation, just a great conversation.

Looking forward to helping your team find your perfect piece of Texas!

Warmly,
Kareesa Gonzales
Licensed TX Real Estate Agent
Keller Williams Preferred | Pearland, TX
cham4547@gmail.com

P.S. Feel free to text me anytime — I respond quickly and love connecting with my clients!$$,
    NOW()
),

-- ── STEP 3 — Day 3 — Check-In Text ───────────────────────────────────────────
(
    3,
    'text',
    NULL,
    $$Hi Sharon, Kareesa here! Just making sure my email made it through — sometimes they slip into spam. No rush at all, just want to make sure you got it. Whenever you're ready to chat, I'm here!$$,
    NOW() + INTERVAL '3 days'
),

-- ── STEP 4 — Day 7 — Value-Add Email ─────────────────────────────────────────
(
    4,
    'email',
    '5 Things Every Texas Land Buyer Should Know Before Making an Offer',
    $$Hi Sharon,

I hope your week is going well! I wanted to share a few things that come up with almost every land buyer I work with in Texas — knowing these upfront will save you time, money, and surprises down the road.

1. WATER IS EVERYTHING
Whether it's a water well, a rural water supply connection, or access to a creek, knowing your water source before making an offer is critical. Some properties look perfect but have no reliable water access at all.

2. AGRICULTURAL TAX EXEMPTIONS (1-D-1)
Many Texas land parcels qualify for an ag exemption, which can dramatically reduce your annual property taxes — sometimes by 90% or more. If the land you're buying doesn't currently have one, you may be able to apply after purchase. This can save thousands per year.

3. CHECK THE DEED RESTRICTIONS
Not all Texas rural land is wide open. Some tracts — especially those carved out of larger ranches — have deed restrictions on what you can build, whether you can subdivide, or what activities are permitted. We'll always pull these before you make an offer.

4. ROAD FRONTAGE AND LEGAL ACCESS
If a property doesn't have direct frontage on a maintained road, you'll need a recorded easement for legal access. This is easy to miss in online listings and critical to verify before moving forward.

5. MINERAL RIGHTS
In Texas, surface and mineral rights can be severed — and many sellers have already sold or reserved the minerals. It's important to know exactly what you're buying (and what you're not) before signing anything.

When we connect, I'll walk you through all of these for any property that catches your eye. My goal is for you and your co-purchasers to feel completely confident before we ever make an offer.

Have a wonderful week, Sharon — looking forward to hearing from you soon!

Warmly,
Kareesa Gonzales
KW Preferred | Pearland, TX | cham4547@gmail.com$$,
    NOW() + INTERVAL '7 days'
),

-- ── STEP 5 — Day 14 — Soft Re-Engagement Text ────────────────────────────────
(
    5,
    'text',
    NULL,
    $$Hi Sharon, Kareesa here! Just thinking about your Texas land search. Some interesting acreage has been coming to market lately. Whenever you're ready to take a look, I'll have a list ready for you. No rush at all!$$,
    NOW() + INTERVAL '14 days'
),

-- ── STEP 6 — Day 30 — Market Update Email ────────────────────────────────────
(
    6,
    'email',
    'Texas Land Market Update — And Checking In, Sharon',
    $$Hi Sharon,

I hope the past few weeks have been good to you! I've been keeping an eye on the Texas land market and wanted to share a few things that might be helpful for your search.

WHAT'S HAPPENING IN THE TEXAS LAND MARKET RIGHT NOW:
- Smaller rural tracts (under 50 acres) continue to see strong demand from buyers leaving urban areas — good selection if you move at the right time
- Hill Country inventory remains tight — properties there often receive multiple offers quickly and don't sit long
- East Texas and Southeast TX offer excellent value per acre right now for buyers looking for timber, recreation, or privacy
- Rural lending has remained steady — Farm Credit and Texas-based lenders are active and offering competitive terms

WHERE THINGS STAND FOR YOUR SEARCH:
When we last connected, I was hoping to learn more about your specific vision — the right acreage size, county preferences, and what you and your co-purchasers are ultimately looking to create. I haven't heard back yet, and I completely understand — life gets full!

I wanted to reach out one more time because I genuinely believe we can find something special for your group. When you're ready to dig in, I'm fully prepared to make your search efficient and exciting.

Would love to set up even a quick 15-minute call to get the conversation started. Just reply here or text me anytime.

Here for you whenever you're ready,

Kareesa Gonzales
Licensed TX Real Estate Agent
Keller Williams Preferred | Pearland, TX
cham4547@gmail.com$$,
    NOW() + INTERVAL '30 days'
)

) AS steps (step, channel, subject, content, scheduled_at)
ON CONFLICT (lead_id, step) DO NOTHING;
