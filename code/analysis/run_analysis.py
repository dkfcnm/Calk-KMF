import time
import os
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ensure imports work
sys.path.insert(0, os.getcwd())

from code.analysis.engine import RuleEngine
from code.common.db_manager import db
from code.bazi_calendar.db import get_placeholder

def vacuum_db():
    """Performs database maintenance."""
    # PostgreSQL autovacuum handles most things, but we can run explicit ANALYZE
    print("Running Database Maintenance (ANALYZE)...")
    try:
        # VACUUM cannot run inside transaction block. DBManager uses transaction by default.
        # Check if we can run it. For now, just ANALYZE or skip.
        # db.execute_query("ANALYZE") 
        print("Maintenance skipped (handled by autovacuum).")
    except Exception as e:
        print(f"Maintenance failed: {e}")

def ensure_analysis_tables():
    """Creates hierarchical analysis tables if they do not exist."""
    
    tables = {
        "t_analysis_year": """
            CREATE TABLE IF NOT EXISTS t_analysis_year (
                year INTEGER,
                year_pillar TEXT,
                rule_id TEXT,
                result_value TEXT,
                score DOUBLE PRECISION,
                PRIMARY KEY (year, rule_id, result_value, year_pillar)
            )
        """,
        "t_analysis_month": """
            CREATE TABLE IF NOT EXISTS t_analysis_month (
                year INTEGER,
                month INTEGER,
                year_pillar TEXT,
                month_pillar TEXT,
                rule_id TEXT,
                result_value TEXT,
                score DOUBLE PRECISION,
                PRIMARY KEY (year, month, rule_id, result_value, year_pillar, month_pillar)
            )
        """,
        "t_analysis_day": """
            CREATE TABLE IF NOT EXISTS t_analysis_day (
                date_val DATE,
                year_pillar TEXT,
                month_pillar TEXT,
                day_pillar TEXT,
                rule_id TEXT,
                result_value TEXT,
                score DOUBLE PRECISION,
                PRIMARY KEY (date_val, rule_id, result_value, year_pillar, month_pillar, day_pillar)
            )
        """,
        "t_analysis_hour": """
            CREATE TABLE IF NOT EXISTS t_analysis_hour (
                hour_id TEXT,
                year_pillar TEXT,
                month_pillar TEXT,
                day_pillar TEXT,
                hour_pillar TEXT,
                rule_id TEXT,
                result_value TEXT,
                score DOUBLE PRECISION,
                PRIMARY KEY (hour_id, rule_id)
            )
        """,
        "t_analysis_direction_year": """
            CREATE TABLE IF NOT EXISTS t_analysis_direction_year (
                year INTEGER,
                year_pillar TEXT,
                palace_no INTEGER,
                system_type TEXT,
                rule_id TEXT,
                result_value TEXT,
                score DOUBLE PRECISION,
                PRIMARY KEY (year, palace_no, system_type, rule_id, year_pillar)
            )
        """,
        "t_analysis_direction_month": """
            CREATE TABLE IF NOT EXISTS t_analysis_direction_month (
                year INTEGER,
                month INTEGER,
                year_pillar TEXT,
                month_pillar TEXT,
                palace_no INTEGER,
                system_type TEXT,
                rule_id TEXT,
                result_value TEXT,
                score DOUBLE PRECISION,
                PRIMARY KEY (year, month, palace_no, system_type, rule_id, year_pillar, month_pillar)
            )
        """,
        "t_analysis_direction_day": """
            CREATE TABLE IF NOT EXISTS t_analysis_direction_day (
                date_val DATE,
                year_pillar TEXT,
                month_pillar TEXT,
                day_pillar TEXT,
                palace_no INTEGER,
                system_type TEXT,
                rule_id TEXT,
                result_value TEXT,
                score DOUBLE PRECISION,
                PRIMARY KEY (date_val, palace_no, system_type, rule_id, year_pillar, month_pillar, day_pillar)
            )
        """,
        "t_analysis_direction_hour": """
            CREATE TABLE IF NOT EXISTS t_analysis_direction_hour (
                hour_id TEXT,
                year_pillar TEXT,
                month_pillar TEXT,
                day_pillar TEXT,
                hour_pillar TEXT,
                palace_no INTEGER,
                system_type TEXT,
                rule_id TEXT,
                result_value TEXT,
                score DOUBLE PRECISION,
                PRIMARY KEY (hour_id, palace_no, system_type, rule_id)
            )
        """
    }
    
    for tbl, ddl in tables.items():
        db.execute_query(ddl)

def create_analysis_indexes():
    """Indexes are now defined in schema (setup_db.py). This function is kept for compatibility."""
    pass

