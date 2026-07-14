"""Task management endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.project_manager_agent import ProjectManagerAgent

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class TaskRequest(BaseModel):
    request: str


class ChatRequest(BaseModel):
    message: str


@router.get("")
def list_tasks(business_unit: str | None = None, status: str | None = None):
    """List open tasks, optionally filtered by business unit."""
    agent = ProjectManagerAgent()
    tasks = agent.get_open_tasks(business_unit=business_unit)
    if status:
        tasks = [t for t in tasks if t.get("status") == status]
    return {"count": len(tasks), "tasks": tasks}


@router.get("/overdue")
def overdue_tasks():
    """Return all overdue tasks."""
    agent = ProjectManagerAgent()
    tasks = agent.get_overdue_tasks()
    return {"count": len(tasks), "tasks": tasks}


@router.get("/summary")
def task_summary():
    """Generate a plain-English daily task summary."""
    agent = ProjectManagerAgent()
    return {"summary": agent.daily_task_summary()}


@router.get("/weekly")
def weekly_report():
    """Generate a weekly status report across all business units."""
    agent = ProjectManagerAgent()
    return {"report": agent.weekly_status_report()}


@router.post("")
def create_task(body: TaskRequest):
    """Create a task from a plain-English request."""
    agent = ProjectManagerAgent()
    result = agent.create_task_from_text(body.request)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/chat")
def chat(body: ChatRequest):
    """Free-form task management chat — create, query, or summarize."""
    agent = ProjectManagerAgent()
    response = agent.chat(body.message)
    return {"response": response}


@router.patch("/{task_id}/complete")
def complete_task(task_id: str):
    """Mark a task as done."""
    agent = ProjectManagerAgent()
    success = agent.complete_task(task_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not complete task.")
    return {"status": "done", "task_id": task_id}
