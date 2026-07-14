"""
Shared Twilio SMS client for all AICC agents and routers.
Usage:
    from integrations.twilio_client import send_sms, send_alert

send_alert("Your message")          # always sends to KAREESA_PHONE
send_sms("+17135551234", "Message") # send to any number
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger


def _load_env() -> None:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / ".env"
        if candidate.exists():
            load_dotenv(candidate)
            return


_load_env()

# ── Milestone alert messages ───────────────────────────────────────────────────

MILESTONE_MESSAGES: dict[str, str] = {
    "offer_submitted":  "🏠 Offer submitted on {address}. Waiting on the seller.",
    "under_contract":   "🔐 LOCKED IN! {address} is under contract. Closing: {closing_date}.",
    "inspection":       "🔍 Inspection period started for {address}.",
    "closing":          "📋 Clear to close! {address} is heading to the closing table. Date: {closing_date}.",
    "closed":           "🎉 CLOSED! {address} — go celebrate, Kareesa! 💪",
    "fallen_through":   "⚠️ {address} has fallen through. Check transaction notes.",
}


# ── Core send functions ────────────────────────────────────────────────────────

def send_sms(to: str, body: str) -> bool:
    """Send an SMS to any number. Returns True on success."""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    auth_token  = os.getenv("TWILIO_AUTH_TOKEN", "")
    from_number = os.getenv("TWILIO_PHONE_NUMBER", "")

    if not all([account_sid, auth_token, from_number, to]):
        logger.warning("[twilio] Missing credentials or recipient — SMS skipped.")
        return False

    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        for chunk in _split(body):
            client.messages.create(body=chunk, from_=from_number, to=to)
        logger.info(f"[twilio] SMS sent to {to} ({len(body)} chars).")
        return True
    except Exception as exc:
        logger.error(f"[twilio] SMS failed to {to}: {exc}")
        return False


def send_alert(body: str) -> bool:
    """Send an SMS alert to Kareesa's phone (KAREESA_PHONE env var)."""
    to = os.getenv("KAREESA_PHONE", "")
    if not to:
        logger.warning("[twilio] KAREESA_PHONE not set — alert skipped.")
        return False
    return send_sms(to, body)


def send_milestone_alert(status: str, address: str, closing_date: str | None = None) -> bool:
    """Fire the appropriate milestone SMS when a transaction status changes."""
    template = MILESTONE_MESSAGES.get(status)
    if not template:
        return False
    body = template.format(
        address=address,
        closing_date=closing_date or "TBD",
    )
    logger.info(f"[twilio] Milestone alert — {status}: {address}")
    return send_alert(body)


# ── Helper ────────────────────────────────────────────────────────────────────

def _split(text: str, limit: int = 1550) -> list[str]:
    """Split long messages at paragraph boundaries to stay within SMS segment limits."""
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    current = ""
    for para in text.split("\n\n"):
        candidate = (current + "\n\n" + para).lstrip() if current else para
        if len(candidate) <= limit:
            current = candidate
        else:
            if current:
                chunks.append(current.strip())
            current = para
    if current:
        chunks.append(current.strip())
    return chunks or [text[:limit]]
