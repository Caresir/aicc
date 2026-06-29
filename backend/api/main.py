from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from api.routers import agents, leads

app = FastAPI(
    title="AICC — AI Command Center",
    description="Backend API for Locked In with Kareesa's AI Command Center",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        os.getenv("SITE_URL", "http://localhost:3001"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents.router)
app.include_router(leads.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "aicc-api", "version": "0.2.0"}


@app.get("/")
def root():
    return {
        "message": "AICC API is running. Class is in session.",
        "docs": "/docs",
        "health": "/health",
        "agents": "/api/agents/status",
        "leads": "/api/leads",
    }
