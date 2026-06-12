-- =============================================================================
-- Скрипт создания критических индексов для Calk_KMF
-- Дата: 2026-05-16
-- Цель: Ускорение запросов к большим таблицам и устранение Full Table Scan
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Индексы на t_analysis_date (14.5M строк)
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_analysis_date_hour_id ON t_analysis_date(hour_id);
CREATE INDEX IF NOT EXISTS idx_analysis_date_rule_id ON t_analysis_date(rule_id);

-- -----------------------------------------------------------------------------
-- 2. Индексы на t_analysis_direction (1.8M строк)
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_analysis_direction_hour_id ON t_analysis_direction(hour_id);
CREATE INDEX IF NOT EXISTS idx_analysis_direction_palace ON t_analysis_direction(palace_no);

-- -----------------------------------------------------------------------------
-- 3. Индексы на Qimen hourly (оптимизация поиска по rasklad_id)
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_qumen_chauby_hourly_rasklad ON t_qumen_chauby_hourly(rasklad_id);
CREATE INDEX IF NOT EXISTS idx_qumen_dgiren_hourly_rasklad ON t_qumen_dgiren_hourly(rasklad_id);

-- -----------------------------------------------------------------------------
-- 4. Индексы на Qimen day/month/year
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_qumen_chauby_day_rasklad ON t_qumen_chauby_day(rasklad_id);
CREATE INDEX IF NOT EXISTS idx_qumen_dgiren_day_rasklad ON t_qumen_dgiren_day(rasklad_id);
CREATE INDEX IF NOT EXISTS idx_qumen_chauby_month_rasklad ON t_qumen_chauby_month(rasklad_id);
CREATE INDEX IF NOT EXISTS idx_qumen_dgiren_month_rasklad ON t_qumen_dgiren_month(rasklad_id);
CREATE INDEX IF NOT EXISTS idx_qumen_chauby_year_rasklad ON t_qumen_chauby_year(rasklad_id);
CREATE INDEX IF NOT EXISTS idx_qumen_dgiren_year_rasklad ON t_qumen_dgiren_year(rasklad_id);

-- -----------------------------------------------------------------------------
-- 5. Индексы на t_bazi_hourly для частых фильтров (если отсутствуют)
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_bazi_hourly_date ON t_bazi_hourly(date);
CREATE INDEX IF NOT EXISTS idx_bazi_hourly_day_stem ON t_bazi_hourly(day_stem);
CREATE INDEX IF NOT EXISTS idx_bazi_hourly_hour_stem ON t_bazi_hourly(hour_stem);

-- -----------------------------------------------------------------------------
-- 6. Анализ таблиц после создания индексов
-- -----------------------------------------------------------------------------
ANALYZE t_analysis_date;
ANALYZE t_analysis_direction;
ANALYZE t_qumen_chauby_hourly;
ANALYZE t_qumen_dgiren_hourly;
