# AICC Project Roadmap

**Owner:** Kareesa Gonzales | **Brand:** Locked In with Kareesa  
**Started:** 2026-06-26 | **Status:** Phase 2 — AI Employees (Real Estate Assistant first)

---

## Phase Overview

| Phase | Name | Status | Target |
|---|---|---|---|
| 1 | Foundation Build | ✅ COMPLETE | Week 1-2 |
| 2 | AI Employees Core | 🔄 IN PROGRESS | Week 3-4 |
| 3 | Real Estate Integration | QUEUED | Week 5-6 |
| 4 | GymnastDiva Content Engine | QUEUED | Week 7 |
| 5 | Agency + FBA Automation | QUEUED | Week 8-9 |
| 6 | Full Dashboard + Polish | QUEUED | Week 10-11 |
| 7 | Production Hardening | QUEUED | Week 12 |

---

## PHASE 1 — Foundation Build ✅ COMPLETE

**Completed:** 2026-06-26  
**Objective:** Establish the full infrastructure stack locally. Every subsequent phase builds on this.

### 1.1 Repository & Version Control
- [x] Create `aicc/` project folder structure
- [x] Create README.md
- [x] Create .env.example with all API keys listed
- [x] Create docker-compose.yml
- [x] `git init` + push to GitHub (private repo)
- [x] Create `.gitignore` (exclude .env, secrets/, __pycache__, node_modules, .DS_Store)
- [x] Set up branch protection on `main`

### 1.2 Infrastructure (Docker)
- [x] docker-compose.yml with all services defined
- [x] Run `docker compose up -d` — all services healthy
- [x] Supabase Studio accessible at http://localhost:3000
- [x] n8n accessible at http://localhost:5678
- [x] Postgres health check passing
- [x] Create n8n postgres database (separate from aicc db)

### 1.3 Database Schema (Supabase)
- [x] Create `backend/memory/migrations/001_core_schema.sql`
- [x] Tables: `agents`, `agent_memory`, `conversations`, `tasks`, `leads`, `listings`, `content_queue`, `transactions`
- [x] Row Level Security (RLS) policies on all tables
- [x] Create Supabase service role in .env
- [x] Run migrations against local Postgres

### 1.4 FastAPI Backend Scaffold
- [x] `backend/api/main.py` — FastAPI app with health endpoint
- [x] `backend/api/routers/` — agents, leads, content, tasks
- [x] `backend/api/middleware/` — auth, logging, CORS
- [x] `backend/Dockerfile`
- [x] `backend/requirements.txt`
- [x] API accessible at http://localhost:8080
- [x] `/docs` Swagger UI working

### 1.5 React Frontend Scaffold
- [x] `npx create-vite frontend --template react-ts`
- [x] Install Tailwind CSS + configure brand colors
- [x] Install shadcn/ui component library
- [x] `frontend/Dockerfile.dev`
- [x] Brand colors in tailwind.config: emerald, black, gold, cream
- [x] Font stack: Montserrat, Poppins, Lato via Google Fonts
- [x] Dashboard layout shell: sidebar + header + main content area
- [x] App accessible at http://localhost:3001

### 1.6 Environment & Secrets
- [x] `.env` filled with real values (local only, never committed)
- [x] Cryptographically generated: POSTGRES_PASSWORD, JWT_SECRET, SECRET_KEY_BASE, N8N_ENCRYPTION_KEY
- [x] Document every env var in `.env.example` with description

**Phase 1 Success Criteria — ALL MET ✅**
- `docker compose up -d` runs with 0 errors ✅
- All 4 dashboard URLs return 200 ✅
- FastAPI `/health` returns `{"status": "ok"}` ✅
- React app loads with AICC branding ✅
- Supabase Studio shows aicc database with schema ✅

---

## PHASE 2 — AI Employees Core 🔄 IN PROGRESS

**Started:** 2026-06-26  
**Objective:** Build the AI employee agents with system prompts, memory access, and API endpoints. Real Estate Assistant is Priority #1 — active leads need attention now.

### 2.1 Agent Architecture (build first — everything depends on this)
- [ ] `backend/agents/base_agent.py` — Abstract base class
- [ ] Agent interface: `think()`, `act()`, `remember()`, `report()`
- [ ] Supabase memory layer: read/write agent state
- [ ] Claude API client wrapper with retry, rate limiting, cost tracking
- [ ] Agent registry — maps agent names to classes

