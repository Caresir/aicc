"""Metricool scheduling and analytics endpoints."""
from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase import create_client

from integrations.metricool_client import (
    get_post_analytics,
    next_slot,
    ping,
    schedule_carousel,
    schedule_post,
)

router = APIRouter(prefix="/api/metricool", tags=["metricool"])


def _db():
    return create_client(
        os.getenv("SUPABASE_URL", ""),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
    )


class ScheduleRequest(BaseModel):
    video_id: str
    media_url: str
    networks: list[str] = ["instagram", "tiktok"]
    publish_datetime: Optional[str] = None  # ISO8601, e.g. "2026-07-15T09:00:00"
    caption_override: Optional[str] = None  # if not set, uses notes field from video_tracker


class CarouselScheduleRequest(BaseModel):
    video_id: str
    image_urls: list[str]                   # ordered list of 2–10 public image URLs
    publish_datetime: Optional[str] = None  # ISO8601, defaults to next Tue/Thu 9am CT
    caption_override: Optional[str] = None  # if not set, uses notes field from video_tracker


class MetricsPullRequest(BaseModel):
    days_back: int = 30


# ── Setup / Discovery ─────────────────────────────────────────────────────────

@router.get("/setup")
def setup_info():
    """Verify Metricool connection and confirm userId/blogId are set."""
    try:
        return ping()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Metricool error: {e}")


@router.get("/scheduled")
def list_scheduled(days: int = 14):
    """Return scheduled posts for the next N days."""
    from integrations.metricool_client import get_scheduled_posts
    from_date = datetime.utcnow().strftime("%Y-%m-%d")
    to_date   = (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d")
    try:
        posts = get_scheduled_posts(from_date=from_date, to_date=to_date)
        return {"count": len(posts) if isinstance(posts, list) else 0, "posts": posts}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Metricool error: {e}")


@router.get("/next-slot")
def preview_next_slot():
    """Preview the next Tuesday/Thursday 9am CT slot."""
    return {"next_slot": next_slot(), "timezone": "America/Chicago"}


# ── Schedule a Post ───────────────────────────────────────────────────────────

@router.post("/schedule")
def schedule_video(body: ScheduleRequest):
    """
    Schedule a video from the content calendar into Metricool.
    Reads caption from video_tracker notes; optionally override with caption_override.
    Media must be a publicly accessible URL (Google Drive share link works).
    """
    db = _db()

    # Load the video record
    row = db.table("video_tracker").select("*").eq("id", body.video_id).single().execute()
    if not row.data:
        raise HTTPException(status_code=404, detail="Video not found")

    video = row.data
    caption = body.caption_override or video.get("notes") or video.get("title", "")

    if not body.media_url:
        raise HTTPException(status_code=400, detail="media_url is required — provide a public Google Drive link")

    try:
        result = schedule_post(
            caption=caption,
            media_url=body.media_url,
            networks=body.networks,
            publish_datetime=body.publish_datetime,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Metricool API error: {e}")

    # Update video_tracker: mark caption_status as approved, store scheduled date
    scheduled_at = body.publish_datetime or next_slot()
    db.table("video_tracker").update({
        "caption_status": "approved",
        "scheduled_for": scheduled_at[:10],  # just the date portion
    }).eq("id", body.video_id).execute()

    return {
        "scheduled": True,
        "video_id": body.video_id,
        "title": video.get("title"),
        "networks": body.networks,
        "publish_datetime": scheduled_at,
        "metricool_response": result,
    }


# ── Schedule a Carousel ───────────────────────────────────────────────────────

@router.post("/schedule-carousel")
def schedule_carousel_post(body: CarouselScheduleRequest):
    """
    Schedule an Instagram carousel (2–10 images) via Metricool.
    Caption is read from video_tracker notes; optionally override with caption_override.
    Each image must be a publicly accessible URL (Google Drive share links work —
    use the format: https://drive.google.com/uc?export=download&id=FILE_ID).
    """
    db = _db()

    row = db.table("video_tracker").select("*").eq("id", body.video_id).single().execute()
    if not row.data:
        raise HTTPException(status_code=404, detail="Video not found")

    video = row.data
    caption = body.caption_override or video.get("notes") or video.get("title", "")

    if not body.image_urls:
        raise HTTPException(status_code=400, detail="image_urls is required — provide at least 2 public image URLs")

    try:
        result = schedule_carousel(
            caption=caption,
            image_urls=body.image_urls,
            publish_datetime=body.publish_datetime,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Metricool API error: {e}")

    scheduled_at = body.publish_datetime or next_slot()
    db.table("video_tracker").update({
        "caption_status": "approved",
        "scheduled_for": scheduled_at[:10],
    }).eq("id", body.video_id).execute()

    return {
        "scheduled": True,
        "video_id": body.video_id,
        "title": video.get("title"),
        "network": "instagram",
        "format": "carousel",
        "slide_count": len(body.image_urls),
        "publish_datetime": scheduled_at,
        "metricool_response": result,
    }


# ── Pull Metrics ──────────────────────────────────────────────────────────────

@router.post("/pull-metrics")
def pull_metrics(body: MetricsPullRequest):
    """
    Pull engagement metrics from Metricool and write them into video_tracker.
    Matches by title/neighborhood — best-effort sync.
    """
    db = _db()

    to_date   = datetime.utcnow().strftime("%Y-%m-%d")
    from_date = (datetime.utcnow() - timedelta(days=body.days_back)).strftime("%Y-%m-%d")

    try:
        posts = get_post_analytics(from_date=from_date, to_date=to_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Metricool API error: {e}")

    updated = 0
    for post in posts:
        network   = (post.get("network") or "").lower()
        post_text = post.get("message") or post.get("text") or ""
        stats     = post.get("stats") or post.get("analytics") or {}

        # Look for a matching video_tracker row by title substring
        rows = db.table("video_tracker").select("id, title, neighborhood").execute().data
        match = next(
            (r for r in rows if r.get("title", "").lower() in post_text.lower()
             or (r.get("neighborhood") or "").lower() in post_text.lower()),
            None,
        )
        if not match:
            continue

        update_payload: dict = {}
        if network == "instagram":
            update_payload["ig_likes"]    = stats.get("likes", 0)
            update_payload["ig_comments"] = stats.get("comments", 0)
            update_payload["ig_saves"]    = stats.get("saves", 0)
            update_payload["ig_shares"]   = stats.get("shares", 0)
        elif network == "tiktok":
            update_payload["tiktok_views"] = stats.get("views", stats.get("plays", 0))
            update_payload["tiktok_likes"] = stats.get("likes", 0)

        if update_payload:
            db.table("video_tracker").update(update_payload).eq("id", match["id"]).execute()
            updated += 1

    return {
        "pulled": len(posts),
        "updated": updated,
        "from_date": from_date,
        "to_date": to_date,
    }
