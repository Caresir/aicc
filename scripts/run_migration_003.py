"""Run migration 003 statements via Supabase Python client."""
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load .env from repo root
for parent in Path(__file__).resolve().parents:
    candidate = parent / ".env"
    if candidate.exists():
        load_dotenv(candidate)
        break

url = os.getenv("SUPABASE_URL", "")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")
db = create_client(url, key)

steps = [
    ("Register fba_manager agent", lambda: db.table("agents").upsert({
        "name": "fba_manager",
        "display_name": "FBA Manager",
        "description": "Amazon FBA brand approvals, distributor management, wholesale strategy",
    }, on_conflict="name").execute()),

    ("Register content_director agent", lambda: db.table("agents").upsert({
        "name": "content_director",
        "display_name": "Content Director",
        "description": "GymnastDiva content, captions, hashtags, platform scheduling",
    }, on_conflict="name").execute()),

    ("Enrich Cairnvillage listing", lambda: db.table("listings").update({
        "listing_type": "sale",
        "status": "on_hold",
        "city": "Houston",
        "state": "TX",
        "zip": "77084",
        "notes": (
            "Probate listing — on hold pending title clearance due to sibling estate dispute. "
            "Client: Nadine. Already loaded in Lone Wolf Transactions. "
            "Do not market or show until hold is lifted. Contact Jennifer before any action on this file."
        ),
    }).eq("address", "4707 Cairnvillage St").execute()),
]

for label, fn in steps:
    try:
        result = fn()
        print(f"  OK: {label}")
    except Exception as e:
        print(f"  FAIL: {label}: {e}")

print("\nDone. The meets table requires raw SQL — run this in Supabase Studio separately:")
print("""
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
""")
