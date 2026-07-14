"""
Real estate content system context for Locked In with Kareesa.
All structured knowledge the RE Content Agent loads at startup.
Updated: July 2026
"""

# ── BRAND IDENTITY ─────────────────────────────────────────────────────────────

BRAND = {
    "name": "Locked In with Kareesa",
    "realtor": "Kareesa Gonzales",
    "brokerage": "Keller Williams Preferred",
    "markets": ["Iowa Colony", "Rosharon", "Manvel", "Pearland"],
    "corridor": "Highway 288 corridor south of Houston",
    "handle": "@LockedInWithKareesa",
    "signature_signoff": "Let's get you Locked In 🔐",
    "tagline": "Class is in session — let's get you home.",
    "differentiators": [
        "Former teacher with 15 years Houston-area classroom experience",
        "Actual resident — lives in Sierra Vista, Rosharon (formerly Sterling Lakes)",
        "Teaches buyers like a class: lessons, pop quizzes, homework CTAs",
        "Only agent in market teaching land-buying on camera",
    ],
}

PALETTE = {
    "emerald": "#0E4D3C",
    "black": "#1A1A1A",
    "gold": "#C9A227",
    "cream": "#F7F3E8",
    "headline_fonts": ["Montserrat Black", "Poppins ExtraBold"],
    "body_font": "Lato",
}

RESIDENT_INSIGHTS = {
    "current_neighborhood": "Sierra Vista, Rosharon",
    "previous_neighborhood": "Sterling Lakes, Rosharon",
    "address_quirk": (
        "Her address says Rosharon but the city is Iowa Colony — "
        "a common jurisdiction quirk in this corridor. Great teaching moment for buyers."
    ),
    "closer_grocery": "H-E-B in Manvel — opened and now Kareesa's nearest store (growth proof)",
    "flood_zones": (
        "Sierra Vista and Sterling Lakes are in different FEMA flood zones. "
        "Always check FEMA Map Service Center per address — never assume."
    ),
    "infrastructure": "Local police and fire station coverage = infrastructure proof for new buyers",
}


# ── CONTENT FUNNEL ──────────────────────────────────────────────────────────────

FUNNEL = {
    "entry_CTA": "Comment HOUSTON",
    "trigger": "ManyChat auto-DM (tested and live on Instagram)",
    "lead_magnet": {
        "name": "Houston Relocation Guide",
        "url": "https://lockedinhomes.com/houston-relocation-guide.pdf",
    },
    "conversion_step": {
        "name": "Home Goals Call",
        "url": "https://calendly.com/coachcaresir/homegoalscall",
        "description": "Free 30-minute strategy call — booked via Calendly",
    },
    "website": "https://lockedinhomes.com",
    "standard_CTAs": [
        "Comment HOUSTON for my free Houston Relocation Guide",
        "Book a free Home Goals Call — link in bio",
    ],
    "flow": "Video/post → 'Comment HOUSTON' → ManyChat DM → Relocation Guide PDF → Calendly booking",
}


# ── CONTENT CALENDAR ────────────────────────────────────────────────────────────

CONTENT_CALENDAR = {
    "cadence": {
        "short_posts": "Monday (Reels, Shorts, TikTok clips)",
        "long_form": "Thursday (full neighborhood tour video)",
        "frequency": "one neighborhood per week",
    },
    "neighborhood_rotation": [
        {
            "order": 1,
            "neighborhood": "Rosharon",
            "angle": "Resident perspective — she lives here now",
            "status": "filming now (July 2026)",
            "communities": ["Sierra Vista", "Sterling Lakes"],
            "unique_hooks": [
                "I actually LIVE here — insider view",
                "Rural acreage side vs master-planned side contrast",
                "Land-buying checklist segment: mineral rights, easements, septic, USDA loans",
                "Address says Rosharon but it's Iowa Colony — teach the quirk",
            ],
        },
        {
            "order": 2,
            "neighborhood": "Iowa Colony",
            "angle": "Meridiana master-planned spotlight",
            "status": "up next",
            "communities": ["Meridiana"],
            "unique_hooks": [
                "Meridiana Tower (60-ft sundial) = perfect teacher-brand shot",
                "Community literally builds education into its parks",
                "Top-selling master-planned community nationally",
                "Alvin ISD school cluster in/adjacent to community",
            ],
        },
        {
            "order": 3,
            "neighborhood": "Manvel",
            "angle": "Growth story — H-E-B opened, more coming",
            "status": "queued",
            "communities": ["Pomona", "Rodeo Palms", "Del Bello Lakes"],
            "unique_hooks": [
                "H-E-B is NOW OPEN — Kareesa's closer grocery store (authentic proof)",
                "Teacher line: 'Pop quiz: what does a new H-E-B tell you about a town?'",
                "1M+ sq ft retail/dining planned (Target, Lowe's attached)",
                "Pomona: Camp Pomona, treehouse/zipline park, fishing lake",
            ],
        },
        {
            "order": 4,
            "neighborhood": "Pearland",
            "angle": "Established suburb — everything already built",
            "status": "queued",
            "communities": ["Shadow Creek Ranch"],
            "unique_hooks": [
                "Pearland Town Center: 75+ stores, mature infrastructure",
                "Shadow Creek Ranch: 17 lakes, 150 acres parks, built since 1990s",
                "Shadow Creek Ranch Nature Trail: wetlands viewing deck walk-and-talk",
                "PearScape pear sculptures: fun local recognition moment for engagement",
            ],
        },
    ],
}


