"""Listings management endpoints."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase import create_client
import os

def _load_env() -> None:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / ".env"
        if candidate.exists():
            load_dotenv(candidate)
            return

_load_env()

def _db():
    from agents.base_agent import _supabase_key
    return create_client(os.getenv("SUPABASE_URL", ""), _supabase_key())

router = APIRouter(prefix="/api/listings", tags=["listings"])


class ListingCreate(BaseModel):
    address: str
    city: str
    state: str = "TX"
    zip: str | None = None
    status: str = "active"
    listing_type: str | None = None
    price: float | None = None
    bedrooms: int | None = None
    bathrooms: float | None = None
    sqft: int | None = None
    mls_number: str | None = None
    notes: str | None = None


class ListingUpdate(BaseModel):
    status: str | None = None
    price: float | None = None
    notes: str | None = None
    mls_number: str | None = None


@router.get("")
def list_listings(status: str | None = None):
    db = _db()
    q = db.table("listings").select("*").order("created_at", desc=True)
    if status:
        q = q.eq("status", status)
    rows = q.execute().data or []
    return {"count": len(rows), "listings": rows}


@router.get("/{listing_id}")
def get_listing(listing_id: str):
    db = _db()
    rows = db.table("listings").select("*").eq("id", listing_id).limit(1).execute().data
    if not rows:
        raise HTTPException(status_code=404, detail="Listing not found")
    return rows[0]


@router.post("")
def create_listing(body: ListingCreate):
    db = _db()
    result = db.table("listings").insert(body.model_dump(exclude_none=True)).execute()
    if not result.data:
        raise HTTPException(status_code=400, detail="Could not create listing")
    return result.data[0]


@router.patch("/{listing_id}")
def update_listing(listing_id: str, body: ListingUpdate):
    db = _db()
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = db.table("listings").update(updates).eq("id", listing_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Listing not found")
    return result.data[0]
