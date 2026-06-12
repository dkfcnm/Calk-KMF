-- DDL: Все views проекта Calk_KMF
-- Экспортировано: 2026-02-23
-- Количество views: 35

-- ============================================
-- VIEW: v_bazi_hourly
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly AS
 SELECT t.hour_id,
    t.tz_offset_hours,
    t.slot_start_date_utc,
    t.slot_start_time_utc,
    t.slot_end_date_utc,
    t.slot_end_time_utc,
    t.slot_start_date_local,
    t.slot_start_time_local,
    t.slot_end_date_local,
    t.slot_end_time_local,
    t.weekday_local,
    t.solar_term_id,
    st.solar_term_name_ru,
    t.year_pillar,
    t.month_pillar,
    t.day_pillar,
    t.hour_pillar,
    t.year_stem,
    t.year_branch,
    t.month_stem,
    t.month_branch,
    t.day_stem,
    t.day_branch,
    t.hour_stem,
    t.hour_branch AS hour_branch_char,
    t.lunar_month,
    t.lunar_day,
    t.lunar_is_leap,
    t.lunar_month_zi,
    t.lunar_day_zi,
    t.lunar_is_leap_zi,
    eb.branch_rus AS hour_name_ru
   FROM t_bazi_hourly t
     LEFT JOIN spr_solar_term st ON st.solar_term_id = t.solar_term_id
     LEFT JOIN spr_earthly_branch eb ON eb.branch_char = t.hour_branch
  ORDER BY t.tz_offset_hours, t.slot_start_date_utc, t.slot_start_time_utc;


-- ============================================
-- VIEW: v_bazi_hourly_analiz
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_analiz AS
 WITH per AS (
         SELECT v_bazi_hourly_msk.hour_id,
            v_bazi_hourly_msk.start_date_time_utc,
            v_bazi_hourly_msk.end_date_time_utc,
            v_bazi_hourly_msk.start_date_time_local,
            v_bazi_hourly_msk.end_date_time_local,
            v_bazi_hourly_msk.weekday_msk,
            v_bazi_hourly_msk.hour_name_ru,
            v_bazi_hourly_msk.hour_branch_char,
            v_bazi_hourly_msk.solar_term_id,
            v_bazi_hourly_msk.solar_term_name_ru,
            v_bazi_hourly_msk.year_pillar,
            v_bazi_hourly_msk.month_pillar,
            v_bazi_hourly_msk.day_pillar,
            v_bazi_hourly_msk.hour_pillar,
            v_bazi_hourly_msk.year_stem,
            v_bazi_hourly_msk.year_branch,
            v_bazi_hourly_msk.month_stem,
            v_bazi_hourly_msk.month_branch,
            v_bazi_hourly_msk.day_stem,
            v_bazi_hourly_msk.day_branch,
            v_bazi_hourly_msk.hour_stem,
            v_bazi_hourly_msk.hour_branch,
            v_bazi_hourly_msk.lunar_month,
            v_bazi_hourly_msk.lunar_day,
            v_bazi_hourly_msk.lunar_is_leap,
            v_bazi_hourly_msk.lunar_month_zi,
            v_bazi_hourly_msk.lunar_day_zi,
            v_bazi_hourly_msk.lunar_is_leap_zi
           FROM v_bazi_hourly_msk
          WHERE 1 = 1 AND v_bazi_hourly_msk.start_date_time_local::date >= CURRENT_DATE AND v_bazi_hourly_msk.start_date_time_local::date <= (CURRENT_DATE + '5 days'::interval)
        ), per_year AS (
         SELECT DISTINCT per.year_pillar
           FROM per
        ), per_mnth AS (
         SELECT DISTINCT per.year_pillar,
            per.month_pillar
           FROM per
        ), per_day AS (
         SELECT DISTINCT per.year_pillar,
            per.month_pillar,
            per.day_pillar
           FROM per
        ), per_hr AS (
         SELECT DISTINCT per.year_pillar,
            per.month_pillar,
            per.day_pillar,
            per.hour_pillar
           FROM per
        ), per_analiz AS (
         SELECT 'Год'::text AS level,
            y.year_pillar,
            NULL::text AS month_pillar,
            NULL::text AS day_pillar,
            NULL::text AS hour_pillar,
            y.rule_id,
            y.result_value,
            y.score
           FROM t_analysis_year y
             JOIN per_year ON y.year_pillar = per_year.year_pillar
        UNION ALL
         SELECT 'Месяц'::text AS text,
            m.year_pillar,
            m.month_pillar,
            NULL::text,
            NULL::text,
            m.rule_id,
            m.result_value,
            m.score
           FROM t_analysis_month m
             JOIN per_mnth ON m.year_pillar = per_mnth.year_pillar AND m.month_pillar = per_mnth.month_pillar
        UNION ALL
         SELECT 'День'::text AS text,
            d.year_pillar,
            d.month_pillar,
            d.day_pillar,
            NULL::text,
            d.rule_id,
            d.result_value,
            d.score
           FROM t_analysis_day d
             JOIN per_day ON d.year_pillar = per_day.year_pillar AND d.month_pillar = per_day.month_pillar AND d.day_pillar = per_day.day_pillar
        UNION ALL
         SELECT DISTINCT 'Час'::text AS text,
            h.year_pillar,
            h.month_pillar,
            h.day_pillar,
            h.hour_pillar,
            h.rule_id,
            h.result_value,
            h.score
           FROM t_analysis_hour h
             JOIN per_hr ON h.year_pillar = per_hr.year_pillar AND h.month_pillar = per_hr.month_pillar AND h.day_pillar = per_hr.day_pillar AND h.hour_pillar = per_hr.hour_pillar
        )
 SELECT vh.level,
    vh.year_pillar,
    vh.month_pillar,
    vh.day_pillar,
    vh.hour_pillar,
    vh.rule_id,
    vh.result_value,
    vh.score,
    reg.name_ru AS rule_nm,
    reg.description AS rule_description,
    reg.params_json AS rule_params,
    ((((vh.level || vh.year_pillar) || COALESCE(vh.month_pillar, ''::text)) || COALESCE(vh.day_pillar, ''::text)) || COALESCE(vh.hour_pillar, ''::text)) || COALESCE(vh.rule_id, ''::text) AS id
   FROM per_analiz vh
     LEFT JOIN t_rule_registry reg ON vh.rule_id = reg.rule_id;

