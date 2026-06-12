-- Phase 2: Personalization — Schema Changes
-- 2026-05-31

-- 1. City timezone reference (for 2.2)
CREATE TABLE IF NOT EXISTS spr_city_timezone (
    city_id SERIAL PRIMARY KEY,
    city_name_ru VARCHAR(100) NOT NULL,
    city_name_en VARCHAR(100),
    country_ru VARCHAR(100),
    lat NUMERIC(10, 6),
    lon NUMERIC(10, 6),
    timezone VARCHAR(50),
    utc_offset INTEGER, -- offset in minutes from UTC
    region VARCHAR(100),
    population INTEGER,
    UNIQUE(city_name_ru, region)
);

CREATE INDEX IF NOT EXISTS idx_city_name_ru ON spr_city_timezone(city_name_ru);
CREATE INDEX IF NOT EXISTS idx_city_name_en ON spr_city_timezone(city_name_en);

-- 2. Hidden Stems reference (for 2.5)
CREATE TABLE IF NOT EXISTS spr_hidden_stems (
    id SERIAL PRIMARY KEY,
    branch_id INTEGER NOT NULL REFERENCES spr_earthly_branch(branch_id),
    branch_char VARCHAR(10) NOT NULL,
    stem_id INTEGER NOT NULL REFERENCES spr_heavenly_stem(stem_id),
    stem_char VARCHAR(10) NOT NULL,
    position INTEGER NOT NULL DEFAULT 1, -- 1, 2, 3
    is_main BOOLEAN NOT NULL DEFAULT FALSE,
    percentage NUMERIC(5, 2) DEFAULT 0, -- approximate strength percentage
    UNIQUE(branch_id, stem_id, position)
);

CREATE INDEX IF NOT EXISTS idx_hidden_stems_branch ON spr_hidden_stems(branch_id);

-- 3. Extend t_tung_shu_daily with personalization fields
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 't_tung_shu_daily' AND column_name = 'symbolic_stars') THEN
        ALTER TABLE t_tung_shu_daily ADD COLUMN symbolic_stars JSONB;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 't_tung_shu_daily' AND column_name = 'combinations') THEN
        ALTER TABLE t_tung_shu_daily ADD COLUMN combinations JSONB;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 't_tung_shu_daily' AND column_name = 'qi_phases') THEN
        ALTER TABLE t_tung_shu_daily ADD COLUMN qi_phases JSONB;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 't_tung_shu_daily' AND column_name = 'ten_gods') THEN
        ALTER TABLE t_tung_shu_daily ADD COLUMN ten_gods JSONB;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 't_tung_shu_daily' AND column_name = 'hidden_stems') THEN
        ALTER TABLE t_tung_shu_daily ADD COLUMN hidden_stems JSONB;
    END IF;
END $$;

-- 4. Extend t_profile_birth_chart (for 2.3)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 't_profile_birth_chart' AND column_name = 'year_stem') THEN
        ALTER TABLE t_profile_birth_chart ADD COLUMN year_stem VARCHAR(10);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 't_profile_birth_chart' AND column_name = 'year_branch') THEN
        ALTER TABLE t_profile_birth_chart ADD COLUMN year_branch VARCHAR(10);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 't_profile_birth_chart' AND column_name = 'month_stem') THEN
        ALTER TABLE t_profile_birth_chart ADD COLUMN month_stem VARCHAR(10);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 't_profile_birth_chart' AND column_name = 'month_branch') THEN
        ALTER TABLE t_profile_birth_chart ADD COLUMN month_branch VARCHAR(10);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 't_profile_birth_chart' AND column_name = 'day_stem') THEN
        ALTER TABLE t_profile_birth_chart ADD COLUMN day_stem VARCHAR(10);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 't_profile_birth_chart' AND column_name = 'day_branch') THEN
        ALTER TABLE t_profile_birth_chart ADD COLUMN day_branch VARCHAR(10);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 't_profile_birth_chart' AND column_name = 'hour_stem') THEN
        ALTER TABLE t_profile_birth_chart ADD COLUMN hour_stem VARCHAR(10);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 't_profile_birth_chart' AND column_name = 'hour_branch') THEN
        ALTER TABLE t_profile_birth_chart ADD COLUMN hour_branch VARCHAR(10);
    END IF;
END $$;
