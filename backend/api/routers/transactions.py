"""Transaction pipeline endpoints."""
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

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

PIPELINE_STAGES = [
    "pending",
    "offer_submitted",
    "under_contract",
    "inspection",
    "closing",
    "closed",
    "fallen_through",
]


class TransactionCreate(BaseModel):
    lead_id: str | None = None
    listing_id: str | None = None
    status: str = "pending"
    contract_price: float | None = None
    closing_date: str | None = None
    lone_wolf_id: str | None = None
    notes: str | None = None


class TransactionUpdate(BaseModel):
    status: str | None = None
    contract_price: float | None = None
    closing_date: str | None = None
    lone_wolf_id: str | None = None
    notes: str | None = None


class DraftCreate(BaseModel):
    lead_id: str | None = None
    transaction_id: str | None = None
    draft_type: str  # 'buyer_agreement' | 'listing_agreement' | 'offer' | 'addendum'
    content: str
    notes: str | None = None


@router.get("")
def list_transactions():
    db = _db()
    rows = (
        db.table("transactions")
        .select("*, leads(first_name, last_name), listings(address, city)")
        .order("created_at", desc=True)
        .execute()
        .data
    ) or []
    return {"count": len(rows), "transactions": rows}


@router.get("/pipeline")
def pipeline():
    """Return transactions grouped by pipeline stage."""
    db = _db()
    rows = (
        db.table("transactions")
        .select("*, leads(first_name, last_name), listings(address, city)")
        .not_.eq("status", "closed")
        .not_.eq("status", "fallen_through")
        .execute()
        .data
    ) or []

    stages: dict[str, list] = {s: [] for s in PIPELINE_STAGES}
    for tx in rows:
        stage = tx.get("status", "pending")
        if stage in stages:
            stages[stage].append(tx)

    return stages


@router.post("")
def create_transaction(body: TransactionCreate):
    db = _db()
    result = db.table("transactions").insert(body.model_dump(exclude_none=True)).execute()
    if not result.data:
        raise HTTPException(status_code=400, detail="Could not create transaction")
    return result.data[0]


@router.patch("/{tx_id}/status")
def advance_status(tx_id: str, body: TransactionUpdate):
    db = _db()
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()

    # Fetch current record for milestone alert context
    existing = db.table("transactions").select(
        "status, closing_date, listings(address, city)"
    ).eq("id", tx_id).limit(1).execute().data
    old_status = existing[0]["status"] if existing else None

    result = db.table("transactions").update(updates).eq("id", tx_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Transaction not found")

    tx = result.data[0]
    new_status = tx.get("status")

    # Fire SMS alert when status actually changes to a milestone stage
    if new_status and new_status != old_status:
        try:
            from integrations.twilio_client import send_milestone_alert
            listing = existing[0].get("listings") if existing else None
            address = (
                f"{listing['address']}, {listing['city']}" if listing
                else "your listing"
            )
            send_milestone_alert(
                status=new_status,
                address=address,
                closing_date=tx.get("closing_date"),
            )
        except Exception as exc:
            # Never let SMS failure break the API response
            from loguru import logger
            logger.warning(f"[transactions] milestone SMS skipped: {exc}")

    return tx


# ── Agreement Draft Queue ──────────────────────────────────────────────────────

@router.get("/drafts")
def list_drafts(status: str = "pending_review"):
    """Return agreement drafts awaiting Jennifer's review."""
    db = _db()
    q = db.table("agent_memory").select("*").eq("agent_name", "real_estate").eq("memory_type", "draft")
    rows = q.execute().data or []
    return {"count": len(rows), "drafts": rows}


@router.post("/drafts")
def save_draft(body: DraftCreate):
    """Store an agreement draft in agent memory for Jennifer's review."""
    db = _db()
    key = f"draft_{body.draft_type}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    payload = {
        "agent_name": "real_estate",
        "memory_type": "draft",
        "key": key,
        "value": {
            "draft_type": body.draft_type,
            "content": body.content,
            "lead_id": body.lead_id,
            "transaction_id": body.transaction_id,
            "notes": body.notes,
            "status": "pending_review",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    }
    result = db.table("agent_memory").insert(payload).execute()
    if not result.data:
        raise HTTPException(status_code=400, detail="Could not save draft")
    return {"key": key, "status": "saved", "data": result.data[0]}


@router.patch("/drafts/{key}/approve")
def approve_draft(key: str):
    """Mark a draft as approved by Jennifer — ready for Lone Wolf execution."""
    db = _db()
    rows = (
        db.table("agent_memory")
        .select("*")
        .eq("agent_name", "real_estate")
        .eq("memory_type", "draft")
        .eq("key", key)
        .limit(1)
        .execute()
        .data
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Draft not found")

    current_value = rows[0]["value"]
    current_value["status"] = "approved"
    current_value["approved_at"] = datetime.now(timezone.utc).isoformat()

    db.table("agent_memory").update({"value": current_value}).eq("key", key).eq("agent_name", "real_estate").execute()
    return {"key": key, "status": "approved", "message": "Draft approved. Execute in Lone Wolf Transactions."}
