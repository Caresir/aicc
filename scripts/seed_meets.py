"""Seed Iyah Gonzales 2027 competition meets into AICC agent_memory."""
import os
import uuid
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

for parent in Path(__file__).resolve().parents:
    candidate = parent / ".env"
    if candidate.exists():
        load_dotenv(candidate)
        break

url = os.getenv("SUPABASE_URL", "")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")
db = create_client(url, key)

meets = [
    {"date": "2027-01-07", "name": "Rally in Valley",        "location": "Glendale, AZ",        "discipline": "All"},
    {"date": "2027-01-21", "name": "Pikes Peak Cup",          "location": "Colorado Springs, CO", "discipline": "All"},
    {"date": "2027-01-29", "name": "Biles Invitational",      "location": "Houston, TX",          "discipline": "All"},
    {"date": "2027-02-04", "name": "Metroplex Challenge",     "location": "Ft. Worth, TX",        "discipline": "All"},
    {"date": "2027-02-19", "name": "WOGA Classic",            "location": "Frisco, TX",           "discipline": "All"},
    {"date": "2027-02-26", "name": "Yellow Rose Invitational","location": "Pearland, TX",         "discipline": "All"},
    {"date": "2027-03-19", "name": "Level 9/10 State",        "location": "TBD",                  "discipline": "All"},
    {"date": "2027-04-02", "name": "Level 7/8 State",         "location": "TBD",                  "discipline": "All"},
    {"date": "2027-04-08", "name": "Level 9/10 Regionals",   "location": "Kansas City, KS",      "discipline": "All"},
    {"date": "2027-04-16", "name": "Level 6/7/8 Regionals",  "location": "TBD",                  "discipline": "All"},
    {"date": "2027-05-07", "name": "Level 9 Westerns",        "location": "Galveston, TX",        "discipline": "All"},
    {"date": "2027-05-13", "name": "Level 10 Nationals",      "location": "TBD",                  "discipline": "All"},
]

for m in meets:
    m["id"] = str(uuid.uuid4())

try:
    db.table("agent_memory").upsert(
        {
            "agent_name": "content_director",
            "memory_type": "schedule",
            "key": "gymnast_meets",
            "value": {"meets": meets},
        },
        on_conflict="agent_name,memory_type,key",
    ).execute()
    print("OK: Seeded 12 meets into agent_memory")
    for m in meets:
        print(f"  - {m['date']}  {m['name']}  ({m['location']})")
except Exception as e:
    print(f"FAIL: {e}")
