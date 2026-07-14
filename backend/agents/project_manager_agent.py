"""ProjectManagerAgent — task tracking and prioritization for Kareesa Gonzales."""
from __future__ import annotations

import os
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

SYSTEM_PROMPT = """You are the Project Manager Agent for Kareesa Gonzales — you keep every \
business running on time across all 5 operations.

KAREESA'S BUSINESSES:
- real_estate: KW Preferred Pearland TX — leads, listings, transactions
- gymnastics: GymnastDiva — content, athletes, scheduling
- agency: AI Agency — client projects, deliverables, proposals
- fba: Amazon FBA — inventory, listings, shipments
- digital: Digital products — courses, templates, launches
- admin: Cross-business admin, legal, finance

YOUR ROLE:
- Turn plain-English requests into structured tasks
- Report what is open, overdue, blocked, or due today
- Prioritize ruthlessly — Kareesa's time is limited
- Flag anything that will miss a deadline if not acted on today
- Keep task descriptions clear and actionable, not vague

TASK STRUCTURE:
Every task you create must have:
- title: short, verb-first (e.g. "Call Sharon Traylor re: land search")
- priority: critical / high / medium / low
- business_unit: real_estate / gymnastics / agency / fba / digital / admin
- due_date: specific date if mentioned, otherwise null
- description: one sentence of context if needed

PRIORITY RULES:
- critical: client-facing, legal, financial, or time-sensitive today
- high: important but not on fire — due within 3 days
- medium: should happen this week
- low: nice to have, no deadline pressure

OUTPUT FORMAT FOR TASK LISTS:
Group by business unit. For each task show:
[PRIORITY] Task title | Due: date or "no deadline"

OUTPUT FORMAT FOR NEW TASKS:
Confirm what you created:
✅ Created: [title] | [priority] | [business_unit] | Due: [date or none]

TONE:
- Direct and efficient — no filler
- If something is overdue, say it plainly
- If the task list is clear, say so — don't manufacture urgency
"""


