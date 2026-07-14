"""Amazon FBA brand approvals and distributor management endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.fba_agent import FBAAgent

router = APIRouter(prefix="/api/fba", tags=["fba"])


class BrandCreate(BaseModel):
    name: str
    distributor: str
    notes: str = ""


class BrandStatusUpdate(BaseModel):
    status: str
    notes: str = ""


class DistributorCreate(BaseModel):
    name: str
    contact: str = ""
    website: str = ""
    notes: str = ""


class DistributorStatusUpdate(BaseModel):
    account_status: str  # no_account | applied | active


# ── Brands ────────────────────────────────────────────────────────────────────

@router.get("/brands")
def list_brands():
    agent = FBAAgent()
    brands = agent.get_brands()
    pending  = sum(1 for b in brands if b["status"] == "pending")
    approved = sum(1 for b in brands if b["status"] == "approved")
    denied   = sum(1 for b in brands if b["status"] == "denied")
    return {"count": len(brands), "pending": pending, "approved": approved, "denied": denied, "brands": brands}


@router.post("/brands")
def add_brand(body: BrandCreate):
    agent = FBAAgent()
    return agent.add_brand(name=body.name, distributor=body.distributor, notes=body.notes)


@router.patch("/brands/{brand_id}/status")
def update_brand_status(brand_id: str, body: BrandStatusUpdate):
    agent = FBAAgent()
    ok = agent.update_brand_status(brand_id, body.status, body.notes)
    if not ok:
        raise HTTPException(status_code=404, detail="Brand not found")
    return {"id": brand_id, "status": body.status}


@router.post("/brands/{brand_id}/research")
def research_brand(brand_id: str):
    agent = FBAAgent()
    brands = agent.get_brands()
    brand = next((b for b in brands if b["id"] == brand_id), None)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    research = agent.research_brand(brand_id, brand["name"], brand["distributor"])
    return {"id": brand_id, "research": research}


@router.delete("/brands/{brand_id}")
def delete_brand(brand_id: str):
    agent = FBAAgent()
    ok = agent.delete_brand(brand_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Brand not found")
    return {"deleted": brand_id}


# ── Distributors ──────────────────────────────────────────────────────────────

@router.get("/distributors")
def list_distributors():
    agent = FBAAgent()
    items = agent.get_distributors()
    return {"count": len(items), "distributors": items}


@router.post("/distributors")
def add_distributor(body: DistributorCreate):
    agent = FBAAgent()
    return agent.add_distributor(
        name=body.name, contact=body.contact,
        website=body.website, notes=body.notes,
    )


@router.patch("/distributors/{dist_id}/status")
def update_distributor_status(dist_id: str, body: DistributorStatusUpdate):
    agent = FBAAgent()
    ok = agent.update_distributor_status(dist_id, body.account_status)
    if not ok:
        raise HTTPException(status_code=404, detail="Distributor not found")
    return {"id": dist_id, "account_status": body.account_status}


@router.delete("/distributors/{dist_id}")
def delete_distributor(dist_id: str):
    agent = FBAAgent()
    ok = agent.delete_distributor(dist_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Distributor not found")
    return {"deleted": dist_id}


@router.post("/distributors/{dist_id}/email")
def application_email(dist_id: str):
    agent = FBAAgent()
    distributors = agent.get_distributors()
    dist = next((d for d in distributors if d["id"] == dist_id), None)
    if not dist:
        raise HTTPException(status_code=404, detail="Distributor not found")
    email = agent.distributor_application_email(dist["name"])
    return {"distributor": dist["name"], "email": email}


@router.get("/setup/checklist")
def document_checklist():
    agent = FBAAgent()
    return {"checklist": agent.account_document_checklist()}


@router.get("/setup/starter-distributors")
def starter_distributors():
    agent = FBAAgent()
    return {"suggestions": agent.suggest_starter_distributors()}


# ── AI Advice ─────────────────────────────────────────────────────────────────

class BusinessProfile(BaseModel):
    business_name: str
    owner_name: str
    address: str
    phone: str
    email: str
    amazon_store: str


class DiscoverRequest(BaseModel):
    distributor: str
    category: str = ""


@router.post("/discover")
def discover_brands(body: DiscoverRequest):
    agent = FBAAgent()
    return {"brands": agent.discover_brands(body.distributor, body.category)}


@router.post("/prioritize")
def prioritize():
    agent = FBAAgent()
    return {"advice": agent.prioritize_brands()}


@router.get("/debug/distributors-raw")
def debug_distributors_raw():
    agent = FBAAgent()
    rows = agent._db.table("agent_memory").select("*").eq("agent_name", agent.name).eq("memory_type", "fba").eq("key", "distributors").execute()
    return {"row_count": len(rows.data), "rows": rows.data}


@router.get("/profile")
def get_profile():
    agent = FBAAgent()
    return agent.get_business_profile()


@router.post("/profile")
def save_profile(body: BusinessProfile):
    agent = FBAAgent()
    agent.save_business_profile(body.model_dump())
    return {"status": "saved"}


@router.post("/chat")
def chat(body: dict):
    agent = FBAAgent()
    return {"response": agent.chat(body.get("message", ""))}
