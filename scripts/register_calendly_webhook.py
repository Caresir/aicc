"""One-time setup: register the AICC n8n webhook with Calendly's API.

Calendly webhook subscriptions can only be created via API, not through the
Calendly UI for a personal account, so this script does it for you. Run it
once after n8n is reachable from the public internet (see
n8n/calendly_lesson_booking.json's notes field for why that matters).

Usage:
    python scripts/register_calendly_webhook.py https://your-public-n8n-url.com

Requires CALENDLY_API_KEY and CALENDLY_USER_URI already set in .env.
"""
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

for parent in Path(__file__).resolve().parents:
    candidate = parent / ".env"
    if candidate.exists():
        load_dotenv(candidate)
        break

API_KEY = os.getenv("CALENDLY_API_KEY", "")
USER_URI = os.getenv("CALENDLY_USER_URI", "")

if not API_KEY or not USER_URI:
    sys.exit("CALENDLY_API_KEY and/or CALENDLY_USER_URI missing from .env")

if len(sys.argv) != 2:
    sys.exit(
        "Usage: python scripts/register_calendly_webhook.py "
        "https://your-public-n8n-url.com"
    )

n8n_base = sys.argv[1].rstrip("/")
webhook_url = f"{n8n_base}/webhook/calendly-lesson-booking"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

me = httpx.get("https://api.calendly.com/users/me", headers=headers)
me.raise_for_status()
organization_uri = me.json()["resource"]["current_organization"]

resp = httpx.post(
    "https://api.calendly.com/webhook_subscriptions",
    headers=headers,
    json={
        "url": webhook_url,
        "events": ["invitee.created"],
        "organization": organization_uri,
        "user": USER_URI,
        "scope": "user",
    },
)

if resp.status_code == 201:
    print(f"Registered Calendly webhook -> {webhook_url}")
    print(resp.json())
else:
    print(f"Calendly API returned {resp.status_code}:")
    print(resp.text)
    sys.exit(1)