class ProjectManagerAgent(BaseAgent):
    """Task tracking and prioritization agent."""

    def _agent_name(self) -> str:
        return "project_manager"

    def _system_prompt(self) -> str:
        return SYSTEM_PROMPT

    # ── Task creation ──────────────────────────────────────────────────────────

    def create_task_from_text(self, request: str) -> dict[str, Any]:
        """Parse a plain-English request and create a task in Supabase."""
        now = datetime.now(timezone.utc).isoformat()

        raw = self.think(
            f"The user wants to create a task. Parse this request and output a JSON object "
            f"with these fields: title, description, priority, business_unit, due_date "
            f"(ISO date string or null). Today is {now[:10]}. "
            f"Output ONLY valid JSON, no markdown, no explanation.\n\nRequest: {request}"
        )

        task = _parse_json(raw)
        if not task or "title" not in task:
            logger.warning(f"[pm] Could not parse task from: {raw}")
            return {"error": "Could not parse task from request.", "raw": raw}

        task.setdefault("status", "todo")
        task.setdefault("priority", "medium")
        task.setdefault("description", None)
        task.setdefault("due_date", None)
        task.setdefault("business_unit", "admin")

        try:
            result = self._db.table("tasks").insert(task).execute()
            created = result.data[0] if result.data else task
            logger.info(f"[pm] Task created: {task['title']}")
            return created
        except Exception as exc:
            logger.error(f"[pm] create_task failed: {exc}")
            return {"error": str(exc), "task": task}

    # ── Task queries ───────────────────────────────────────────────────────────

    def get_open_tasks(self, business_unit: str | None = None) -> list[dict]:
        """Return all non-done tasks, optionally filtered by business unit."""
        try:
            q = (
                self._db.table("tasks")
                .select("*")
                .neq("status", "done")
                .order("priority")
                .order("due_date")
            )
            if business_unit:
                q = q.eq("business_unit", business_unit)
            return q.execute().data or []
        except Exception as exc:
            logger.error(f"[pm] get_open_tasks failed: {exc}")
            return []

    def get_overdue_tasks(self) -> list[dict]:
        """Return all tasks past their due date that are not done."""
        now = datetime.now(timezone.utc).isoformat()
        try:
            return (
                self._db.table("tasks")
                .select("*")
                .neq("status", "done")
                .lt("due_date", now)
                .order("due_date")
                .execute()
                .data
            ) or []
        except Exception as exc:
            logger.error(f"[pm] get_overdue_tasks failed: {exc}")
            return []

    def complete_task(self, task_id: str) -> bool:
        """Mark a task as done."""
        try:
            self._db.table("tasks").update({
                "status": "done",
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }).eq("id", task_id).execute()
            logger.info(f"[pm] Task {task_id} marked done.")
            return True
        except Exception as exc:
            logger.error(f"[pm] complete_task failed: {exc}")
            return False

    # ── Reporting ──────────────────────────────────────────────────────────────

    def daily_task_summary(self) -> str:
        """Generate a plain-English summary of today's task situation."""
        open_tasks = self.get_open_tasks()
        overdue = self.get_overdue_tasks()
        now_str = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")

        context = {
            "date": now_str,
            "total_open": len(open_tasks),
            "overdue_count": len(overdue),
            "overdue_tasks": [
                {"title": t["title"], "due": t.get("due_date", "?"), "unit": t.get("business_unit")}
                for t in overdue
            ],
            "open_tasks": [
                {
                    "title": t["title"],
                    "priority": t.get("priority", "medium"),
                    "unit": t.get("business_unit", "admin"),
                    "due": t.get("due_date"),
                    "status": t.get("status"),
                }
                for t in open_tasks
            ],
        }

        summary = self.think(
            "Generate a concise daily task summary. Group by business unit. "
            "Call out anything overdue first. If the list is empty, say so clearly. "
            "Be direct — no filler.",
            context=context,
        )

        self.remember("last_daily_summary", summary, memory_type="report")
        return summary

    def weekly_status_report(self) -> str:
        """Generate a weekly task status report grouped by business unit."""
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        week_start = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        open_tasks = self.get_open_tasks()
        overdue = self.get_overdue_tasks()

        try:
            completed_this_week = (
                self._db.table("tasks")
                .select("*")
                .eq("status", "done")
                .gte("completed_at", week_start.isoformat())
                .execute()
                .data
            ) or []
        except Exception:
            completed_this_week = []

        context = {
            "week_of": now.strftime("%B %d, %Y"),
            "open_by_unit": _group_by_unit(open_tasks),
            "overdue": [
                {"title": t["title"], "due": t.get("due_date"), "unit": t.get("business_unit")}
                for t in overdue
            ],
            "completed_this_week": [
                {"title": t["title"], "unit": t.get("business_unit")}
                for t in completed_this_week
            ],
            "totals": {
                "open": len(open_tasks),
                "overdue": len(overdue),
                "completed_this_week": len(completed_this_week),
            },
        }

        report = self.think(
            "Generate a concise weekly status report. Lead with wins (completed tasks), "
            "then open tasks grouped by business unit, then overdue items. "
            "End with 3 priorities for next week. Be direct — no filler.",
            context=context,
        )

        self.remember("last_weekly_report", report, memory_type="report")
        return report

    def chat(self, message: str) -> str:
        """
        Handle a free-form task management request.
        Detects intent and routes to create, query, or summarize.
        """
        lower = message.lower()

        # Route to task creation
        if any(w in lower for w in ("add", "create", "new task", "remind", "schedule", "need to")):
            task = self.create_task_from_text(message)
            if "error" in task:
                return f"Couldn't create the task: {task['error']}"
            return (
                f"✅ Created: {task.get('title')} | "
                f"{task.get('priority', 'medium')} priority | "
                f"{task.get('business_unit', 'admin')} | "
                f"Due: {task.get('due_date') or 'no deadline'}"
            )

        # Route to summary
        if any(w in lower for w in ("what's on", "whats on", "my plate", "today", "summary",
                                    "overdue", "open tasks", "task list", "what do i")):
            return self.daily_task_summary()

        # Default: free-form think
        return self.think(message, context={"open_tasks": len(self.get_open_tasks())})


# ── Helpers ───────────────────────────────────────────────────────────────────

def _group_by_unit(tasks: list[dict]) -> dict[str, list]:
    groups: dict[str, list] = {}
    for t in tasks:
        unit = t.get("business_unit", "admin")
        groups.setdefault(unit, []).append(
            {"title": t["title"], "priority": t.get("priority"), "due": t.get("due_date")}
        )
    return groups


def _parse_json(text: str) -> dict | None:
    """Extract and parse the first JSON object found in a string."""
    import json
    import re
    text = text.strip()
    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find a {...} block inside the text
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return None


# ── Runnable script ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    agent = ProjectManagerAgent()

    print("\n=== DAILY TASK SUMMARY ===")
    print(agent.daily_task_summary())

    print("\n=== OPEN TASKS ===")
    tasks = agent.get_open_tasks()
    print(f"{len(tasks)} open tasks")
    for t in tasks:
        print(f"  [{t.get('priority','?')}] {t['title']} | {t.get('business_unit','?')} | due: {t.get('due_date','none')}")
