# AICC — AI Command Center

**Kareesa Gonzales | Locked In with Kareesa | @LockedInWithKareesa**

> "Class is in session — let's get you home."

The AI Command Center is a single AI-powered operating system that runs five businesses simultaneously: Real Estate (Keller Williams Preferred), GymnastDiva Iyah, AI Automation Agency, Amazon FBA (scholarshipee.com), and Digital Products/SaaS.

---

## Five Businesses, One Brain

| Business | Brand | Key Tools |
|---|---|---|
| Real Estate | Locked In with Kareesa | KW Command, HAR MLS, DocuSign, Lone Wolf |
| Gymnastics | GymnastDiva Iyah | Instagram, TikTok, YouTube Shorts, Calendly |
| AI Agency | AICC-as-a-service | n8n, Supabase, Claude API |
| Amazon FBA | scholarshipee.com | SP-API, Infinity Distribution, Catalist, Faire |
| Digital Products | In build | Stripe, Supabase |

---

## Technology Stack

| Layer | Technology |
|---|---|
| AI Engine | Anthropic Claude API (claude-sonnet-4-6) |
| Automation | n8n (self-hosted, Docker) |
| Database | Supabase (PostgreSQL + Auth + Storage + Realtime) |
| Backend | Python 3.11 + FastAPI |
| Frontend | React 18 + Vite + Tailwind CSS |
| Infrastructure | Docker + Docker Compose |
| CI/CD | GitHub + GitHub Actions |
| Integrations | MCP Servers + Google Workspace APIs |

---

## AI Employees

Twelve specialized agents, each with its own system prompt, memory, and tool access:

1. **CEO Agent** — Daily priorities, business performance, strategic decisions
2. **Project Manager** — Task assignment, progress, deadline alerts
3. **Real Estate Assistant** — Leads, CRM, emails, transaction tracking
4. **Content Director** — GymnastDiva captions, hashtags, content scheduling
5. **Marketing Agent** — Social media, ad copy, email campaigns
6. **Research Agent** — Prospect research, market analysis, competitor intel
7. **Sales Agent** — Proposals, follow-ups, agency pipeline
8. **Finance Assistant** — Revenue tracking, invoices, expense log
9. **Document Assistant** — Contract review, paperwork, file organization
10. **Customer Support** — Client communications, follow-up sequences
11. **SEO Agent** — Content optimization, keyword research, Google profile
12. **Analytics Agent** — KPI dashboards, engagement reports, trend detection

---

## Getting Started (Local Dev)

### Prerequisites
- Docker Desktop 4.x+
- Node.js 20+
- Python 3.11+
- Git

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/your-username/aicc.git
cd aicc

# 2. Copy environment template
cp .env.example .env
# Fill in your API keys in .env

# 3. Start all services
docker compose up -d

# 4. Verify everything is running
docker compose ps
```

### Service URLs (local dev)

| Service | URL |
|---|---|
| AICC Dashboard | http://localhost:3001 |
| FastAPI Docs | http://localhost:8080/docs |
| n8n Workflows | http://localhost:5678 |
| Supabase Studio | http://localhost:3000 |
| Supabase API | http://localhost:8000 |

---

## Brand Standards

- **Colors:** Emerald · Black · Gold · Cream
- **Fonts:** Montserrat (headings) · Poppins (subheadings) · Lato (body)
- **Logo:** Padlock with emerald key
- **Handle:** @LockedInWithKareesa
- **Client tone:** Warm, conversational, emoji-inclusive, always personalized

---

## Project Structure

```
aicc/
├── README.md
├── PROJECT_ROADMAP.md
├── TODO.md
├── .env.example
├── docker-compose.yml
├── backend/
│   ├── agents/          ← 12 AI employee workers
│   ├── workflows/       ← n8n workflow JSON exports
│   ├── integrations/    ← Google, KW Command, HAR MLS, DocuSign, etc.
│   ├── memory/          ← Supabase schema + memory layer
│   ├── api/             ← FastAPI application
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── pages/       ← Dashboard, Real Estate, GymnastDiva, Agency, FBA
│   │   ├── components/  ← Reusable UI components
│   │   └── agents/      ← AI Employee "office" panels
│   └── public/
├── scripts/             ← Setup, migration, seed scripts
└── docs/                ← Architecture docs, API references, runbooks
```

---

## Documentation

- [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) — All phases, timelines, success criteria
- [TODO.md](TODO.md) — Active task list
- [docs/](docs/) — Architecture, API references, runbooks

---

*Built with Claude Code · Powered by Anthropic · Locked In with Kareesa*
"# AI Command Center" 
