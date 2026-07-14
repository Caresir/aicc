-- ============================================================
-- AICC SCORE Tracker Module — Supabase Schema
-- Weekly Point Tracker: Social, Contracts, Open Houses,
-- Real Estate Conversations, Equity Analysis (CMA)
-- Run this in the Supabase SQL Editor.
-- ============================================================

-- 1. Activity log: one row per logged activity
create table if not exists score_activities (
  id uuid primary key default gen_random_uuid(),
  activity_date date not null default current_date,
  activity_type text not null check (activity_type in (
    'social_post',        -- 2 pts each, max 5/week
    'kwp_class',          -- 5 pts/week when >= 2 classes attended
    'signed_agreement',   -- 5 pts each, no max
    'oh_flyer_share',     -- 2 pts, no max
    'oh_doorknock',       -- 2 pts, no max
    'oh_host',            -- 2 pts, no max
    'oh_followup',        -- 4 pts, no max
    'conversation',       -- 5x5: 5 pts per day with >= 5 convos, max 25/week
    'command_opportunity',-- 1 pt each, no max
    'cma'                 -- 2 pts each, max 10/week
  )),
  quantity int not null default 1 check (quantity > 0),
  notes text,
  source text default 'sms',  -- sms | manual | n8n | agent
  created_at timestamptz not null default now()
);

create index if not exists idx_score_activities_date
  on score_activities (activity_date);

-- 2. Weekly scoring function with all SCORE caps applied.
--    week_start should be the Monday of the week you want scored.
create or replace function get_weekly_score(week_start date)
returns table (
  category text,
  raw_count bigint,
  points int
)
language sql
stable
as $$
with wk as (
  select *
  from score_activities
  where activity_date >= week_start
    and activity_date < week_start + 5  -- Mon-Fri only
),
-- Social: 2 pts each, capped at 5 posts (10 pts)
social as (
  select coalesce(sum(quantity), 0) as cnt from wk
  where activity_type = 'social_post'
),
-- Classes: 5 pts flat if 2+ attended this week
classes as (
  select coalesce(sum(quantity), 0) as cnt from wk
  where activity_type = 'kwp_class'
),
agreements as (
  select coalesce(sum(quantity), 0) as cnt from wk
  where activity_type = 'signed_agreement'
),
oh as (
  select
    coalesce(sum(quantity) filter (where activity_type = 'oh_flyer_share'), 0) as flyer,
    coalesce(sum(quantity) filter (where activity_type = 'oh_doorknock'), 0)   as knock,
    coalesce(sum(quantity) filter (where activity_type = 'oh_host'), 0)        as host,
    coalesce(sum(quantity) filter (where activity_type = 'oh_followup'), 0)    as followup
  from wk
),
-- 5x5: for each day, 5 pts if convo count >= 5; max 25/week
convo_days as (
  select activity_date, sum(quantity) as convos
  from wk
  where activity_type = 'conversation'
  group by activity_date
),
convos as (
  select
    coalesce(sum(convos), 0) as total_convos,
    coalesce(count(*) filter (where convos >= 5), 0) as complete_5x5_days
  from convo_days
),
opps as (
  select coalesce(sum(quantity), 0) as cnt from wk
  where activity_type = 'command_opportunity'
),
-- CMA: 2 pts each, capped at 10/week (20 pts)
cmas as (
  select coalesce(sum(quantity), 0) as cnt from wk
  where activity_type = 'cma'
)
select 'S - Social Media', social.cnt,
       (least(social.cnt, 5) * 2)::int from social
union all
select 'C - Classes', classes.cnt,
       (case when classes.cnt >= 2 then 5 else 0 end)::int from classes
union all
select 'C - Signed Agreements', agreements.cnt,
       (agreements.cnt * 5)::int from agreements
union all
select 'O - Open Houses',
       (oh.flyer + oh.knock + oh.host + oh.followup),
       (oh.flyer * 2 + oh.knock * 2 + oh.host * 2 + oh.followup * 4)::int
from oh
union all
select 'R - 5x5 Conversations', convos.total_convos,
       (least(convos.complete_5x5_days, 5) * 5)::int from convos
union all
select 'R - Command Opportunities', opps.cnt,
       (opps.cnt * 1)::int from opps
union all
select 'E - CMA', cmas.cnt,
       (least(cmas.cnt, 10) * 2)::int from cmas;
$$;

-- 3. Convenience: grand total for a week
create or replace function get_weekly_grand_total(week_start date)
returns int
language sql
stable
as $$
  select coalesce(sum(points), 0)::int
  from get_weekly_score(week_start);
$$;

-- 4. Convenience view: current week (Mon-Fri) score at a glance
create or replace view current_week_score as
select *
from get_weekly_score(date_trunc('week', current_date)::date);

-- 5. Habit streaks: consecutive weekdays with a completed 5x5
create or replace view fivexfive_streak as
with daily as (
  select activity_date, sum(quantity) as convos
  from score_activities
  where activity_type = 'conversation'
  group by activity_date
  having sum(quantity) >= 5
),
gaps as (
  select activity_date,
         activity_date - (row_number() over (order by activity_date))::int as grp
  from daily
)
select min(activity_date) as streak_start,
       max(activity_date) as streak_end,
       count(*) as days
from gaps
group by grp
order by streak_end desc;

-- ============================================================
-- Quick test after running:
--   insert into score_activities (activity_type, quantity)
--     values ('conversation', 5);
--   select * from current_week_score;
--   select get_weekly_grand_total(date_trunc('week', current_date)::date);
-- ============================================================