### 2.2 Real Estate Assistant Agent ⭐ PRIORITY #1 (active leads now)
- [ ] **System prompt** — KW Preferred Pearland agent, HAR MLS expertise, warm professional tone, always defers document execution to broker Jennifer via Lone Wolf Transactions
- [ ] **Lead intake** — `POST /api/leads` — name, source, type (buyer/seller/investor), status, notes
- [ ] **Lead record: Sharon Traylor** — land buyer, create profile in Supabase leads table
- [ ] **Follow-up drafter** — "Follow up with [lead name]" → agent reads lead history, drafts personalized message (email or SMS)
- [ ] **Lead status workflow** — New → Contacted → Nurturing → Under Contract → Closed / Dead
- [ ] **HAR MLS integration** — query active listings matching buyer criteria, attach results to lead record
- [ ] **Showing notes** — voice/text input → structured note saved to lead memory
- [ ] **Listing status tracker** — 4707 Cairnvillage St Houston TX 77084 (probate, on hold) — auto-update from MLS
- [ ] **n8n workflow: lead follow-up reminder** — no contact in 3 days → agent drafts follow-up → notify Kareesa for approval before sending
- [ ] **Lone Wolf guard rail** — agent can draft agreements but NEVER executes in Lone Wolf; flags for Jennifer approval
- [ ] **Memory** — stores each lead's preferences, pain points, timeline, prior conversations

### 2.3 CEO Agent (Priority #2)
- [ ] System prompt: business performance, daily priorities, cross-business alerts
- [ ] Morning briefing workflow: auto-runs at 7:00 AM CT
- [ ] Reads: lead count, new emails, calendar today, task backlog, revenue MTD
- [ ] Outputs: prioritized daily plan + push notification summary
- [ ] Memory: decision log, preference learning

### 2.4 Project Manager Agent
- [ ] System prompt: task tracking, deadline detection, blocker alerts
- [ ] Reads TODO.md + Supabase tasks table
- [ ] Creates tasks from plain-English input
- [ ] Weekly status report generation
- [ ] Integrates with CEO Agent briefing

### 2.5 Remaining Agents (scaffolded now, fully activated in Phases 3–5)
- [ ] Content Director (Phase 4)
- [ ] Marketing Agent (Phase 4)
- [ ] Research Agent (Phase 3)
- [ ] Sales Agent (Phase 5)
- [ ] Finance Assistant (Phase 5)
- [ ] Document Assistant (Phase 3)
- [ ] Customer Support (Phase 5)
- [ ] SEO Agent (Phase 4)
- [ ] Analytics Agent (Phase 6)

### 2.6 Agent API Endpoints
- [ ] `POST /api/agents/{agent_name}/chat` — send message, get response
- [ ] `GET /api/agents/{agent_name}/memory` — agent's stored context
- [ ] `GET /api/agents/status` — all agents health check
- [ ] `POST /api/leads` — create/update lead record
- [ ] `GET /api/leads` — lead list with filters (status, type, last contact)
- [ ] `POST /api/agents/broadcast` — send to all agents simultaneously

### 2.7 Frontend: Agent Offices + Lead View
- [ ] Agent selector sidebar
- [ ] Chat interface per agent (threaded conversation)
- [ ] Agent status indicator (active/idle/processing)
- [ ] Memory viewer panel
- [ ] **Leads table** — name, type, status, last contact, quick action buttons
- [ ] **Lead detail drawer** — full history, notes, agent chat scoped to that lead
- [ ] **Quick action bar** — "Follow up", "Draft agreement", "Pull MLS comps"

**Phase 2 Success Criteria:**
- Can type "follow up with Sharon Traylor" → Real Estate Assistant drafts a personalized message
- Sharon Traylor lead profile visible in dashboard with full history
- CEO Agent sends morning briefing at 7 AM CT
- Can chat with any agent from the dashboard
- Agent responses stored in Supabase with timestamps
- No agent exceeds 10s response time

---

## PHASE 3 — Real Estate Integration

