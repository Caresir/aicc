# Product Research Agent — n8n Workflow + Supabase Schema

Design doc for AICC Phase 2. This is the piece you can build now, independent of the Amazon SP-API application.

## What it does

Given a list of vetted distributor sites, the agent pulls their current catalog/pricing, scores each product against your sourcing criteria, and logs results to Supabase so you can review before committing to a purchase order.

## n8n Workflow — nodes in order

1. **Schedule Trigger** (or Manual Trigger to start) — run daily/weekly per distributor.
2. **Supabase node — Get Distributor List** — reads from `vetted_suppliers` table (only status = 'approved', from your vetting checklist).
3. **HTTP Request node** (loop per distributor, via Split In Batches) — fetches the distributor's catalog page or CSV/API feed if they provide one. Check each site's `robots.txt` and terms of service first — some distributors explicitly prohibit scraping and only allow catalog access via login/API, which you'll need to respect.
4. **HTML Extract / Code node** — parses product name, price, MOQ, category, UPC from the fetched page.
5. **Claude API node (Anthropic)** — for each product, prompt Claude to:
   - Estimate Amazon FBA landed cost and rough margin (given category-average referral fee)
   - Flag whether the category is typically gated (electronics, beauty, supplements, grocery, etc.)
   - Score sourcing risk 1–5 based on your vetting checklist criteria
6. **Filter node** — drop anything below your margin/risk threshold.
7. **Supabase node — Upsert to `product_candidates`** — store results.
8. **Slack/Email/Notification node** — daily digest of new qualifying products.

## Supabase schema

```sql
create table vetted_suppliers (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  website text not null,
  status text check (status in ('approved','rejected','pending')) default 'pending',
  verification_notes text,
  authorized_brands text[],
  catalog_url text,
  catalog_access_method text, -- 'scrape', 'csv_feed', 'api', 'login_required'
  last_checked timestamptz default now()
);

create table product_candidates (
  id uuid primary key default gen_random_uuid(),
  supplier_id uuid references vetted_suppliers(id),
  product_name text,
  upc text,
  category text,
  unit_cost numeric,
  moq integer,
  est_amazon_price numeric,
  est_margin_pct numeric,
  is_gated_category boolean,
  risk_score integer check (risk_score between 1 and 5),
  claude_notes text,
  discovered_at timestamptz default now(),
  status text check (status in ('new','reviewing','ordered','rejected')) default 'new'
);
```

## Claude API prompt skeleton (for the research node)

```
System: You are a sourcing analyst for an Amazon FBA reseller. Given a product name,
category, unit cost, and MOQ, estimate:
1. Likely Amazon referral fee % for this category
2. Rough landed cost including FBA fees
3. Whether this category typically requires ungating approval
4. A risk score 1-5 based on: category restriction level, brand recognition, MOQ size
Return only JSON: {margin_estimate_pct, is_gated_category, risk_score, notes}

User: Product: {{product_name}}, Category: {{category}}, Unit cost: {{unit_cost}}, MOQ: {{moq}}
```

## Important constraints to respect

- **Scraping legality**: only pull from sites whose robots.txt/ToS allow it, or that offer a CSV/API feed. Several established distributors (Wholesale Central members, brand B2B portals) offer these directly — ask for one instead of scraping when possible.
- **Rate limiting**: add a Wait node between requests to avoid hammering distributor servers and getting your IP blocked.
- **This does not replace the vetting checklist** — the agent only researches products from suppliers you've already verified in `vetted_suppliers`. Never let it auto-add new distributors.

## Next phase: SP-API connection

Once your Amazon SP-API developer application is approved, add:
- An **SP-API node** (community n8n node or custom HTTP calls with OAuth) to check current Buy Box price and sales rank for each `product_candidates` row before you order — closing the loop from "found a product" to "confirmed it sells."
