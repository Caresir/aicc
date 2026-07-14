"""
Sharon Traylor — Lead Onboarding Package
=========================================
Referred by: Shay Mims
Lead type:   Land buyer
Situation:   Purchasing acreage in Texas with co-purchasers
Initialized: 2026-06-26

This module documents Sharon's pre-written onboarding content and provides
a run_onboarding() function that generates + saves her follow-up sequence
via the Real Estate Assistant agent.

The sequence is also seeded in migration 002 — run this script only if you
need to regenerate or refresh the sequence after making edits.

RESOLVED 2026-07-13: Sharon was manually enrolled in the KW Command "Locked In
Land Buyer Class" SmartPlan on 2026-07-09 (auto-sending, 10 emails/19 days,
same land-education curriculum as step 4 below). Step 4 has been marked
"skipped" in follow_up_sequences to avoid duplicate content — the SmartPlan is
now the primary land-education channel for her. If this script is re-run to
regenerate the sequence, re-apply that skip afterward.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root before anything else.
# Walks up the directory tree so this works regardless of CWD.
def _load_env() -> None:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / ".env"
        if candidate.exists():
            load_dotenv(candidate)
            return

_load_env()

# ── Pre-written onboarding content ────────────────────────────────────────────

LEAD_PROFILE = {
    "first_name": "Sharon",
    "last_name": "Traylor",
    "source": "referral",
    "referrer": "Shay Mims",
    "lead_type": "land",
    "status": "new",
    "notes": (
        "Land buyer referred by Shay Mims. Interested in purchasing acreage in Texas "
        "with co-purchasers. Acreage range, county preferences, purpose, and financing "
        "TBD at intake call."
    ),
    "co_purchasers": [
        {"name": "TBD", "notes": "Co-purchaser details to be gathered during intake call"}
    ],
    "property_criteria": {
        "type": "land",
        "acreage_min": None,
        "acreage_max": None,
        "counties_preferred": [],
        "purpose": "TBD — personal/homesite/agricultural/investment",
        "water_needed": True,
        "road_access": True,
        "utilities_notes": "TBD at intake",
        "mineral_rights_preference": "TBD",
    },
}

WELCOME_TEXT = (
    "Hi Sharon! This is Kareesa Gonzales with Keller Williams Preferred. "
    "Shay Mims mentioned you're searching for land in Texas — so excited to help! "
    "Sending you an email now with a few questions to get started."
)

WELCOME_EMAIL_SUBJECT = "Your Texas Land Search Starts Here, Sharon"

WELCOME_EMAIL_BODY = """Hi Sharon,

It was so wonderful to hear about you through Shay Mims — anyone in Shay's circle \
is someone I'm truly excited to work with!

I'm Kareesa Gonzales, your dedicated real estate agent with Keller Williams Preferred \
in Pearland, TX. Helping buyers find their perfect piece of Texas land is one of my \
favorite parts of this work, and I'd love to make your search as smooth and successful \
as possible.

To make sure I'm finding the right properties for you and your co-purchasers, I have \
a few quick discovery questions:

ABOUT YOUR SEARCH:
1. What regions or counties of Texas are you most interested in? \
(Hill Country, East Texas, Brazos Valley, Southeast TX — or open to anywhere?)
2. What's your ideal acreage range? (Under 10 acres, 10–50, 50–100, 100+?)
3. What's the primary purpose for the land? \
(Personal homesite, hunting/recreation, agriculture, investment, or a combination?)
4. Are utilities important — do you need existing electricity, a water well, \
or septic already in place?
5. Do you have a target purchase timeline in mind?
6. Will this be a financed purchase or cash? \
(I can connect you with Texas land financing specialists if helpful.)

ABOUT YOUR CO-PURCHASERS:
7. Will everyone be viewing properties together, or will we need to coordinate \
remote walkthroughs?
8. Is there a point person for communication, or should I keep all co-purchasers \
in the loop?

Once I have your answers, I'll pull a curated list of available properties that \
match your vision and set up a time to walk through your options together — no \
obligation, just a great conversation.

