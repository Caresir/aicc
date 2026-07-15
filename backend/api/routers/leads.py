"""Lead CRUD and Real Estate Assistant action endpoints."""
from __future__ import annotations

import os
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase import create_client

from agents.real_estate_agent import RealEstateAgent

router = APIRouter(prefix="/api/leads", tags=["leads"])


def _db():
    return create_client(
        os.getenv("SUPABASE_URL", ""),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
    )


# ── Pydantic models ────────────────────────────────────────────────────────────

class LeadCreate(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = "direct"
    referrer: Optional[str] = None
    lead_type: Optional[str] = "buyer"
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    desired_areas: Optional[list[str]] = None
    notes: Optional[str] = None
    co_purchasers: Optional[list[dict[str, Any]]] = None
    property_criteria: Optional[dict[str, Any]] = None
    sequence_track: Optional[str] = None  # 'aicc' (default), 'smartplan', or 'none'


class LeadUpdate(BaseModel):
    status: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    desired_areas: Optional[list[str]] = None
    co_purchasers: Optional[list[dict[str, Any]]] = None
    property_criteria: Optional[dict[str, Any]] = None
    last_contact_at: Optional[str] = None
    sequence_track: Optional[str] = None  # 'aicc', 'smartplan', or 'none'


# ── CRUD ───────────────────────────────────────────────────────────────────────

@router.get("")
def list_leads(
    status: Optional[str] = None,
    lead_type: Optional[str] = None,
    email: Optional[str] = None,
):
    q = _db().table("leads").select("*").order("created_at", desc=True)
    if status:
        q = q.eq("status", status)
    if lead_type:
        q = q.eq("lead_type", lead_type)
    if email:
        q = q.eq("email", email)
    return q.execute().data


@router.get("/{lead_id}")
def get_lead(lead_id: str):
    rows = (
        _db().table("leads").select("*").eq("id", lead_id).limit(1).execute().data
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Lead not found.")
    return rows[0]


@router.post("", status_code=201)
def create_lead(body: LeadCreate):
    data = body.model_dump(exclude_none=True)
    result = _db().table("leads").insert(data).execute()
    return result.data[0]


@router.patch("/{lead_id}")
def update_lead(lead_id: str, body: LeadUpdate):
    data = body.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update.")
    result = _db().table("leads").update(data).eq("id", lead_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Lead not found.")
    return result.data[0]


# ── Agent actions ──────────────────────────────────────────────────────────────

@router.post("/{lead_id}/welcome-text")
def welcome_text(lead_id: str):
    """Draft a welcome SMS for this lead using the Real Estate Assistant."""
    lead = get_lead(lead_id)
    draft = RealEstateAgent().draft_welcome_text(lead)
    return {"lead_id": lead_id, "channel": "text", "draft": draft}


@router.post("/{lead_id}/welcome-email")
def welcome_email(lead_id: str):
    """Draft a welcome email for this lead using the Real Estate Assistant."""
    lead = get_lead(lead_id)
    result = RealEstateAgent().draft_welcome_email(lead)
    return {"lead_id": lead_id, "channel": "email", **result}


@router.post("/{lead_id}/research")
def research_lead(lead_id: str):
    """Generate a research brief for this lead."""
    lead = get_lead(lead_id)
    brief = RealEstateAgent().research_lead(lead)
    return {"lead_id": lead_id, "brief": brief}


@router.post("/{lead_id}/follow-up")
def draft_follow_up(lead_id: str, step: int = 3, channel: str = "text"):
    """Draft a follow-up message at a specific sequence step."""
    lead = get_lead(lead_id)
    draft = RealEstateAgent().draft_follow_up(lead, step=step, channel=channel)
    return {"lead_id": lead_id, "step": step, "channel": channel, "draft": draft}


@router.post("/{lead_id}/sequence")
def generate_sequence(lead_id: str):
    """Generate and save a full 6-step follow-up sequence for this lead.

    Refuses to run for leads whose sequence_track is 'smartplan' — those leads
    are owned by a KW Command SmartPlan and must not also get AICC-native
    outreach (see the Sharon Traylor dual-track incident in REAL_ESTATE_ASSETS.md).
    """
    lead = get_lead(lead_id)
    if lead.get("sequence_track") == "smartplan":
        raise HTTPException(
            status_code=409,
            detail=(
                "This lead is marked sequence_track='smartplan' — a KW Command SmartPlan "
                "owns their follow-up. Generating an AICC sequence would duplicate outreach. "
                "Change sequence_track on the lead first if that's no longer correct."
            ),
        )
    agent = RealEstateAgent()
    steps = agent.generate_sequence(lead)
    agent.save_sequence(lead_id, steps)
    return {"lead_id": lead_id, "steps_created": len(steps), "steps": steps}


@router.get("/{lead_id}/sequence")
def get_sequence(lead_id: str):
    """Return the saved follow-up sequence for this lead."""
    rows = (
        _db()
        .table("follow_up_sequences")
        .select("*")
        .eq("lead_id", lead_id)
        .order("step")
        .execute()
        .data
    )
    return {"lead_id": lead_id, "steps": rows}