COMMENT ON VIEW v_bazi_hourly_analiz IS 'Аналитический view: все уровни анализа (год/месяц/день/час) для ближайших 5 дней от текущей даты (МСК)';

-- ============================================
-- VIEW: v_bazi_hourly_msk
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_msk AS
 SELECT hour_id,
    (((slot_start_date_utc || ' '::text) || slot_start_time_utc) || '+00'::text)::timestamp with time zone AS start_date_time_utc,
    (((slot_end_date_utc || ' '::text) || slot_end_time_utc) || '+00'::text)::timestamp with time zone AS end_date_time_utc,
    (((slot_start_date_local || ' '::text) || slot_start_time_local) || '+03'::text)::timestamp with time zone AS start_date_time_local,
    (((slot_end_date_local || ' '::text) || slot_end_time_local) || '+03'::text)::timestamp with time zone AS end_date_time_local,
    weekday_local AS weekday_msk,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly_tz_p03 tz
  WHERE 1 = 1 AND slot_start_date_utc::date >= CURRENT_DATE
  ORDER BY slot_start_date_local, slot_start_time_local;

COMMENT ON VIEW v_bazi_hourly_msk IS 'Часовые данные Бацзы для Москвы (UTC+3). Даты/время как timestamp с часовым поясом. Фильтр: от текущей даты.';
COMMENT ON COLUMN v_bazi_hourly_msk.start_date_time_utc IS 'Начало слота UTC (timestamptz UTC+0)';
COMMENT ON COLUMN v_bazi_hourly_msk.end_date_time_utc IS 'Конец слота UTC (timestamptz UTC+0)';
COMMENT ON COLUMN v_bazi_hourly_msk.start_date_time_local IS 'Начало слота МСК (timestamptz UTC+3)';
COMMENT ON COLUMN v_bazi_hourly_msk.end_date_time_local IS 'Конец слота МСК (timestamptz UTC+3)';
COMMENT ON COLUMN v_bazi_hourly_msk.weekday_msk IS 'День недели (МСК)';
COMMENT ON COLUMN v_bazi_hourly_msk.hour_name_ru IS 'Название часа (рус.)';
COMMENT ON COLUMN v_bazi_hourly_msk.hour_branch_char IS 'Земная Ветвь часа (символ)';
COMMENT ON COLUMN v_bazi_hourly_msk.year_pillar IS 'Столп года';
COMMENT ON COLUMN v_bazi_hourly_msk.month_pillar IS 'Столп месяца';
COMMENT ON COLUMN v_bazi_hourly_msk.day_pillar IS 'Столп дня';
COMMENT ON COLUMN v_bazi_hourly_msk.hour_pillar IS 'Столп часа';