**Objective:** Full CRM for Locked In with Kareesa. Lead tracking, listing management, Lone Wolf Transactions integration, and HAR MLS data.

### 3.1 Lead Management
- [ ] Lead intake form (web + API endpoint)
- [ ] Auto-capture leads from HAR MLS saved searches
- [ ] Lead table in Supabase: name, source, status, last_contact, notes
- [ ] Sharon Traylor (land buyer) — active lead profile
- [ ] Lead scoring with Real Estate Assistant Agent

### 3.2 Listing Management
- [ ] Active listing: 4707 Cairnvillage St Houston TX 77084 (probate, on hold)
- [ ] Listing status tracking: active / under contract / on hold / sold
- [ ] Auto-pull MLS data via HAR API
- [ ] Listing page in dashboard

### 3.3 Lone Wolf Transactions Integration
- [ ] AI drafts listing agreements and buyer agreements — text output only, stored in Supabase
- [ ] Jennifer approval gate — AI NEVER executes documents in Lone Wolf directly
- [ ] Lone Wolf API read integration — sync transaction status into Supabase
- [ ] Transaction status webhook → update Supabase transaction record
- [ ] Draft review queue in dashboard — Jennifer clicks approve, then executes in Lone Wolf manually

### 3.4 Transaction Tracking
- [ ] Transaction timeline UI (offer → contract → closing)
- [ ] Lone Wolf Transactions API integration (read-only first)
- [ ] Milestone alerts via Twilio SMS + email

### 3.5 Real Estate Dashboard Page
- [ ] Active leads table with status badges
- [ ] Listings grid with photos (from Google Drive)
- [ ] Transaction pipeline (kanban-style)
- [ ] Quick action: "Draft follow-up to [lead name]"

**Phase 3 Success Criteria:**
- Sharon Traylor's lead profile visible in dashboard
- Can type "follow up with Sharon" → Real Estate Agent drafts message
- Agent drafts a listing or buyer agreement; Jennifer reviews in dashboard and executes it herself in Lone Wolf
- Listing at 4707 Cairnvillage shows correct status

---

## PHASE 4 — GymnastDiva Content Engine

**Objective:** Full content automation for @LockedInWithKareesa and GymnastDiva Iyah across Instagram, TikTok, YouTube Shorts, and Facebook.

### 4.1 Content Calendar
- [ ] Content queue table in Supabase
- [ ] Meet schedule Jan–May 2027 synced from Google Calendar
- [ ] Content type taxonomy: highlight reel, skills breakdown, meet recap, motivational
- [ ] Weekly content plan auto-generated by Content Director Agent

### 4.2 Caption & Hashtag Generation
- [ ] Content Director prompt: warm, authentic voice for young athlete brand
- [ ] Hashtag sets by content type (skills, meets, motivation)
- [ ] Auto-draft captions from video title + notes
- [ ] Caption review queue in dashboard

### 4.3 Platform Integrations
- [ ] Instagram Graph API: draft + schedule posts
- [ ] TikTok API: upload + caption draft
- [ ] YouTube Data API: upload Shorts + title/description
- [ ] Facebook Pages API: cross-post

### 4.4 Private Lessons (Calendly)
- [ ] Calendly webhook → new booking → Content Director notified
- [ ] Auto send confirmation + prep instructions to client

### 4.5 GymnastDiva Dashboard Page
- [ ] Content calendar view
- [ ] Draft queue (approve / edit / schedule)
- [ ] Meet schedule from Google Calendar
- [ ] Platform post status (published / scheduled / draft)

**Phase 4 Success Criteria:**
- Content Director drafts captions for Nastia's videos from a short description
- Meet schedule visible in dashboard
- Calendly booking triggers confirmation workflow

---

## PHASE 5 — Agency + FBA Automation

**Objective:** Build the client acquisition and delivery system for the AI Automation Agency, and automate FBA inventory monitoring for scholarshipee.com.

### 5.1 AI Agency CRM
- [ ] Prospect table: company name, owner, pain point, status, proposal sent
- [ ] Sales Agent: writes proposals from prospect research
- [ ] Proposal template: services menu, pricing tiers, ROI examples
- [ ] Follow-up sequence: 3-touch automated email + manual SMS trigger

