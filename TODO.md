# AICC TODO

**Phase:** 3 — Real Estate Integration (finishing up)
**Updated:** 2026-07-06

---

## 🔥 Unblocked Right Now — Do These Next

- [ ] **Add Twilio credentials to .env** — TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, KAREESA_PHONE
- [ ] **Test CEO morning briefing SMS** — Twilio account now active; briefing is built, just needs live credentials
- [ ] **Wire Twilio SMS milestone alerts** — transaction status changes → SMS (Phase 3.4 — built, pending Twilio)
- [ ] **Deploy website to Netlify** — footer has IABS, brokerage info, EHO, correct email. Copy IABS PDF first:
      rename your PDF → `Caresir_IABS_2026_KWP.pdf` → drop into `locked-in-homes-site/` → deploy folder

---

## Phase 3 — Remaining (3 items)

- [ ] **HAR MLS lead intake n8n workflow** — auto-capture leads from saved searches → Supabase leads table
- [ ] **Twilio SMS milestone alerts** — 🔓 unblocked now (see above)
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

- Twilio account: ACTIVE as of 2026-07-06 — unblocks CEO briefing SMS + milestone alerts
- Broker Jennifer must approve any agreements before they are executed in Lone Wolf
- Sharon Traylor: active land buyer lead, 6-step sequence loaded, referred by Shay Mims
- 4707 Cairnvillage St Houston TX 77084: probate listing, on hold (sibling estate dispute)
- Iyah meet season: January–May 2027
- Website: LIVE at lockedinhomes.com — needs redeploy with footer + IABS updates
- All scheduled jobs: America/Chicago timezone
