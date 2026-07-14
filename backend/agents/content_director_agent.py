"""ContentDirectorAgent — GymnastDiva Iyah content creation for Kareesa Gonzales."""
from __future__ import annotations

import json
from datetime import datetime, timezone
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

SYSTEM_PROMPT = """You are the Content Director for GymnastDiva, the gymnastics social \
media brand for Iyah Gonzales, a young athlete managed by her mom Kareesa Gonzales.

PLATFORMS: Instagram, TikTok, YouTube Shorts, Facebook

BRAND VOICE:
- Fun, energetic, celebratory of hard work and dedication
- Audience: gymnastics families, parents, young athletes, coaches
- Highlight Iyah's skill progression, personality, and competitive journey
- Content themes: training highlights, meet moments, skill unlocks,
  behind the scenes, motivation, private lesson promos

GYMNASTICS CONTEXT:
- Athlete: Iyah Gonzales
- Disciplines: Black Floor, Rod Floor, Trampoline
- Equipment featured: foam pit, trampolines, Tumbl Trak, rod floor, stall bars
- Meet season: January through May 2027
- Coach/Brand Manager: Kareesa Gonzales
- Private lessons available via Calendly

CONTENT TYPES:
- highlight: Training highlight clips showing skills
- skills: Specific skill breakdowns or progressions
- meet_recap: Competition day content and results
- motivation: Inspirational and mindset content
- lesson_promo: Private lesson availability and promotion

CAPTION RULES:
- Instagram: 3-5 sentences, storytelling, warm and personal, emojis welcome
  Hashtags: 15-20 relevant hashtags (place in first comment, not caption)
- TikTok: 1-2 punchy sentences, trending energy, 3-5 hashtags inline
- YouTube Shorts: Keyword-rich, 2-4 sentences, no slang, searchable title
- Facebook: Warm, parent-friendly, 2-3 sentences, minimal hashtags

CRITICAL RULES:
- NEVER post or schedule without Kareesa's approval — always produce drafts only
- Flag any content showing Iyah's face prominently for extra privacy review
- Never use AI-sounding phrases — write like a proud coach/mom
- No hyphens or dashes in captions
- Always personalize — reference specific skills or moments from the description

HASHTAG SETS BY CONTENT TYPE:
- highlight/skills: #GymnastDiva #Iyah #Gymnastics #TumblingLife #GymLife #FloorRoutine #TrampolineGymnastics #RodFloor #SkillsUnlocked #YoungGymnast #FutureChampion #GymMom #GymnasticsFamily #TrainingDay #GymProgress
- meet_recap: #MeetDay #CompetitionDay #Gymnastics #GymnastDiva #Iyah #GymMeet #CompetitionReady #GymLife #YoungChampion #GymFamily #Compete #GymResults #GymnasticsLife
- motivation: #Motivation #GymLife #NeverGiveUp #GymnastDiva #HardWork #Dedication #YoungAthlete #Gymnastics #BelieveInYourself #GymMindset #ChampionMindset
- lesson_promo: #PrivateLessons #GymnasticsLessons #LearnGymnastics #GymCoach #GymnastDiva #BookNow #TumblingLessons #Pearland #Houston #GymnasticsTraining"""


HASHTAGS: dict[str, list[str]] = {
    "highlight": ["#GymnastDiva", "#Iyah", "#Gymnastics", "#TumblingLife", "#GymLife",
                  "#FloorRoutine", "#TrampolineGymnastics", "#RodFloor", "#SkillsUnlocked",
                  "#YoungGymnast", "#FutureChampion", "#GymMom", "#GymnasticsFamily",
                  "#TrainingDay", "#GymProgress"],
    "skills":    ["#GymnastDiva", "#Iyah", "#Gymnastics", "#TumblingLife", "#GymLife",
                  "#FloorRoutine", "#TrampolineGymnastics", "#RodFloor", "#SkillsUnlocked",
                  "#YoungGymnast", "#FutureChampion", "#GymMom", "#GymnasticsFamily",
                  "#TrainingDay", "#GymProgress"],
    "meet_recap": ["#MeetDay", "#CompetitionDay", "#Gymnastics", "#GymnastDiva", "#Iyah",
                   "#GymMeet", "#CompetitionReady", "#GymLife", "#YoungChampion",
                   "#GymFamily", "#Compete", "#GymResults", "#GymnasticsLife"],
    "motivation": ["#Motivation", "#GymLife", "#NeverGiveUp", "#GymnastDiva", "#HardWork",
                   "#Dedication", "#YoungAthlete", "#Gymnastics", "#BelieveInYourself",
                   "#GymMindset", "#ChampionMindset"],
    "lesson_promo": ["#PrivateLessons", "#GymnasticsLessons", "#LearnGymnastics", "#GymCoach",
                     "#GymnastDiva", "#BookNow", "#TumblingLessons", "#Pearland",
                     "#Houston", "#GymnasticsTraining"],
}


