"""FBAAgent — Amazon FBA business manager for Kareesa Gonzales."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from loguru import logger

from agents.base_agent import BaseAgent


SYSTEM_PROMPT = """You are the Amazon FBA Business Manager for Kareesa Gonzales. \
You help run and grow her Amazon wholesale FBA store.

ABOUT KAREESA'S FBA BUSINESS:
- Amazon store is active and running
- Business model: wholesale — buying from distributors, reselling on Amazon
- Current distributors: Infinity Distribution LLC, EN Distribution, Catalist, Faire
- Primary bottleneck right now: getting brand approval (ungating) to sell more brands
- Once approved for a brand, money moves fast — FBA is her most immediate income opportunity

YOUR ROLE:
- Track brand approval requests (pending, approved, denied)
- Research brands to assess ungating likelihood and profit potential
- Advise on which brands to prioritize based on approval requirements and ROI
- Manage distributor relationships and catalog access
- Spot fast-moving products and opportunities in her distributor catalogs

BRAND UNGATING KNOWLEDGE:
- Common ungating requirements: 3 invoices from authorized distributor showing 10+ units, \
brand authorization letter, product images, utility bill, business license
- Easier to ungate: brands already sold by the distributor (shows supply chain legitimacy)
- Harder to ungate: Nike, Apple, Disney, Hasbro, Lego — typically gated for 3P sellers
- Amazon IP Accelerator brands: harder without brand direct relationship
- Wholesale accounts from authorized distributors are the strongest ungating proof
- Some brands use Transparency codes or Project Zero — avoid these for new sellers
- Best categories for fast approval: grocery, health & household, beauty, tools, sports

PROFIT EVALUATION:
- Target: 30%+ ROI after Amazon fees, COGS, prep, shipping
- Amazon fees: referral (8-15%) + FBA (varies by size/weight)
- BSR under 50,000 in main category = decent velocity
- Check for hazmat flags, IP complaints, or brand restrictions before ordering
- Aim for at least 3-4 fast-moving ASINs per approved brand

DISTRIBUTORS:
- Infinity Distribution LLC: check for restricted/gated brand flags before ordering
- EN Distribution: strong on health & beauty categories
- Catalist: broad catalog, good for grocery/household
- Faire: retail-focused, better for unique/boutique items, less typical for FBA

