# AICC Project Roadmap

**Owner:** Kareesa Gonzales | **Brand:** Locked In with Kareesa  
**Started:** 2026-06-26 | **Status:** Phase 3 complete + Phase 4 largely complete

---

## Phase Overview

| Phase | Name | Status | Target |
|---|---|---|---|
| 1 | Foundation Build | ✅ COMPLETE | Week 1-2 |
| 2 | AI Employees Core | ✅ COMPLETE | Week 3-4 |
| 3 | Real Estate Integration | ✅ COMPLETE (pending APIs) | Week 5-6 |
| 4 | GymnastDiva Content Engine | ✅ LARGELY COMPLETE | Week 7 |
| 5 | Agency + FBA Automation | 🔄 IN PROGRESS | Week 8-9 |
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

## PHASE 2 — AI Employees Core ✅ COMPLETE

**Started:** 2026-06-26 | **Completed:** 2026-06-30  
**Objective:** Build the AI employee agents with system prompts, memory access, and API endpoints. Real Estate Assistant is Priority #1 — active leads need attention now.

### 2.1 Agent Architecture ✅
- [x] `backend/agents/base_agent.py` — Abstract base class
- [x] Agent interface: `think()`, `remember()`, `recall()`, `report()`
- [x] Supabase memory layer: read/write agent state
- [x] Claude API client wrapper with retry (3 attempts, exponential backoff), token logging
- [x] Agent registry — maps agent names to classes in `/api/routers/agents.py`

### 2.2 Real Estate Assistant Agent ✅
- [x] **System prompt** — KW Preferred Pearland agent, warm professional tone, defers document execution to Jennifer via Lone Wolf Transactions
- [x] **Lead intake** — `POST /api/leads` — name, source, type, status, notes
- [x] **Lead record: Sharon Traylor** — land buyer, profile in Supabase, co_purchasers + property_criteria JSONB
- [x] **Follow-up drafter** — agent reads lead history, drafts personalized text or email
- [x] **Lead status workflow** — New → Contacted → Nurturing → Under Contract → Closed / Dead
- [x] **6-step follow-up sequence** — Sharon Traylor onboarding seeded and confirmed working
- [x] **Lone Wolf guard rail** — agent drafts agreements only, NEVER executes in Lone Wolf
- [x] **Memory** — stores lead preferences, research briefs, sequence drafts per lead
- [ ] **HAR MLS integration** — query active listings matching buyer criteria (Phase 3)
- [ ] **Showing notes** — voice/text input → structured note saved to lead memory (Phase 3)
- [x] **n8n workflow: lead follow-up reminder** — no contact in 3 days → agent drafts follow-up (`n8n/lead_followup_reminder.json` — import into n8n)

### 2.3 CEO Agent ✅
- [x] System prompt: business performance, daily priorities, cross-business alerts
- [x] Morning briefing workflow: auto-runs at 7:00 AM CT via n8n Schedule Trigger
- [x] Reads: active leads, overdue follow-ups, open tasks, active listings, sequence steps due
- [x] Outputs: prioritized daily plan delivered via Twilio SMS (pending carrier approval)
- [x] Memory: briefing stored in agent_memory after each run
- [x] API endpoint: `POST /api/agents/ceo/briefing` — manually triggerable

### 2.4 Project Manager Agent
- [x] System prompt: task tracking, deadline detection, blocker alerts
- [x] Reads Supabase tasks table
- [x] Creates tasks from plain-English input
- [x] Weekly status report generation
- [x] Integrates with CEO Agent briefing

### 2.5 Remaining Agents (scaffolded now, fully activated in Phases 3–5)
- [x] Content Director — built and registered (Phase 4 complete)
- [x] FBA Manager — built and registered (Phase 5 in progress)
- [ ] Marketing Agent (Phase 4)
- [ ] Research Agent (Phase 3)
- [ ] Sales Agent (Phase 5)
- [ ] Finance Assistant (Phase 5)
- [ ] Document Assistant (Phase 3)
- [ ] Customer Support (Phase 5)
- [ ] SEO Agent (Phase 4)
- [ ] Analytics Agent (Phase 6)

