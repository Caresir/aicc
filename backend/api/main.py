from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from api.routers import agents, leads, tasks, listings, transactions, content, fba, real_estate, video_tracker, metricool

app = FastAPI(
    title="AICC — AI Command Center",
    description="Backend API for Locked In with Kareesa's AI Command Center",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        os.getenv("SITE_URL", "http://localhost:3001"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents.router)
app.include_router(leads.router)
app.include_router(tasks.router)
app.include_router(listings.router)
app.include_router(transactions.router)
app.include_router(content.router)
app.include_router(fba.router)
app.include_router(real_estate.router)
app.include_router(video_tracker.router)
app.include_router(metricool.router)


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