def run_analysis(logger=None, target_year=None, max_workers=1):
    print("Starting Optimized Hierarchical Analysis Cycle (PostgreSQL)...")
    start_time = time.time()
    
    log_id = None
    if logger:
        log_id = logger.start_stage("Analysis Cycle")
    
    # 1. Init Engine
    engine = RuleEngine() 
    print(f"Loaded {len(engine.rules_generic) + len(engine.rules_by_stem)} rules/groups.")
    
    # Ensure Tables & Indexes
    ensure_analysis_tables()
    create_analysis_indexes()
    
    # 2. Clean results
    # Only truncate if we are running full analysis (no target year)
    # If target_year is set, we delete only for that year (handled in processing or separate delete)
    if target_year is None:
        print("Cleaning old results (TRUNCATE ALL)...")
        tables = [
            "t_analysis_year", "t_analysis_month", "t_analysis_day", 
            "t_analysis_hour", 
            "t_analysis_direction_year", "t_analysis_direction_month", 
            "t_analysis_direction_day", "t_analysis_direction_hour"
        ]
        for tbl in tables:
            db.execute_query(f"TRUNCATE TABLE {tbl}")
    else:
        print(f"Cleaning results for year {target_year}...")
        # Note: Delete logic for specific year is more complex due to dependencies, 
        # but for now we rely on ON CONFLICT UPDATE/DO NOTHING or explicit delete.
        # Ideally, we should delete.
        db.execute_query("DELETE FROM t_analysis_year WHERE year = %s", [int(target_year)])
        db.execute_query("DELETE FROM t_analysis_month WHERE year = %s", [int(target_year)])
        db.execute_query("DELETE FROM t_analysis_direction_year WHERE year = %s", [int(target_year)])
        db.execute_query("DELETE FROM t_analysis_direction_month WHERE year = %s", [int(target_year)])
        
        # For Day/Hour/Direction Day/Hour
        # Simplified: We just proceed with UPSERT/INSERT IGNORE logic which is already in place (ON CONFLICT DO NOTHING/UPDATE)
        # However, to be clean, we should delete. 
        # For Day:
        db.execute_query("DELETE FROM t_analysis_day WHERE extract(year from date_val) = %s", [int(target_year)])
        db.execute_query("DELETE FROM t_analysis_direction_day WHERE extract(year from date_val) = %s", [int(target_year)])
        
        # For Hour tables: удаляем через связь с t_bazi_hourly по hour_id
        db.execute_query("""
            DELETE FROM t_analysis_hour WHERE hour_id IN (
                SELECT hour_id FROM t_bazi_hourly WHERE year_int = %s
            )
        """, [int(target_year)])
        db.execute_query("""
            DELETE FROM t_analysis_direction_hour WHERE hour_id IN (
                SELECT hour_id FROM t_bazi_hourly WHERE year_int = %s
            )
        """, [int(target_year)])
    
    # Get Years
    if target_year:
        years = [str(target_year)]
    else:
        print("Fetching years for batch processing...")
        years_res = db.fetch_all("SELECT DISTINCT year_int FROM t_bazi_hourly ORDER BY 1")
        years = [str(r[0]) for r in years_res if r[0] is not None]
    
    print(f"Found years: {years}")

    if max_workers == 1 or len(years) == 1:
        # Sequential mode (fallback for debugging or single year)
        for year in years:
            process_year_batch(year)
    else:
        # Parallel mode: one thread per year (I/O-bound, PostgreSQL handles CPU)
        print(f"Running parallel analysis with {max_workers} workers...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_year_batch, year): year for year in years}
            for future in as_completed(futures):
                year = futures[future]
                try:
                    future.result()
                    print(f"  Year {year} completed successfully.")
                except Exception as e:
                    print(f"  ERROR: Year {year} failed: {e}")
                    import traceback
                    traceback.print_exc()

    duration = time.time() - start_time
    print(f"Hierarchical Analysis completed in {duration:.2f} seconds.")
    
    if logger and log_id:
        logger.end_stage(log_id, record_count=0)

def process_year_batch(year):
    """Executes hierarchical analysis for a specific year."""
    print(f"\n>>> Processing Batch: Year {year}...")
    try:
        process_year_level(year)
        process_month_level(year)
        process_day_level(year)
        process_hour_level(year)
        process_skdg_hour_level(year)
        process_skdg_day_level(year)
        process_direction_level(year)
    except Exception as e:
        print(f"ERROR processing year {year}: {e}")
        import traceback
        traceback.print_exc()
        raise

def process_year_level(year):
    print(f"  > Year Level Analysis [{year}]...")
    
    # 1. Nayin & Da Gua (Year) & Qi Phase (Year)
    # We select distinct years from bazi_hourly. 
    # Logic: simple distinct year columns.
    sql = """
    INSERT INTO t_analysis_year (year, year_pillar, rule_id, result_value, score)
    SELECT DISTINCT
        CAST(substring(h.slot_start_date_local, 1, 4) AS INTEGER),
        h.year_pillar,
        r.rule_id,
        CASE 
            WHEN r.predicate_code = 'CHECK_NAYIN_YEAR_EL' THEN j.nayin_element
            WHEN r.predicate_code = 'CHECK_NAYIN_YEAR_NM' THEN j.nayin_name
            WHEN r.predicate_code = 'CHECK_DAGUA_YEAR_EL' THEN CAST(j.dagua_element AS TEXT)
            WHEN r.predicate_code = 'CHECK_DAGUA_YEAR_PER' THEN CAST(j.dagua_period AS TEXT)
            WHEN r.predicate_code = 'CHECK_DAGUA_YEAR_FAM' THEN array_to_string(ARRAY(SELECT DISTINCT family_name FROM spr_scdg WHERE jiazi_id = j.jiazi_id), ',')
            WHEN r.predicate_code = 'CHECK_DAGUA_YEAR_ROLE' THEN j.dagua_role
            WHEN r.predicate_code = 'CHECK_QI_PHASE_PILLAR_YEAR' THEN 
                qp.phase_name || ' (НС:' || h.year_stem || ' - ЗВ:' || h.year_branch || ')'
            ELSE 'Year Rule'
        END,
        CASE
            WHEN r.predicate_code = 'CHECK_QI_PHASE_PILLAR_YEAR' THEN COALESCE(qp.numeric_score, 0)::double precision
            ELSE 0.0::double precision
        END
    FROM t_bazi_hourly h
    JOIN spr_jiazi_extended j ON h.year_stem=j.stem AND h.year_branch=j.branch
    LEFT JOIN spr_bazi_qi_phase qp ON qp.stem_char = h.year_stem AND qp.branch_char = h.year_branch
    JOIN t_rule_registry r ON r.period_type = 'year' AND r.is_active = 1
        AND r.predicate_code != 'CHECK_QI_PHASE_DM_YEAR'  -- обрабатывается отдельным CROSS JOIN
    WHERE h.year_int = %s
    ON CONFLICT (year, rule_id, result_value, year_pillar) DO NOTHING
    """
    # Note: Using %s for LIKE with year%
    db.execute_query(sql, [str(year)])

    # 2. Фаза Ци ЭЛ в ЗВ Года (CHECK_QI_PHASE_DM_YEAR) — 10 строк (по одной на каждый НС)
    sql_dm_year = """
    INSERT INTO t_analysis_year (year, year_pillar, rule_id, result_value, score)
    SELECT 
        y.year_val,
        y.year_pillar,
        r.rule_id,
        qp.phase_name || ' (ЭЛ:' || s.stem_char || ' - ' || y.year_branch || ')',
        COALESCE(qp.numeric_score, 0)::double precision
    FROM (
        SELECT DISTINCT 
            CAST(substring(h.slot_start_date_local, 1, 4) AS INTEGER) as year_val,
            h.year_pillar,
            h.year_branch
        FROM t_bazi_hourly h
        WHERE h.year_int = %s
    ) y
    CROSS JOIN spr_heavenly_stem s
    LEFT JOIN spr_bazi_qi_phase qp ON qp.stem_char = s.stem_char AND qp.branch_char = y.year_branch
    JOIN t_rule_registry r ON r.predicate_code = 'CHECK_QI_PHASE_DM_YEAR' AND r.is_active = 1
    ON CONFLICT (year, rule_id, result_value, year_pillar) DO NOTHING
    """
    db.execute_query(sql_dm_year, [str(year)])

def process_month_level(year):
    print(f"  > Month Level Analysis [{year}]...")
    
    # Nayin, Da Gua, Qi Phase (Month)
    sql = """
    INSERT INTO t_analysis_month (year, month, year_pillar, month_pillar, rule_id, result_value, score)
    SELECT DISTINCT
        CAST(substring(h.slot_start_date_local, 1, 4) AS INTEGER),
        CAST(substring(h.slot_start_date_local, 6, 2) AS INTEGER),
        h.year_pillar,
        h.month_pillar,
        r.rule_id,
        CASE 
            -- Nayin/Dagua Month
            WHEN r.predicate_code LIKE 'CHECK_NAYIN_MONTH_%' THEN 
                CASE 
                    WHEN r.predicate_code LIKE '%_EL' THEN j.nayin_element 
                    ELSE j.nayin_name 
                END
            WHEN r.predicate_code LIKE 'CHECK_DAGUA_MONTH_%' THEN 
                CASE 
                    WHEN r.predicate_code LIKE '%_EL' THEN CAST(j.dagua_element AS TEXT)
                    WHEN r.predicate_code LIKE '%_PER' THEN CAST(j.dagua_period AS TEXT)
                    WHEN r.predicate_code LIKE '%_FAM' THEN array_to_string(ARRAY(SELECT DISTINCT family_name FROM spr_scdg WHERE jiazi_id = j.jiazi_id), ',')
                    ELSE j.dagua_role 
                END
            -- Qi Phase Pillar Month
            WHEN r.predicate_code = 'CHECK_QI_PHASE_PILLAR_MONTH' THEN
                q_pillar.phase_name || ' (НС:' || h.month_stem || ' - ЗВ:' || h.month_branch || ')'
            
            -- Qi Phase DM (Month) - Note: This technically depends on Day Stem, so belongs to Day or Mixed.
            -- Actually CHECK_QI_PHASE_DM_MONTH depends on Day Master + Month Branch. This is a DAY rule!
            -- Moved to Day Level in classification logic.
            
            ELSE 'Month Rule'
        END,
        CASE 
            WHEN r.predicate_code = 'CHECK_QI_PHASE_PILLAR_MONTH' THEN COALESCE(q_pillar.numeric_score, 0)::double precision
            ELSE 0.0::double precision
        END
    FROM t_bazi_hourly h
    LEFT JOIN spr_jiazi_extended j ON h.month_stem=j.stem AND h.month_branch=j.branch
    LEFT JOIN spr_bazi_qi_phase q_pillar ON q_pillar.stem_char = h.month_stem AND q_pillar.branch_char = h.month_branch
    JOIN t_rule_registry r ON r.period_type = 'month' AND r.is_active = 1
        AND r.predicate_code != 'CHECK_QI_PHASE_DM_MONTH'  -- обрабатывается отдельным CROSS JOIN
    WHERE h.year_int = %s
    ON CONFLICT (year, month, rule_id, result_value, year_pillar, month_pillar) DO NOTHING
    """
    db.execute_query(sql, [str(year)])

    # 2. Year Qi Phase calculated at Month Level (Dual Phase: Year+Year / Month+Year)
    # This inserts into t_analysis_month but uses the Year Rule ID
    sql_year_phase = """
    INSERT INTO t_analysis_month (year, month, year_pillar, month_pillar, rule_id, result_value, score)
    SELECT DISTINCT
        CAST(substring(h.slot_start_date_local, 1, 4) AS INTEGER),
        CAST(substring(h.slot_start_date_local, 6, 2) AS INTEGER),
        h.year_pillar,
        h.month_pillar,
        r.rule_id,
        -- Phase 1: Year Stem + Year Branch
        qp1.phase_name || ' (НС:' || h.year_stem || ' - ЗВ:' || h.year_branch || ')' ||
        ' / ' ||
        -- Phase 2: Month Stem + Year Branch
        qp2.phase_name || ' (НС:' || h.month_stem || ' - ЗВ:' || h.year_branch || ')',
        
        COALESCE(qp1.numeric_score, 0)::double precision
    FROM t_bazi_hourly h
    JOIN t_rule_registry r ON r.predicate_code = 'CHECK_QI_PHASE_PILLAR_YEAR' AND r.is_active = 1
    LEFT JOIN spr_bazi_qi_phase qp1 ON qp1.stem_char = h.year_stem AND qp1.branch_char = h.year_branch
    LEFT JOIN spr_bazi_qi_phase qp2 ON qp2.stem_char = h.month_stem AND qp2.branch_char = h.year_branch
    WHERE h.year_int = %s
    ON CONFLICT (year, month, rule_id, result_value, year_pillar, month_pillar) DO NOTHING
    """
    db.execute_query(sql_year_phase, [str(year)])

    # 3. Фаза Ци ЭЛ в ЗВ Месяца (CHECK_QI_PHASE_DM_MONTH) — 10 строк на каждый НС × месяц
    sql_dm_month = """
    INSERT INTO t_analysis_month (year, month, year_pillar, month_pillar, rule_id, result_value, score)
    SELECT 
        m.year_val,
        m.month_val,
        m.year_pillar,
        m.month_pillar,
        r.rule_id,
        qp.phase_name || ' (ЭЛ:' || s.stem_char || ' - ' || m.month_branch || ')',
        COALESCE(qp.numeric_score, 0)::double precision
    FROM (
        SELECT DISTINCT 
            CAST(substring(h.slot_start_date_local, 1, 4) AS INTEGER) as year_val,
            CAST(substring(h.slot_start_date_local, 6, 2) AS INTEGER) as month_val,
            h.year_pillar,
            h.month_pillar,
            h.month_branch
        FROM t_bazi_hourly h
        WHERE h.year_int = %s
    ) m
    CROSS JOIN spr_heavenly_stem s
    LEFT JOIN spr_bazi_qi_phase qp ON qp.stem_char = s.stem_char AND qp.branch_char = m.month_branch
    JOIN t_rule_registry r ON r.predicate_code = 'CHECK_QI_PHASE_DM_MONTH' AND r.is_active = 1
    ON CONFLICT (year, month, rule_id, result_value, year_pillar, month_pillar) DO NOTHING
    """
    db.execute_query(sql_dm_month, [str(year)])

    # Combinations (Year + Month) - Handled separately to join rule table
    pairs = [
        ('year_stem', 'month_stem', 'BAZI_STEM', 'spr_tongshu_stem_combo_rule'),
        ('year_branch', 'month_branch', 'BAZI_BRANCH', 'spr_tongshu_branch_combo_rule')
    ]
    
    for p1, p2, prefix, table in pairs:
        # Check if table is stem rule (no item3) or branch rule (has item3)
        item3_condition = "AND r.item3 IS NULL" if "branch" in table else ""
        
        q = f"""
        INSERT INTO t_analysis_month (year, month, year_pillar, month_pillar, rule_id, result_value, score)
        SELECT DISTINCT
            CAST(substring(h.slot_start_date_local, 1, 4) AS INTEGER),
            CAST(substring(h.slot_start_date_local, 6, 2) AS INTEGER),
            h.year_pillar,
            h.month_pillar,
            reg.rule_id,
            r.combo_name || ' (' || r.item1 || '-' || r.item2 || ') [Год+Месяц]',
            COALESCE(r.numeric_score, 0)::double precision
        FROM t_bazi_hourly h
        JOIN {table} r ON (h.{p1} = r.item1 AND h.{p2} = r.item2) OR (h.{p1} = r.item2 AND h.{p2} = r.item1)
        JOIN t_rule_registry reg ON reg.is_active = 1 AND reg.predicate_code LIKE '{prefix}%' 
            AND reg.period_type = 'month'
            -- Filter logic for types omitted for brevity, assuming reg name matches
        WHERE h.year_int = %s
        {item3_condition} -- Ensure pairs only if item3 column exists
        ON CONFLICT (year, month, rule_id, result_value, year_pillar, month_pillar) DO NOTHING
        """
        db.execute_query(q, [str(year)])

def process_day_level(year):
    print(f"  > Day Level Analysis [{year}]...")
    # Key strategy: Select distinct daily properties from Horse hour (11:00-13:00) to represent the day.
    # This avoids duplicates for day-bound properties.
    
    # 1. Day Officers, Master Dong, Yellow/Black, Black Rabbit, Nayin/Dagua Day
    # Optimization: DISTINCT removed — all LEFT JOINs are to unique-key lookup tables.
    sql = """
    INSERT INTO t_analysis_day (date_val, year_pillar, month_pillar, day_pillar, rule_id, result_value, score)
    SELECT
        date(h.slot_start_date_local),
        h.year_pillar,
        h.month_pillar,
        h.day_pillar,
        r.rule_id,
        CASE 
            -- Day Officers
            WHEN r.predicate_code = 'CHECK_DAY_OFFICER' THEN 
                COALESCE(iv_do.name_ru || ': ' || iv_do.description_ru, iv_do.name_ru)
            -- Master Dong
            WHEN r.predicate_code = 'CHECK_MASTER_DONG' THEN 
                COALESCE(iv_md.name_ru || ': ' || iv_md.description_ru, iv_md.name_ru)
            -- Yellow/Black
            WHEN r.predicate_code = 'CHECK_YELLOW_BLACK' THEN 
                CASE WHEN yb_s.score > 0 THEN 'Желтый путь: ' || yb_s.name ELSE 'Черный путь: ' || yb_s.name END
            -- Black Rabbit (Basic)
            WHEN r.predicate_code = 'CHECK_BLACK_RABBIT_M1' THEN 'ЧК (Баз): ' || br_m1.star_name
            WHEN r.predicate_code = 'CHECK_BLACK_RABBIT_M2' THEN 'ЧК (Усил): ' || br_m2.star_name || ' (из 1-го ЛД)'
            -- Black Rabbit (Joey Day)
            WHEN r.predicate_code = 'CHECK_BLACK_RABBIT_JOEY_DAY' THEN 'ЧК (День): ' || br_joey.star_name
            
            -- Nayin/Dagua Day
            WHEN r.predicate_code LIKE 'CHECK_NAYIN_DAY_%' THEN 
                CASE WHEN r.predicate_code LIKE '%_EL' THEN j.nayin_element ELSE j.nayin_name END
            WHEN r.predicate_code LIKE 'CHECK_DAGUA_DAY_%' THEN 
                CASE 
                    WHEN r.predicate_code LIKE '%_EL' THEN CAST(j.dagua_element AS TEXT)
                    WHEN r.predicate_code LIKE '%_PER' THEN CAST(j.dagua_period AS TEXT)
                    WHEN r.predicate_code LIKE '%_FAM' THEN array_to_string(ARRAY(SELECT DISTINCT family_name FROM spr_scdg WHERE jiazi_id = j.jiazi_id), ',')
                    ELSE j.dagua_role 
                END
            
            -- Qi Phases (Day Pillar & DM-Day)
            WHEN r.predicate_code = 'CHECK_QI_PHASE_PILLAR_DAY' THEN
                -- Phase 1: Day Stem + Day Branch
                qp_day.phase_name || ' (НС:' || h.day_stem || ' - ЗВ:' || h.day_branch || ')'

            WHEN r.predicate_code = 'CHECK_QI_PHASE_DM_DAY' THEN
                qp_dm_day.phase_name || ' (ЭЛ:' || h.day_stem || ' - ' || h.day_branch || ')'
            -- CHECK_QI_PHASE_DM_MONTH и CHECK_QI_PHASE_DM_YEAR перенесены на уровень месяца/года
            
            -- Yan Qin (Цинь Птицы) - созвездие дня
            WHEN r.predicate_code = 'CHECK_YANQIN_DAY' THEN
                yq.constellation_char || ' ' || yq.constellation_name || ' (' || yq.star_element || ')'

            -- Tai Yi Day Quality
            WHEN r.predicate_code = 'CHECK_TAIYI_DAY_QUALITY' THEN
                CASE 
                    WHEN tyd.total_score IS NULL THEN 'Нет данных Тай И'
                    WHEN tyd.total_score >= 2 THEN 'Большое счастье (П' || tyd.tai_yi_palace || ')'
                    WHEN tyd.total_score >= 0.5 THEN 'Малое счастье (П' || tyd.tai_yi_palace || ')'
                    WHEN tyd.total_score >= -0.5 THEN 'Нейтрально (П' || tyd.tai_yi_palace || ')'
                    WHEN tyd.total_score >= -2 THEN 'Малое несчастье (П' || tyd.tai_yi_palace || ')'
                    ELSE 'Большое несчастье (П' || tyd.tai_yi_palace || ')'
                END

            -- Lunar Date Rules
            WHEN r.predicate_code = 'CHECK_LUNAR_MONTH_NUM' THEN 
                CASE WHEN h.lunar_is_leap = 1 THEN h.lunar_month::text || ' (Високосный)' ELSE h.lunar_month::text END
            WHEN r.predicate_code = 'CHECK_LUNAR_DAY_NUM' THEN 
                h.lunar_day::text

            ELSE 'Day Rule'
        END,
        
        CASE 
            WHEN r.predicate_code = 'CHECK_DAY_OFFICER' THEN COALESCE(iv_do.numeric_score, 0)
            WHEN r.predicate_code = 'CHECK_MASTER_DONG' THEN COALESCE(iv_md.numeric_score, 0)
            WHEN r.predicate_code = 'CHECK_YELLOW_BLACK' THEN COALESCE(yb_s.score, 0)
            WHEN r.predicate_code = 'CHECK_BLACK_RABBIT_M1' THEN COALESCE(brs_m1.numeric_score, 0)
            WHEN r.predicate_code = 'CHECK_BLACK_RABBIT_M2' THEN COALESCE(brs_m2.numeric_score, 0)
            WHEN r.predicate_code = 'CHECK_BLACK_RABBIT_JOEY_DAY' THEN 0
            WHEN r.predicate_code LIKE 'CHECK_QI_PHASE_%' THEN 0 -- Placeholder, simplified
            WHEN r.predicate_code = 'CHECK_YANQIN_DAY' THEN COALESCE(yq.score, 0)
            WHEN r.predicate_code = 'CHECK_TAIYI_DAY_QUALITY' THEN COALESCE(tyd.total_score, 0)
            ELSE 0.0
        END::double precision
        
    FROM t_bazi_hourly h
    
    -- Joins for Day Officers
    LEFT JOIN spr_earthly_branch mb ON h.month_branch = mb.branch_char
    LEFT JOIN spr_earthly_branch db_branch ON h.day_branch = db_branch.branch_char
    LEFT JOIN spr_day_officer_mapping dom ON mb.branch_id = dom.month_branch_id AND db_branch.branch_id = dom.day_branch_id
    LEFT JOIN spr_indicator_value iv_do ON dom.officer_value_id = iv_do.value_id
    
    -- Joins for Master Dong
    LEFT JOIN spr_heavenly_stem ds ON h.day_stem = ds.stem_char
    LEFT JOIN spr_master_dano_mapping mdm ON mb.branch_id = mdm.month_branch_id AND ds.stem_id = mdm.day_stem_id AND db_branch.branch_id = mdm.day_branch_id
    LEFT JOIN spr_indicator_value iv_md ON mdm.indicator_value_id = iv_md.value_id
    
    -- Joins for Yellow/Black
    LEFT JOIN spr_yellow_black_matrix yb_m ON yb_m.month_branch = h.month_branch AND yb_m.day_branch = h.day_branch
    LEFT JOIN spr_yellow_black_stars yb_s ON yb_s.id = yb_m.star_id
    
    -- Joins for Jiazi (Nayin/Dagua/BlackRabbit)
    LEFT JOIN spr_jiazi_extended j ON h.day_stem=j.stem AND h.day_branch=j.branch
    
    -- Black Rabbit
    LEFT JOIN spr_black_rabbit_matrix br_m1 ON br_m1.jiazi_id = j.jiazi_id AND br_m1.lunar_day = h.lunar_day_zi
    LEFT JOIN spr_black_rabbit_matrix br_m2 ON br_m2.jiazi_id = (((j.jiazi_id - h.lunar_day_zi) %% 60 + 60) %% 60 + 1) AND br_m2.lunar_day = h.lunar_day_zi
    LEFT JOIN spr_black_rabbit_day_joey br_joey ON br_joey.first_day_jiazi_id = ((((j.jiazi_id - 1) - (h.lunar_day_zi - 1)) %% 60 + 60) %% 60) + 1 AND br_joey.lunar_day = h.lunar_day_zi
    LEFT JOIN spr_black_rabbit_scores brs_m1 ON brs_m1.star_name = br_m1.star_name
    LEFT JOIN spr_black_rabbit_scores brs_m2 ON brs_m2.star_name = br_m2.star_name
    
    -- Tai Yi Day Quality
    LEFT JOIN t_qumen_tayi_day tyd ON tyd.date_val = date(h.slot_start_date_local) AND tyd.palace_no = tyd.tai_yi_palace

    -- Yan Qin (Цинь Птицы): созвездие дня по дню недели + группе ветвей
    LEFT JOIN spr_yanqin_day_constellation yq ON yq.dow = EXTRACT(DOW FROM h.slot_start_date_local::date)::int
        AND yq.branch_group = CASE
            WHEN h.day_branch IN ('申','子','辰') THEN 1
            WHEN h.day_branch IN ('巳','酉','丑') THEN 2
            WHEN h.day_branch IN ('寅','午','戌') THEN 3
            WHEN h.day_branch IN ('亥','卯','未') THEN 4
        END

    -- Qi Phases
    LEFT JOIN spr_bazi_qi_phase qp_day ON qp_day.stem_char = h.day_stem AND qp_day.branch_char = h.day_branch
    LEFT JOIN spr_bazi_qi_phase qp_day_by_month ON qp_day_by_month.stem_char = h.month_stem AND qp_day_by_month.branch_char = h.day_branch

    LEFT JOIN spr_bazi_qi_phase qp_dm_day ON qp_dm_day.stem_char = h.day_stem AND qp_dm_day.branch_char = h.day_branch
    -- qp_dm_month и qp_dm_year убраны: DM_MONTH перенесён на уровень месяца, DM_YEAR — на уровень года

    JOIN t_rule_registry r ON r.period_type = 'day' AND r.is_active = 1
    AND r.predicate_code NOT LIKE 'SKDG_%'  -- СКДГ обрабатывается отдельно
    
    WHERE h.year_int = %s 
      AND h.hour_branch = '午' -- Select "Noon" to represent the day
    ON CONFLICT (date_val, rule_id, result_value, year_pillar, month_pillar, day_pillar) DO NOTHING
    """
    db.execute_query(sql, [str(year)])
    
    # Combinations Day-related (Year+Day, Month+Day)
    pairs = [
        ('year_stem', 'day_stem', 'BAZI_STEM', 'spr_tongshu_stem_combo_rule', 'Год+День'),
        ('month_stem', 'day_stem', 'BAZI_STEM', 'spr_tongshu_stem_combo_rule', 'Месяц+День'),
        ('year_branch', 'day_branch', 'BAZI_BRANCH', 'spr_tongshu_branch_combo_rule', 'Год+День'),
        ('month_branch', 'day_branch', 'BAZI_BRANCH', 'spr_tongshu_branch_combo_rule', 'Месяц+День')
    ]
    for p1, p2, prefix, table, label in pairs:
        # Check if table is stem rule (no item3) or branch rule (has item3)
        item3_condition = "AND r.item3 IS NULL" if "branch" in table else ""
        
        q = f"""
        INSERT INTO t_analysis_day (date_val, year_pillar, month_pillar, day_pillar, rule_id, result_value, score)
        SELECT DISTINCT
            date(h.slot_start_date_local),
            h.year_pillar,
            h.month_pillar,
            h.day_pillar,
            reg.rule_id,
            r.combo_name || ' (' || r.item1 || '-' || r.item2 || ') [{label}]',
            COALESCE(r.numeric_score, 0)::double precision
        FROM t_bazi_hourly h
        JOIN {table} r ON (h.{p1} = r.item1 AND h.{p2} = r.item2) OR (h.{p1} = r.item2 AND h.{p2} = r.item1)
        JOIN t_rule_registry reg ON reg.is_active = 1 AND reg.predicate_code LIKE '{prefix}%' 
            AND reg.period_type = 'day'
        WHERE h.year_int = %s
        AND h.hour_branch = '午'
        {item3_condition}
        ON CONFLICT (date_val, rule_id, result_value, year_pillar, month_pillar, day_pillar) DO NOTHING
        """
        db.execute_query(q, [str(year)])

def process_hour_level(year):
    print(f"  > Hour Level Analysis [{year}]...")
    
    # 1. Guigu, Black Rabbit Hour, Nayin/Dagua Hour, Qi Phase Hour
    # Optimization: DISTINCT removed — all LEFT JOINs are to unique-key lookup tables,
    # so no row multiplication can occur. This saves a full sort+dedup of ~118K rows.
    sql = """
    INSERT INTO t_analysis_hour (hour_id, year_pillar, month_pillar, day_pillar, hour_pillar, rule_id, result_value, score)
    SELECT
        h.hour_id,
        h.year_pillar,
        h.month_pillar,
        h.day_pillar,
        h.hour_pillar,
        r.rule_id,
        CASE 
            -- Guigu
            WHEN r.predicate_code = 'CHECK_GUIGU_NUMBER' THEN 
                COALESCE(iv_gg.name_ru || ': ' || iv_gg.description_ru, iv_gg.name_ru)
            -- Black Rabbit Joey Hour
            WHEN r.predicate_code = 'CHECK_BLACK_RABBIT_JOEY_HOUR' THEN 'ЧК (Час): ' || br_joey_h.star_name
            
            -- Nayin/Dagua Hour
            WHEN r.predicate_code LIKE 'CHECK_NAYIN_HOUR_%' THEN 
                CASE WHEN r.predicate_code LIKE '%_EL' THEN j.nayin_element ELSE j.nayin_name END
            WHEN r.predicate_code LIKE 'CHECK_DAGUA_HOUR_%' THEN 
                CASE 
                    WHEN r.predicate_code LIKE '%_EL' THEN CAST(j.dagua_element AS TEXT)
                    WHEN r.predicate_code LIKE '%_PER' THEN CAST(j.dagua_period AS TEXT)
                    WHEN r.predicate_code LIKE '%_FAM' THEN array_to_string(ARRAY(SELECT DISTINCT family_name FROM spr_scdg WHERE jiazi_id = j.jiazi_id), ',')
                    ELSE j.dagua_role 
                END
            
            -- Qi Phases (Hour Pillar & DM-Hour)
            WHEN r.predicate_code = 'CHECK_QI_PHASE_PILLAR_HOUR' THEN
                -- Фаза Ци: НС Часа в ЗВ Часа (одна фаза, по аналогии с day/month/year)
                qp_hour.phase_name || ' (НС:' || h.hour_stem || ' - ЗВ:' || h.hour_branch || ')'

            WHEN r.predicate_code = 'CHECK_QI_PHASE_DM_HOUR' THEN
                qp_dm_hour.phase_name || ' (ЭЛ:' || h.day_stem || ' - ' || h.hour_branch || ')'

            ELSE 'Hour Rule'
        END,
        
        CASE 
            WHEN r.predicate_code = 'CHECK_GUIGU_NUMBER' THEN COALESCE(iv_gg.numeric_score, 0)
            WHEN r.predicate_code = 'CHECK_BLACK_RABBIT_JOEY_HOUR' THEN COALESCE(br_joey_h.score, 0)
            WHEN r.predicate_code = 'CHECK_QI_PHASE_PILLAR_HOUR' THEN COALESCE(qp_hour.numeric_score, 0)
            ELSE 0.0
        END::double precision
        
    FROM t_bazi_hourly h
    
    -- Guigu
    LEFT JOIN spr_heavenly_stem ds ON h.day_stem = ds.stem_char
    LEFT JOIN spr_earthly_branch db_branch ON h.day_branch = db_branch.branch_char
    LEFT JOIN spr_earthly_branch hb ON h.hour_branch = hb.branch_char
    LEFT JOIN spr_tongshu_guigu_outcome iv_gg ON (ds.guigu_score + db_branch.guigu_score + hb.guigu_score) = iv_gg.outcome_number
    
    -- Black Rabbit Hour
    LEFT JOIN spr_black_rabbit_hour_joey br_joey_h ON h.day_stem = br_joey_h.day_stem AND h.hour_branch = br_joey_h.hour_branch
    
    -- Joins for Jiazi (Nayin/Dagua)
    LEFT JOIN spr_jiazi_extended j ON h.hour_stem=j.stem AND h.hour_branch=j.branch
    
    -- Qi Phases
    LEFT JOIN spr_bazi_qi_phase qp_hour ON qp_hour.stem_char = h.hour_stem AND qp_hour.branch_char = h.hour_branch
    -- qp_hour_by_month убран: вторая фаза удалена из CHECK_QI_PHASE_PILLAR_HOUR
    
    LEFT JOIN spr_bazi_qi_phase qp_dm_hour ON qp_dm_hour.stem_char = h.day_stem AND qp_dm_hour.branch_char = h.hour_branch

    JOIN t_rule_registry r ON r.period_type = 'hour' AND r.is_active = 1
    -- Exclude Qimen, Tai Yi Noble, SKDG (processed separately)
    AND r.predicate_code NOT LIKE 'CHECK_QIMEN%'
    AND r.predicate_code != 'CHECK_TAIYI_NOBLE_HOUR'
    AND r.predicate_code NOT LIKE 'SKDG_%'
    
    WHERE h.year_int = %s
    ON CONFLICT (hour_id, rule_id) DO NOTHING
    """
    db.execute_query(sql, [str(year)])
    
    # Tai Yi Noble Hour — отдельный INSERT только для благородных часов
    # Optimization: DISTINCT removed — t_taiyi_hours (is_noble) is unique on (date_val, hour_branch).
    sql_taiyi_noble = """
    INSERT INTO t_analysis_hour (hour_id, year_pillar, month_pillar, day_pillar, hour_pillar, rule_id, result_value, score)
    SELECT
        h.hour_id,
        h.year_pillar,
        h.month_pillar,
        h.day_pillar,
        h.hour_pillar,
        r.rule_id,
        'Благородный Тай И: ' || tyh.spirit_name,
        1.0::double precision
    FROM t_bazi_hourly h
    JOIN spr_earthly_branch eb ON h.hour_branch = eb.branch_char
    JOIN t_taiyi_hours tyh ON tyh.date_val = date(h.slot_start_date_local) 
        AND tyh.hour_branch = eb.branch_id
        AND tyh.is_noble = true
    JOIN t_rule_registry r ON r.predicate_code = 'CHECK_TAIYI_NOBLE_HOUR' AND r.is_active = 1
    WHERE h.year_int = %s
    ON CONFLICT (hour_id, rule_id) DO NOTHING
    """
    db.execute_query(sql_taiyi_noble, [str(year)])
    
    # Combinations Hour-related (Year+Hour, Month+Hour, Day+Hour)
    pairs = [
        ('year_stem', 'hour_stem', 'BAZI_STEM', 'spr_tongshu_stem_combo_rule', 'Год+Час'),
        ('month_stem', 'hour_stem', 'BAZI_STEM', 'spr_tongshu_stem_combo_rule', 'Месяц+Час'),
        ('day_stem', 'hour_stem', 'BAZI_STEM', 'spr_tongshu_stem_combo_rule', 'День+Час'),
        ('year_branch', 'hour_branch', 'BAZI_BRANCH', 'spr_tongshu_branch_combo_rule', 'Год+Час'),
        ('month_branch', 'hour_branch', 'BAZI_BRANCH', 'spr_tongshu_branch_combo_rule', 'Месяц+Час'),
        ('day_branch', 'hour_branch', 'BAZI_BRANCH', 'spr_tongshu_branch_combo_rule', 'День+Час')
    ]
    for p1, p2, prefix, table, label in pairs:
        # Check if table is stem rule (no item3) or branch rule (has item3)
        item3_condition = "AND r.item3 IS NULL" if "branch" in table else ""
        
        q = f"""
        INSERT INTO t_analysis_hour (hour_id, year_pillar, month_pillar, day_pillar, hour_pillar, rule_id, result_value, score)
        SELECT DISTINCT
            h.hour_id,
            h.year_pillar,
            h.month_pillar,
            h.day_pillar,
            h.hour_pillar,
            reg.rule_id,
            r.combo_name || ' (' || r.item1 || '-' || r.item2 || ') [{label}]',
            COALESCE(r.numeric_score, 0)::double precision
        FROM t_bazi_hourly h
        JOIN {table} r ON (h.{p1} = r.item1 AND h.{p2} = r.item2) OR (h.{p1} = r.item2 AND h.{p2} = r.item1)
        JOIN t_rule_registry reg ON reg.is_active = 1 AND reg.predicate_code LIKE '{prefix}%' 
            AND reg.period_type = 'hour'
        WHERE h.year_int = %s
        {item3_condition}
        ON CONFLICT (hour_id, rule_id) DO NOTHING
        """
        db.execute_query(q, [str(year)])

def process_skdg_hour_level(year):
    """СКДГ: оценка даты по методу Сюань Кун Да Гуа (hour level).
    
    16 правил: порождение/контроль (4), элементы (3), периоды (3),
    смешивание (1), семья (3), комбинированные (2).
    
    Группы элементов Хэ Ту: 1,6=Вода(1), 2,7=Огонь(2), 3,8=Дерево(3), 4,9=Металл(4).
    Порождение (生): 1→3, 3→2, 4→1 (Вода→Дерево, Дерево→Огонь, Металл→Вода).
    Контроль (克): 4→3, 1→2, 2→4 (Металл→Дерево, Вода→Огонь, Огонь→Металл).
    День — центр; Час/Месяц/Год — внешние столпы.
    Элементы/Периоды — все 6 пар столпов.
    
    Оптимизация: временная таблица tmp_dagua создается один раз
    и используется всеми ~16 INSERT-ами вместо повторной материализации CTE.
    Все запросы выполняются в одном соединении, т.к. db_manager
    открывает новую сессию на каждый вызов execute_query/fetch_all.
    
    Обновлено: 2025-05-16
    """
    print(f"  > SKDG Hour Level Analysis [{year}]...")
    
    # Единое соединение для всех операций с tmp_dagua
    conn = db.get_connection()
    try:
        cur = conn.cursor()
        
        # Создаем временную таблицу один раз вместо CTE в каждом из ~16 запросов
        cur.execute("DROP TABLE IF EXISTS tmp_dagua")
        cur.execute("""
            CREATE TEMP TABLE tmp_dagua AS
            SELECT 
                h.hour_id, h.year_pillar, h.month_pillar, h.day_pillar, h.hour_pillar,
                jy.dagua_element el_y, jy.dagua_period per_y,
                jm.dagua_element el_m, jm.dagua_period per_m,
                jd.dagua_element el_d, jd.dagua_period per_d,
                jh.dagua_element el_h, jh.dagua_period per_h,
                ARRAY(SELECT DISTINCT family_name FROM spr_scdg WHERE jiazi_id = jy.jiazi_id) fam_arr_y,
                ARRAY(SELECT DISTINCT family_name FROM spr_scdg WHERE jiazi_id = jm.jiazi_id) fam_arr_m,
                ARRAY(SELECT DISTINCT family_name FROM spr_scdg WHERE jiazi_id = jd.jiazi_id) fam_arr_d,
                ARRAY(SELECT DISTINCT family_name FROM spr_scdg WHERE jiazi_id = jh.jiazi_id) fam_arr_h,
                CASE WHEN jy.dagua_element IN (1,6) THEN 1 WHEN jy.dagua_element IN (2,7) THEN 2 
                     WHEN jy.dagua_element IN (3,8) THEN 3 ELSE 4 END g_y,
                CASE WHEN jm.dagua_element IN (1,6) THEN 1 WHEN jm.dagua_element IN (2,7) THEN 2 
                     WHEN jm.dagua_element IN (3,8) THEN 3 ELSE 4 END g_m,
                CASE WHEN jd.dagua_element IN (1,6) THEN 1 WHEN jd.dagua_element IN (2,7) THEN 2 
                     WHEN jd.dagua_element IN (3,8) THEN 3 ELSE 4 END g_d,
                CASE WHEN jh.dagua_element IN (1,6) THEN 1 WHEN jh.dagua_element IN (2,7) THEN 2 
                     WHEN jh.dagua_element IN (3,8) THEN 3 ELSE 4 END g_h
            FROM t_bazi_hourly h
            JOIN spr_jiazi_extended jy ON jy.stem = h.year_stem AND jy.branch = h.year_branch
            JOIN spr_jiazi_extended jm ON jm.stem = h.month_stem AND jm.branch = h.month_branch
            JOIN spr_jiazi_extended jd ON jd.stem = h.day_stem AND jd.branch = h.day_branch
            JOIN spr_jiazi_extended jh ON jh.stem = h.hour_stem AND jh.branch = h.hour_branch
            WHERE h.year_int = %s
        """, (str(year),))
        cur.execute("CREATE INDEX ON tmp_dagua (hour_id)")
        
        # Загрузка rule_id по predicate_code для каждого правила
        cur.execute("""
            SELECT predicate_code, rule_id, score_base 
            FROM t_rule_registry 
            WHERE predicate_code LIKE 'SKDG_%%' AND period_type = 'hour' AND is_active = 1
        """)
        skdg_rules = cur.fetchall()
        rule_map = {r[0]: (r[1], r[2]) for r in skdg_rules}
        
        # Макрос: 6 пар для CONCAT_WS
        def _pairs_concat(col_prefix, condition_tpl):
            """Генерирует CONCAT_WS для 6 пар столпов."""
            pairs = [('y','m','Г-М'), ('y','d','Г-Д'), ('y','h','Г-Ч'),
                     ('m','d','М-Д'), ('m','h','М-Ч'), ('d','h','Д-Ч')]
            cases = []
            for a, b, label in pairs:
                cond = condition_tpl.format(a=f"{col_prefix}_{a}", b=f"{col_prefix}_{b}")
                cases.append(f"CASE WHEN {cond} THEN '{label}' END")
            return "CONCAT_WS(', ', " + ", ".join(cases) + ")"

        same_tpl = "{a} = {b}"
        c10_tpl = "{a} + {b} = 10"
        hetu_tpl = "ABS({a} - {b}) = 5"
        
        rules_defs = []
        
        # --- Элементы: 3 правила ---
        for code, prefix, tpl in [
            ('SKDG_EL_SAME_GUA',  'Эл. такое же Гуа', same_tpl),
            ('SKDG_EL_COMBO10',   'Эл. Комб.10', c10_tpl),
            ('SKDG_EL_HETU',      'Эл. Хэ Ту', hetu_tpl),
        ]:
            expr = _pairs_concat('el', tpl)
            rules_defs.append((code, f"'{prefix}: ' || v.val", expr, "v.val != ''"))
        
        # --- Периоды: 3 правила ---
        for code, prefix, tpl in [
            ('SKDG_PER_SAME_GUA', 'Пер. такое же Гуа', same_tpl),
            ('SKDG_PER_COMBO10',  'Пер. Комб.10', c10_tpl),
            ('SKDG_PER_HETU',     'Пер. Хэ Ту', hetu_tpl),
        ]:
            expr = _pairs_concat('per', tpl)
            rules_defs.append((code, f"'{prefix}: ' || v.val", expr, "v.val != ''"))
        
        # --- Комбинированные: 2 правила ---
        combined_pairs = [('y','m','Г-М'), ('y','d','Г-Д'), ('y','h','Г-Ч'),
                          ('m','d','М-Д'), ('m','h','М-Ч'), ('d','h','Д-Ч')]
        for code, prefix, el_cond, per_cond in [
            ('SKDG_EL_PER_HETU', 'Эл+Пер Хэ Ту', 'ABS(el_{a} - el_{b}) = 5', 'ABS(per_{a} - per_{b}) = 5'),
            ('SKDG_EL_PER_COMBO10', 'Эл+Пер Комб.10', '(el_{a} + el_{b}) = 10', '(per_{a} + per_{b}) = 10'),
        ]:
            cases = []
            for a, b, label in combined_pairs:
                ec = el_cond.format(a=a, b=b)
                pc = per_cond.format(a=a, b=b)
                cases.append(f"CASE WHEN {ec} AND {pc} THEN '{label}' END")
            expr = "CONCAT_WS(', ', " + ", ".join(cases) + ")"
            rules_defs.append((code, f"'{prefix}: ' || v.val", expr, "v.val != ''"))
        
        # --- Порождение/Контроль: 4 правила ---
        gen_cond = "(g_{a}=1 AND g_{b}=3) OR (g_{a}=3 AND g_{b}=2) OR (g_{a}=4 AND g_{b}=1)"
        ctrl_cond = "(g_{a}=4 AND g_{b}=3) OR (g_{a}=1 AND g_{b}=2) OR (g_{a}=2 AND g_{b}=4)"
        
        for code, prefix, cond_tpl, pairs_list in [
            ('SKDG_GEN_INWARD', 'Порождение внутрь', gen_cond,
             [('h','d','Час'), ('m','d','Мес'), ('y','d','Год')]),
            ('SKDG_GEN_OUTWARD', 'Порождение наружу', gen_cond,
             [('d','h','Час'), ('d','m','Мес'), ('d','y','Год')]),
            ('SKDG_CTRL_INWARD', 'Контроль внутрь', ctrl_cond,
             [('h','d','Час'), ('m','d','Мес'), ('y','d','Год')]),
            ('SKDG_CTRL_OUTWARD', 'Контроль наружу', ctrl_cond,
             [('d','h','Час'), ('d','m','Мес'), ('d','y','Год')]),
        ]:
            cases = [f"CASE WHEN {cond_tpl.format(a=a, b=b)} THEN '{label}' END"
                     for a, b, label in pairs_list]
            expr = "CONCAT_WS(', ', " + ", ".join(cases) + ")"
            rules_defs.append((code, f"'{prefix}: ' || v.val", expr, "v.val != ''"))
        
        # --- Смешивание: 1 правило ---
        gc_parts = {}
        for key, cond, plist in [
            ('gen_in', gen_cond, [('h','d','Час'), ('m','d','Мес'), ('y','d','Год')]),
            ('gen_out', gen_cond, [('d','h','Час'), ('d','m','Мес'), ('d','y','Год')]),
            ('ctrl_in', ctrl_cond, [('h','d','Час'), ('m','d','Мес'), ('y','d','Год')]),
            ('ctrl_out', ctrl_cond, [('d','h','Час'), ('d','m','Мес'), ('d','y','Год')]),
        ]:
            cases = [f"CASE WHEN {cond.format(a=a, b=b)} THEN '{label}' END"
                     for a, b, label in plist]
            gc_parts[key] = "CONCAT_WS(', ', " + ", ".join(cases) + ")"
        
        mixed_expr = (f"CONCAT_WS(' ', "
            f"CASE WHEN {gc_parts['gen_in']}  != '' THEN 'Пор←' || {gc_parts['gen_in']} END, "
            f"CASE WHEN {gc_parts['gen_out']} != '' THEN 'Пор→' || {gc_parts['gen_out']} END, "
            f"CASE WHEN {gc_parts['ctrl_in']}  != '' THEN 'Кон←' || {gc_parts['ctrl_in']} END, "
            f"CASE WHEN {gc_parts['ctrl_out']} != '' THEN 'Кон→' || {gc_parts['ctrl_out']} END)")
        mixed_where = (
            f"(({gc_parts['gen_in']} != '' OR {gc_parts['gen_out']} != '') "
            f"AND ({gc_parts['ctrl_in']} != '' OR {gc_parts['ctrl_out']} != ''))")
        rules_defs.append(('SKDG_MIXED_GEN_CTRL', "'Смешивание: ' || v.val", mixed_expr, mixed_where))
        
        # --- Семья: 3 правила ---
        rules_defs.append(('SKDG_FAM_DH', "'Семья Д-Ч: ' || array_to_string(d.fam_arr_d, ',')", "1",
                            "d.fam_arr_d && d.fam_arr_h"))
        rules_defs.append(('SKDG_FAM_DHM', "'Семья Д-Ч-М: ' || array_to_string(d.fam_arr_d, ',')", "1",
                            "d.fam_arr_d && d.fam_arr_h AND d.fam_arr_d && d.fam_arr_m"))
        rules_defs.append(('SKDG_FAM_DHMY', "'Семья Д-Ч-М-Г: ' || array_to_string(d.fam_arr_d, ',')", "1",
                            "d.fam_arr_d && d.fam_arr_h AND d.fam_arr_d && d.fam_arr_m AND d.fam_arr_d && d.fam_arr_y"))

        # Выполнение: один INSERT для каждого правила
        for code, result_expr, val_expr, where_cond in rules_defs:
            if code not in rule_map:
                continue
            rule_id, score = rule_map[code]
            
            if val_expr == "1":
                sql = f"""
                SELECT d.hour_id, d.year_pillar, d.month_pillar, d.day_pillar, d.hour_pillar,
                    '{rule_id}', {result_expr}, {score}::double precision
                FROM tmp_dagua d
                WHERE {where_cond}
                """
            else:
                sql = f"""
                SELECT v.hour_id, v.year_pillar, v.month_pillar, v.day_pillar, v.hour_pillar,
                    '{rule_id}', {result_expr}, {score}::double precision
                FROM (
                    SELECT d.*, {val_expr} as val
                    FROM tmp_dagua d
                ) v
                WHERE {where_cond}
                """
            
            full_sql = f"""
            INSERT INTO t_analysis_hour (hour_id, year_pillar, month_pillar, day_pillar, hour_pillar, rule_id, result_value, score)
            {sql}
            ON CONFLICT (hour_id, rule_id) DO NOTHING
            """
            cur.execute(full_sql)
        
        conn.commit()
    finally:
        # Очистка временной таблицы перед закрытием соединения
        try:
            cur.execute("DROP TABLE IF EXISTS tmp_dagua")
            conn.commit()
        except Exception:
            pass
        conn.close()


def process_skdg_day_level(year):
    """СКДГ: поиск гексаграмм-партнёров для каждого дня (day level).
    
    Для гексаграммы дня находит все гексаграммы из spr_skdg_hexagram_pairs,
    формирующие: Хэ Ту (эл+пер), Комб.10 (эл+пер), одинак. период, одинак. элемент.
    Каждый партнёр — отдельная строка в t_analysis_day (score=0, информационное правило).
    
    Обновлено: 2025-02-09
    """
    print(f"  > SKDG Day Level (Partner Search) [{year}]...")
    
    sql = """
    INSERT INTO t_analysis_day (date_val, year_pillar, month_pillar, day_pillar, rule_id, result_value, score)
    SELECT DISTINCT
        date(h.slot_start_date_local),
        h.year_pillar, h.month_pillar, h.day_pillar,
        r.rule_id,
        CASE r.predicate_code
            WHEN 'SKDG_DAY_PARTNER_HETU'     THEN 'ХТ: ' || p.pillar_b || ' (эл:' || p.el_b || ' пер:' || p.per_b || ')'
            WHEN 'SKDG_DAY_PARTNER_C10'      THEN 'К10: ' || p.pillar_b || ' (эл:' || p.el_b || ' пер:' || p.per_b || ')'
            WHEN 'SKDG_DAY_PARTNER_SAME_PER' THEN '=Пер: ' || p.pillar_b || ' (пер:' || p.per_b || ')'
            WHEN 'SKDG_DAY_PARTNER_SAME_EL'  THEN '=Эл: ' || p.pillar_b || ' (эл:' || p.el_b || ')'
        END,
        0.0::double precision
    FROM t_bazi_hourly h
    JOIN spr_jiazi_extended j ON j.stem = h.day_stem AND j.branch = h.day_branch
    JOIN spr_skdg_hexagram_pairs p ON p.jiazi_id_a = j.jiazi_id
    CROSS JOIN t_rule_registry r
    WHERE h.year_int = %s
      AND h.hour_branch = '午'
      AND r.predicate_code LIKE 'SKDG_DAY_PARTNER_%%'
      AND r.period_type = 'day' AND r.is_active = 1
      AND CASE r.predicate_code
          WHEN 'SKDG_DAY_PARTNER_HETU'     THEN p.is_hetu_el_per
          WHEN 'SKDG_DAY_PARTNER_C10'      THEN p.is_c10_el_per
          WHEN 'SKDG_DAY_PARTNER_SAME_PER' THEN p.is_same_period
          WHEN 'SKDG_DAY_PARTNER_SAME_EL'  THEN p.is_same_element
          ELSE false
      END
    ON CONFLICT (date_val, rule_id, result_value, year_pillar, month_pillar, day_pillar) DO NOTHING
    """
    db.execute_query(sql, [str(year)])


def process_direction_level(year):
    print(f"  > Direction Analysis (Qimen Hierarchical) [{year}]...")
    process_direction_year(year)
    process_direction_month(year)
    process_direction_day(year)
    process_direction_hour(year)

def process_direction_year(year):
    # Year Chart Analysis
    # Source: t_qumen_dgiren_year
    # Join: t_bazi_hourly (to get year_pillar for the year)
    sql = """
    INSERT INTO t_analysis_direction_year (year, year_pillar, palace_no, system_type, rule_id, result_value, score)
    WITH qimen_rules AS (
        SELECT 
            rule_id, 
            params_json::json ->> 'heaven' as h_stem, 
            params_json::json ->> 'earth' as e_stem,
            name_ru, description, score_base
        FROM t_rule_registry 
        WHERE predicate_code = 'CHECK_QIMEN_STEMS' AND is_active = 1
    ),
    bh_unique AS (
        SELECT DISTINCT year_int, year_pillar
        FROM t_bazi_hourly
        WHERE year_int = %s
    )
    SELECT
        bh.year_int as year_val,
        bh.year_pillar,
        t.palace_no,
        'ZhiRun',
        r.rule_id,
        r.name_ru || '. ' || COALESCE(r.description, ''),
        r.score_base
    FROM bh_unique bh
    JOIN t_qumen_dgiren_year t ON bh.year_pillar = t.year_pillar
    JOIN spr_qimen_templates tmpl ON t.rasklad_id = tmpl.rasklad_id AND t.palace_no = tmpl.palace_no
    JOIN qimen_rules r ON tmpl.heaven_stem = r.h_stem AND tmpl.earth_stem = r.e_stem
    ON CONFLICT (year, palace_no, system_type, rule_id, year_pillar) DO UPDATE SET result_value = EXCLUDED.result_value, score = EXCLUDED.score
    """
    db.execute_query(sql, [str(year)])

def process_direction_month(year):
    # Month Chart Analysis
    # Source: t_qumen_dgiren_month
    sql = """
    INSERT INTO t_analysis_direction_month (year, month, year_pillar, month_pillar, palace_no, system_type, rule_id, result_value, score)
    WITH qimen_rules AS (
        SELECT 
            rule_id, 
            params_json::json ->> 'heaven' as h_stem, 
            params_json::json ->> 'earth' as e_stem,
            name_ru, description, score_base
        FROM t_rule_registry 
        WHERE predicate_code = 'CHECK_QIMEN_STEMS' AND is_active = 1
    ),
    bh_unique AS (
        SELECT DISTINCT year_int, CAST(substring(slot_start_date_local, 6, 2) AS INTEGER) as month, year_pillar, month_pillar
        FROM t_bazi_hourly
        WHERE year_int = %s
    )
    SELECT
        bh.year_int,
        bh.month,
        bh.year_pillar,
        bh.month_pillar,
        t.palace_no,
        'ZhiRun',
        r.rule_id,
        r.name_ru || '. ' || COALESCE(r.description, ''),
        r.score_base
    FROM bh_unique bh
    JOIN t_qumen_dgiren_month t ON (bh.year_pillar = t.year_pillar AND bh.month_pillar = t.month_pillar)
    JOIN spr_qimen_templates tmpl ON t.rasklad_id = tmpl.rasklad_id AND t.palace_no = tmpl.palace_no
    JOIN qimen_rules r ON tmpl.heaven_stem = r.h_stem AND tmpl.earth_stem = r.e_stem
    ON CONFLICT (year, month, palace_no, system_type, rule_id, year_pillar, month_pillar) DO UPDATE SET result_value = EXCLUDED.result_value, score = EXCLUDED.score
    """
    db.execute_query(sql, [str(year)])

def process_direction_day(year):
    # Day Chart Analysis
    # Source: t_qumen_dgiren_day
    sql = """
    INSERT INTO t_analysis_direction_day (date_val, year_pillar, month_pillar, day_pillar, palace_no, system_type, rule_id, result_value, score)
    WITH qimen_rules AS (
        SELECT 
            rule_id, 
            params_json::json ->> 'heaven' as h_stem, 
            params_json::json ->> 'earth' as e_stem,
            name_ru, description, score_base
        FROM t_rule_registry 
        WHERE predicate_code = 'CHECK_QIMEN_STEMS' AND is_active = 1
    ),
    bh_unique AS (
        SELECT DISTINCT date(slot_start_date_local) as date_val, year_pillar, month_pillar, day_pillar
        FROM t_bazi_hourly
        WHERE year_int = %s AND hour_branch = '午'
    )
    SELECT
        bh.date_val,
        bh.year_pillar,
        bh.month_pillar,
        bh.day_pillar,
        t.palace_no,
        'ZhiRun',
        r.rule_id,
        r.name_ru || '. ' || COALESCE(r.description, ''),
        r.score_base
    FROM bh_unique bh
    JOIN t_qumen_dgiren_day t ON (bh.year_pillar = t.year_pillar AND bh.month_pillar = t.month_pillar AND bh.day_pillar = t.day_pillar)
    JOIN spr_qimen_templates tmpl ON t.rasklad_id = tmpl.rasklad_id AND t.palace_no = tmpl.palace_no
    JOIN qimen_rules r ON tmpl.heaven_stem = r.h_stem AND tmpl.earth_stem = r.e_stem
    ON CONFLICT (date_val, palace_no, system_type, rule_id, year_pillar, month_pillar, day_pillar) DO UPDATE SET result_value = EXCLUDED.result_value, score = EXCLUDED.score
    """
    db.execute_query(sql, [str(year)])

def process_direction_hour(year):
    # Hour Chart Analysis
    # Source: t_qumen_dgiren_hourly
    sql = """
    INSERT INTO t_analysis_direction_hour (hour_id, year_pillar, month_pillar, day_pillar, hour_pillar, palace_no, system_type, rule_id, result_value, score)
    WITH qimen_rules AS (
        SELECT 
            rule_id, 
            params_json::json ->> 'heaven' as h_stem, 
            params_json::json ->> 'earth' as e_stem,
            name_ru, description, score_base
        FROM t_rule_registry 
        WHERE predicate_code = 'CHECK_QIMEN_STEMS' AND is_active = 1
    ),
    bh_unique AS (
        SELECT DISTINCT hour_id, year_pillar, month_pillar, day_pillar, hour_pillar
        FROM t_bazi_hourly
        WHERE year_int = %s
    )
    SELECT
        bh.hour_id,
        bh.year_pillar,
        bh.month_pillar,
        bh.day_pillar,
        bh.hour_pillar,
        t.palace_no,
        'ZhiRun',
        r.rule_id,
        r.name_ru || '. ' || COALESCE(r.description, ''),
        r.score_base
    FROM t_qumen_dgiren_hourly t
    JOIN spr_qimen_templates tmpl ON t.rasklad_id = tmpl.rasklad_id AND t.palace_no = tmpl.palace_no
    JOIN bh_unique bh ON t.hour_id = bh.hour_id
    JOIN qimen_rules r ON tmpl.heaven_stem = r.h_stem AND tmpl.earth_stem = r.e_stem
    ON CONFLICT (hour_id, palace_no, system_type, rule_id) DO UPDATE SET result_value = EXCLUDED.result_value, score = EXCLUDED.score
    """
    try:
        db.execute_query(sql, [str(year)])
    except Exception as e:
        print(f"Qimen Hour analysis skipped or failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Analysis Cycle")
    parser.add_argument("--year", type=int, help="Specific year to process (e.g., 2026)")
    parser.add_argument("--workers", type=int, default=None, 
                        help="Number of parallel workers for batch processing (default: auto = CPU count). Use 1 for sequential mode.")
    args = parser.parse_args()
    
    run_analysis(target_year=args.year, max_workers=args.workers)