TONE:
- Direct and strategic — Kareesa needs income now
- Flag anything that could waste time or money
- Prioritize speed to first sale over perfect setup
- Always give a clear recommended next action"""


class FBAAgent(BaseAgent):
    """Amazon FBA business manager — brand approvals, research, distributor management."""

    def __init__(self) -> None:
        super().__init__()
        self._register()

    def _register(self) -> None:
        """Insert fba_manager into agents table if not already there."""
        try:
            self._db.table("agents").insert({
                "name": self.name,
                "display_name": "FBA Manager",
                "description": "Amazon FBA brand approvals, distributor management, wholesale strategy",
            }).execute()
        except Exception:
            pass  # Already registered

    def _agent_name(self) -> str:
        return "fba_manager"

    def _system_prompt(self) -> str:
        return SYSTEM_PROMPT

    # ── Storage helpers ────────────────────────────────────────────────────────

    def _load(self, key: str) -> list[dict]:
        try:
            rows = (
                self._db.table("agent_memory")
                .select("value")
                .eq("agent_name", self.name)
                .eq("memory_type", "fba")
                .eq("key", key)
                .limit(1)
                .execute()
            ).data
            if rows:
                val = rows[0]["value"]
                return val.get("items", []) if isinstance(val, dict) else []
        except Exception as exc:
            logger.error(f"[fba_manager] _load({key}) failed: {exc}")
        return []

    def _save(self, key: str, items: list[dict]) -> None:
        try:
            self._db.table("agent_memory").delete().eq("agent_name", self.name).eq("memory_type", "fba").eq("key", key).execute()
            self._db.table("agent_memory").insert({
                "agent_name": self.name,
                "memory_type": "fba",
                "key": key,
                "value": {"items": items},
            }).execute()
        except Exception as exc:
            logger.error(f"[fba_manager] _save({key}) failed: {exc}")

    # ── Brand Approvals ────────────────────────────────────────────────────────

    def get_brands(self) -> list[dict]:
        return self._load("brands")

    def add_brand(self, name: str, distributor: str, notes: str = "") -> dict:
        brands = self.get_brands()
        brand = {
            "id": str(uuid.uuid4()),
            "name": name,
            "distributor": distributor,
            "status": "pending",
            "date_submitted": datetime.now(timezone.utc).date().isoformat(),
            "notes": notes,
            "research": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        brands.append(brand)
        self._save("brands", brands)
        return brand

    def update_brand_status(self, brand_id: str, status: str, notes: str = "") -> bool:
        brands = self.get_brands()
        for b in brands:
            if b["id"] == brand_id:
                b["status"] = status
                if notes:
                    b["notes"] = notes
                b["updated_at"] = datetime.now(timezone.utc).isoformat()
                self._save("brands", brands)
                return True
        return False

    def delete_brand(self, brand_id: str) -> bool:
        brands = self.get_brands()
        updated = [b for b in brands if b["id"] != brand_id]
        if len(updated) == len(brands):
            return False
        self._save("brands", updated)
        return True

    def research_brand(self, brand_id: str, brand_name: str, distributor: str) -> str:
        """AI research on a brand's ungating likelihood and profit potential."""
        research = self.think(
            f"Research this Amazon brand for Kareesa's FBA store.\n\n"
            f"Brand: {brand_name}\n"
            f"Distributor: {distributor}\n\n"
            "Provide:\n"
            "1. UNGATING LIKELIHOOD (Easy / Moderate / Hard / Avoid) with specific reason\n"
            "2. TYPICAL REQUIREMENTS to get approved for this brand\n"
            "3. PROFIT POTENTIAL — category, typical BSR range, competition level\n"
            "4. RED FLAGS to watch for (IP issues, transparency codes, restrictions)\n"
            "5. RECOMMENDED NEXT ACTION — exactly what Kareesa should do first\n\n"
            "Be direct and specific. Lead with the most important thing.",
        )
        brands = self.get_brands()
        for b in brands:
            if b["id"] == brand_id:
                b["research"] = research
                b["researched_at"] = datetime.now(timezone.utc).isoformat()
                break
        self._save("brands", brands)
        return research

    # ── Distributors ───────────────────────────────────────────────────────────

    def get_distributors(self) -> list[dict]:
        items = self._load("distributors")
        if not items:
            items = _DEFAULT_DISTRIBUTORS()
            self._save("distributors", items)
        return items

    def add_distributor(self, name: str, contact: str = "", website: str = "", notes: str = "") -> dict:
        distributors = self.get_distributors()
        dist = {
            "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, name.lower())),
            "name": name,
            "contact": contact,
            "website": website,
            "notes": notes,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        distributors.append(dist)
        self._save("distributors", distributors)
        return dist

    def update_distributor_status(self, dist_id: str, account_status: str) -> bool:
        distributors = self.get_distributors()
        for d in distributors:
            if d["id"] == dist_id:
                d["account_status"] = account_status
                d["updated_at"] = datetime.now(timezone.utc).isoformat()
                self._save("distributors", distributors)
                return True
        return False

    def delete_distributor(self, dist_id: str) -> bool:
        distributors = self.get_distributors()
        updated = [d for d in distributors if d["id"] != dist_id]
        if len(updated) == len(distributors):
            return False
        self._save("distributors", updated)
        return True

    # ── AI Advice ──────────────────────────────────────────────────────────────

    def get_business_profile(self) -> dict:
        """Load saved business profile from memory."""
        try:
            rows = (
                self._db.table("agent_memory")
                .select("value")
                .eq("agent_name", self.name)
                .eq("memory_type", "profile")
                .eq("key", "business_profile")
                .limit(1)
                .execute()
            ).data
            if rows:
                return rows[0]["value"]
        except Exception as exc:
            logger.error(f"[fba_manager] get_business_profile failed: {exc}")
        return {}

    def save_business_profile(self, profile: dict) -> None:
        """Persist business profile to agent memory."""
        try:
            self._db.table("agent_memory").delete().eq("agent_name", self.name).eq("memory_type", "profile").eq("key", "business_profile").execute()
            self._db.table("agent_memory").insert({
                "agent_name": self.name,
                "memory_type": "profile",
                "key": "business_profile",
                "value": profile,
            }).execute()
        except Exception as exc:
            logger.error(f"[fba_manager] save_business_profile failed: {exc}")

    def distributor_application_email(self, distributor_name: str) -> str:
        """Draft a wholesale account application email for a specific distributor."""
        profile = self.get_business_profile()
        biz_name  = profile.get("business_name", "Scholar Ship Early Education LLC")
        owner     = profile.get("owner_name",    "Kareesa Gonzales")
        address   = profile.get("address",       "1806 Corsica Creek Ln A, Iowa Colony, TX 77583")
        phone     = profile.get("phone",         "832-349-1105")
        email     = profile.get("email",         "caresir@scholarshipee.com")
        store     = profile.get("amazon_store",  "Cho Go Unlimited")

        return self.think(
            f"Draft a professional wholesale account application email for {owner} "
            f"to send to {distributor_name}.\n\n"
            f"BUSINESS INFO (use exactly as written):\n"
            f"- Legal Business Name: {biz_name}\n"
            f"- Owner: {owner}\n"
            f"- Address: {address}\n"
            f"- Phone: {phone}\n"
            f"- Email: {email}\n"
            f"- Amazon Store Name: {store}\n"
            f"- Primary sales channel: Amazon FBA\n"
            f"- Business purpose: purchasing wholesale inventory to resell on Amazon.com\n\n"
            "The email should:\n"
            "1. Introduce Kareesa and her business by legal name professionally\n"
            "2. State she is an active Amazon FBA seller looking to establish a wholesale account\n"
            "3. Mention her Amazon storefront by name as proof of active selling\n"
            "4. Ask what their application process requires and what documents to submit\n"
            "5. State she has EIN, Texas resale certificate, and business license ready to provide\n"
            "6. Request a price sheet or catalog access once approved\n"
            "7. Sound like a real person wrote it — warm but professional\n\n"
            "Format as:\nSUBJECT: [subject line]\n\nBODY:\n[email body]\n\n"
            "Keep it concise — under 220 words. No hyphens or dashes."
        )

    def account_document_checklist(self) -> str:
        """Return what documents Kareesa needs to apply for wholesale accounts."""
        return self.think(
            "Kareesa Gonzales is a new Amazon FBA seller trying to open wholesale distributor accounts. "
            "She is based in Texas.\n\n"
            "Give her a clear, practical checklist of every document she needs to gather BEFORE "
            "applying to any wholesale distributor. For each document:\n"
            "1. What it is and why distributors require it\n"
            "2. How to get it if she doesn't have it yet (with specific steps for Texas)\n"
            "3. How long it typically takes to obtain\n\n"
            "Also include:\n"
            "- What her Amazon seller account info they may ask for\n"
            "- Tips for making her application stronger as a new seller\n"
            "- Common reasons applications get denied and how to avoid them\n\n"
            "Be specific and practical. She needs to take action today."
        )

    def suggest_starter_distributors(self) -> str:
        """Suggest wholesale distributors that are easiest for new Amazon FBA sellers to get into."""
        return self.think(
            "Kareesa is a brand new Amazon FBA wholesale seller with no distributor accounts yet. "
            "She needs distributors that approve new sellers and don't require a long track record.\n\n"
            "Suggest 6-8 wholesale distributors or platforms that are EASY for new FBA sellers to get into. "
            "For each one include:\n"
            "- Name and website\n"
            "- Why they are beginner-friendly\n"
            "- Application process (online form, email, call, etc.)\n"
            "- Minimum order requirements\n"
            "- What categories/brands they carry relevant to Amazon FBA\n"
            "- One tip to get approved faster\n\n"
            "Include a mix of: online wholesale platforms (no application needed), "
            "easy-to-apply broadline distributors, and specialty distributors.\n"
            "Rank them easiest to hardest to get into. "
            "Be specific with real company names, websites, and actionable steps."
        )

    def discover_brands(self, distributor: str, category: str = "") -> str:
        """Suggest specific brands to pursue from a given distributor."""
        return self.think(
            f"Kareesa is brand new to wholesale FBA and has zero brands approved yet. "
            f"She needs to find brands to apply for through her distributor.\n\n"
            f"DISTRIBUTOR: {distributor}\n"
            f"CATEGORY PREFERENCE: {category or 'No preference — suggest the best opportunities'}\n\n"
            "Give her a specific, actionable brand list. For each brand provide:\n"
            "- Brand name\n"
            "- Why this distributor likely carries it\n"
            "- Ungating difficulty (Easy / Moderate / Hard)\n"
            "- What ungating typically requires for this brand\n"
            "- Profit potential (Low / Medium / High) with a quick reason\n"
            "- One fast-moving product example to look for\n\n"
            "List 6-8 brands. Start with the easiest wins — brands she could get approved for "
            "and selling within 2-4 weeks. Be specific with real brand names, not generic examples. "
            "End with the single best brand she should go after FIRST and exactly what to do.",
        )

    def prioritize_brands(self) -> str:
        """AI recommendation on which brands to pursue first."""
        brands = self.get_brands()
        pending = [b for b in brands if b["status"] == "pending"]
        approved = [b for b in brands if b["status"] == "approved"]

        return self.think(
            "Kareesa needs income NOW from her Amazon FBA store. "
            "Review her brand list and give her a clear action plan.\n\n"
            f"Pending approval: {[b['name'] for b in pending]}\n"
            f"Already approved: {[b['name'] for b in approved]}\n\n"
            "Provide:\n"
            "1. Which pending brands to prioritize and why\n"
            "2. What specific steps to take THIS WEEK to get approvals\n"
            "3. If approved brands are listed — are there obvious fast-moving products to order?\n"
            "4. Any brands she should drop/skip to save time\n\n"
            "Be direct. She needs revenue, not theory.",
        )

    def chat(self, message: str) -> str:
        brands = self.get_brands()
        context: dict[str, Any] = {
            "pending_brands": [b["name"] for b in brands if b["status"] == "pending"],
            "approved_brands": [b["name"] for b in brands if b["status"] == "approved"],
            "denied_brands": [b["name"] for b in brands if b["status"] == "denied"],
        }
        return self.think(message, context=context)


def _DEFAULT_DISTRIBUTORS() -> list[dict]:
    """Use uuid5 so IDs are stable and never regenerate."""
    now = datetime.now(timezone.utc).isoformat()
    names = [
        ("Infinity Distribution LLC", "Active distributor"),
        ("EN Distribution",           "Strong on health & beauty"),
        ("Catalist",                  "Broad catalog — grocery & household"),
        ("Faire",                     "Boutique/retail focus"),
    ]
    return [
        {
            "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, name.lower())),
            "name": name,
            "contact": "",
            "website": "",
            "notes": notes,
            "account_status": "no_account",
            "created_at": now,
        }
        for name, notes in names
    ]
