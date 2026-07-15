---
spec: aicc-social-content
version: 1.0
owner: Kareesa (Locked In with Kareesa)
brokerage: Keller Williams Preferred, Pearland TX
purpose: >
  Single source of truth for the AICC social-media module. The content agent
  loads this file to generate on-brand posts, hooks, captions, and CTAs across
  TikTok, Instagram, and Facebook, and to route DM/comment leads into the
  existing AICC + KW Command follow-up sequences.
reconciles:
  - Facebook Marketing Playbook (6 pillars)
  - TikTok Playbook (5 weighted pillars)
  - Instagram Playbook (5 pillars)
---

# AICC Social Content Spec

This is the reference framework the content agent reads before generating anything.
It replaces the three separate platform playbooks with one canonical brand +
pillar system. Where the playbooks disagreed, the reconciliation notes explain
the call that was made.

---

## 1. Brand identity (applies to every platform, every post)

**Brand name:** Locked In with Kareesa
**Handle (all platforms):** @LockedInWithKareesa
**Tagline:** Class is in session, let's get you home
**Name usage:** "Kareesa" in all public-facing content and handles. "Caresir
Gonzales" only on legal documents and contracts, never in social copy.
**Brokerage line:** Keller Williams Preferred, Pearland TX

### Voice
Warm, educational, direct. A teacher persona is the through line: 15 years in the
classroom is the differentiator, so content should *teach* first and sell second.
Think "here's what nobody explained to you," not "call me to buy a house."

### Visual system
- Colors: emerald green, gold, black, cream
- Fonts: Montserrat (headlines), Lato (body)
- Motif: padlock (ties to "Locked In")

### Copy rules (hard constraints — the agent must enforce these)
1. **No hyphens or em dashes as connector punctuation.** Rewrite into separate
   sentences, commas, or a colon instead. This is the single most important copy
   rule and it applies to every caption, hook, and CTA.
2. Keep the teacher framing. Lead with the lesson.
3. One message, one CTA per piece of content.
4. Captions are conversational, not corporate.

---

## 2. Canonical content pillars

Six pillars. Every piece of content the agent produces maps to exactly one.
Use `id` values in code; use `name` in anything human-facing.

```yaml
pillars:
  - id: local_expert
    name: Local Expert & Community
    covers: [neighborhood tours, restaurant and coffee spotlights, weekend events,
             community updates, hidden gems, local market news]
    baseline_mix: 25          # % of monthly content
    role: discovery           # reaches strangers, most searchable
    sources:
      tiktok: "Local Expert Content (30%)"
      instagram: "Community"
      facebook: "Community"

  - id: education
    name: Education
    covers: [buyer tips, seller tips, financing, closing costs, contracts,
             market explainers, "nobody tells buyers this" lessons]
    baseline_mix: 25
    role: trust
    sources:
      tiktok: "Educational Content (25%)"
      instagram: "Education"
      facebook: "Education"

  - id: listings
    name: Listings & Property
    covers: [home tours, open houses, just listed, just sold, price drops,
             "what $X buys in Pearland", luxury walkthroughs]
    baseline_mix: 20
    role: proof
    sources:
      tiktok: "Property Content (20%)"
      instagram: "Listings"
      facebook: "Listings"

  - id: client_stories
    name: Client Stories
    covers: [testimonials, closing day reactions, before/after, buyer wins,
             bidding-war stories, home-iversary shoutouts]
    baseline_mix: 15
    role: social_proof
    sources:
      tiktok: "(folded into Property/Personal on TikTok — see note)"
      instagram: "Client Stories"
      facebook: "Client Stories"

  - id: personal_brand
    name: Personal Brand & Lifestyle
    covers: [day in the life, teacher-to-Realtor story, family, volunteer work,
             team culture, why I do this]
    baseline_mix: 10
    role: relationship
    sources:
      tiktok: "Personal Brand Content (15%)"
      instagram: "Lifestyle"
      facebook: "Lifestyle"

  - id: realtor_reality
    name: Realtor Reality & Behind-the-Scenes
    covers: [funny stories, inspection surprises, behind the scenes, the process,
             myth-busting the job]
    baseline_mix: 5
    role: authenticity
    sources:
      tiktok: "Realtor Reality Content (10%)"
      instagram: "(covered under Lifestyle on IG)"
      facebook: "Behind-the-Scenes"
```

