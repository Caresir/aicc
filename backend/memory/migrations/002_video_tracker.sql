-- AICC Migration 002 — Video Production Tracker
-- Tracks real estate neighborhood videos and GymnastDiva content through the full pipeline

CREATE TABLE IF NOT EXISTS video_tracker (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category TEXT DEFAULT 're' CHECK (category IN ('re', 'gymnastics')),
    title TEXT NOT NULL,
    neighborhood TEXT,
    topic TEXT,
    film_status TEXT DEFAULT 'not_filmed' CHECK (film_status IN ('not_filmed', 'filmed')),
    edit_status TEXT DEFAULT 'raw' CHECK (edit_status IN ('raw', 'edited', 'approved')),
    platforms TEXT[] DEFAULT ARRAY['instagram', 'tiktok'],
    caption_status TEXT DEFAULT 'draft' CHECK (caption_status IN ('draft', 'approved', 'posted')),
    scheduled_for DATE,
    posted_at DATE,
    ig_likes INTEGER DEFAULT 0,
    ig_comments INTEGER DEFAULT 0,
    ig_shares INTEGER DEFAULT 0,
    ig_saves INTEGER DEFAULT 0,
    tiktok_views INTEGER DEFAULT 0,
    tiktok_likes INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed the 4 real estate neighborhood videos
INSERT INTO video_tracker (category, title, neighborhood, topic, film_status, edit_status, notes) VALUES
    ('re', 'Meridian Community Tour', 'Meridian', 'Master-planned community, Manvel TX — Alvin ISD, resort amenities, $360k–$600k+', 'filmed', 'raw', 'Filmed. Needs editing and caption.'),
    ('re', 'Pomona Community Tour', 'Pomona', 'Master-planned community, Manvel TX — nature-inspired, Alvin ISD, $327k–$1.5M', 'filmed', 'raw', 'Filmed. Needs editing and caption.'),
    ('re', 'Rosharon Sierra Vista Tour', 'Rosharon - Sierra Vista', 'Where Kareesa lives — resident POV, personal angle, authentic community feel', 'not_filmed', 'raw', 'Kareesa lives here. Lead with that.'),
    ('re', 'Iowa Colony Community Tour', 'Iowa Colony', 'Affordable new construction south of Houston — first-time buyers, growing area', 'not_filmed', 'raw', 'Highlight affordability and new builds.')
ON CONFLICT DO NOTHING;

CREATE INDEX IF NOT EXISTS idx_video_tracker_status ON video_tracker(film_status, edit_status, caption_status);
CREATE INDEX IF NOT EXISTS idx_video_tracker_category ON video_tracker(category, created_at);

CREATE TRIGGER trg_video_tracker_updated_at
    BEFORE UPDATE ON video_tracker
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
