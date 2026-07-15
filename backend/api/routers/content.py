"""GymnastDiva content queue endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.content_director_agent import ContentDirectorAgent
from agents.real_estate_content_agent import RealEstateContentAgent

router = APIRouter(prefix="/api/content", tags=["content"])


class GenerateRequest(BaseModel):
    description: str
    content_type: str = "highlight"
    title: str = ""
    save: bool = False
    media_url: str = ""


class StatusUpdate(BaseModel):
    status: str


class ContentCreate(BaseModel):
    platform: str
    content_type: str
    title: str
    caption: str
    hashtags: list[str] = []
    media_url: str = ""


class MeetCreate(BaseModel):
    date: str
    name: str
    location: str
    discipline: str


@router.post("/generate")
def generate_captions(body: GenerateRequest):
    """Generate platform captions + hashtags from a video description."""
    agent = ContentDirectorAgent()
    result = agent.generate_captions(
        description=body.description,
        content_type=body.content_type,
        title=body.title,
    )

    if body.save and "captions" in result:
        caps = result["captions"]
        hashtags = result["hashtags"]
        saved = []
        platform_map = {
            "instagram":      caps.get("instagram", ""),
            "tiktok":         caps.get("tiktok", ""),
            "youtube_shorts": caps.get("youtube_description", ""),
            "facebook":       caps.get("facebook", ""),
        }
        for platform, caption in platform_map.items():
            if caption:
                row = agent.save_to_queue(
                    platform=platform,
                    content_type=body.content_type,
                    title=caps.get("youtube_title", body.title),
                    caption=caption,
                    hashtags=hashtags,
                    media_url=body.media_url,
                )
                saved.append(row)
        result["saved"] = saved

    return result


@router.get("/queue")
def list_queue(status: str | None = None):
    """Return content queue, optionally filtered by status."""
    agent = ContentDirectorAgent()
    items = agent.get_queue(status=status)
    return {"count": len(items), "items": items}


@router.post("/queue")
def create_content(body: ContentCreate):
    """Manually add a content item to the queue."""
    agent = ContentDirectorAgent()
    result = agent.save_to_queue(
        platform=body.platform,
        content_type=body.content_type,
        title=body.title,
        caption=body.caption,
        hashtags=body.hashtags,
        media_url=body.media_url,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.patch("/queue/{content_id}/status")
def update_status(content_id: str, body: StatusUpdate):
    """Update the status of a content item (approve, archive, publish, etc.)."""
    agent = ContentDirectorAgent()
    ok = agent.update_status(content_id, body.status)
    if not ok:
        raise HTTPException(status_code=400, detail="Could not update status")
    return {"id": content_id, "status": body.status}


@router.get("/plan")
def weekly_plan():
    """Generate a weekly content plan for GymnastDiva."""
    agent = ContentDirectorAgent()
    return {"plan": agent.weekly_content_plan()}


@router.post("/chat")
def chat(body: dict):
    """Free-form content director chat."""
    agent = ContentDirectorAgent()
    return {"response": agent.chat(body.get("message", ""))}


# ── Meet Schedule ─────────────────────────────────────────────────────────────

@router.get("/meets")
def list_meets():
    """Return the full gymnast meet schedule."""
    agent = ContentDirectorAgent()
    meets = agent.get_meets()
    return {"count": len(meets), "meets": meets}


@router.post("/meets")
def create_meet(body: MeetCreate):
    """Add a meet to the schedule."""
    agent = ContentDirectorAgent()
    meet = agent.add_meet(
        date=body.date,
        name=body.name,
        location=body.location,
        discipline=body.discipline,
    )
    return meet


@router.delete("/meets/{meet_id}")
def delete_meet(meet_id: str):
    """Remove a meet from the schedule."""
    agent = ContentDirectorAgent()
    ok = agent.delete_meet(meet_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Meet not found")
    return {"deleted": meet_id}


# ── Google Photos Integration ─────────────────────────────────────────────────

class NewVideoPayload(BaseModel):
    title: str
    album: str = ""
    category: str = "gymnastics"          # "gymnastics" or "re"
    content_type: str = "highlight"
    description: str = ""
    photos_url: str = ""
    duration_seconds: int = 0
    neighborhood: str = ""                 # "re" videos only: Rosharon, Iowa Colony, Manvel, Pearland


@router.post("/notify-new-video")
def notify_new_video(body: NewVideoPayload):
    """Called by n8n when a new video lands in Google Photos.
    Auto-generates captions for all 4 platforms and saves them as drafts.
    Routes to the matching brand agent: real estate ("re") videos get the
    Locked In with Kareesa voice, everything else gets GymnastDiva."""
    is_real_estate = body.category == "re"
    agent = RealEstateContentAgent() if is_real_estate else ContentDirectorAgent()

    parts = []
    if body.description:
        parts.append(body.description)
    if body.album:
        parts.append(f"Album: {body.album}.")
    if body.duration_seconds:
        parts.append(f"Duration: {body.duration_seconds}s.")
    full_desc = " ".join(parts) or f"New {body.category} video: {body.title}"

    if is_real_estate:
        result = agent.generate_captions(
            description=full_desc,
            neighborhood=body.neighborhood or "Rosharon",
            content_type=body.content_type,
        )
    else:
        result = agent.generate_captions(
            description=full_desc,
            content_type=body.content_type,
            title=body.title,
        )

    caps = result.get("captions", {})
    hashtags = result.get("hashtags", [])
    youtube_title = caps.get("youtube_title", body.title)

    platform_map = {
        "instagram":      caps.get("instagram", ""),
        "tiktok":         caps.get("tiktok", ""),
        "youtube_shorts": caps.get("youtube_description", ""),
        "facebook":       caps.get("facebook", ""),
    }

    saved = []
    for platform, caption in platform_map.items():
        if caption:
            row = agent.save_to_queue(
                platform=platform,
                content_type=body.content_type,
                title=youtube_title,
                caption=caption,
                hashtags=hashtags,
                media_url=body.photos_url,
            )
            saved.append(row)

    return {
        "status": "queued",
        "title": body.title,
        "category": body.category,
        "drafts_created": len(saved),
        "platforms": list(platform_map.keys()),
    }
