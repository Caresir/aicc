"""Video production tracker — neighborhood tours and GymnastDiva content pipeline."""
from __future__ import annotations

import os
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase import create_client

router = APIRouter(prefix="/api/video-tracker", tags=["video-tracker"])


def _db():
    return create_client(
        os.getenv("SUPABASE_URL", ""),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
    )


class VideoCreate(BaseModel):
    title: str
    category: str = "re"
    neighborhood: Optional[str] = None
    topic: Optional[str] = None
    film_status: str = "not_filmed"
    edit_status: str = "raw"
    platforms: list[str] = ["instagram", "tiktok"]
    caption_status: str = "draft"
    scheduled_for: Optional[str] = None
    posted_at: Optional[str] = None
    notes: Optional[str] = None


class VideoUpdate(BaseModel):
    title: Optional[str] = None
    film_status: Optional[str] = None
    edit_status: Optional[str] = None
    caption_status: Optional[str] = None
    platforms: Optional[list[str]] = None
    scheduled_for: Optional[str] = None
    posted_at: Optional[str] = None
    ig_likes: Optional[int] = None
    ig_comments: Optional[int] = None
    ig_shares: Optional[int] = None
    ig_saves: Optional[int] = None
    tiktok_views: Optional[int] = None
    tiktok_likes: Optional[int] = None
    notes: Optional[str] = None


@router.get("")
def list_videos(category: str | None = None):
    db = _db()
    q = db.table("video_tracker").select("*").order("created_at", desc=False)
    if category:
        q = q.eq("category", category)
    rows = q.execute().data
    return {"count": len(rows), "videos": rows}


@router.post("")
def create_video(body: VideoCreate):
    db = _db()
    data = body.model_dump(exclude_none=True)
    row = db.table("video_tracker").insert(data).execute().data
    if not row:
        raise HTTPException(status_code=400, detail="Could not create video")
    return row[0]


@router.patch("/{video_id}")
def update_video(video_id: str, body: VideoUpdate):
    db = _db()
    data = body.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    row = db.table("video_tracker").update(data).eq("id", video_id).execute().data
    if not row:
        raise HTTPException(status_code=404, detail="Video not found")
    return row[0]


@router.delete("/{video_id}")
def delete_video(video_id: str):
    db = _db()
    db.table("video_tracker").delete().eq("id", video_id).execute()
    return {"deleted": video_id}