Looking forward to helping your team find your perfect piece of Texas!

Warmly,
Kareesa Gonzales
Licensed TX Real Estate Agent
Keller Williams Preferred | Pearland, TX
cham4547@gmail.com

P.S. Feel free to text me anytime — I respond quickly and love connecting with clients!"""

FOLLOW_UP_SEQUENCE = [
    {
        "step": 1,
        "day": 0,
        "channel": "text",
        "subject": None,
        "content": WELCOME_TEXT,
    },
    {
        "step": 2,
        "day": 0,
        "channel": "email",
        "subject": WELCOME_EMAIL_SUBJECT,
        "content": WELCOME_EMAIL_BODY,
    },
    {
        "step": 3,
        "day": 3,
        "channel": "text",
        "subject": None,
        "content": (
            "Hi Sharon, Kareesa here! Just making sure my email made it through — "
            "sometimes they slip into spam. No rush at all, just want to make sure "
            "you got it. Whenever you're ready to chat, I'm here!"
        ),
    },
    {
        "step": 4,
        "day": 7,
        "channel": "email",
        "subject": "5 Things Every Texas Land Buyer Should Know Before Making an Offer",
        "content": (
            "Educational email covering: water access, ag tax exemptions (1-d-1), "
            "deed restrictions, road frontage/legal access, and mineral rights. "
            "See migration 002 for full body text."
        ),
    },
    {
        "step": 5,
        "day": 14,
        "channel": "text",
        "subject": None,
        "content": (
            "Hi Sharon, Kareesa here! Just thinking about your Texas land search. "
            "Some interesting acreage has been coming to market lately. Whenever "
            "you're ready to take a look, I'll have a list ready for you. No rush!"
        ),
    },
    {
        "step": 6,
        "day": 30,
        "channel": "email",
        "subject": "Texas Land Market Update — And Checking In, Sharon",
        "content": (
            "Market update email covering current land trends by region, "
            "Hill Country inventory, East TX value per acre, and rural lending. "
            "See migration 002 for full body text."
        ),
    },
]


# ── Runnable script ────────────────────────────────────────────────────────────

def run_onboarding() -> None:
    """
    Look up Sharon's lead record, generate her sequence via the Real Estate
    Assistant agent (Claude), and save it to follow_up_sequences.

    Run from the backend/ directory:
        python -m agents.sequences.sharon_traylor
    """
    from supabase import create_client

    supabase_key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_ANON_KEY")
        or os.getenv("SUPABASE_SECRET_KEY")
        or os.getenv("SUPABASE_PUBLISHABLE_KEY")
        or ""
    )
    db = create_client(os.getenv("SUPABASE_URL", ""), supabase_key)

    rows = (
        db.table("leads")
        .select("*")
        .eq("first_name", "Sharon")
        .eq("last_name", "Traylor")
        .limit(1)
        .execute()
        .data
    )

    if not rows:
        print("Sharon Traylor not found in leads table. Run migration 002 first.")
        sys.exit(1)

    lead = rows[0]
    print(f"Found lead: {lead['first_name']} {lead['last_name']} (ID: {lead['id']})")

    from agents.real_estate_agent import RealEstateAgent

    agent = RealEstateAgent()

    print("\n--- RESEARCH BRIEF ---")
    brief = agent.research_lead(lead)
    print(brief)

    print("\n--- WELCOME TEXT DRAFT ---")
    text = agent.draft_welcome_text(lead)
    print(text)

    print("\n--- WELCOME EMAIL DRAFT ---")
    email = agent.draft_welcome_email(lead)
    print(f"SUBJECT: {email['subject']}\n\n{email['body']}")

    print("\n--- GENERATING 6-STEP SEQUENCE ---")
    steps = agent.generate_sequence(lead)
    agent.save_sequence(lead["id"], steps)
    print(f"Saved {len(steps)} steps to follow_up_sequences.")
    for s in steps:
        print(f"  Step {s['step']} | {s['channel']} | {s['scheduled_at'][:10]}")


if __name__ == "__main__":
    run_onboarding()
