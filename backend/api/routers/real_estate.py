"""Real estate social content generation and DM-lead-routing endpoints."""
from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase import create_client

from agents.context.real_estate_content_context import DM_ROUTING_CONFIG
from agents.real_estate_agent import RealEstateAgent
from agents.real_estate_content_agent import RealEstateContentAgent

router = APIRouter(prefix="/api/real-estate", tags=["real-estate"])


def _db():
    return create_client(
        os.getenv("SUPABASE_URL", ""),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
    )


class SocialRequest(BaseModel):
    content_type: str
    platform: str
    context: str = ""


class NeighborhoodCaptionRequest(BaseModel):
    neighborhood: str
    description: str
    content_type: str = "neighborhood_tour"


@router.post("/social")
def generate_social(body: SocialRequest):
    """Generate a real estate social media post for Kareesa's brand."""
    agent = RealEstateAgent()
    post = agent.generate_social_post(
        content_type=body.content_type,
        platform=body.platform,
        context=body.context,
    )
    return {"post": post, "platform": body.platform, "content_type": body.content_type}


@router.post("/neighborhood-captions")
def generate_neighborhood_captions(body: NeighborhoodCaptionRequest):
    """Generate all-platform captions for a neighborhood tour video."""
    agent = RealEstateContentAgent()
    result = agent.generate_captions(
        description=body.description,
        neighborhood=body.neighborhood,
        content_type=body.content_type,
    )
    return result


# ── DM / Comment Lead Routing (spec section 7) ──────────────────────────────────

class DMLeadPayload(BaseModel):
    keyword: str                        # e.g. "CLASS", "LAND", "PEARLAND" (case-insensitive)
    trigger: str = "dm"                 # "dm" or "comment"
    platform: str = "instagram"
    name: str = ""
    contact: str = ""                   # phone, email, or @handle, whatever ManyChat has captured
    post_id: str = ""
    manychat_subscriber_id: str = ""


@router.post("/dm-lead")
def capture_dm_lead(body: DMLeadPayload):
    """Called by the ManyChat DM Router n8n workflow when a tracked keyword fires
    (see specs/aicc-social-spec.md section 7 and specs/aicc-social-spec.config.json).

    Looks up the keyword, captures/dedupes the lead in Supabase, and enrolls it in
    the AICC-native follow-up sequence UNLESS the lead is already marked
    sequence_track='smartplan' or 'none' — see the dedup guard on
    POST /api/leads/{id}/sequence for why that check exists.
    """
    keyword_norm = body.keyword.strip().upper()
    routing = next(
        (r for r in DM_ROUTING_CONFIG.get("dm_routing", []) if r["keyword"] == keyword_norm),
        None,
    )
    if not routing:
        known = [r["keyword"] for r in DM_ROUTING_CONFIG.get("dm_routing", [])]
        raise HTTPException(
            status_code=404,
            detail=f"No routing entry for keyword '{body.keyword}'. Known keywords: {known}",
        )

    db = _db()
    name_parts = body.name.strip().split(maxsplit=1)
    first_name = name_parts[0] if name_parts else "Unknown"
    last_name = name_parts[1] if len(name_parts) > 1 else "Lead"

    is_email = "@" in body.contact and "." in body.contact.split("@")[-1]
    existing = []
    if is_email:
        existing = db.table("leads").select("*").eq("email", body.contact).limit(1).execute().data
    elif body.contact:
        existing = db.table("leads").select("*").eq("phone", body.contact).limit(1).execute().data

    magnet_note = (
        f"{routing['lead_magnet']} ({routing['lead_magnet_url']})"
        if routing.get("lead_magnet_url")
        else f"{routing['lead_magnet']} [no delivery URL set yet, see specs/aicc-social-spec.config.json]"
    )
    notes = (
        f"Social {routing['trigger']} lead. Platform: {body.platform}. Keyword: {keyword_norm}. "
        f"Lead magnet: {magnet_note}."
        + (f" Post: {body.post_id}." if body.post_id else "")
        + (f" ManyChat subscriber: {body.manychat_subscriber_id}." if body.manychat_subscriber_id else "")
    )

    if existing:
        lead = existing[0]
    else:
        insert_data = {
            "first_name": first_name,
            "last_name": last_name,
            "source": "social",
            "lead_type": routing["lead_type"],
            "status": "new",
            "notes": notes,
        }
        if routing.get("neighborhood"):
            insert_data["desired_areas"] = [routing["neighborhood"]]
        if is_email:
            insert_data["email"] = body.contact
        elif body.contact:
            insert_data["phone"] = body.contact
        lead = db.table("leads").insert(insert_data).execute().data[0]

    sequence_result = None
    track = lead.get("sequence_track", "aicc")
    if track == "aicc":
        try:
            agent = RealEstateAgent()
            steps = agent.generate_sequence(lead)
            agent.save_sequence(lead["id"], steps)
            sequence_result = {"enrolled": True, "steps_created": len(steps)}
        except Exception as exc:
            sequence_result = {"enrolled": False, "error": str(exc)}
    else:
        sequence_result = {"enrolled": False, "reason": f"sequence_track is '{track}', not 'aicc'"}

    return {
        "lead_id": lead["id"],
        "is_new_lead": not existing,
        "matched_keyword": keyword_norm,
        "lead_magnet": routing["lead_magnet"],
        "lead_magnet_url": routing.get("lead_magnet_url"),
        "routing_status": routing["status"],
        "routing_note": routing.get("note"),
        "sequence": sequence_result,
    }