-- ============================================
-- VIEW: v_bazi_hourly_tz_m01
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_m01 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = '-1'::integer
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_m02
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_m02 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = '-2'::integer
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_m03
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_m03 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = '-3'::integer
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_m04
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_m04 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = '-4'::integer
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_m05
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_m05 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = '-5'::integer
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_m06
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_m06 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = '-6'::integer
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_m07
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_m07 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = '-7'::integer
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_m08
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_m08 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = '-8'::integer
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_m09
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_m09 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = '-9'::integer
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_m10
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_m10 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = '-10'::integer
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_m11
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_m11 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = '-11'::integer
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_m12
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_m12 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = '-12'::integer
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_p00
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_p00 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = 0
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_p01
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_p01 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = 1
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_p02
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_p02 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = 2
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_p03
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_p03 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = 3
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_p04
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_p04 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = 4
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_p05
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_p05 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = 5
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_p06
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_p06 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = 6
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_p07
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_p07 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = 7
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_p08
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_p08 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = 8
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_p09
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_p09 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = 9
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_p10
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_p10 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = 10
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_p11
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_p11 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = 11
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_p12
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_p12 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = 12
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_p13
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_p13 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = 13
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_bazi_hourly_tz_p14
-- ============================================
CREATE OR REPLACE VIEW v_bazi_hourly_tz_p14 AS
 SELECT hour_id,
    slot_start_date_local,
    slot_start_time_local,
    slot_end_date_local,
    slot_end_time_local,
    slot_start_date_utc,
    slot_start_time_utc,
    slot_end_date_utc,
    slot_end_time_utc,
    weekday_local,
    hour_name_ru,
    hour_branch_char,
    solar_term_id,
    solar_term_name_ru,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    year_stem,
    year_branch,
    month_stem,
    month_branch,
    day_stem,
    day_branch,
    hour_stem,
    hour_branch_char AS hour_branch,
    lunar_month,
    lunar_day,
    lunar_is_leap,
    lunar_month_zi,
    lunar_day_zi,
    lunar_is_leap_zi
   FROM v_bazi_hourly v
  WHERE tz_offset_hours = 14
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_good_sequence_gate
-- ============================================
CREATE OR REPLACE VIEW v_good_sequence_gate AS
 WITH y AS (
         SELECT q_y.year_pillar,
            q_y.palace_no,
            q_y.gate,
            q_y.is_main_gate,
            q_y.star,
            q_y.is_main_star,
            q_y.spirit,
            q_y.structure,
            q_y.is_fou_tou_heaven,
            q_y.is_fou_tou_earth
           FROM v_qumen_chauby_year q_y
          WHERE 1 = 1 AND (q_y.gate = ANY (ARRAY['生'::text, '休'::text, '開'::text]))
        ), m AS (
         SELECT q_m.year_pillar,
            q_m.month_pillar,
            q_m.palace_no,
            q_m.gate,
            q_m.is_main_gate,
            q_m.star,
            q_m.is_main_star,
            q_m.spirit,
            q_m.structure,
            q_m.is_fou_tou_heaven,
            q_m.is_fou_tou_earth
           FROM v_qumen_chauby_month q_m
          WHERE 1 = 1 AND (q_m.gate = ANY (ARRAY['生'::text, '休'::text, '開'::text]))
        ), d AS (
         SELECT q_d.year_pillar,
            q_d.month_pillar,
            q_d.day_pillar,
            q_d.palace_no,
            q_d.gate,
            q_d.is_main_gate,
            q_d.star,
            q_d.is_main_star,
            q_d.spirit,
            q_d.structure,
            q_d.is_fou_tou_heaven,
            q_d.is_fou_tou_earth
           FROM v_qumen_chauby_day q_d
          WHERE 1 = 1 AND (q_d.gate = ANY (ARRAY['生'::text, '休'::text, '開'::text]))
        ), h AS (
         SELECT q_h.slot_start_date_local,
            q_h.slot_start_time_local,
            q_h.tz_offset_hours,
            q_h.weekday_local,
            q_h.year_pillar,
            q_h.month_pillar,
            q_h.day_pillar,
            q_h.hour_pillar,
            q_h.palace_no,
            q_h.gate,
            q_h.is_main_gate,
            q_h.star,
            q_h.is_main_star,
            q_h.spirit,
            q_h.structure,
            q_h.is_fou_tou_heaven,
            q_h.is_fou_tou_earth
           FROM v_qumen_chauby_hourly q_h
          WHERE 1 = 1 AND (q_h.gate = ANY (ARRAY['生'::text, '休'::text, '開'::text]))
        ), st_1 AS (
         SELECT h.slot_start_date_local,
            h.slot_start_time_local,
            h.weekday_local,
            h.year_pillar,
            h.month_pillar,
            h.day_pillar,
            h.hour_pillar,
            h.palace_no,
            h.gate AS hour_gate,
            d.gate AS day_gate,
            m.gate AS month_gate,
            y.gate AS year_gate,
                CASE
                    WHEN (h.palace_no = ANY (ARRAY[2, 4])) AND y.gate = m.gate AND m.gate = d.gate AND d.gate = h.gate THEN 1
                    WHEN m.gate = d.gate AND d.gate = h.gate THEN 2
                    WHEN ((m.gate || d.gate) || h.gate) = ANY (ARRAY['生開休'::text, '生生開'::text, '生開開'::text, '開開休'::text, '開休休'::text]) THEN 3
                    ELSE 0
                END AS prioritet
           FROM h
             LEFT JOIN d ON h.year_pillar = d.year_pillar AND h.month_pillar = d.month_pillar AND h.day_pillar = d.day_pillar AND h.palace_no = d.palace_no
             LEFT JOIN m ON h.year_pillar = m.year_pillar AND h.month_pillar = m.month_pillar AND h.palace_no = m.palace_no
             LEFT JOIN y ON h.year_pillar = y.year_pillar AND h.palace_no = y.palace_no
          WHERE 1 = 1 AND h.tz_offset_hours = 3 AND d.gate IS NOT NULL
        )
 SELECT slot_start_date_local,
    slot_start_time_local,
    weekday_local,
    year_pillar,
    month_pillar,
    day_pillar,
    hour_pillar,
    palace_no,
    hour_gate,
    day_gate,
    month_gate,
    year_gate,
    prioritet
   FROM st_1
  WHERE 1 = 1 AND month_gate IS NOT NULL AND day_gate IS NOT NULL AND hour_gate IS NOT NULL AND (slot_start_time_local <> ALL (ARRAY['03:00'::text, '21:00'::text, '19:00'::text]))
  ORDER BY slot_start_date_local, slot_start_time_local;


