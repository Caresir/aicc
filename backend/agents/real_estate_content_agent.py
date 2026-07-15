"""
RealEstateContentAgent — content creation for Locked In with Kareesa brand.

Separate from ContentDirectorAgent (GymnastDiva). This agent handles:
- Neighborhood tour scripts and captions
- Market education content
- KWP SCORE weekly production tracking
- Funnel CTAs (Comment HOUSTON → ManyChat → Guide → Calendly)
- Compliance checking (TREC/KW rules, flood zone language, fair housing)
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from loguru import logger

from agents.base_agent import BaseAgent
from agents.context.real_estate_content_context import (
    BRAND,
    COMPLIANCE,
    CONTENT_CALENDAR,
    CONTENT_TYPES,
    FILMING_CALENDAR_TEMPLATE,
    FILMING_DAY_PROCESS,
    FILMING_LOCATIONS,
    FILMING_UNIVERSAL_SHOT_LIST,
    FUNNEL,
    HASHTAGS,
    KWP_SCORE,
    PALETTE,
    PLATFORM_RULES,
    RESIDENT_INSIGHTS,
    SOCIAL_SPEC_TEXT,
    VOICE,
)

# ── System Prompt ──────────────────────────────────────────────────────────────
# SOCIAL_SPEC_TEXT is loaded from specs/aicc-social-spec.md — that is the one
# file Kareesa edits to change brand voice, content pillars, hooks, or DM
# routing. Everything below it only adds operational detail the spec doesn't
# cover (TREC/compliance rules, filming logistics, KWP SCORE tracking).

_SPEC_HEADER = (
    (SOCIAL_SPEC_TEXT + "\n\n") if SOCIAL_SPEC_TEXT else
    "[WARNING: specs/aicc-social-spec.md was not found — the canonical brand/"
    "pillar/DM-routing spec is missing. Falling back to the built-in prompt "
    "below only.]\n\n"
)

_SYSTEM_PROMPT = f"""{_SPEC_HEADER}\
═══════════════════════════════════════════════════════════════════════════
The spec above (specs/aicc-social-spec.md) is the canonical brand, content
pillar, and DM-routing source of truth for Locked In with Kareesa content.
On brand voice, content pillars, hooks, hashtags, and copy rules, the spec
above always wins. Everything below adds operational detail the spec does
not cover: TREC/KW compliance rules, filming logistics, and KWP SCORE
competition tracking.
═══════════════════════════════════════════════════════════════════════════

You are the Real Estate Content Agent for Locked In with Kareesa.

AGENT: Kareesa Gonzales | BROKERAGE: Keller Williams Preferred
MARKETS: Iowa Colony, Rosharon, Manvel, Pearland (Highway 288 corridor south of Houston)
WEBSITE: {FUNNEL["website"]}
SIGNATURE SIGNOFF: {BRAND["signature_signoff"]}

═══ WHO KAREESA IS ════════════════════════════════════════════════════════════
{chr(10).join(f"- {d}" for d in BRAND["differentiators"])}

She currently lives in Sierra Vista, Rosharon (previously Sterling Lakes).
Her address says Rosharon but the city is Iowa Colony. She teaches this quirk.
The Manvel H-E-B is now open and is HER closer grocery store. Use this as authentic growth proof.