### 2.6 Agent API Endpoints ✅
- [x] `POST /api/agents/{agent_name}/chat` — send message, get response
- [x] `GET /api/agents/{agent_name}/memory/{key}` — agent's stored context
- [x] `GET /api/agents/status` — all agents health check
- [x] `POST /api/agents/ceo/briefing` — trigger CEO morning briefing
- [x] `POST /api/leads` — create/update lead record
- [x] `GET /api/leads` — lead list with filters
- [x] `POST /api/agents/broadcast` — send to all agents simultaneously

### 2.7 Frontend: Agent Offices + Lead View ✅
- [x] Agent selector sidebar
- [x] Chat interface per agent (threaded conversation)
- [x] Agent status indicator (active/idle/processing)
- [x] Memory viewer panel
- [x] **Leads table** — name, type, status, last contact, quick action buttons + Add Lead modal
- [x] **Lead detail drawer** — contact info, status badges, notes, AI draft quick actions
- [x] **Quick action bar** — "Draft Text", "Draft Email", "Draft Agreement", lead agent chat
- [x] **Real Estate page** — listings grid, transaction pipeline, draft queue, social content generator
- [x] **Tasks page** — plain-English task creation, overdue alerts, complete button, weekly report
- [x] **FBA page** — brand tracker, distributor manager, AI research, application email drafts
- [x] **GymnastDiva page** — content queue, caption generator, meet schedule (Iyah Gonzales)
- [x] App running at http://localhost:5174 (port changed from 3001 — Docker conflict resolved)

**Phase 2 Success Criteria:**
- [x] Can type "follow up with Sharon Traylor" → Real Estate Assistant drafts a personalized message
- [x] Sharon Traylor lead profile in Supabase with full sequence history
- [x] CEO Agent sends morning briefing at 7 AM CT (SMS pending Twilio carrier approval)
- [x] Agent responses stored in Supabase with timestamps
- [x] No agent exceeds 10s response time
- [x] Sharon Traylor lead profile visible in dashboard (Phase 2.7)
- [x] Can chat with any agent from the dashboard (Phase 2.7)

---

## PHASE 3 — Real Estate Integration

**Objective:** Full CRM for Locked In with Kareesa. Lead tracking, listing management, Lone Wolf Transactions integration, and HAR MLS data.

### 3.1 Lead Management ✅
- [x] Lead intake form (web + API endpoint)
- [x] Lead table in Supabase: name, source, status, last_contact, notes
- [x] Sharon Traylor (land buyer) — active lead profile with 6-step sequence
- [ ] Auto-capture leads from HAR MLS saved searches (n8n workflow)
- [ ] Lead scoring with Real Estate Assistant Agent

### 3.2 Listing Management ✅
- [x] Active listing: 4707 Cairnvillage St Houston TX 77084 (probate, on hold) — seeded
- [x] Listing status tracking: active / under contract / on hold / sold
- [x] Listing page in dashboard with status controls
- [x] Migration 003: enriched Cairnvillage with listing_type, full notes, client name
- [ ] MLS data import (CSV upload or KW Command export)

### 3.3 Lone Wolf Transactions Integration ✅ (partially)
- [x] AI drafts listing agreements and buyer agreements — text output only, stored in Supabase
- [x] Jennifer approval gate — AI NEVER executes documents in Lone Wolf directly
- [x] Draft review queue in dashboard — Jennifer clicks approve, then executes in Lone Wolf manually
- [ ] Lone Wolf API read integration — sync transaction status into Supabase (waiting for API access)
- [ ] Transaction status webhook → update Supabase transaction record

