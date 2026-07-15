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

- [x] **HAR MLS lead intake n8n workflow** — `n8n/har_lead_intake.json`, built 2026-07-13.
      No public HAR/Matrix saved-search API exists (same reason Lone Wolf below
      is blocked), so this watches Gmail for HAR/Matrix lead notification emails
      and parses them instead. Duplicate-check bug fixed 2026-07-15 (the
      `?email=` filter it relied on was silently ignored by the API, and the
      node's isDuplicate logic read a field the API never returned — see git
      log). **Still needed before this is live:** import the workflow into the
      running n8n instance and configure the `Gmail — caresir.gonzales@kw.com`
      OAuth2 credential it references (both manual, Kareesa only).
- [ ] **Lone Wolf API read** — ⏳ still blocked, waiting on API access from Lone Wolf

---

## Phase 4 — GymnastDiva Content Engine (next phase)

- [ ] Content queue table in Supabase
- [ ] Meet schedule Jan–May 2027 synced from Google Calendar
- [ ] Content Director Agent fully activated (scaffolded, needs system prompt + captions wired)
- [ ] Caption & hashtag generation for Iyah's content
- [ ] Caption review queue in dashboard
- [ ] Calendly webhook → booking confirmation workflow
- [ ] Instagram Graph API integration
- [ ] TikTok API integration
- [ ] YouTube Data API integration

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