# ── KWP SCORE COMPETITION ──────────────────────────────────────────────────────

KWP_SCORE = {
    "active": True,
    "max_counting_posts_per_week": 5,
    "qualifying_post_types": [
        "short video clips (Reels, TikTok, Shorts)",
        "carousels",
        "market education posts",
        "relocation guide promos",
        "neighborhood tours",
    ],
    "weekly_goal": "Produce 5 postable, competition-qualifying pieces per week",
    "note": "Every content draft should be scored against this — is it postable and competition-qualifying?",
}


# ── COMPLIANCE RULES ────────────────────────────────────────────────────────────

COMPLIANCE = {
    "required_disclosures": [
        "Kareesa Gonzales' name must appear in video OR caption",
        "Brokerage name (Keller Williams Preferred) must appear per TREC/KW advertising rules",
    ],
    "price_language": [
        "NEVER state prices as guarantees",
        "Use 'ranging around...' or 'starting from approximately...'",
        "Always note: 'verify current pricing at the sales office / on the MLS'",
    ],
    "flood_zone_rule": (
        "NEVER state a property's or community's flood status without FEMA map verification. "
        "Always direct buyers to check FEMA Map Service Center by address. "
        "Sierra Vista and Sterling Lakes are in DIFFERENT flood zones — do not generalize."
    ),
    "fair_housing": "Fair housing language always — avoid language that steers buyers by neighborhood demographics",
    "school_filming": "Never film schools while students are present — exterior/drive-by only",
    "school_disclaimer": "School info changes — always direct buyers to verify directly with the district",
    "hoa_amenities": (
        "HOA amenities (Meridiana Adventure Cove, Pomona Camp Pomona, Shadow Creek Ranch rec centers) "
        "are PRIVATE — film from public streets and entrances only unless you have express developer permission."
    ),
    "never_film_while_driving": "Passenger films, or use a mounted phone. Never drive and film.",
    "price_verify_note": "All [VERIFY] items in scripts must be confirmed morning-of before filming.",
}


# ── VOICE AND STYLE RULES ───────────────────────────────────────────────────────

VOICE = {
    "tone": "warm, direct, teacher energy — not salesy, not robotic",
    "persona": "the teacher-turned-realtor who actually lives in the neighborhood",
    "teaching_formats": [
        "Pop quiz (e.g., 'Pop quiz: what does a new H-E-B tell you about a town?')",
        "Lesson of the day",
        "Homework CTA (e.g., 'Your homework: drop your must-have in the comments')",
        "Extra credit callout",
        "Class is in session openers",
    ],
    "signoff": "Let's get you Locked In 🔐",
    "dos": [
        "Personalize — reference specific places, real data",
        "Be the neighbor, not the brochure",
        "Use first-person resident experiences when relevant",
        "Keep CTAs clear and singular — one ask per post",
        "Emojis: use intentionally, not in every sentence",
    ],
    "donts": [
        "No hyphens or dashes in captions",
        "No AI-sounding phrases",
        "No guaranteed price statements",
        "No flood zone generalizations without FEMA verification",
        "Never sound like a press release",
    ],
}


# ── CONTENT TYPES ───────────────────────────────────────────────────────────────

CONTENT_TYPES = {
    "neighborhood_tour": {
        "format": "long-form video (Thursday post)",
        "length": "5–10 min full video, 60–90 sec highlight clip for Shorts",
        "structure": "Intro piece-to-camera → b-roll walk → teacher moment → stats → CTA outro",
    },
    "market_education": {
        "format": "carousel or short talking-head clip",
        "topics": [
            "Land buying checklist (mineral rights, easements, septic, USDA loans)",
            "Flood zone 101 — how to check your address",
            "Jurisdiction quirks (e.g., address says Rosharon, city is Iowa Colony)",
            "MLS vs off-market: what buyers need to know",
            "First-time buyer education posts",
        ],
    },
    "growth_story": {
        "format": "before/after b-roll + voiceover",
        "hook": "Show the proof of growth (H-E-B open, new roads, construction) — let the footage teach",
    },
    "guide_promo": {
        "format": "short clip or static graphic",
        "CTA": "Comment HOUSTON for the free Houston Relocation Guide",
        "frequency": "at least once per week",
    },
    "resident_pov": {
        "format": "casual, phone-shot authenticity",
        "hook": "I literally live here. Let me show you what it's ACTUALLY like.",
        "use_cases": ["grocery run reveal", "commute time", "neighborhood vibe check"],
    },
}


