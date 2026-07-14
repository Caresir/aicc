"""Agent chat and status endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

from agents.ceo_agent import CEOAgent
from agents.content_director_agent import ContentDirectorAgent
from agents.project_manager_agent import ProjectManagerAgent
from agents.real_estate_agent import RealEstateAgent

router = APIRouter(prefix="/api/agents", tags=["agents"])

_AGENT_CLASSES: dict[str, type] = {
    "ceo": CEOAgent,
    "content_director": ContentDirectorAgent,
    "project_manager": ProjectManagerAgent,
    "real_estate": RealEstateAgent,
}


def _get_agent(name: str):
    cls = _AGENT_CLASSES.get(name)
    if not cls:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{name}' not found or not yet active.",
        )
    return cls()


class ChatRequest(BaseModel):
    message: str
    context: dict[str, Any] | None = None


@router.get("/status")
def all_status():
    """Return a health snapshot for every active agent."""
    results = []
    for name, cls in _AGENT_CLASSES.items():
        try:
            results.append(cls().report())
        except Exception as exc:
            results.append({"agent": name, "status": "error", "error": str(exc)})
    return results


@router.post("/{agent_name}/chat")
def chat(agent_name: str, body: ChatRequest):
    """Send a message to an agent and get its response."""
    agent = _get_agent(agent_name)
    response = agent.chat(body.message)
    return {"agent": agent_name, "response": response}


@router.post("/broadcast")
def broadcast(body: ChatRequest):
    """Send the same message to all active agents and collect responses."""
    results = []
    for name, cls in _AGENT_CLASSES.items():
        try:
            agent = cls()
            response = agent.chat(body.message)
            results.append({"agent": name, "response": response})
        except Exception as exc:
            results.append({"agent": name, "error": str(exc)})
    return {"message": body.message, "responses": results}


@router.get("/{agent_name}/report")
def report(agent_name: str):
    """Return memory and conversation stats for a single agent."""
    return _get_agent(agent_name).report()


@router.get("/{agent_name}/memory/{key}")
def recall(agent_name: str, key: str, memory_type: str = "context"):
    """Retrieve a specific memory entry for an agent."""
    agent = _get_agent(agent_name)
    value = agent.recall(key, memory_type=memory_type)
    if value is None:
        raise HTTPException(status_code=404, detail=f"Memory key '{key}' not found.")
    return {"agent": agent_name, "key": key, "value": value}


@router.post("/ceo/briefing")
def run_briefing():
    """Trigger the CEO Agent morning briefing manually and send via SMS."""
    agent = CEOAgent()
    briefing = agent.run_morning_briefing()
    return {"status": "sent", "briefing": briefing}
