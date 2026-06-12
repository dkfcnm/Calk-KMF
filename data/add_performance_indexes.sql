-- Performance indexes for Calk_KMF
-- Run: psql -h 127.0.0.1 -U postgres -d calk_kmf -f data/add_performance_indexes.sql

-- t_bazi_hourly: year_int filter used in all process_*_level() functions
CREATE INDEX IF NOT EXISTS idx_bazi_hourly_year_int ON t_bazi_hourly(year_int);

-- spr_tongshu_shensha_rule: lookup by (master_scope, master_value)
CREATE INDEX IF NOT EXISTS idx_shensha_lookup ON spr_tongshu_shensha_rule(master_scope, master_value);

-- spr_tongshu_stem_combo_rule: lookup by (item1, item2)
CREATE INDEX IF NOT EXISTS idx_stem_combo_items ON spr_tongshu_stem_combo_rule(item1, item2);

-- spr_tongshu_branch_combo_rule: lookup by (item1, item2, item3)
CREATE INDEX IF NOT EXISTS idx_branch_combo_items ON spr_tongshu_branch_combo_rule(item1, item2, item3);

-- spr_tongshu_ten_god: lookup by (day_stem, related_stem) — different from PK
CREATE INDEX IF NOT EXISTS idx_ten_god_lookup ON spr_tongshu_ten_god(day_stem, related_stem);

-- t_crm_client: trigram index for ILIKE searches
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS idx_crm_client_name_trgm ON t_crm_client USING gin (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_crm_client_email_trgm ON t_crm_client USING gin (email gin_trgm_ops);

ANALYZE;
