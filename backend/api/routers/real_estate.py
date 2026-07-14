"""Real estate social content generation endpoint."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from agents.real_estate_agent import RealEstateAgent
from agents.real_estate_content_agent import RealEstateContentAgent

router = APIRouter(prefix="/api/real-estate", tags=["real-estate"])


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
