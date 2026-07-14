# SCORE Tracker

Weekly SCORE point tracker for the KW SCORE team: 5x5 morning nudges, SMS-based
activity logging with a Friday teacher-style report card + next-week game plan.

Built on the AICC stack that's already running (n8n in Docker) and the
Supabase Cloud project the rest of AICC's live app actually uses (see note
below — this is not the local Docker Postgres also present in this repo).

---

## Important context: which Supabase this targets

AICC turned out to have two separate Postgres backends in play: a local
Docker Postgres (used only by `run_migrations.py`, mostly vestigial) and a
Supabase **Cloud** project (`SUPABASE_URL`/`SUPABASE_SERVICE_ROLE_KEY` in
root `.env`) that every actual agent/router in the running app reads and
writes through. This module targets **Supabase Cloud** — confirmed by
querying it directly and finding the real, live `leads` table with Sharon
Traylor's actual record. If that architecture changes later (e.g. everything
gets consolidated onto local Docker Postgres), this module's env vars and
the n8n workflows' REST calls will need to move with it.

---

## Schema review notes (flagged, not changed — `schema.sql` is used as-is)

1. **Weekend gaps break the streak calculation.** `fivexfive_streak` groups
   consecutive *calendar* dates. If you log a 5x5 on Friday and again on
   Monday, that's a 3-day calendar gap (Sat/Sun have no rows), so the view
   treats Monday as day 1 of a new streak rather than a continuation of a
   business-day streak. Since the whole point is "don't break the chain" for
   a Mon–Fri habit, you may want the streak logic to treat Fri→Mon as
   consecutive. The morning nudge workaround (see `morning-5x5-nudge.json`)
   accounts for this when deciding whether to show the streak line, but the
   `days` count itself will still reset to 1 every Monday even on a real
   unbroken streak.
2. **No idempotency key.** `score_activities` has no column to record the
   Twilio `MessageSid`. If Twilio retries a webhook delivery (it does this
   on slow responses), the same reply could get inserted twice. Low risk
   for a single personal-use number with modest volume, but worth knowing.
3. **No RLS.** `score_activities` has no Row Level Security policy. Since
   this table is accessed with the service_role key (which bypasses RLS
   regardless), this doesn't currently matter — but if you ever expose it
   to the anon key or a client-side app, it'd need policies first.

None of these blocked the acceptance criteria, so I left the schema
untouched — flagging per the brief.

---

## Setup

### 1. Run the schema

This has to be done in the Supabase **Cloud** dashboard's SQL Editor (not
`localhost:3000` — that's the separate local stack). Open your project at
`https://supabase.com/dashboard/project/<your-ref>` → SQL Editor → paste in
`schema.sql` → run. I can't run this one for you — it requires DDL access
Supabase's REST API doesn't expose, and I only have the REST API keys.

### 2. Env vars

`score-tracker/.env` is already created with your real `SUPABASE_URL` /
service role key (copied from root `.env`, gitignored, not committed) — the
Python CLI works out of the box once step 1 is done.

Two vars needed in the root `.env` for the n8n workflows — one already set,
one placeholder to fill in:

| Var | Status |
|---|---|
| `MY_CELL` | Already set — reused your existing `KAREESA_PHONE` value |
| `MY_EMAIL` | **Placeholder — fill in** which inbox gets the Friday report card |

`TWILIO_PHONE_NUMBER`, `ANTHROPIC_API_KEY`, `SUPABASE_URL`, and
`SUPABASE_SERVICE_ROLE_KEY` are reused from the existing root `.env`.