# ── PLATFORM RULES ──────────────────────────────────────────────────────────────

PLATFORM_RULES = {
    "instagram": {
        "caption_length": "3–6 sentences, storytelling, teacher energy",
        "hashtags": "20–25, place in first comment — NOT in the caption body",
        "CTA": "always ends with: 'Comment HOUSTON' or 'Link in bio to book'",
        "format": "Reels preferred, carousels for education posts",
    },
    "tiktok": {
        "caption_length": "1–2 punchy lines + 3–5 hashtags inline",
        "energy": "hook in first 2 seconds — start mid-sentence or mid-action",
        "CTA": "verbal on-camera CTA + comment HOUSTON in caption",
    },
    "youtube_shorts": {
        "title": "searchable, under 70 chars, include neighborhood name and keyword (e.g., 'Moving to Manvel TX? Here's what opened')",
        "description": "2–4 sentences, keyword-dense, include website URL and Calendly link",
        "CTA": "screen text CTA at end + verbal",
    },
    "facebook": {
        "caption_length": "2–4 sentences, warm and parent/family-friendly",
        "hashtags": "3–5 maximum",
        "note": "Facebook audience skews older — lean into family infrastructure, schools, safety, growth",
    },
}


# ── HASHTAG SETS ────────────────────────────────────────────────────────────────

HASHTAGS = {
    "rosharon": [
        "#Rosharon", "#RosharonTX", "#SierraVista", "#SterlingLakes",
        "#LockedInWithKareesa", "#HoustonRealEstate", "#288Corridor",
        "#MoveToTexas", "#HoustonRelocation", "#SuburbanHouston",
        "#NewHomeTX", "#KellerWilliams", "#HoustonRealtor",
        "#IowaColonyTX", "#RuralTexas",
    ],
    "iowa_colony": [
        "#IowaColony", "#IowaColonyTX", "#Meridiana", "#MeridianaTX",
        "#LockedInWithKareesa", "#HoustonRealEstate", "#288Corridor",
        "#MasterPlanned", "#NewConstruction", "#AlvinISD",
        "#MoveToTexas", "#HoustonRelocation", "#HoustonRealtor",
        "#KellerWilliams", "#NewHomeTX",
    ],
    "manvel": [
        "#Manvel", "#ManvelTX", "#Pomona", "#ManvelHEB",
        "#LockedInWithKareesa", "#HoustonRealEstate", "#288Corridor",
        "#ManvelGrowth", "#NewConstruction", "#MoveToTexas",
        "#HoustonRelocation", "#HoustonRealtor", "#KellerWilliams",
        "#SuburbanHouston", "#NewHomeTX",
    ],
    "pearland": [
        "#Pearland", "#PearlandTX", "#ShadowCreekRanch",
        "#LockedInWithKareesa", "#HoustonRealEstate",
        "#PearlandRealEstate", "#MoveToTexas", "#HoustonRelocation",
        "#EstablishedNeighborhood", "#HoustonRealtor", "#KellerWilliams",
        "#SuburbanHouston", "#FamilyFriendly", "#PearlandLife", "#NewHomeTX",
    ],
    "market_education": [
        "#LockedInWithKareesa", "#HoustonRealEstate", "#RealEstateTips",
        "#HomeBuyingTips", "#FirstTimeHomeBuyer", "#HoustonRealtor",
        "#TeacherTurnedRealtor", "#RealEstateEducation", "#HomeBuyer101",
        "#KellerWilliams", "#MoveToTexas", "#HoustonRelocation",
        "#288Corridor", "#RealEstate", "#HomeBuyingAdvice",
    ],
    "relocation_guide": [
        "#HoustonRelocation", "#MovingToHouston", "#HoustonRealEstate",
        "#LockedInWithKareesa", "#HoustonRealtor", "#RelocatingToTexas",
        "#HoustonGuide", "#288Corridor", "#KellerWilliams",
        "#MoveToTexas", "#TexasRealEstate", "#RelocationGuide",
        "#HoustonNeighborhoods", "#SuburbanHouston", "#NewHomeTX",
    ],
}


# ── FILMING LOCATION QUICK REFERENCE ────────────────────────────────────────────