> **TEST CASE — 4707 Cairnvillage St, Houston TX 77084**
> Client: Nadine | Type: Probate listing | Status: On hold pending title clearance
> Hold reason: Sibling dispute over estate title
> Already loaded in Lone Wolf Transactions — use this transaction as the live smoke test
> when the API integration is built. Verify status sync, hold flag, and milestone alerts.

### 3.4 Transaction Tracking ✅ (frontend + backend built)
- [x] Transaction pipeline UI (kanban — pending → offer → under contract → inspection → closing)
- [x] Backend API: list, pipeline view, status update
- [ ] Lone Wolf Transactions API integration (read-only first — waiting for API access)
- [ ] Milestone alerts via Twilio SMS (pending carrier approval)

### 3.5 Real Estate Dashboard Page ✅
- [x] Listings grid with status badges and status controls
- [x] Transaction pipeline (kanban-style, horizontally scrollable)
- [x] Agreement draft queue with Jennifer approve button
- [x] Social content generator (4 platforms, 8 content types, brand voice rules)

**Phase 3 Remaining:**
- [ ] HAR MLS lead intake n8n workflow (auto-capture from saved searches)
- [ ] Twilio SMS milestone alerts (pending carrier A2P 10DLC approval)
- [ ] Lone Wolf API read (pending API access from Lone Wolf)

**Phase 3 Success Criteria:**
- [x] Sharon Traylor's lead profile visible in dashboard
- [x] Can type "follow up with Sharon" → Real Estate Agent drafts message
- [x] Agent drafts a listing or buyer agreement; Jennifer reviews in dashboard and executes it herself in Lone Wolf
- [x] Listing at 4707 Cairnvillage shows correct status

---

## PHASE 4 — GymnastDiva Content Engine ✅ LARGELY COMPLETE

**Objective:** Full content automation for GymnastDiva Iyah Gonzales across Instagram, TikTok, YouTube Shorts, and Facebook.

### 4.1 Content Calendar ✅
- [x] Content queue table in Supabase (content_queue)
- [x] Meet schedule Jan–May 2027 — 12 meets seeded from Google Calendar (thegymnastdiva99@gmail.com)
- [x] Content type taxonomy: highlight, skills, meet_recap, motivation, lesson_promo
- [x] Weekly content plan auto-generated by Content Director Agent
- [x] Athlete name corrected throughout: Iyah Gonzales

**2027 Meet Schedule (seeded 2026-07-08):**
| Date | Meet | Location |
|---|---|---|
| Jan 7 | Rally in Valley | Glendale, AZ |
| Jan 21 | Pikes Peak Cup | Colorado Springs, CO |
| Jan 29 | Biles Invitational | Houston, TX |
| Feb 4 | Metroplex Challenge | Ft. Worth, TX |
| Feb 19 | WOGA Classic | Frisco, TX |
| Feb 26 | Yellow Rose Invitational | Pearland, TX |
| Mar 19 | Level 9/10 State | TBD |
| Apr 2 | Level 7/8 State | TBD |
| Apr 8 | Level 9/10 Regionals | Kansas City, KS |
| Apr 16 | Level 6/7/8 Regionals | TBD |
| May 7 | Level 9 Westerns | Galveston, TX |
| May 13 | Level 10 Nationals | TBD |

### 4.2 Caption & Hashtag Generation ✅
- [x] Content Director Agent (backend/agents/content_director_agent.py)
- [x] System prompt: warm authentic voice for young athlete brand, Iyah Gonzales
- [x] Hashtag sets by content type (highlight, skills, meet_recap, motivation, lesson_promo)
- [x] Auto-draft captions from video title + notes — all 4 platforms
- [x] Caption review queue in dashboard

### 4.3 Platform Integrations
- [ ] Instagram Graph API: draft + schedule posts
- [ ] TikTok API: upload + caption draft
- [ ] YouTube Data API: upload Shorts + title/description
- [ ] Facebook Pages API: cross-post

