# AICC TODO

**Phase:** 3 — Real Estate Integration (finishing up)
**Updated:** 2026-07-06

---

## 🔥 Unblocked Right Now — Do These Next

- [x] **Add Twilio credentials to .env** — done 2026-07-13
- [x] **Test CEO morning briefing SMS** — done 2026-07-13, endpoint fires and reports "sent"; A2P campaign still under carrier re-review after Error 30925 fix, so actual delivery unconfirmed until approval clears
- [ ] **Wire Twilio SMS milestone alerts** — code + env wiring done 2026-07-13; same carrier-review caveat as above
- [x] **Deploy website to Netlify** — done 2026-07-13 (SMS consent checkbox fix)

---

## Phase 3 — Remaining (2 items)

- [x] **HAR MLS lead intake n8n workflow** — `n8n/har_lead_intake.json`, built 2026-07-13,
      imported into the live n8n instance by Kareesa. No public HAR/Matrix
      saved-search API exists (same reason Lone Wolf below is blocked), so this
      watches Gmail for HAR/Matrix lead notification emails and parses them
      instead. Two bugs fixed 2026-07-15:
      1. Duplicate-check was broken both ways — the `?email=` filter it relied
         on was silently ignored by the API, and the node's isDuplicate logic
         read a field the API never returned.
      2. Credential was pointed at `caresir.gonzales@kw.com`, which Kareesa
         can't authorize (KW's managed Google Workspace blocks third-party
         OAuth apps) — HAR/Matrix mail is forwarded to her personal Gmail
         instead, so the trigger now uses the `Gmail - cham4547@gmail.com`
         credential already connected for other workflows.
      **Unverified:** whether forwarded copies still carry the original HAR/
      Matrix sender address (the trigger's sender filter matches on that) —
      depends on how the KW→personal forward was set up. Worth checking n8n's
      execution log after a real HAR lead comes in to confirm it actually fires.
- [ ] **Lone Wolf API read** — ⏳ still blocked, waiting on API access from Lone Wolf

---

## Phase 4 — GymnastDiva Content Engine (next phase)

**Corrected 2026-07-15 — most of this phase was actually already done, this
list was stale.** Verified live against the running `aicc_api` + cloud
Supabase, not just by reading code:

- [x] Content queue table in Supabase — `content_queue`, confirmed live (empty, functional)
- [x] Meet schedule Jan–May 2027 — `meets` table has all 12 real 2027 meets loaded and live.
      Entered manually via `add_meet`, not auto-synced from Google Calendar as
      originally envisioned — but the actual data goal is met either way.
- [x] Content Director Agent fully activated — `backend/agents/content_director_agent.py`
      (319 lines: full system prompt, caption generation, queue CRUD, meet CRUD,
      weekly plan, chat), wired into `backend/api/routers/content.py` and
      `agents.py`. Not scaffolded, not missing a system prompt.
- [x] Caption & hashtag generation for Iyah's content — `generate_captions()`, live
- [x] Caption review queue in dashboard — `frontend/src/pages/GymnastDiva.tsx`
      (577 lines): draft → approved → published flow with copy/approve/archive
      buttons, wired to the real queue via React Query.
- [x] **Calendly webhook → booking confirmation workflow** — built 2026-07-15:
      `n8n/calendly_lesson_booking.json` + `scripts/register_calendly_webhook.py`.
      On a new booking: auto sends the client a confirmation email (and SMS if
      a phone number is available) with lesson time/location/prep instructions,
      and notifies Kareesa via task + SMS. **Not live yet, needs Kareesa:**
      (1) n8n must be reachable from the public internet for Calendly to reach
      it (ngrok or a real domain — same requirement as the score-tracker's
      inbound Twilio SMS webhook), (2) run `register_calendly_webhook.py` once
      to register the subscription with Calendly's API, (3) import the
      workflow and confirm the `Gmail - cham4547@gmail.com` / `Twilio account`
      credentials are connected. **Unverified:** the payload-parsing code is
      written against Calendly's documented v2 webhook schema but has not
      been tested against a real booking — check the first real execution's
      log in n8n and adjust `Parse Booking` if fields don't match.
- [ ] Instagram Graph API integration — still open. Current flow is draft →
      Kareesa copies caption → posts manually; no auto-publish to any platform.
- [ ] TikTok API integration — still open, same manual-posting gap as above.
- [ ] YouTube Data API integration — still open, same manual-posting gap as above.

---

## Phase 4 — RE Content Engine (parallel to GymnastDiva)

- [ ] **neighborhood-video-scripts.md** — create full on-camera scripts for all 4 neighborhoods
- [ ] RE Content Agent (`re_content`) fully activated — context files built, needs wiring to dashboard
- [ ] Weekly 5-post KWP SCORE plan generation
- [ ] Filming prep checklist generator per neighborhood

---

## Blocked (waiting on external access)

- [ ] Lone Wolf Transactions API — waiting for API credentials from Lone Wolf
- [ ] KW Command API — deferred (cost)

---

## Notes

- **Fixed 2026-07-13:** `scripts/init-aicc.sql` only granted the `postgres`
  role schema privileges on the `n8n` database, never `aicc` — every
  migration against `aicc` had been silently failing since first init
  (`permission denied for schema public`). No tables existed; nothing
  described as "seeded"/"confirmed working" in PROJECT_ROADMAP.md before this
  date was actually persisted. Fixed the init script and applied the grant to
  the live database, then re-ran migrations — all 11 tables now exist and
  Sharon Traylor's lead + sequence records are real. If anyone spins up a
  fresh volume, this fix is now baked into init-aicc.sql.
- Sharon Traylor dual-track outreach conflict: resolved 2026-07-13 — see
  REAL_ESTATE_ASSETS.md. SmartPlan wins for land education; AICC sequence
  step 4 skipped, other steps still active.
- Twilio account: ACTIVE as of 2026-07-06 — unblocks CEO briefing SMS + milestone alerts
- Broker Jennifer must approve any agreements before they are executed in Lone Wolf
- Sharon Traylor: active land buyer lead, 6-step sequence loaded, referred by Shay Mims
- 4707 Cairnvillage St Houston TX 77084: probate listing, on hold (sibling estate dispute)
- Iyah meet season: January–May 2027
- Website: LIVE at lockedinhomes.com — needs redeploy with footer + IABS updates
- All scheduled jobs: America/Chicago timezone