FILMING_LOCATIONS = {
    "Rosharon": {
        "anchor_communities": ["Sierra Vista", "Sterling Lakes"],
        "permission_needed": ["Sierra Vista pool/lagoon (ask sales office)"],
        "always_public": ["entrance monuments", "public roads", "county roads FM 1462/CR 56-57"],
        "signature_shots": [
            "Sierra Vista entrance monument",
            "Open land/acreage on county roads — land buying segment backdrop",
            "Contrast shot: new construction rising near open fields",
        ],
        "filming_tips": "Rural side is Kareesa's differentiator — nobody else teaches land buying on camera here",
        "best_time": "First 2 hours after sunrise — Houston July heat starts by 9–10am",
    },
    "Iowa Colony": {
        "anchor_communities": ["Meridiana"],
        "welcome_center": "Oasis Village Welcome Center — ask permission AND introduce yourself as a KW agent",
        "permission_needed": ["Meridiana Adventure Cove amenities (ask Welcome Center)"],
        "always_public": ["entrance monument", "exterior of Conservatory clubhouse", "schools exterior (no students)"],
        "signature_shots": [
            "Meridiana Tower (60-ft sundial) — teacher brand alignment",
            "Entrance monument with waterway landscaping",
            "School cluster drive-by b-roll (summer timing = no students)",
        ],
        "price_verify": "Verify home price range at Welcome Center while on-site before stating on camera",
    },
    "Manvel": {
        "anchor_communities": ["Pomona"],
        "welcome_center": "Pomona Welcome Center — ask permission for Camp Pomona, Fish Camp, The Backyard, Orchard Park",
        "permission_needed": ["Camp Pomona", "Fish Camp", "The Backyard (treehouse/zipline)", "Orchard Park"],
        "always_public": ["Pomona entrance", "H-E-B parking lot (be quick and respectful)", "highway 288 corridor"],
        "signature_shots": [
            "H-E-B exterior — Kareesa actually shops here (authentic growth proof)",
            "Two-part: open H-E-B + surrounding construction (growth arrived + more coming)",
            "288 corridor between Pearland and Iowa Colony",
        ],
        "teacher_line": "Pop quiz: what does a brand-new H-E-B tell you about where a town is heading? Extra credit: it's already MY grocery store.",
    },
    "Pearland": {
        "anchor_communities": ["Shadow Creek Ranch"],
        "all_public": True,
        "signature_shots": [
            "Pearland Town Center open-air mall (morning, before crowds)",
            "Shadow Creek Ranch entrance + lake views (from public streets)",
            "Shadow Creek Ranch Nature Trail — wetlands deck walk-and-talk",
            "PearScape pear sculpture (fun local recognition, drives comments)",
        ],
        "note": "Pearland = no permission issues, all public — most efficient filming day",
    },
}

FILMING_UNIVERSAL_SHOT_LIST = [
    "Community/city monument sign — establishing shot, stand next to it for intro",
    "Slow driving b-roll down main parkway (passenger seat, phone stabilized)",
    "Walking shot toward camera (tripod or ask a friend)",
    "3–5 static beauty shots: lakes, trails, playgrounds, construction, retail",
    "One teacher moment piece-to-camera at a visually interesting backdrop",
    "Vertical 9:16 versions of 3 best shots for Shorts",
]

FILMING_DAY_PROCESS = {
    "night_before": [
        "Re-read that neighborhood's script",
        "Verify all [VERIFY] facts: MLS, community website, quick call to welcome center",
        "Scout route on Google Maps satellite view, drop pins",
        "Charge phone + backup battery, clear 20GB+ storage",
        "Lay out outfit: brand colors (emerald or cream top reads great), no busy patterns",
    ],
    "filming_day": [
        "Leave early — arrive Stop 1 within 2 hours of sunrise",
        "Film INTRO piece-to-camera first while energy and light are best",
        "At each stop: establishing shot → b-roll → piece-to-camera if scripted",
        "Say each on-camera line 3 times",
        "Film vertical 9:16 versions of 3 best moments per stop before leaving",
        "Final stop: film OUTRO/CTA piece-to-camera ('Comment HOUSTON...')",
        "In car after: voice-memo any voiceover lines while visuals are fresh",
    ],
    "same_night": [
        "Dump footage to laptop/cloud",
        "Pick 10 best clips and star them",
        "Stop here — editing is a separate session. Just secure and sort.",
    ],
    "gear": [
        "Phone + gimbal or simple tripod",
        "Wired lapel mic or earbuds mic (improves audio 10x)",
        "Backup battery, water, sunscreen, bug spray (Rosharon + Nature Trail)",
    ],
}

FILMING_CALENDAR_TEMPLATE = {
    "Iowa Colony": "Wed AM",
    "Rosharon": "Sat AM",
    "Manvel": "Next Wed AM",
    "Pearland": "Next Sat AM",
    "verify_days": "Mon/Tue before each filming day",
    "post_rhythm": "Short Monday → Long-form Thursday → one neighborhood per week",
}