### 4.4 Private Lessons (Calendly)
- [ ] Calendly webhook → new booking → Content Director notified
- [ ] Auto send confirmation + prep instructions to client

### 4.5 GymnastDiva Dashboard Page ✅
- [x] Caption generator with platform tabs
- [x] Content queue (draft / approved / published)
- [x] Meet schedule tab with Add Meet modal and delete
- [x] Disciplines: All, Floor, Trampoline, Rod Floor, Black Floor

**Phase 4 Success Criteria:**
- [x] Content Director drafts captions for Iyah's videos from a short description
- [x] Meet schedule visible in dashboard — 12 meets loaded
- [ ] Calendly booking triggers confirmation workflow

---

## PHASE 5 — Agency + FBA Automation 🔄 IN PROGRESS

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

### 5.3 Amazon FBA (scholarshipee.com) ✅ (partially)
- [x] FBA Manager Agent built (backend/agents/fba_agent.py) — registered in Supabase
- [x] FBA page in dashboard — brand tracker, distributor manager, AI research, application email drafts
- [x] Agent stores brands/distributors in agent_memory (memory_type: "fba")
- [ ] Amazon SP-API connection
- [ ] Inventory level monitoring — alert if any SKU < reorder point
- [ ] Distributor intake: Infinity Distribution, EN Distribution, Catalist, Faire (manual entry via dashboard for now)
- [ ] Wholesale order tracker in Supabase
- [ ] Finance Assistant: monthly P&L for FBA business

### 5.4 Agency + FBA Dashboard Pages ✅ (partially)
- [ ] Agency pipeline (kanban: prospect / proposal / onboarding / active / retained)
- [x] FBA page live — brand tracker, distributor manager, AI research panel
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
| Frontend port | 5174 (changed from 3001) | Docker port conflict — Supabase Studio on 3000, n8n on 5678 |
| Timezone | America/Chicago (CT) | All five businesses are Houston/Pearland-based |
| FBA distributor tracking | agent_memory (Supabase) | Simple, queryable, no extra SaaS needed |
| SMS provider | Twilio | Best API, reliable delivery, easy n8n integration |
| Doc storage | Google Drive | Already in use; native Google Workspace integration |
| Meet schedule storage | agent_memory (key: gymnast_meets) | No dedicated table needed; ContentDirectorAgent manages reads/writes |
| Python dev environment | C:\aicc-venv (venv) | Windows MAX_PATH limit exceeded by Twilio package paths |
| Supabase DDL execution | docker exec aicc_postgres psql | Supabase Studio (localhost:3000) errors on multi-statement DDL |
| GymnastDiva Google Calendar | thegymnastdiva99@gmail.com | Shared to cham4547@gmail.com for MCP access |

---

## Content Assets Created

| Asset | Location | Notes |
|---|---|---|
| Neighborhood video scripts | docs/neighborhood-video-scripts.md | 4 scripts: Rosharon, Iowa Colony, Manvel, Pearland |
| Supplier vetting SOP | docs/supplier-vetting.md | FBA supplier research process |
| Product research SOP | docs/product-research-agent.md | FBA product research process |

---

## Pending Items (next to build)

- [ ] Twilio A2P 10DLC carrier approval (10–15 day review, submitted ~2026-07)
- [ ] Buy Twilio phone number + update TWILIO_PHONE_NUMBER in .env
- [ ] HAR MLS lead intake n8n workflow (auto-capture from saved searches)
- [ ] Lone Wolf API read integration (waiting for API access)
- [ ] Platform API integrations: Instagram, TikTok, YouTube, Facebook
- [ ] Calendly webhook → Content Director notification
- [ ] Update TBD venues in meet schedule when announced
- [ ] AI Agency CRM (Phase 5.1–5.2)

---

*Last updated: 2026-07-08 | Phase 3 complete | Phase 4 largely complete | Phase 5 in progress*