### 5.2 Agency Delivery System
- [ ] Client onboarding checklist
- [ ] Deliverable tracker per client
- [ ] n8n workflow library (reusable automations to sell)
- [ ] Client reporting: auto-generate weekly performance PDF

### 5.3 Amazon FBA (scholarshipee.com)
- [ ] Amazon SP-API connection
- [ ] Inventory level monitoring — alert if any SKU < reorder point
- [ ] Distributor intake: Infinity Distribution, EN Distribution, Catalist, Faire
- [ ] Wholesale order tracker in Supabase
- [ ] Finance Assistant: monthly P&L for FBA business

### 5.4 Agency + FBA Dashboard Pages
- [ ] Agency pipeline (kanban: prospect / proposal / onboarding / active / retained)
- [ ] FBA inventory table with reorder alerts
- [ ] Revenue by business unit (real estate, gymnastics lessons, agency, FBA)

**Phase 5 Success Criteria:**
- Can type "research [company name] and draft a proposal" → Sales Agent delivers
- FBA inventory alert fires when stock drops below threshold
- Monthly P&L auto-generated by Finance Assistant

---

## PHASE 6 — Full Dashboard + Morning Briefing

**Objective:** The command center experience — one screen that shows everything, every morning.

### 6.1 Command Center Dashboard
- [ ] Morning briefing widget (CEO Agent summary)
- [ ] Business health tiles: RE leads / content scheduled / FBA inventory / agency MRR
- [ ] Command bar: type any plain-English command → routed to correct agent
- [ ] Real-time updates via Supabase Realtime subscriptions
- [ ] Mobile-responsive layout

### 6.2 Notification System
- [ ] Push notification via Twilio SMS for high-priority alerts
- [ ] Email digest at 7 AM CT
- [ ] In-app notification bell
- [ ] Alert routing rules: RE leads → SMS, content → in-app, FBA → email

### 6.3 Memory & Preference Learning
- [ ] Agent preference table: tone preferences, decision patterns, correction history
- [ ] "Remember that I prefer…" commands update agent memory
- [ ] Preference applied automatically on next interaction

**Phase 6 Success Criteria:**
- Dashboard loads in < 2 seconds
- Morning briefing SMS arrives at 7:00 AM CT daily
- Command bar routes to correct agent 100% of the time

---

## PHASE 7 — Production Hardening

**Objective:** Prepare for real usage. Security audit, performance optimization, monitoring, and deployment to production server.

### 7.1 Security
- [ ] All API endpoints authenticated (Supabase JWT)
- [ ] No secrets in code (audit with `git secrets`)
- [ ] CORS locked to known origins
- [ ] Rate limiting on all public endpoints
- [ ] Supabase RLS verified on all tables

### 7.2 Monitoring & Observability
- [ ] Structured JSON logging (all services)
- [ ] Error alerting to SMS on critical failures
- [ ] Uptime monitoring for n8n, API, and frontend
- [ ] Claude API cost dashboard (daily spend tracking)

### 7.3 Production Deployment
- [ ] Target: VPS (DigitalOcean Droplet or Hetzner Cloud — 4 vCPU, 8GB RAM)
- [ ] Nginx reverse proxy with SSL (Let's Encrypt)
- [ ] GitHub Actions CI/CD: test → build → deploy on push to `main`
- [ ] Daily Postgres backups to Google Drive
- [ ] Domain: aicc.lockedinwithkareesa.com (or similar)

**Phase 7 Success Criteria:**
- Production site live at custom domain with HTTPS
- Zero downtime deploys working
- Claude API monthly cost < $50 at current usage

---

## Decisions Made

| Decision | Choice | Reason |
|---|---|---|
| Default AI model | claude-sonnet-4-6 | Best balance of speed, cost, and capability |
| Frontend port | 3001 | Avoids conflict with Supabase Studio on 3000 |
| Timezone | America/Chicago (CT) | All five businesses are Houston/Pearland-based |
| FBA distributor tracking | Supabase table | Simple, queryable, no extra SaaS needed |
| SMS provider | Twilio | Best API, reliable delivery, easy n8n integration |
| Doc storage | Google Drive | Already in use; native Google Workspace integration |

---

*Last updated: 2026-06-26 | Phase 1 complete ✅ | Phase 2 in progress — building Real Estate Assistant first*
