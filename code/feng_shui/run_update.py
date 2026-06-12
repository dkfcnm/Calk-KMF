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
        log_id = logger.start_stage("Flying Stars Calculation (SQL)")

    print("Starting Flying Stars Calculation (SQL-Centric)...")
    start_time = time.time()

    # 1. Prepare Tables
    print("Recreating t_flying_stars table...")
    db.execute_query("DROP TABLE IF EXISTS t_flying_stars CASCADE")
    db.execute_query("""
    CREATE TABLE t_flying_stars (
        hour_id TEXT,
        palace INTEGER,
        year_star INTEGER,
        month_star INTEGER,
        day_star INTEGER,
        hour_star INTEGER,
        PRIMARY KEY (hour_id, palace)
    )
    """)
    
    # 2. Execute Huge Insert Query
    print("Executing SQL calculation...")
    
    # Note on Logic:
    # Year Star: 
    #   If term in (23, 24) [Xiao Han, Da Han], it's technically previous year for star calculation (Li Chun not reached).
    #   Formula: 10 - (Year % 100 % 9 + 1). If 0 -> 1.
    # Month Star:
    #   Join spr_month_stars (year_branch, month_branch).
    # Day Star:
    #   Find latest solstice (10 or 22) <= current date.
    #   Diff days.
    #   Winter (22): (diff % 9) + 1.
    #   Summer (10): 9 - (diff % 9).
    # Hour Star:
    #   Day Yin/Yang: Summer(10) <= term <= Da Xue(21) -> Yin(1). Else Yang(2).
    #   Join spr_hour_stars (day_branch, yin_yang, hour_branch).
    # Distribution:
    #   Join spr_flying_star_map for each star type.
    
    sql = """
    INSERT INTO t_flying_stars (hour_id, palace, year_star, month_star, day_star, hour_star)
    WITH base_data AS (
        SELECT 
            h.hour_id,
            h.slot_start_date_utc::DATE as curr_date,
            EXTRACT(YEAR FROM h.slot_start_date_utc::DATE)::INT as cal_year,
            h.year_branch,
            h.month_branch,
            h.day_branch,
            h.hour_branch,
            h.solar_term_id
        FROM t_bazi_hourly h
    ),
    solstices AS (
        SELECT 
            solar_term_id,
            crossing_utc::DATE as s_date
        FROM t_solar_term_time 
        WHERE solar_term_id IN (10, 22)
    ),
    -- Optimization: LATERAL on unique dates (~1K) instead of all rows (~354K)
    date_solstice AS (
        SELECT
            d.curr_date,
            s.solar_term_id as solstice_type,
            (d.curr_date - s.s_date) as days_diff
        FROM (SELECT DISTINCT curr_date FROM base_data) d
        LEFT JOIN LATERAL (
            SELECT solar_term_id, s_date
            FROM solstices st
            WHERE st.s_date <= d.curr_date
            ORDER BY st.s_date DESC
            LIMIT 1
        ) s ON TRUE
    ),
    calc_centers AS (
        SELECT
            b.hour_id,
            -- YEAR CENTER
            -- Logic: if term 23,24 -> year-1.
            (
                CASE 
                    WHEN b.solar_term_id IN (23, 24) THEN 
                         CASE WHEN (10 - ((b.cal_year - 1) % 100 % 9 + 1)) = 0 THEN 1 
                              ELSE (10 - ((b.cal_year - 1) % 100 % 9 + 1)) 
                         END
                    ELSE 
                         CASE WHEN (10 - (b.cal_year % 100 % 9 + 1)) = 0 THEN 1 
                              ELSE (10 - (b.cal_year % 100 % 9 + 1)) 
                         END
                END
            ) as year_center,
            
            b.year_branch,
            b.month_branch,
            
            -- DAY CENTER PREP
            ds.solstice_type,
            ds.days_diff,
            
            -- HOUR CENTER PREP
            -- Yin(1) if 10 <= term <= 21. Else Yang(2).
            (CASE WHEN b.solar_term_id BETWEEN 10 AND 21 THEN 1 ELSE 2 END) as day_yy,
            b.day_branch,
            b.hour_branch
            
        FROM base_data b
        LEFT JOIN date_solstice ds ON ds.curr_date = b.curr_date
    ),
    resolved_centers AS (
        SELECT
            c.hour_id,
            c.year_center,
            
            -- MONTH CENTER
            COALESCE(ms.star, 5) as month_center,
            
            -- DAY CENTER
            (CASE 
                WHEN c.solstice_type = 22 THEN -- Winter, Asc
                    (c.days_diff % 9) + 1
                ELSE -- Summer (10), Desc
                    9 - (c.days_diff % 9)
             END) as day_center,
             
             -- HOUR CENTER
             COALESCE(hs.star, 5) as hour_center
             
        FROM calc_centers c
        LEFT JOIN spr_month_stars ms 
            ON ms.year_branch = c.year_branch 
            AND ms.month_branch = c.month_branch
        LEFT JOIN spr_hour_stars hs 
            ON hs.day_branch = c.day_branch 
            AND hs.yin_yang = c.day_yy 
            AND hs.hour_branch = c.hour_branch
    )
    SELECT 
        rc.hour_id,
        m_y.palace,
        m_y.resident_star as year_star,
        m_m.resident_star as month_star,
        m_d.resident_star as day_star,
        m_h.resident_star as hour_star
    FROM resolved_centers rc
    -- Join map for Year Star
    JOIN spr_flying_star_map m_y ON m_y.center_star = rc.year_center
    -- Join map for Month Star (match palace)
    JOIN spr_flying_star_map m_m ON m_m.center_star = rc.month_center AND m_m.palace = m_y.palace
    -- Join map for Day Star (match palace)
    JOIN spr_flying_star_map m_d ON m_d.center_star = rc.day_center AND m_d.palace = m_y.palace
    -- Join map for Hour Star (match palace)
    JOIN spr_flying_star_map m_h ON m_h.center_star = rc.hour_center AND m_h.palace = m_y.palace
    """
    
    db.execute_query(sql)
    
    # 3. Indexes
    print("Creating index...")
    db.execute_query("CREATE INDEX idx_fs_hour ON t_flying_stars(hour_id)")
    
    duration = time.time() - start_time
    print(f"Flying Stars (SQL) completed in {duration:.4f} seconds.")
    
    if logger and log_id:
        logger.end_stage(log_id)

if __name__ == "__main__":
    run_update()
