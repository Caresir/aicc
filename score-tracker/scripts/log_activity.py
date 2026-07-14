"""
SCORE Tracker — manual CLI logger.

Fallback for logging a SCORE activity from the terminal instead of SMS.

Usage:
    python log_activity.py conversation 5 --note "called sphere"
    python log_activity.py cma 1
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ALLOWED_ACTIVITY_TYPES = [
    "social_post",
    "kwp_class",
    "signed_agreement",
    "oh_flyer_share",
    "oh_doorknock",
    "oh_host",
    "oh_followup",
    "conversation",
    "command_opportunity",
    "cma",
]


def _load_env() -> None:
    for parent in [Path(__file__).resolve().parent, *Path(__file__).resolve().parents]:
        candidate = parent / ".env"
        if candidate.exists():
            load_dotenv(candidate)
            return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Log a SCORE activity manually.")
    parser.add_argument("activity_type", choices=ALLOWED_ACTIVITY_TYPES, help="Activity type")
    parser.add_argument("quantity", type=int, help="Quantity (must be a positive integer)")
    parser.add_argument("--note", default=None, help="Optional note")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.quantity <= 0:
        print(f"ERROR: quantity must be a positive integer, got {args.quantity}")
        sys.exit(1)

    _load_env()

    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")

    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set (score-tracker/.env or shell env).")
        sys.exit(1)

    from supabase import create_client

    client = create_client(supabase_url, supabase_key)

    row = {
        "activity_type": args.activity_type,
        "quantity": args.quantity,
        "notes": args.note,
        "source": "manual",
    }

    result = client.table("score_activities").insert(row).execute()

    if not result.data:
        print("ERROR: insert returned no data — check Supabase credentials and RLS policies.")
        sys.exit(1)

    inserted = result.data[0]
    print(f"Logged: {args.quantity}x {args.activity_type}" + (f" — {args.note}" if args.note else ""))
    print(f"Row ID: {inserted.get('id')}")


if __name__ == "__main__":
    main()
