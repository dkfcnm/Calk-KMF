import sys
import os
import time

# Ensure we can import from code/ - MUST BE FIRST
sys.path.insert(0, os.getcwd())

from code.common.db_manager import db
from code.common.config import load_config_from_db

def run_update(logger=None):
    log_id = None
    if logger:
        log_id = logger.start_stage("Qimen Calculation (SQL-Centric)")

    print("Starting Qimen Calculation (SQL-Centric)...")
    start_time = time.time()

    # 1. Initialize Tables
    # We use the same table structure as before: t_qumen_dgiren_year/month/day/hourly
    # We will TRUNCATE/DROP and recreate to ensure clean state.
    
    tables_def = {
        "t_qumen_dgiren_year": """
            CREATE TABLE t_qumen_dgiren_year (
                chart_id TEXT PRIMARY KEY,
                year_pillar TEXT,
                rasklad_id TEXT,
                palace_no INTEGER,
                chart_type TEXT
            )
        """,
        "t_qumen_dgiren_month": """
            CREATE TABLE t_qumen_dgiren_month (
                chart_id TEXT PRIMARY KEY,
                year_pillar TEXT,
                month_pillar TEXT,
                rasklad_id TEXT,
                palace_no INTEGER,
                chart_type TEXT
            )
        """,
        "t_qumen_dgiren_day": """
             CREATE TABLE t_qumen_dgiren_day (
                chart_id TEXT PRIMARY KEY,
                year_pillar TEXT,
                month_pillar TEXT,
                day_pillar TEXT,
                rasklad_id TEXT,
                palace_no INTEGER,
                chart_type TEXT
            )
        """,
        "t_qumen_dgiren_hourly": """
             CREATE TABLE t_qumen_dgiren_hourly (
                chart_id TEXT PRIMARY KEY,
                hour_id TEXT NOT NULL,
                rasklad_id TEXT,
                palace_no INTEGER,
                chart_type TEXT
            )
        """
    }

    print("Recreating Qimen tables...")
    for t_name, t_sql in tables_def.items():
        db.execute_query(f"DROP TABLE IF EXISTS {t_name} CASCADE")
        db.execute_query(t_sql)

    # 2. Year Chart Calculation
    # Logic:
    # Year < 1984 ( 甲子 )? Reference is 1984.
    # Diff = Year - 1984.
    # Ju = 7 - (Diff % 9). If <= 0 -> += 9.
    # Yin/Yang: Always Yin (Standard convention for years? Or depends on Half-Year?)
    # Most sources: Year Qimen uses Yin One (or specific).
    # Based on python code: always "Yin".
    # Rasklad ID: Yin_{Ju}_{YearStem}{YearBranch}
    
    print("Calculating Year Charts...")
    sql_year = """
    INSERT INTO t_qumen_dgiren_year (chart_id, year_pillar, rasklad_id, palace_no, chart_type)
    WITH distinct_years AS (
        SELECT DISTINCT year_pillar, year_stem, year_branch, EXTRACT(YEAR FROM slot_start_date_utc::DATE)::INT as cal_year, solar_term_id
        FROM t_bazi_hourly
    ),
    calc_params AS (
        SELECT 
            year_pillar,
            year_stem,
            year_branch,
            -- Adjust year for solar term 23/24 (Early Jan is prev solar year)
            (CASE WHEN solar_term_id >= 23 THEN cal_year - 1 ELSE cal_year END) as true_year
        FROM distinct_years
    ),
    calc_ju AS (
        SELECT
            year_pillar,
            year_stem,
            year_branch,
            (7 - ((true_year - 1984) % 9)) as raw_ju
        FROM calc_params
    ),
    final_ju AS (
        SELECT
            year_pillar,
            year_stem,
            year_branch,
            (CASE WHEN raw_ju <= 0 THEN raw_ju + 9 ELSE raw_ju END) as ju_num
        FROM calc_ju
    ),
    rasklads AS (
        SELECT
            year_pillar,
            'Yin_' || ju_num || '_' || year_stem || year_branch as rasklad_id
        FROM final_ju
    )
    SELECT
        md5(r.year_pillar || '_' || t.palace_no) as chart_id,
        r.year_pillar,
        r.rasklad_id,
        t.palace_no,
        'Годовой'
    FROM rasklads r
    JOIN spr_qimen_templates t ON t.rasklad_id = r.rasklad_id
    ON CONFLICT (chart_id) DO NOTHING
    """
    db.execute_query(sql_year)

    # 3. Month Chart Calculation
    # Logic:
    # Month Index from 1984.
    # Block = (Months - 9) // 10.
    # Ju = 9 - (Block % 9). If 0 -> 9.
    # Yin/Yang: Always Yin.
    
    print("Calculating Month Charts...")
    sql_month = """
    INSERT INTO t_qumen_dgiren_month (chart_id, year_pillar, month_pillar, rasklad_id, palace_no, chart_type)
    WITH distinct_months AS (
        SELECT DISTINCT 
            year_pillar, month_pillar, 
            year_branch, month_stem, month_branch,
            EXTRACT(YEAR FROM slot_start_date_utc::DATE)::INT as cal_year, solar_term_id
        FROM t_bazi_hourly
    ),
    branch_map AS (
        SELECT branch_char, branch_id FROM spr_earthly_branch
    ),
    calc_idx AS (
        SELECT
            dm.year_pillar,
            dm.month_pillar,
            dm.month_stem,
            dm.month_branch,
            (CASE WHEN dm.solar_term_id >= 23 THEN dm.cal_year - 1 ELSE dm.cal_year END) as true_year,
            -- Month index: Tiger(3) is 1st month of year? 
            -- Python code: idx = branches.index(b). if idx>=2: idx-1 else idx+11.
            -- DB IDs: Tiger=3. 
            -- If id=3 (Tiger) -> 2? No.
            -- Python: ['Zi', 'Chou', 'Yin'...] -> 'Yin' is index 2. 2-1 = 1.
            -- So Tiger is 1.
            -- DB IDs: Zi=1, Chou=2, Yin=3.
            -- If id>=3 -> id-2. If id<3 -> id+10.
            (CASE WHEN bm.branch_id >= 3 THEN bm.branch_id - 2 ELSE bm.branch_id + 10 END) as m_idx
        FROM distinct_months dm
        JOIN branch_map bm ON bm.branch_char = dm.month_branch
    ),
    calc_ju AS (
        SELECT
            year_pillar, month_pillar, month_stem, month_branch,
            ((true_year - 1984) * 12 + m_idx) as total_months
        FROM calc_idx
    ),
    final_ju AS (
        SELECT
            year_pillar, month_pillar, month_stem, month_branch,
            (9 - (((total_months - 9) / 10)::INT % 9)) as raw_ju
        FROM calc_ju
    ),
    rasklads AS (
        SELECT
            year_pillar, month_pillar,
            'Yin_' || (CASE WHEN raw_ju = 0 THEN 9 ELSE raw_ju END) || '_' || month_stem || month_branch as rasklad_id
        FROM final_ju
    )
    SELECT
        md5(r.year_pillar || '_' || r.month_pillar || '_' || t.palace_no) as chart_id,
        r.year_pillar,
        r.month_pillar,
        r.rasklad_id,
        t.palace_no,
        'Месячный'
    FROM rasklads r
    JOIN spr_qimen_templates t ON t.rasklad_id = r.rasklad_id
    ON CONFLICT (chart_id) DO NOTHING
    """
    db.execute_query(sql_month)

    # 4. Day Chart Calculation
    # Logic:
    # Based on Ri Jia (Day Pillar + Solar Term -> Ju).
    # Is Yin? 10 <= term <= 21.
    # Level: Count JiaZi from Solar Term Start. 
    #   (curr_ord - term_start_ord) // 60 -> num_cycles.
    #   Level = (num_cycles % 3) + 1. (Upper/Middle/Lower for Day?)
    #   Actually code says: ju = config.ri_jia_table[pillar][yy][level-1]
    
    print("Calculating Day Charts...")
    # Need efficient way to get term start for day
    sql_day = """
    INSERT INTO t_qumen_dgiren_day (chart_id, year_pillar, month_pillar, day_pillar, rasklad_id, palace_no, chart_type)
    WITH distinct_days AS (
        SELECT DISTINCT
            year_pillar, month_pillar, day_pillar,
            day_stem, day_branch,
            slot_start_date_utc::DATE as curr_date
        FROM t_bazi_hourly
    ),
    term_info AS (
        SELECT 
            d.year_pillar, d.month_pillar, d.day_pillar, d.day_stem, d.day_branch, d.curr_date,
            st.solar_term_id
        FROM distinct_days d
        JOIN LATERAL (
            SELECT solar_term_id
            FROM t_solar_term_time
            WHERE crossing_utc::DATE <= d.curr_date
            ORDER BY crossing_utc DESC
            LIMIT 1
        ) st ON TRUE
    ),
    calc_ju_idx AS (
        SELECT 
            year_pillar, month_pillar, day_pillar, day_stem, day_branch, curr_date, solar_term_id,
            (CASE WHEN solar_term_id BETWEEN 10 AND 21 THEN 'yin' ELSE 'yang' END) as yy_key,
            (CASE WHEN solar_term_id BETWEEN 10 AND 21 THEN 'Yin' ELSE 'Yang' END) as yy_str,
            -- Позиция термина в полугодии (1-12): pos 1-4=Upper, 5-8=Middle, 9-12=Lower
            (((CASE
                WHEN solar_term_id BETWEEN 10 AND 21 THEN solar_term_id - 9
                WHEN solar_term_id >= 22 THEN solar_term_id - 21
                ELSE solar_term_id + 3
              END) - 1) / 4)::INT + 1 as level
        FROM term_info
    ),
    lookup_ju AS (
        SELECT
            c.year_pillar, c.month_pillar, c.day_pillar, c.day_stem, c.day_branch, c.yy_str,
            (CASE 
                WHEN c.yy_key = 'yang' AND c.level = 1 THEN r.upper_ju_yang
                WHEN c.yy_key = 'yang' AND c.level = 2 THEN r.middle_ju_yang
                WHEN c.yy_key = 'yang' THEN r.lower_ju_yang
                WHEN c.yy_key = 'yin' AND c.level = 1 THEN r.upper_ju_yin
                WHEN c.yy_key = 'yin' AND c.level = 2 THEN r.middle_ju_yin
                ELSE r.lower_ju_yin
             END) as ju_num
        FROM calc_ju_idx c
        JOIN spr_jiazi_extended r ON r.stem = c.day_stem AND r.branch = c.day_branch
    ),
    rasklads AS (
        SELECT
            year_pillar, month_pillar, day_pillar,
            yy_str || '_' || ju_num || '_' || day_stem || day_branch as rasklad_id
        FROM lookup_ju
    )
    SELECT
        md5(r.year_pillar || '_' || r.month_pillar || '_' || r.day_pillar || '_' || t.palace_no) as chart_id,
        r.year_pillar,
        r.month_pillar,
        r.day_pillar,
        r.rasklad_id,
        t.palace_no,
        'Дневной'
    FROM rasklads r
    JOIN spr_qimen_templates t ON t.rasklad_id = r.rasklad_id
    ON CONFLICT (chart_id) DO NOTHING
    """
    db.execute_query(sql_day)

    # 5. Hourly Chart Calculation (Zhi Run)
    # Logic:
    # Fu Tou Offset = stem_idx % 5.
    # Fu Tou Date = curr_date - offset.
    # Term of Fu Tou.
    # Yuan = (JiaZi_Idx // 5) % 3. (Upper/Middle/Lower).
    # Ju = solar_term_ju[term][yuan].
    # Rasklad = {Yin/Yang}_{Ju}_{HourStem}{HourBranch}.
    
    print("Calculating Hourly Charts (Zhi Run)...")
    sql_hour = """
    INSERT INTO t_qumen_dgiren_hourly (chart_id, hour_id, rasklad_id, palace_no, chart_type)
    WITH base_data AS (
        SELECT 
            h.hour_id,
            h.slot_start_date_local::DATE as curr_date,
            h.day_stem, h.day_branch,
            h.hour_stem, h.hour_branch,
            hs.stem_id as d_stem_id,
            hb.branch_id as d_branch_id
        FROM t_bazi_hourly h
        JOIN spr_heavenly_stem hs ON hs.stem_char = h.day_stem
        JOIN spr_earthly_branch hb ON hb.branch_char = h.day_branch
    ),
    calc_futou AS (
        SELECT
            hour_id, curr_date, day_stem, day_branch, hour_stem, hour_branch,
            d_stem_id, d_branch_id,
            ((d_stem_id - 1) % 5) as offset_days,
            -- JiaZi Index for Day Pillar (to find Yuan)
            -- Logic in Python: get_jiazi_index(day_stem, day_branch)
            -- (6 * (s-1) - 5 * (b-1) + 60) % 60
            (6 * (d_stem_id - 1) - 5 * (d_branch_id - 1) + 60) % 60 as jiazi_idx
        FROM base_data
    ),
    futou_date AS (
        SELECT
            *,
            (curr_date - (offset_days || ' days')::INTERVAL)::DATE as f_date,
            (jiazi_idx / 5)::INT % 3 as yuan_idx -- 0, 1, 2
        FROM calc_futou
    ),
    term_lookup AS (
        SELECT
            f.hour_id, f.hour_stem, f.hour_branch, f.yuan_idx,
            st.solar_term_id
        FROM futou_date f
        JOIN LATERAL (
            SELECT solar_term_id
            FROM t_solar_term_time
            WHERE crossing_utc::DATE <= f.f_date
            ORDER BY crossing_utc DESC
            LIMIT 1
        ) st ON TRUE
    ),
    calc_ju AS (
        SELECT
            tl.hour_id, tl.hour_stem, tl.hour_branch,
            tl.solar_term_id,
            (CASE WHEN tl.solar_term_id BETWEEN 10 AND 21 THEN 'Yin' ELSE 'Yang' END) as yy_str,
            (CASE 
                WHEN tl.yuan_idx = 0 THEN st.upper_ju
                WHEN tl.yuan_idx = 1 THEN st.middle_ju
                ELSE st.lower_ju
             END) as ju_num
        FROM term_lookup tl
        JOIN spr_solar_term st ON st.solar_term_id = tl.solar_term_id
    ),
    rasklads AS (
        SELECT
            hour_id,
            yy_str || '_' || ju_num || '_' || hour_stem || hour_branch as rasklad_id
        FROM calc_ju
    )
    SELECT
        md5(r.hour_id || '_' || t.palace_no) as chart_id,
        r.hour_id,
        r.rasklad_id,
        t.palace_no,
        'Часовой'
    FROM rasklads r
    JOIN spr_qimen_templates t ON t.rasklad_id = r.rasklad_id
    """
    # Note: Inserting huge amount of rows.
    # Optimization: Chunking not easy in one query. PG handles millions okay if temp space allows.
    # 500k hours * 9 = 4.5M rows. Feasible in one go.
    
    db.execute_query(sql_hour)

    # 6. Indexes
    print("Creating Indexes...")
    db.execute_query("CREATE INDEX idx_qimen_hr_hour ON t_qumen_dgiren_hourly(hour_id)")
    db.execute_query("CREATE INDEX idx_qimen_d_date ON t_qumen_dgiren_day(year_pillar, month_pillar, day_pillar)")

    duration = time.time() - start_time
    print(f"Qimen (SQL) completed in {duration:.4f} seconds.")
    
    if logger and log_id:
        logger.end_stage(log_id)

if __name__ == "__main__":
    run_update()
