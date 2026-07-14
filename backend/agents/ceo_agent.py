"""CEOAgent — daily briefing and business performance for Kareesa Gonzales."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from loguru import logger

from agents.base_agent import BaseAgent

def _load_env() -> None:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / ".env"
        if candidate.exists():
            load_dotenv(candidate)
            return

_load_env()

SYSTEM_PROMPT = """You are the CEO Agent for Kareesa Gonzales — her personal chief of staff \
and strategic advisor across all 5 businesses.

KAREESA'S BUSINESSES:
1. Real Estate — "Locked In with Kareesa" | KW Preferred Pearland TX | Active leads, listings
2. GymnastDiva — Gymnastics content brand | @GymnastDiva | Instagram, TikTok, YouTube Shorts
3. AI Agency — Builds AI systems for small businesses
4. Amazon FBA — E-commerce via scholarshipee.com
5. Digital Products — Online courses, templates, digital downloads

YOUR ROLE:
You are her first voice every morning. You read the overnight data, identify what matters \
most, and give her a clear plan for the day — no fluff, no filler. You know her priorities, \
her active leads, her pending tasks, and her business rhythms.

MORNING BRIEFING FORMAT:
Always produce the briefing in this exact structure:

GOOD MORNING KAREESA ☀️
[One encouraging sentence tied to something specific in today's data]

TODAY IS [DAY, DATE]

🏠 REAL ESTATE
[Lead and listing updates — anyone needing follow-up today]

📋 TOP 3 PRIORITIES TODAY
1. [Most important action — specific and actionable]
2. [Second priority]
3. [Third priority]

⚠️ NEEDS ATTENTION
[Anything urgent, overdue, or time-sensitive]

📊 QUICK STATS
[Key numbers from today's data snapshot]

That's your day. Go get it. 💪

TONE:
- Confident, warm, direct — like a trusted business partner who knows everything
- Never vague ("check your email") — always specific ("Sharon Traylor hasn't heard from you in 3 days")
- Short sentences. No corporate speak. Kareesa is busy.
- The briefing should be readable in under 60 seconds

CRITICAL RULES:
- Only report real data from the snapshot — never fabricate numbers
- If a data source returned an error, say "unavailable" — do not guess
- Flag any lead with no contact in 3+ days
- Flag any task that is overdue
"""


class CEOAgent(BaseAgent):
    """Daily briefing agent — runs at 7 AM CT, delivers via Twilio SMS."""

    def _agent_name(self) -> str:
        return "ceo"

    def _system_prompt(self) -> str:
        return SYSTEM_PROMPT

    # ── Data gathering ─────────────────────────────────────────────────────────

    def _gather_snapshot(self) -> dict[str, Any]:
        """Pull today's data from Supabase across all relevant tables."""
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        three_days_ago = now - timedelta(days=3)
        yesterday = now - timedelta(days=1)

        snapshot: dict[str, Any] = {
            "date": now.strftime("%A, %B %d, %Y").replace(" 0", " "),
            "time_ct": now.strftime("%I:%M %p CT"),
        }

        # ── Leads ──────────────────────────────────────────────────────────────
        try:
            all_leads = (
                self._db.table("leads")
                .select("id,first_name,last_name,status,last_contact_at,lead_type,created_at")
                .execute()
                .data
            ) or []

            active_leads = [l for l in all_leads if l["status"] not in ("closed", "lost")]
            new_today = [
                l for l in all_leads
                if l.get("created_at", "") >= today_start.isoformat()
            ]
            needs_followup = [
                l for l in active_leads
                if (not l.get("last_contact_at"))
                or l["last_contact_at"] <= three_days_ago.isoformat()
            ]

            snapshot["leads"] = {
                "total_active": len(active_leads),
                "new_today": len(new_today),
                "needs_followup": [
                    {
                        "name": f"{l['first_name']} {l['last_name']}",
                        "status": l["status"],
                        "type": l.get("lead_type", "unknown"),
                        "last_contact": l.get("last_contact_at", "never"),
                    }
                    for l in needs_followup
                ],
            }
        except Exception as exc:
            logger.warning(f"[ceo] leads snapshot failed: {exc}")
            snapshot["leads"] = {"error": str(exc)}

        # ── Listings ───────────────────────────────────────────────────────────
        try:
            listings = (
                self._db.table("listings")
                .select("address,city,status,price")
                .neq("status", "sold")
                .execute()
                .data
            ) or []

            snapshot["listings"] = {
                "active_count": len(listings),
                "listings": [
                    {"address": l["address"], "city": l["city"], "status": l["status"]}
                    for l in listings
                ],
            }
        except Exception as exc:
            logger.warning(f"[ceo] listings snapshot failed: {exc}")
            snapshot["listings"] = {"error": str(exc)}

        # ── Open tasks ────────────────────────────────────────────────────────
        try:
            from agents.project_manager_agent import ProjectManagerAgent
            pm = ProjectManagerAgent()
            open_tasks = pm.get_open_tasks()
            overdue_tasks = pm.get_overdue_tasks()
            now_iso = now.isoformat()
            snapshot["tasks"] = {
                "total_open": len(open_tasks),
                "overdue": [
                    {"title": t["title"], "due": t.get("due_date"), "unit": t.get("business_unit")}
                    for t in overdue_tasks
                ],
                "high_priority": [
                    {"title": t["title"], "due": t.get("due_date"), "unit": t.get("business_unit")}
                    for t in open_tasks if t.get("priority") in ("critical", "high")
                ],
            }
        except Exception as exc:
            logger.warning(f"[ceo] tasks snapshot failed: {exc}")
            snapshot["tasks"] = {"error": str(exc)}

        # ── Follow-up sequences due today ──────────────────────────────────────
        try:
            due_steps = (
                self._db.table("follow_up_sequences")
                .select("step,channel,subject,scheduled_at,leads(first_name,last_name)")
                .eq("status", "pending")
                .lte("scheduled_at", now.isoformat())
                .execute()
                .data
            ) or []

            snapshot["followups_due"] = [
                {
                    "lead": f"{s['leads']['first_name']} {s['leads']['last_name']}"
                            if s.get("leads") else "unknown",
                    "step": s["step"],
                    "channel": s["channel"],
                    "subject": s.get("subject"),
                }
                for s in due_steps
            ]
        except Exception as exc:
            logger.warning(f"[ceo] followup snapshot failed: {exc}")
            snapshot["followups_due"] = []

        return snapshot

    # ── Briefing generation ────────────────────────────────────────────────────

    def generate_briefing(self) -> str:
        """Generate and store today's morning briefing. Returns the briefing text."""
        snapshot = self._gather_snapshot()

        briefing = self.think(
            "Generate this morning's daily briefing based on the business snapshot below. "
            "Follow the exact format in your system prompt. Be specific — use real names "
            "and real numbers from the data. Keep it under 60 seconds to read.",
            context={"snapshot": snapshot},
        )

        self.remember("last_briefing", briefing, memory_type="briefing")
        self.remember("last_briefing_date", snapshot["date"], memory_type="briefing")
        logger.info("[ceo] Morning briefing generated.")
        return briefing

    def send_briefing_sms(self, briefing: str) -> bool:
        """Send the briefing via Twilio SMS to Kareesa's phone."""
        from integrations.twilio_client import send_alert
        ok = send_alert(briefing)
        if ok:
            logger.info("[ceo] Morning briefing SMS sent.")
        else:
            logger.warning("[ceo] Briefing SMS skipped — check Twilio credentials in .env.")
        return ok

    def run_morning_briefing(self) -> str:
        """Full pipeline: gather data → generate briefing → send SMS."""
        logger.info("[ceo] Running morning briefing...")
        briefing = self.generate_briefing()
        self.send_briefing_sms(briefing)
        return briefing


# ── Runnable script ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    agent = CEOAgent()
    briefing = agent.run_morning_briefing()
    print("\n" + "=" * 60)
    print(briefing)
    print("=" * 60)