class ContentDirectorAgent(BaseAgent):
    """GymnastDiva content creation and scheduling agent."""

    def _agent_name(self) -> str:
        return "content_director"

    def _system_prompt(self) -> str:
        return SYSTEM_PROMPT

    # ── Caption Generation ─────────────────────────────────────────────────────

    def generate_captions(
        self,
        description: str,
        content_type: str = "highlight",
        title: str = "",
    ) -> dict[str, Any]:
        """Generate platform-specific captions from a video description."""
        prompt = (
            f"Generate captions for all four platforms for this gymnastics content.\n\n"
            f"VIDEO DESCRIPTION: {description}\n"
            f"CONTENT TYPE: {content_type}\n"
            f"TITLE (if any): {title or 'not provided'}\n\n"
            "Output a JSON object with exactly these keys: "
            "instagram, tiktok, youtube_title, youtube_description, facebook. "
            "For instagram: the caption only (no hashtags — those go in first comment). "
            "For tiktok: caption with 3-5 hashtags inline. "
            "For youtube_title: a searchable title under 60 characters. "
            "For youtube_description: 2-4 sentences, keyword-rich. "
            "For facebook: warm parent-friendly caption. "
            "Output ONLY valid JSON, no markdown fences."
        )

        raw = self.think(prompt)
        captions = _parse_json(raw) or {"raw": raw}
        hashtags = HASHTAGS.get(content_type, HASHTAGS["highlight"])

        result = {
            "captions": captions,
            "hashtags": hashtags,
            "content_type": content_type,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        return result

    def save_to_queue(
        self,
        platform: str,
        content_type: str,
        title: str,
        caption: str,
        hashtags: list[str],
        media_url: str = "",
    ) -> dict:
        """Save a content draft to the content_queue table."""
        row = {
            "platform": platform,
            "content_type": content_type,
            "athlete_name": "Iyah Gonzales",
            "title": title,
            "caption": caption,
            "hashtags": hashtags,
            "media_url": media_url or None,
            "status": "draft",
        }
        try:
            result = self._db.table("content_queue").insert(row).execute()
            logger.info(f"[content_director] Saved draft for {platform}: {title}")
            return result.data[0] if result.data else row
        except Exception as exc:
            logger.error(f"[content_director] save_to_queue failed: {exc}")
            return {"error": str(exc)}

    def get_queue(self, status: str | None = None) -> list[dict]:
        """Return content queue items, optionally filtered by status."""
        try:
            q = (
                self._db.table("content_queue")
                .select("*")
                .order("created_at", desc=True)
            )
            if status:
                q = q.eq("status", status)
            return q.execute().data or []
        except Exception as exc:
            logger.error(f"[content_director] get_queue failed: {exc}")
            return []

    def update_status(self, content_id: str, status: str) -> bool:
        """Update the status of a content queue item."""
        try:
            self._db.table("content_queue").update({
                "status": status,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                **({"published_at": datetime.now(timezone.utc).isoformat()} if status == "published" else {}),
            }).eq("id", content_id).execute()
            return True
        except Exception as exc:
            logger.error(f"[content_director] update_status failed: {exc}")
            return False

    # ── Weekly Plan ────────────────────────────────────────────────────────────

    def weekly_content_plan(self) -> str:
        """Generate a weekly content plan for GymnastDiva."""
        queue = self.get_queue()
        draft_count = sum(1 for c in queue if c["status"] == "draft")
        approved_count = sum(1 for c in queue if c["status"] == "approved")

        context = {
            "week_of": datetime.now(timezone.utc).strftime("%B %d, %Y"),
            "drafts_in_queue": draft_count,
            "approved_ready": approved_count,
            "recent_content": [
                {"platform": c["platform"], "type": c["content_type"], "title": c.get("title")}
                for c in queue[:5]
            ],
        }

        plan = self.think(
            "Generate a weekly content plan for GymnastDiva Iyah. "
            "Recommend 5-7 posts across all platforms for the week. "
            "Mix content types. Note which platform needs most attention. "
            "End with 3 content ideas that would perform well right now.",
            context=context,
        )
        self.remember("last_weekly_plan", plan, memory_type="plan")
        return plan

    # ── Meet Schedule ─────────────────────────────────────────────────────────

    def get_meets(self) -> list[dict]:
        """Return all gymnast meets from persistent memory."""
        try:
            rows = (
                self._db.table("agent_memory")
                .select("value")
                .eq("agent_name", self.name)
                .eq("memory_type", "schedule")
                .eq("key", "gymnast_meets")
                .limit(1)
                .execute()
            ).data
            if rows:
                val = rows[0]["value"]
                return val.get("meets", []) if isinstance(val, dict) else []
        except Exception as exc:
            logger.error(f"[content_director] get_meets failed: {exc}")
        return []

    def add_meet(self, date: str, name: str, location: str, discipline: str) -> dict:
        """Add a meet to the schedule and persist it."""
        import uuid
        meets = self.get_meets()
        meet = {
            "id": str(uuid.uuid4()),
            "date": date,
            "name": name,
            "location": location,
            "discipline": discipline,
        }
        meets.append(meet)
        meets.sort(key=lambda m: m["date"])
        self._db.table("agent_memory").upsert(
            {
                "agent_name": self.name,
                "memory_type": "schedule",
                "key": "gymnast_meets",
                "value": {"meets": meets},
            },
            on_conflict="agent_name,memory_type,key",
        ).execute()
        return meet

    def delete_meet(self, meet_id: str) -> bool:
        """Remove a meet from the schedule by ID."""
        meets = self.get_meets()
        updated = [m for m in meets if m.get("id") != meet_id]
        if len(updated) == len(meets):
            return False
        self._db.table("agent_memory").upsert(
            {
                "agent_name": self.name,
                "memory_type": "schedule",
                "key": "gymnast_meets",
                "value": {"meets": updated},
            },
            on_conflict="agent_name,memory_type,key",
        ).execute()
        return True

    # ── Chat ──────────────────────────────────────────────────────────────────

    def chat(self, message: str) -> str:
        """Handle content requests — generates captions, plans, or answers questions."""
        lower = message.lower()

        if any(w in lower for w in ("weekly plan", "content plan", "what should", "plan for")):
            return self.weekly_content_plan()

        if any(w in lower for w in ("caption", "write", "draft", "generate", "create post")):
            return self.think(
                message,
                context={"queue_size": len(self.get_queue()), "athlete": "Iyah"},
            )

        return self.think(message)


# ── Helpers ───────────────────────────────────────────────────────────────────

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
