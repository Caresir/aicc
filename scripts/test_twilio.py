"""
Test Twilio SMS integration.
Run from the aicc/backend/ directory:
    python ../scripts/test_twilio.py

Sends two test messages to KAREESA_PHONE:
  1. A plain test ping
  2. A simulated transaction milestone alert
"""
import sys
from pathlib import Path

# Make sure backend modules are importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from integrations.twilio_client import send_alert, send_milestone_alert

print("=" * 55)
print("AICC — Twilio SMS Test")
print("=" * 55)

# Test 1: plain alert
print("\n[1] Sending test ping to KAREESA_PHONE...")
ok = send_alert(
    "✅ AICC Twilio test — your SMS notifications are live! "
    "Morning briefings and milestone alerts are ready. 🔐"
)
print("   Result:", "SENT" if ok else "FAILED -- check .env credentials and Twilio Trust Hub")

# Test 2: milestone alert
print("\n[2] Sending simulated milestone alert (under_contract)...")
ok2 = send_milestone_alert(
    status="under_contract",
    address="4707 Cairnvillage St, Houston TX 77084",
    closing_date="2026-08-15",
)
print("   Result:", "SENT" if ok2 else "FAILED")

print("\nDone. Check your phone.")
print("=" * 55)
