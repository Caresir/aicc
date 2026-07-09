# Real Estate Content Assets

**Owner:** Kareesa Gonzales | **Brand:** Locked In with Kareesa
**Last updated:** 2026-07-09

This file documents the client-facing content systems that live *outside* the AICC
codebase, in KW Command and Canva, so the Real Estate Assistant Agent (and Kareesa)
have one place to see what already exists before building anything new. Nothing in
this file requires a code change; it is a reference doc.

---

## 1. KW Command SmartPlans

Built and configured directly in `agent.kw.com`, not in AICC. Both mirror the
existing **My Buyer Education (First Time Homebuyers)** plan's structure: Send
Email steps only, `Wait 2 Days` cadence, `Any Time` delivery, auto-remove on
reply.

### Locked In Land Buyer Class
- **Steps:** 10 emails, Day 1 → Day 19, every 2 days
- **Trigger tag:** `Land Buyer`
- **Auto-remove:** on reply, and at end of plan (Day 19)
- **Content:** where to start, access/easements, water/septic/power, zoning +
  ag exemption, mineral rights, financing, survey/title, making the offer,
  closing, welcome to landownership
- **Status:** live. Sharon Traylor was manually enrolled via her contact
  profile (Start Now) on 2026-07-09.
- ⚠️ **Known overlap:** `backend/agents/sequences/sharon_traylor.py` already
  defines a separate 6-step AICC-native follow-up sequence for Sharon
  (`FOLLOW_UP_SEQUENCE`), and `real_estate_agent.py`'s system prompt still
  lists her status as "New — welcome sequence pending." Sharon is now on
  **two** parallel outreach tracks. Reconcile before either one sends
  duplicate content — see TODO.md.

### Locked In Monthly: Class Notes
- **Steps:** 12 emails, one per month, `Wait 30 Days` cadence, then `Add
  Repeat` unlimited to cycle annually
- **Trigger tag:** `Newsletter`
- **Audience:** full database — buyers, sellers, sphere, past clients
- **Content:** school-year themed monthly touches (Pop Quiz in February, Back
  to School in August, Grateful for You in November, etc.), each with a
  bracketed placeholder for that month's real stats/story
- **Status:** built, not yet enrolling contacts

**Full copy, step-by-step build instructions, and merge tag notes:** see the
`Locked_In_SmartPlans_Playbook.docx` delivered 2026-07-09 (not stored in this
repo — ask Kareesa for the file if the Real Estate Assistant needs the source
copy).

---

## 2. Canva Guides

### The Complete Land Buyer's Guide
- 11-chapter downloadable PDF/Canva Doc, same 10 topics as the SmartPlan above
  plus Chapter 11: land/homestead financing programs (Texas Veterans Land
  Board land + home loans, USDA Rural Development Section 502 Direct/
  Guaranteed), and a clear split between the homestead tax exemption
  (not purchase money) and actual financing programs (is purchase money).
- Ends with a CTA into the Land Buyer Class SmartPlan and the Class Notes
  newsletter.
- Delivered as file, not yet in Canva (built via docx/PDF pipeline).

### Your Houston Relocation Guide (Canva Doc `DAHMOk5BW4s`)
- Pre-existing one-pager covering Iowa Colony, Rosharon, Manvel, Pearland.
- **Updated 2026-07-09:**
  - Rosharon section now cross-links to the Complete Land Buyer's Guide for
    acreage-curious readers.
  - Added a Class Notes newsletter opt-in line near the closing contact block.
- Edit link: https://www.canva.com/d/_uigwIAXI3Tgk7r

---

## 3. Cross-link Map

```
Houston Relocation Guide  ──(Rosharon section)──▶  Complete Land Buyer's Guide
Houston Relocation Guide  ──(closing CTA)────────▶  Class Notes newsletter
Complete Land Buyer's Guide ──(closing CTA)──────▶  Land Buyer Class SmartPlan
Complete Land Buyer's Guide ──(closing CTA)──────▶  Class Notes newsletter
Land Buyer Class SmartPlan ──(optional Day 19)───▶  Class Notes newsletter
```

Suggested tagging convention for the Real Estate Assistant Agent (Phase 2.2)
once lead intake is wired up: apply `Newsletter` to anyone who downloads
either guide, and additionally apply `Land Buyer` to anyone showing land
intent, so Command's Auto Add rules pick them up automatically.