### Reconciliation notes
- **Client Stories** did not exist as its own pillar on TikTok. Instagram and
  Facebook both broke it out, and it is your strongest referral driver, so it is
  promoted to a full canonical pillar. On TikTok the agent should still produce
  it (closing-reaction reels perform well there) and simply tag it `client_stories`.
- **Realtor Reality** (TikTok) and **Behind-the-Scenes** (Facebook) are the same
  thing. Merged. Instagram folded this under Lifestyle; the agent should split it
  back out for IG so the pillar mix stays consistent across platforms.
- **`baseline_mix`** is anchored to TikTok's explicit percentages, then rebalanced
  to make room for the Client Stories pillar. It is a monthly target, not a rigid
  quota.

---

## 3. Platform roles and pillar emphasis

The playbooks each described their platform's job differently. Reconciled:

| Platform  | Job                                            | Primary function |
|-----------|------------------------------------------------|------------------|
| TikTok    | Discovery. Reaches strangers who search.       | Get found        |
| Instagram | Relationship building. Nurtures the warm audience. | Get trusted  |
| Facebook  | Sphere + reach + reviews. Referral engine.     | Get chosen       |

The same pillar gets weighted differently per platform. `H` = lead heavy here,
`M` = normal, `L` = light.

| Pillar            | TikTok | Instagram | Facebook |
|-------------------|:------:|:---------:|:--------:|
| local_expert      |   H    |     M     |    M     |
| education         |   H    |     M     |    M     |
| listings          |   M    |     M     |    M     |
| client_stories    |   L    |     H     |    H     |
| personal_brand    |   M    |     H     |    M     |
| realtor_reality   |   M    |     L     |    M     |

Rationale: TikTok rewards searchable local + educational content that strangers
find, so those two run heavy there. Instagram and Facebook run on trust and
referrals, so Client Stories and Personal Brand carry more weight. Facebook's
Recommendations engine makes Client Stories especially valuable there.

---

## 4. Content formula (every video / reel / post)

All three playbooks used the identical structure. Canonical:

```
HOOK  →  VALUE  →  CTA
```

- **Hook (first 2 to 3 seconds):** stop the scroll. Bold claim, surprising stat,
  or direct question. Losing them here means nothing else matters.
- **Value:** deliver the promise. Teach, show, or reveal one useful thing.
- **CTA:** exactly one action.

**Length:** 15 to 45 seconds for video. One topic, one message, one CTA.

**Avoid:** talking too long, no hook, no captions, weak audio, no CTA.

### On-brand hook patterns (teacher framing, geo-swapped to your market)
- Nobody tells first-time buyers this.
- Here's what $350K buys in Pearland right now.
- Before you move to Iowa Colony, watch this.
- This Rosharon neighborhood surprised me.
- Class is in session: three things about closing costs.

---

## 5. SEO and keyword framework

TikTok, Instagram, and Facebook all now behave as search engines, and AI search
(ChatGPT, Perplexity, Gemini, Claude) recommends agents by name. The agent should
place keywords in all three spots on every piece:

1. **Say it out loud** in the video (e.g. "moving to Pearland Texas").
2. **On-screen text** overlay with the keyword.
3. **Caption** with the keyword written out.

### Your geo keyword set (replaces the playbooks' Clear Lake / League City examples)
Primary market: **Pearland, Rosharon, Iowa Colony, Manvel**
Subdivisions you already have scripts for: **Lakes of Highland Glen, Meridian,
Pomona, Sierra Vista**
Broader: **Houston, Moving to Houston, South of Houston**

### Niche keywords
Houston Realtor, Pearland real estate agent, first-time homebuyer, VA buyers,
cash offer, home valuation, relocation.

### AI-search consistency rule
Keep name, market, and specialty identical everywhere (Instagram, TikTok,
Facebook, Google Business Profile, Zillow, KW, LinkedIn, Dot Cards). AI search
rewards a consistent public footprint. This is why the handle is
@LockedInWithKareesa everywhere.

