"""RealEstateAgent — AI assistant for Kareesa Gonzales, KW Preferred Pearland TX."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from loguru import logger

from agents.base_agent import BaseAgent

SYSTEM_PROMPT = """You are the Real Estate Assistant for Kareesa Gonzales, a licensed Texas \
real estate agent with Keller Williams Preferred in Pearland, TX.

ABOUT KAREESA:
- Brand: "Locked In with Kareesa"
- Email: cham4547@gmail.com
- Brokerage: Keller Williams Preferred, Pearland TX
- Broker/Coach: Jennifer — ALL transaction documents must be reviewed and approved by Jennifer \
before being executed in Lone Wolf Transactions. This rule is absolute and cannot be overridden.
- Sponsor Agent: Kimberly Spiller
- License State: TX

YOUR ROLE:
You manage Kareesa's real estate business end-to-end:
- Draft follow-up texts and emails for leads (warm, personal, never salesy)
- Research buyer and seller needs, match to available properties
- Maintain lead pipeline notes and status updates
- Draft agreements and documents FOR JENNIFER'S REVIEW ONLY — never send
- Summarize MLS data and Texas land market conditions
- Build nurture sequences to move leads from contact to close

ACTIVE LEAD — SHARON TRAYLOR:
- Lead type: Land buyer
- Referred by: Shay Mims
- Situation: Purchasing acreage in Texas with co-purchasers
- Status: New — welcome sequence pending
- Discovery needed: acreage range, county preferences, purpose, financing status, co-purchaser details

TONE GUIDELINES:
- Warm, authentic, encouraging — never pushy or salesy
- Texts: conversational, first-name basis, under 160 characters when possible
- Emails: clear subject, short paragraphs, one call to action, full signature
- Never use jargon — speak plainly like a trusted advisor

CRITICAL RULES (never break):
1. NEVER execute or submit documents in Lone Wolf Transactions — always draft the text and flag for Jennifer's review
2. NEVER fabricate MLS data, prices, or property details — use placeholders if real data is unavailable
3. NEVER commit to commission rates, timelines, or prices without Kareesa's explicit approval
4. ALWAYS produce drafts — Kareesa approves all outbound communications before delivery
5. For any legal or compliance question, recommend consulting Jennifer or KW compliance

TEXAS LAND EXPERTISE:
- Key regions: Hill Country (Blanco, Gillespie, Kendall), East TX (Nacogdoches, Angelina, Jasper), \
Southeast TX (Liberty, Hardin, Polk), Brazos Valley (Grimes, Washington, Burleson), Piney Woods
- Common uses: residential homesite, hunting/recreation, agricultural (hay/cattle), investment
- Key buyer considerations: water well, septic, electricity access, road frontage, deed restrictions, \
flood zone, mineral rights, survey
- Financing options: USDA rural loans, Farm Credit, Texas Farm Bureau, conventional for small tracts
- Texas-specific: no state income tax, ag tax exemptions (1-d-1), right of first refusal on adjoining tracts