-- ============================================
-- VIEW: v_qumen_chauby_day
-- ============================================
CREATE OR REPLACE VIEW v_qumen_chauby_day AS
 SELECT vh.year_pillar,
    vh.month_pillar,
    vh.day_pillar,
    vh.palace_no,
    spr.gate,
    spr.is_main_gate,
    spr.star,
    spr.is_main_star,
    spr.spirit,
    spr.structure,
    spr.is_fou_tou_heaven,
    spr.is_fou_tou_earth
   FROM t_qumen_chauby_day vh
     LEFT JOIN spr_qimen_templates spr ON vh.rasklad_id = spr.rasklad_id AND vh.palace_no = spr.palace_no;


-- ============================================
-- VIEW: v_qumen_chauby_hourly
-- ============================================
CREATE OR REPLACE VIEW v_qumen_chauby_hourly AS
 SELECT b.slot_start_date_local,
    b.slot_start_time_local,
    b.tz_offset_hours,
    b.weekday_local,
    b.year_pillar,
    b.month_pillar,
    b.day_pillar,
    b.hour_pillar,
    vh.palace_no,
    spr.gate,
    spr.is_main_gate,
    spr.star,
    spr.is_main_star,
    spr.spirit,
    spr.structure,
    spr.is_fou_tou_heaven,
    spr.is_fou_tou_earth
   FROM t_qumen_chauby_hourly vh
     JOIN v_bazi_hourly b ON vh.hour_id = b.hour_id
     LEFT JOIN spr_qimen_templates spr ON vh.rasklad_id = spr.rasklad_id AND vh.palace_no = spr.palace_no
  WHERE 1 = 1 AND b.slot_start_date_local::date >= CURRENT_DATE;


-- ============================================
-- VIEW: v_qumen_chauby_month
-- ============================================
CREATE OR REPLACE VIEW v_qumen_chauby_month AS
 SELECT vh.year_pillar,
    vh.month_pillar,
    vh.palace_no,
    spr.gate,
    spr.is_main_gate,
    spr.star,
    spr.is_main_star,
    spr.spirit,
    spr.structure,
    spr.is_fou_tou_heaven,
    spr.is_fou_tou_earth
   FROM t_qumen_chauby_month vh
     LEFT JOIN spr_qimen_templates spr ON vh.rasklad_id = spr.rasklad_id AND vh.palace_no = spr.palace_no;


-- ============================================
-- VIEW: v_qumen_chauby_year
-- ============================================
CREATE OR REPLACE VIEW v_qumen_chauby_year AS
 SELECT vh.year_pillar,
    vh.palace_no,
    spr.gate,
    spr.is_main_gate,
    spr.star,
    spr.is_main_star,
    spr.spirit,
    spr.structure,
    spr.is_fou_tou_heaven,
    spr.is_fou_tou_earth
   FROM t_qumen_chauby_year vh
     LEFT JOIN spr_qimen_templates spr ON vh.rasklad_id = spr.rasklad_id AND vh.palace_no = spr.palace_no;