### Hashtag bank (Instagram / Facebook)
Use 5 to 10 niche tags, not generic ones:
`#PearlandRealEstate` `#PearlandRealtor` `#RosharonHomes` `#IowaColony`
`#ManvelTX` `#PomonaTX` `#MovingToHouston` `#HoustonRealtor` `#HoustonHomeBuyer`
`#HoustonHomeSeller` `#KellerWilliams` `#LockedInWithKareesa`

---

## 6. Bio formula (per platform)

Reconciled from the three bio formulas (TikTok used 3 parts, Instagram and
Facebook used 4). Canonical 4-part formula:

```
Who you help + Where you help + What you do + Call to action
```

**On-brand example (obeys the no-hyphen rule):**
> Helping Houston families buy and sell with a teacher's patience. Pearland,
> Rosharon, Iowa Colony. DM CLASS for my buyer guide.

Platform notes:
- **Instagram / Facebook name field:** include a keyword, e.g.
  "Kareesa | Pearland Real Estate". This field is indexed by search.
- **Link in bio:** point to home search, home valuation, and a booking link
  (Linktree or KW Command booking).

---

## 7. Lead generation and DM routing

The goal is **conversations**, not views or followers. Canonical funnel:

```
Content → Profile visit → Follow → Comment/DM → Conversation → Appointment → Client → Referral
```

### Signature CTAs (teacher-branded, on the padlock/classroom theme)
| CTA phrase        | Intent            | Delivers                          |
|-------------------|-------------------|-----------------------------------|
| DM CLASS          | buyer, top funnel | Buyer Guide / Relocation Guide    |
| DM HOME           | buyer             | Home search setup                 |
| DM SELL           | seller            | Seller Guide + valuation offer    |
| DM LAND           | land buyer        | Complete Land Buyer's Guide       |
| DM [NEIGHBORHOOD] | local intent      | Neighborhood guide (e.g. DM PEARLAND, DM ROSHARON, DM IOWA COLONY) |
| Comment ADDRESS   | seller            | Home valuation / CMA              |

### Lead magnets you already have
Complete Land Buyer's Guide, Houston Relocation Guide, Buyer Guide, Seller Guide,
Neighborhood Guides. The agent should match the CTA to the pillar: `education` and
`local_expert` posts push guides; `listings` posts push home search; seller-angled
posts push valuation.

### Routing into AICC (integration point)
When a DM keyword or comment trigger fires:
1. Capture the lead (name, keyword, source platform, post ID).
2. Deliver the matching lead magnet.
3. Enroll in the correct **AICC-native follow-up sequence** by intent
   (buyer / seller / land).

> **Open item flagged from AICC:** you run a parallel AICC follow-up sequence
> alongside KW Command SmartPlans. Before this module goes live, the routing
> logic needs a dedup guard so a social lead does not get enrolled in both and
> receive duplicate outreach. This is the same reconciliation already noted in
> the AICC build.

---

## 8. Metrics that matter

All three playbooks agreed here. Optimize for these, not vanity numbers:

**Track:** watch time, retention / completion, saves, shares, comments, profile
visits, DMs, appointments booked.
**Ignore as primary signals:** likes, raw follower count, one-off viral spikes.

Success formula (from the TikTok playbook, applies everywhere):
**Value + Consistency + Searchability + Authenticity.**

---

## 9. Sustainable cadence

A repeatable habit beats bursts. Baseline daily block:

- 10 min: create content
- 10 min: engage with local content
- 10 min: reply to comments and DMs

Posting floor: 4 to 5 times per week per platform, Stories daily on Instagram and
Facebook. Batch a week of content in one sitting and let AICC schedule it.

---

## 10. What the agent should be able to do with this spec

1. Generate a post for any pillar on any platform, on brand, obeying the copy rules.
2. Produce a 30-day calendar mapped to the `baseline_mix` and per-platform emphasis.
3. Write hooks, captions, and one CTA per piece using the geo + niche keyword set.
4. Route inbound DM/comment leads to the right lead magnet and AICC sequence.
