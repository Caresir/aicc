# AICC TODO

**Phase:** 1 — Foundation Build  
**Updated:** 2026-06-26

---

## Doing Now

- [ ] Fill in `.env` with real API keys (start with ANTHROPIC_API_KEY and POSTGRES_PASSWORD)
- [ ] Run `docker compose up -d` and verify all services start

---

## Phase 1 Backlog

### Repository
- [ ] `git init` in `aicc/` folder
- [ ] Create GitHub private repo `aicc`
- [ ] Push initial commit
- [ ] Create `.gitignore`
- [ ] Set up branch protection on `main`

### Infrastructure
- [ ] Confirm all Docker services are healthy: `docker compose ps`
- [ ] Access n8n at http://localhost:5678 and create admin account
- [ ] Access Supabase Studio at http://localhost:3000
- [ ] Generate secrets: run `scripts/generate-secrets.sh`

### Database
- [ ] Write `backend/memory/migrations/001_core_schema.sql`
- [ ] Run migrations against local Supabase Postgres
- [ ] Verify tables visible in Supabase Studio

### Backend
- [ ] Write `backend/api/main.py` (FastAPI app)
- [ ] Write `backend/requirements.txt`
- [ ] Write `backend/Dockerfile`
- [ ] Test: `GET http://localhost:8080/health` returns 200

### Frontend
- [ ] Initialize Vite React app in `frontend/`
- [ ] Install Tailwind CSS + configure brand colors
- [ ] Install shadcn/ui
- [ ] Create `frontend/Dockerfile.dev`
- [ ] Test: http://localhost:3001 loads with AICC branding

---

## Upcoming (Phase 2)

- [ ] Build CEO Agent with morning briefing
- [ ] Build Project Manager Agent
- [ ] Wire agents to Supabase memory layer
- [ ] Agent chat UI in dashboard

---

## Notes

- Broker Jennifer must approve any DocuSign documents before sending to clients
- Sharon Traylor is active lead — land buyer, referred by Shay Mims
- 4707 Cairnvillage St Houston TX 77084 listing is on hold (probate)
- Meet schedule for GymnastDiva Iyah (Nastia) runs January–May 2027
- All scheduled jobs use America/Chicago timezone