**Note on scope:** the n8n workflows read these via `$env.VAR_NAME`, which
requires them to be passed into the `aicc_n8n` container's environment.
`docker-compose.yml`'s `n8n` service didn't pass *any* of your app env vars
through before (only its own DB/host config) — I added the six this module
needs (`MY_CELL`, `MY_EMAIL`, `TWILIO_PHONE_NUMBER`, `ANTHROPIC_API_KEY`,
`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`) to that service's
`environment:` block and recreated the container. That's the edit outside
`score-tracker/` beyond the README link, flagged as required — the
workflows can't function without it. (Aside, out of scope for this task: a
couple of the *existing* workflows in `backend/workflows/` also reference
`$env.SUPABASE_ANON_KEY` etc. against the local stack, which is a separate,
pre-existing question given the split-brain database situation above.)

### 3. Import the three workflows

No database credential to create in n8n this time — the workflows call
Supabase's REST/RPC API directly over HTTPS using the env vars above, same
pattern as this repo's existing `backend/workflows/*.json`.

n8n (`http://localhost:5678`) → Workflows → Import from File → import each of:

- `workflows/morning-5x5-nudge.json`
- `workflows/evening-checkin-logger.json`
- `workflows/friday-rollup.json`

After import, open each workflow and check the Twilio/Gmail nodes — they
reference credentials named **`Twilio account`** and **`Gmail account`**.
Since you said these are already configured in n8n, if your saved credential
has a different name, n8n will show the node with a credential-not-set
warning; just reselect your existing credential from the dropdown (import
won't fail, but the node won't run until you do this).

### 4. Point Twilio's inbound webhook at the evening logger

Twilio Console → Phone Numbers → your SCORE number → Messaging →
"A message comes in" → Webhook →
`{your n8n public/tunnel URL}/webhook/score-checkin-inbound` → HTTP POST.

(If n8n isn't reachable from the internet, use `ngrok http 5678` or similar
during testing, same as you'd need for any other inbound Twilio webhook.)

### 5. Activate all three workflows

Toggle each workflow to **Active** in the n8n UI (top right of the canvas).

---

## Test checklist

1. **Schema runs clean** — run in the Supabase Cloud SQL Editor, confirm no
   errors.
2. **Basic scoring** — in the SQL Editor:
   ```sql
   insert into score_activities (activity_type, quantity) values ('conversation', 5);
   select * from current_week_score;
   ```
   Confirm the `R - 5x5 Conversations` row shows `points = 5`. Then:
   ```sql
   delete from score_activities where activity_type = 'conversation';
   ```
3. **Workflows import clean** — all three imported into n8n with no errors
   (node parameter shapes were verified against the exact installed n8n
   version — 2.27.4 — running in `aicc_n8n`, not guessed from generic docs).
4. **CLI logger**:
   ```
   cd score-tracker
   python scripts/log_activity.py conversation 5 --note "test"
   ```
   Confirm it prints a row ID and the row shows up in `score_activities`
   (Supabase dashboard → Table Editor, or SQL Editor).
5. **Point caps** — in the SQL Editor, verify each:
   ```sql
   -- 6 social posts -> 10 pts, not 12
   insert into score_activities (activity_type, quantity) values ('social_post', 6);
   -- 11 CMAs -> 20 pts, not 22
   insert into score_activities (activity_type, quantity) values ('cma', 11);
   -- 4 convos in one day -> 0 pts for that day
   insert into score_activities (activity_type, quantity, activity_date) values ('conversation', 4, current_date + 1);
   select * from current_week_score;
   ```
6. **Dry-run each workflow** in n8n via "Execute Workflow" (manual trigger)
   before relying on the schedule/webhook:
   - `morning-5x5-nudge` — should text `MY_CELL` immediately
   - `friday-rollup` — should email `MY_EMAIL` and text `MY_CELL`
   - `evening-checkin-logger`'s webhook branch — text your SCORE number
     something like "1 post, 5 convos" and confirm you get the "Logged ✅…"
     reply and a new row in `score_activities` with `source = 'sms'`. Then
     text something nonsensical and confirm you get the "Didn't catch
     that…" fallback instead of a broken workflow.

Clean up test rows afterward:
```sql
delete from score_activities where notes = 'test' or activity_date = current_date + 1 or activity_type in ('social_post','cma');
```