OUTPUT FORMAT:
- Draft texts: label clearly as DRAFT TEXT:
- Draft emails: label as DRAFT EMAIL: with SUBJECT: and BODY: sections
- Sequences: number each step with Day, Channel, and content
- End all drafts with: — Awaiting Kareesa's review before sending
"""


class RealEstateAgent(BaseAgent):
    """AI real estate assistant for lead management, follow-up, and transaction support."""

    def _agent_name(self) -> str:
        return "real_estate"

    def _system_prompt(self) -> str:
        return SYSTEM_PROMPT

    # ── Lead communication ─────────────────────────────────────────────────────

    def draft_welcome_text(self, lead: dict) -> str:
        """Draft a welcome SMS for a new lead."""
        context = self._lead_context(lead)
        result = self.think(
            "Draft a warm welcome text message for this new lead. "
            "Reference who referred them. Keep it under 160 characters. "
            "Mention you are sending an email. Sign off with Kareesa's name.",
            context=context,
        )
        self.remember(f"lead:{lead['id']}:welcome_text", result)
        return result

    def draft_welcome_email(self, lead: dict) -> dict[str, str]:
        """Draft a welcome email with discovery questions for a new lead."""
        context = self._lead_context(lead)
        result = self.think(
            "Draft a warm welcome email for this lead. Include: "
            "(1) reference to their referral source, "
            "(2) brief intro of Kareesa, "
            "(3) 6-7 discovery questions tailored to their property type, "
            "(4) a dedicated question about co-purchasers if applicable, "
            "(5) clear next steps, "
            "(6) full signature with name, brokerage, and email. "
            "Format your response as: SUBJECT: [line]\n\nBODY:\n[content]",
            context=context,
        )
        subject, body = self._parse_email(result)
        output = {"subject": subject, "body": body, "raw": result}
        self.remember(f"lead:{lead['id']}:welcome_email", output)
        return output

    def draft_follow_up(self, lead: dict, step: int, channel: str = "text") -> str:
        """Draft a follow-up message at a specific sequence step."""
        context = self._lead_context(lead)
        context["sequence_step"] = step
        context["channel"] = channel

        guidance = {
            3:  "Day 3 check-in — did they see the welcome email? Short, low-pressure.",
            7:  "Day 7 value add — share something useful about their property type. No ask.",
            14: "Day 14 soft re-engagement — personal and light. Available when they are ready.",
            30: "Day 30 long-term nurture — relevant market update. Pure value, no pressure.",
        }.get(step, f"Follow-up step {step} — continue the nurture sequence.")

        return self.think(
            f"Draft a {channel} for this lead at sequence step {step}. {guidance}",
            context=context,
        )

    def research_lead(self, lead: dict) -> str:
        """Build a research brief for a lead and store it in agent memory."""
        context = self._lead_context(lead)
        brief = self.think(
            "Write a research brief for this lead. Include: "
            "(1) Summary of their situation and known needs, "
            "(2) Key questions still unanswered, "
            "(3) Recommended property criteria based on what we know, "
            "(4) Relevant Texas land/market context, "
            "(5) Suggested approach for the first conversation.",
            context=context,
        )
        self.remember(f"lead:{lead['id']}:research", brief, memory_type="fact")
        return brief

    # ── Sequence management ────────────────────────────────────────────────────

    def generate_sequence(self, lead: dict) -> list[dict[str, Any]]:
        """Ask Claude to generate a complete 6-step follow-up sequence for this lead."""
        context = self._lead_context(lead)
        raw = self.think(
            "Generate a complete 6-step follow-up sequence for this lead. "
            "Steps: Day 0 welcome text, Day 0 welcome email, Day 3 check-in text, "
            "Day 7 value-add email, Day 14 re-engagement text, Day 30 market update email. "
            "Format each step as:\n"
            "STEP [N] | Day [D] | Channel: [text/email]\n"
            "SUBJECT: [subject if email]\n"
            "[message content]\n---",
            context=context,
        )
        self.remember(f"lead:{lead['id']}:sequence_draft", raw)
        return self._parse_sequence(raw, lead)

    def save_sequence(self, lead_id: str, steps: list[dict[str, Any]]) -> None:
        """Persist a follow-up sequence to the follow_up_sequences table."""
        try:
            self._db.table("follow_up_sequences").upsert(
                steps, on_conflict="lead_id,step"
            ).execute()
            logger.info(f"[real_estate] Saved {len(steps)}-step sequence for lead {lead_id}.")
        except Exception as exc:
            logger.error(f"[real_estate] save_sequence() failed: {exc}")

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _lead_context(self, lead: dict) -> dict[str, Any]:
        ctx: dict[str, Any] = {
            "lead_name": f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip(),
            "lead_type": lead.get("lead_type", "unknown"),
            "source": lead.get("source", "unknown"),
            "referrer": lead.get("referrer") or "none",
            "status": lead.get("status", "new"),
        }
        if lead.get("budget_min") or lead.get("budget_max"):
            ctx["budget"] = f"${lead.get('budget_min', '?')} – ${lead.get('budget_max', '?')}"
        if lead.get("desired_areas"):
            ctx["desired_areas"] = ", ".join(lead["desired_areas"])
        if lead.get("co_purchasers"):
            ctx["co_purchasers"] = str(lead["co_purchasers"])
        if lead.get("property_criteria"):
            ctx["property_criteria"] = str(lead["property_criteria"])
        if lead.get("notes"):
            ctx["notes"] = lead["notes"]
        return ctx

    @staticmethod
    def _parse_email(raw: str) -> tuple[str, str]:
        subject, body = "", raw
        for line in raw.splitlines():
            stripped = line.strip()
            if stripped.upper().startswith("SUBJECT:"):
                subject = stripped.split(":", 1)[1].strip()
            elif stripped.upper().startswith("BODY:"):
                body = raw.split("BODY:", 1)[-1].strip()
                break
        return subject, body

    @staticmethod
    def _parse_sequence(raw: str, lead: dict) -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc)
        day_offsets = {1: 0, 2: 0, 3: 3, 4: 7, 5: 14, 6: 30}
        channels    = {1: "text", 2: "email", 3: "text", 4: "email", 5: "text", 6: "email"}

        steps: list[dict[str, Any]] = []
        blocks = [b.strip() for b in raw.split("---") if b.strip()]

        for i, block in enumerate(blocks[:6], start=1):
            subject = ""
            content_lines: list[str] = []
            for line in block.splitlines():
                upper = line.strip().upper()
                if upper.startswith("STEP") or upper.startswith("| DAY") or upper.startswith("CHANNEL"):
                    continue
                elif upper.startswith("SUBJECT:"):
                    subject = line.split(":", 1)[-1].strip()
                else:
                    content_lines.append(line)

            content = "\n".join(content_lines).strip() or block

            steps.append({
                "lead_id": lead["id"],
                "step": i,
                "channel": channels.get(i, "text"),
                "subject": subject or None,
                "content": content,
                "scheduled_at": (now + timedelta(days=day_offsets.get(i, 0))).isoformat(),
                "status": "pending",
            })

        return steps
