-- Database Optimization Migration for Calk_KMF
-- Created: 2026-06-05
-- Purpose: Add GIN indexes on JSONB columns, enable pg_stat_statements, configure autovacuum

-- Enable query performance tracking extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- GIN indexes on JSONB columns in t_tung_shu_daily
-- These indexes accelerate @>, ?, ?& and other JSONB containment/existence queries

CREATE INDEX IF NOT EXISTS idx_tung_shu_symbolic_stars
    ON t_tung_shu_daily USING GIN (symbolic_stars);

CREATE INDEX IF NOT EXISTS idx_tung_shu_combinations
    ON t_tung_shu_daily USING GIN (combinations);

CREATE INDEX IF NOT EXISTS idx_tung_shu_qi_phases
    ON t_tung_shu_daily USING GIN (qi_phases);

CREATE INDEX IF NOT EXISTS idx_tung_shu_ten_gods
    ON t_tung_shu_daily USING GIN (ten_gods);

CREATE INDEX IF NOT EXISTS idx_tung_shu_hidden_stems
    ON t_tung_shu_daily USING GIN (hidden_stems);

-- Note: belt_stars is TEXT, not JSONB, so no GIN index is created for it.
-- If JSON-like queries are needed on belt_stars, consider migrating it to JSONB
-- or adding a functional expression index after casting.

-- ============================================================================
-- Autovacuum tuning for frequently updated tables
-- ============================================================================
-- t_tung_shu_daily: JSONB columns may cause bloat; vacuum more aggressively
ALTER TABLE t_tung_shu_daily SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.025
);

-- t_bazi_hourly: frequently updated with batch inserts
ALTER TABLE t_bazi_hourly SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.025
);

-- spr_tongshu_shensha_rule: reference table, rarely changes — default is fine
-- spr_tongshu_ten_god: static reference — default is fine
