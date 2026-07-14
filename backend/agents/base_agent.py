"""BaseAgent — abstract foundation for all 12 AICC AI employees."""
from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import anthropic
from dotenv import load_dotenv
from loguru import logger
from supabase import create_client, Client
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

# Load .env from project root when running outside Docker.
# load_dotenv is idempotent — it won't overwrite vars already injected by Docker.
def _load_project_env() -> None:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / ".env"
        if candidate.exists():
            load_dotenv(candidate)
            return

_load_project_env()


def _supabase_key() -> str:
    """Return the first non-empty Supabase key found in the environment.
    Legacy JWT keys (SUPABASE_SERVICE_ROLE_KEY / SUPABASE_ANON_KEY) are
    preferred because supabase-py 2.x requires JWT format, not sb_* format.
    """
    for var in (
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_ANON_KEY",
        "SUPABASE_SECRET_KEY",
        "SUPABASE_PUBLISHABLE_KEY",
    ):
        val = os.getenv(var, "")
        if val:
            return val
    return ""


MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096


class BaseAgent(ABC):
    """Abstract base for every AICC AI employee."""

    def __init__(self) -> None:
        self._claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self._db: Client = create_client(
            os.getenv("SUPABASE_URL", ""),
            _supabase_key(),
        )
        self.name: str = self._agent_name()
        self._system: str = self._system_prompt()
        logger.info(f"Agent '{self.name}' initialized.")

    # ── Required overrides ─────────────────────────────────────────────────────

    @abstractmethod
    def _agent_name(self) -> str: ...

    @abstractmethod
    def _system_prompt(self) -> str: ...

    # ── Core interface ─────────────────────────────────────────────────────────

    def chat(self, message: str) -> str:
        """Handle a conversational message. Override in subclasses for intent routing."""
        return self.think(message)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def think(self, message: str, context: dict[str, Any] | None = None) -> str:
        """Call Claude with an optional context dict prepended to the message."""
        payload = message
        if context:
            ctx_text = "\n".join(f"  {k}: {v}" for k, v in context.items())
            payload = f"[CONTEXT]\n{ctx_text}\n\n[REQUEST]\n{message}"

        resp = self._claude.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=self._system,
            messages=[{"role": "user", "content": payload}],
        )
        result = resp.content[0].text
        tokens_in = resp.usage.input_tokens
        tokens_out = resp.usage.output_tokens

        logger.info(
            f"[{self.name}] {tokens_in + tokens_out} tokens "
            f"({tokens_in} in / {tokens_out} out)"
        )
        self._log_conversation(message, result, tokens_in + tokens_out)
        return result

    def remember(self, key: str, value: Any, memory_type: str = "context") -> None:
        """Upsert a key-value fact into this agent's Supabase memory."""
        stored = value if isinstance(value, dict) else {"data": value}
        try:
            self._db.table("agent_memory").upsert(
                {
                    "agent_name": self.name,
                    "memory_type": memory_type,
                    "key": key,
                    "value": stored,
                },
                on_conflict="agent_name,memory_type,key",
            ).execute()
        except Exception as exc:
            logger.error(f"[{self.name}] remember() failed: {exc}")

    def recall(self, key: str, memory_type: str = "context") -> Any | None:
        """Retrieve a stored fact. Returns None if not found."""
        try:
            rows = (
                self._db.table("agent_memory")
                .select("value")
                .eq("agent_name", self.name)
                .eq("memory_type", memory_type)
                .eq("key", key)
                .limit(1)
                .execute()
            ).data
            if rows:
                v = rows[0]["value"]
                return v.get("data", v)
        except Exception as exc:
            logger.error(f"[{self.name}] recall() failed: {exc}")
        return None

    def report(self) -> dict:
        """Return a health snapshot for this agent."""
        try:
            mem_count = (
                self._db.table("agent_memory")
                .select("id", count="exact")
                .eq("agent_name", self.name)
                .execute()
                .count
            ) or 0
            conv_count = (
                self._db.table("conversations")
                .select("id", count="exact")
                .eq("agent_name", self.name)
                .execute()
                .count
            ) or 0
            return {
                "agent": self.name,
                "status": "active",
                "memories": mem_count,
                "conversations": conv_count,
            }
        except Exception as exc:
            return {"agent": self.name, "status": "error", "error": str(exc)}

    # ── Internal ───────────────────────────────────────────────────────────────

    def _log_conversation(self, message: str, response: str, tokens: int) -> None:
        try:
            self._db.table("conversations").insert(
                [
                    {"agent_name": self.name, "role": "user", "content": message},
                    {
                        "agent_name": self.name,
                        "role": "assistant",
                        "content": response,
                        "tokens_used": tokens,
                    },
                ]
            ).execute()
        except Exception as exc:
            logger.warning(f"[{self.name}] conversation log skipped (non-fatal): {exc}")