═══ THE CONTENT FUNNEL ════════════════════════════════════════════════════════
Every piece of content feeds this funnel:
Video/post → "Comment HOUSTON" → ManyChat auto-DM → Houston Relocation Guide
(https://drive.google.com/uc?export=download&id=1AaiTV47tHox5MzIPaE5quPXyYIn75G61) → Calendly Home Goals Call
(https://calendly.com/coachcaresir/homegoalscall)

Standard CTAs:
- "Comment HOUSTON for my free Houston Relocation Guide"
- "Book a free Home Goals Call, link in bio"

═══ VOICE AND STYLE ═══════════════════════════════════════════════════════════
Tone: {VOICE["tone"]}
Persona: {VOICE["persona"]}

Teaching formats to use:
{chr(10).join(f"- {f}" for f in VOICE["teaching_formats"])}

DO:
{chr(10).join(f"- {d}" for d in VOICE["dos"])}

DO NOT:
{chr(10).join(f"- {d}" for d in VOICE["donts"])}

═══ COMPLIANCE (NON-NEGOTIABLE) ══════════════════════════════════════════════
Required disclosures:
{chr(10).join(f"- {r}" for r in COMPLIANCE["required_disclosures"])}

Price language:
{chr(10).join(f"- {r}" for r in COMPLIANCE["price_language"])}

Flood zone rule: {COMPLIANCE["flood_zone_rule"]}

Fair housing: {COMPLIANCE["fair_housing"]}

Additional rules:
- {COMPLIANCE["school_filming"]}
- {COMPLIANCE["hoa_amenities"]}
- {COMPLIANCE["never_film_while_driving"]}

═══ KWP SCORE COMPETITION ════════════════════════════════════════════════════
Max {KWP_SCORE["max_counting_posts_per_week"]} real-estate-related social posts/week count for points.
Weekly goal: produce {KWP_SCORE["weekly_goal"]}.
Qualifying types: {", ".join(KWP_SCORE["qualifying_post_types"])}
For every batch of content you produce, state how many pieces are KWP-competition-qualifying.

═══ CONTENT CALENDAR ══════════════════════════════════════════════════════════
Short posts: Monday | Long-form: Thursday | One neighborhood per week
Current neighborhood in filming: Rosharon (July 2026, resident angle)
Next up: Iowa Colony (Meridiana focus) → Manvel (H-E-B growth story) → Pearland (established suburb)

═══ PLATFORM RULES ════════════════════════════════════════════════════════════
Instagram: 3-6 sentences, storytelling. Hashtags in first comment (NOT caption body). End with CTA.
TikTok: 1-2 punchy lines, hook in first 2 seconds, 3-5 hashtags inline.
YouTube Shorts: searchable title under 70 chars, keyword-dense 2-4 sentence description.
Facebook: 2-4 sentences, warm/family-friendly, 3-5 hashtags max.

═══ OUTPUT RULES ══════════════════════════════════════════════════════════════
- Always produce DRAFTS only. Kareesa approves before posting
- Flag any compliance issue (price guarantee, flood zone, missing disclosure)
- Include a "KWP-qualifying: YES/NO" note on each piece
- Every piece must include one of the two standard CTAs
- {COMPLIANCE["punctuation_rule"]}
- End every response with: {BRAND["signature_signoff"]}
"""


class RealEstateContentAgent(BaseAgent):
    """Content creation agent for Locked In with Kareesa real estate brand."""

    def _agent_name(self) -> str:
        return "re_content"

    def _system_prompt(self) -> str:
        return _SYSTEM_PROMPT

    # ── Caption Generation ────────────────────────────────────────────────────

    def generate_captions(
        self,
        description: str,
        neighborhood: str,
        content_type: str = "neighborhood_tour",
        include_hashtags: bool = True,
    ) -> dict[str, Any]:
        """Generate compliant, on-brand captions for all four platforms."""
        neighborhood_key = neighborhood.lower().replace(" ", "_")
        hashtag_set = HASHTAGS.get(neighborhood_key, HASHTAGS["market_education"])

        prompt = (
            f"Generate captions for all four platforms for this real estate content.\n\n"
            f"DESCRIPTION: {description}\n"
            f"NEIGHBORHOOD: {neighborhood}\n"
            f"CONTENT TYPE: {content_type}\n\n"
            f"RESIDENT CONTEXT TO WEAVE IN IF RELEVANT:\n"
            f"- She lives in Sierra Vista, Rosharon (ex-Sterling Lakes)\n"
            f"- H-E-B in Manvel is now her closer grocery store\n"
            f"- Her address says Rosharon but city is Iowa Colony\n\n"
            "Output a JSON object with exactly these keys:\n"
            "instagram, tiktok, youtube_title, youtube_description, facebook, compliance_notes, kwp_qualifying\n"
            "- instagram: caption only, NO hashtags (they go in first comment)\n"
            "- tiktok: caption with 3-5 hashtags inline\n"
            "- youtube_title: searchable, under 70 chars, include neighborhood name\n"
            "- youtube_description: 2-4 sentences, keyword-rich, include website URL\n"
            "- facebook: warm, family-friendly, 3-5 hashtags inline\n"
            "- compliance_notes: list any compliance flags or 'CLEAN' if none\n"
            "- kwp_qualifying: YES or NO with one-line reason\n"
            "Output ONLY valid JSON. No markdown fences."
        )

        raw = self.think(prompt)
        result_data = _parse_json(raw) or {"raw": raw}

        return {
            "captions": result_data,
            "hashtags": hashtag_set,
            "neighborhood": neighborhood,
            "content_type": content_type,
            "funnel_CTA": FUNNEL["standard_CTAs"][0],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def save_to_queue(
        self,
        platform: str,
        content_type: str,
        title: str,
        caption: str,
        hashtags: list[str],
        media_url: str = "",
    ) -> dict:
        """Save a real estate content draft to the shared content_queue table."""
        row = {
            "platform": platform,
            "content_type": content_type,
            "athlete_name": None,
            "title": title,
            "caption": caption,
            "hashtags": hashtags,
            "media_url": media_url or None,
            "status": "draft",
        }
        try:
            result = self._db.table("content_queue").insert(row).execute()
            logger.info(f"[re_content] Saved draft for {platform}: {title}")
            return result.data[0] if result.data else row
        except Exception as exc:
            logger.error(f"[re_content] save_to_queue failed: {exc}")
            return {"error": str(exc)}

    # ── Weekly Content Plan ───────────────────────────────────────────────────

    def weekly_plan(self, focus_neighborhood: str | None = None) -> str:
        """Generate a KWP-SCORE-aware weekly content plan (5 qualifying pieces)."""
        neighborhood = focus_neighborhood or "Rosharon"

        location_data = FILMING_LOCATIONS.get(neighborhood, {})
        prompt = (
            f"Generate a weekly real estate content plan for Locked In with Kareesa.\n\n"
            f"FOCUS NEIGHBORHOOD THIS WEEK: {neighborhood}\n"
            f"FILMING STATUS: {next((n['status'] for n in CONTENT_CALENDAR['neighborhood_rotation'] if n['neighborhood'] == neighborhood), 'queued')}\n"
            f"UNIQUE HOOKS FOR THIS NEIGHBORHOOD:\n"
            + "\n".join(f"- {h}" for h in (
                next((n['unique_hooks'] for n in CONTENT_CALENDAR['neighborhood_rotation'] if n['neighborhood'] == neighborhood), [])
            )) + "\n\n"
            f"SIGNATURE SHOTS AVAILABLE:\n"
            + "\n".join(f"- {s}" for s in location_data.get("signature_shots", [])) + "\n\n"
            f"REQUIREMENTS:\n"
            f"- Produce exactly 5 KWP-competition-qualifying pieces\n"
            f"- Monday: short-form clip or Reel\n"
            f"- Thursday: long-form neighborhood tour\n"
            f"- Include at least one market education piece\n"
            f"- At least one guide promo (Comment HOUSTON CTA)\n"
            f"- All pieces must carry required TREC disclosures and proper price language\n\n"
            "For each piece: title, platform, content type, hook line, CTA, KWP-qualifying: YES.\n"
            "End with one sentence on what to film first this week."
        )

        plan = self.think(prompt)
        self.remember("last_weekly_plan", {
            "neighborhood": neighborhood,
            "plan": plan,
            "week_of": datetime.now(timezone.utc).strftime("%B %d, %Y"),
        }, memory_type="plan")
        return plan

    # ── Filming Prep ──────────────────────────────────────────────────────────

    def filming_prep(self, neighborhood: str) -> str:
        """Generate a day-of filming checklist and shot list for a neighborhood."""
        location = FILMING_LOCATIONS.get(neighborhood, {})
        if not location:
            return f"No filming location data found for {neighborhood}. Available: {list(FILMING_LOCATIONS.keys())}"

        permission_needed = location.get("permission_needed", [])
        signature_shots = location.get("signature_shots", [])
        tips = location.get("filming_tips", location.get("note", ""))

        checklist = [
            f"FILMING PREP — {neighborhood.upper()}",
            "",
            "NIGHT BEFORE:",
        ]
        checklist.extend(f"  □ {step}" for step in FILMING_DAY_PROCESS["night_before"])
        checklist += [
            "",
            "PERMISSION REQUIRED (do these FIRST on arrival):",
        ]
        if permission_needed:
            checklist.extend(f"  □ {p}" for p in permission_needed)
        else:
            checklist.append("  ✓ No special permissions needed — all public locations")
        checklist += [
            "",
            "UNIVERSAL SHOT LIST (get these at EVERY location):",
        ]
        checklist.extend(f"  □ {s}" for s in FILMING_UNIVERSAL_SHOT_LIST)
        checklist += [
            "",
            f"SIGNATURE SHOTS FOR {neighborhood.upper()} (get these specifically):",
        ]
        checklist.extend(f"  □ {s}" for s in signature_shots)
        if tips:
            checklist += ["", f"LOCAL TIP: {tips}"]
        checklist += [
            "",
            "FILMING DAY FLOW:",
        ]
        checklist.extend(f"  {i+1}. {step}" for i, step in enumerate(FILMING_DAY_PROCESS["filming_day"]))
        checklist += [
            "",
            "SAME NIGHT (non-negotiable):",
        ]
        checklist.extend(f"  □ {step}" for step in FILMING_DAY_PROCESS["same_night"])
        checklist += [
            "",
            "GEAR BAG:",
        ]
        checklist.extend(f"  □ {g}" for g in FILMING_DAY_PROCESS["gear"])
        checklist += [
            "",
            "COMPLIANCE REMINDERS:",
            "  □ Verify all [VERIFY] price facts before stating on camera",
            "  □ Your name + KW Preferred must appear in video or caption",
            "  □ Use 'ranging around...' not hard price guarantees",
            "  □ No flood zone statements without FEMA verification",
            "",
            f"OUTRO CTA (say this at your final stop): 'Comment HOUSTON for my free Houston Relocation Guide!'",
        ]

        return "\n".join(checklist)

    # ── Compliance Check ──────────────────────────────────────────────────────

    def check_compliance(self, draft_text: str) -> dict[str, Any]:
        """Flag any TREC/KW/fair housing compliance issues in a content draft."""
        prompt = (
            "Review this real estate content draft for compliance issues.\n\n"
            f"DRAFT:\n{draft_text}\n\n"
            "Check for:\n"
            "1. Missing REALTOR name or brokerage disclosure\n"
            "2. Any price guarantee language (should say 'ranging around' or 'approximately')\n"
            "3. Any flood zone statements made without FEMA verification caveat\n"
            "4. Any fair housing issues (language that steers by demographics)\n"
            "5. School info stated as fact without 'verify with district' disclaimer\n"
            "6. HOA amenity descriptions that imply public access\n"
            "7. Any AI-sounding or salesy language that doesn't sound like Kareesa\n"
            "8. Missing CTA (should have Comment HOUSTON or Calendly link reference)\n"
            "9. Any hyphen or em dash used as connector punctuation joining two clauses "
            "or phrases (ordinary hyphenated compound words like 'move-in ready' are fine)\n\n"
            "Output JSON with keys: issues (list of strings), clean (bool), revised_draft (string with issues corrected).\n"
            "Output ONLY valid JSON."
        )
        raw = self.think(prompt)
        return _parse_json(raw) or {"raw": raw, "clean": False}

    # ── Script Draft ──────────────────────────────────────────────────────────

    def draft_script(
        self,
        neighborhood: str,
        segment: str = "intro",
        duration_seconds: int = 60,
    ) -> str:
        """Draft a speaking script for a neighborhood video segment."""
        location = FILMING_LOCATIONS.get(neighborhood, {})
        unique_hooks = next(
            (n["unique_hooks"] for n in CONTENT_CALENDAR["neighborhood_rotation"]
             if n["neighborhood"] == neighborhood),
            [],
        )

        prompt = (
            f"Write a {duration_seconds}-second speaking script for the '{segment}' segment "
            f"of the {neighborhood} neighborhood video.\n\n"
            f"UNIQUE HOOKS AVAILABLE:\n"
            + "\n".join(f"- {h}" for h in unique_hooks) + "\n\n"
            f"SIGNATURE SHOTS AT THIS LOCATION:\n"
            + "\n".join(f"- {s}" for s in location.get("signature_shots", [])) + "\n\n"
            "REQUIREMENTS:\n"
            "- Write exactly what Kareesa says on camera. First person, conversational\n"
            "- Include one teacher-style moment (pop quiz, lesson, homework CTA)\n"
            "- End the intro with the subject hook; end the outro with 'Comment HOUSTON'\n"
            "- No AI-sounding phrases. No hyphens or dashes.\n"
            "- Include [VISUAL CUE] notes in brackets for the editor\n"
            "- Kareesa's name and KW Preferred must appear somewhere in the script notes\n"
            "- If stating any price: use 'ranging around' and add [VERIFY THIS MORNING]\n"
            f"- End with: {BRAND['signature_signoff']}"
        )

        return self.think(prompt)

    # ── Chat ──────────────────────────────────────────────────────────────────

    def chat(self, message: str) -> str:
        lower = message.lower()

        if any(w in lower for w in ("weekly plan", "content plan", "this week", "5 posts")):
            neighborhood = _extract_neighborhood(lower)
            return self.weekly_plan(neighborhood)

        if any(w in lower for w in ("filming", "shot list", "checklist", "prep")):
            neighborhood = _extract_neighborhood(lower) or "Rosharon"
            return self.filming_prep(neighborhood)

        if any(w in lower for w in ("check compliance", "compliance", "trec", "fair housing")):
            return self.think(message)

        if any(w in lower for w in ("script", "what to say", "write my")):
            neighborhood = _extract_neighborhood(lower) or "Rosharon"
            segment = "intro" if "intro" in lower else "outro" if "outro" in lower else "tour"
            return self.draft_script(neighborhood, segment)

        if any(w in lower for w in ("caption", "write", "draft", "generate", "create post", "carousel")):
            neighborhood = _extract_neighborhood(lower) or "Rosharon"
            return self.generate_captions(message, neighborhood).get("captions", {}).get("raw", self.think(message))

        return self.think(message)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_neighborhood(text: str) -> str | None:
    for n in ["pearland", "manvel", "rosharon", "iowa colony"]:
        if n in text:
            return n.title()
    return None


def _parse_json(text: str) -> dict | None:
    import re
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return None
