import sys
import os
import time
from datetime import date

# Ensure we can import from code/
sys.path.insert(0, os.getcwd())

from code.common.db_manager import db

def run_update(year_start=2026, year_end=2026, logger=None):
    log_id = None
    if logger:
        log_id = logger.start_stage("Tai Yi Calculation (SQL Optimized)")

    print(f"Starting Tai Yi calculation (SQL Optimized) for {year_start}-{year_end}...")
    start_time = time.time()
    
    # 1. Create Tables
    print("Creating tables...")
    with db.get_cursor(commit=True) as cursor:
        # Daily Chart Table
        try:
             cursor.execute("DROP TABLE IF EXISTS t_taiyi_day CASCADE")
        except:
             cursor.execute("DROP TABLE IF EXISTS t_taiyi_day")

        cursor.execute("""
            CREATE TABLE t_taiyi_day (
                date_val DATE PRIMARY KEY,
                day_ganzhi_idx INTEGER,
                day_stem INTEGER,
                day_branch INTEGER,
                solar_term_id INTEGER,
                run_type TEXT,
                
                -- Chart Roots
                xiu_men_palace INTEGER,
                tai_yi_palace INTEGER,
                xi_shen_palace INTEGER,
                
                -- Palace Scores
                palace_1_score INTEGER,
                palace_2_score INTEGER,
                palace_3_score INTEGER,
                palace_4_score INTEGER,
                palace_5_score INTEGER,
                palace_6_score INTEGER,
                palace_7_score INTEGER,
                palace_8_score INTEGER,
                palace_9_score INTEGER,
                
                chart_data JSONB
            )
        """)
        
        # Hourly Details Table
        try:
            cursor.execute("DROP TABLE IF EXISTS t_taiyi_hours CASCADE")
        except:
            cursor.execute("DROP TABLE IF EXISTS t_taiyi_hours")

        cursor.execute("""
            CREATE TABLE t_taiyi_hours (
                date_val DATE,
                hour_branch INTEGER, -- 1..12 (Zi..Hai)
                spirit_name TEXT,
                spirit_score INTEGER,
                is_noble BOOLEAN,
                is_kong_wang BOOLEAN,
                
                PRIMARY KEY (date_val, hour_branch)
            )
        """)
        
        cursor.execute("CREATE INDEX idx_taiyi_hours_date ON t_taiyi_hours(date_val)")

    # 2. Execute Calculation via SQL
    print("Executing SQL calculation...")
    
    sql_logic = f"""
    WITH params AS (
        SELECT '{year_start}-01-01'::date as start_date, '{year_end}-12-31'::date as end_date
    ),
    calendar AS (
        SELECT 
            d::date as date_val,
            (d::date - '1984-01-31'::date) % 60 as day_idx_60
        FROM params, generate_series(start_date, end_date, '1 day'::interval) d
    ),
    solar_terms AS (
        SELECT 
            c.date_val,
            c.day_idx_60,
            (c.day_idx_60 % 10) + 1 as day_stem,
            (c.day_idx_60 % 12) + 1 as day_branch,
            st.solar_term_id,
            CASE WHEN st.solar_term_id BETWEEN 10 AND 21 THEN 'YIN' ELSE 'YANG' END as run_type,
            (c.day_idx_60 / 3) % 8 as xiu_seq_idx,
            (c.day_idx_60 / 10) as decade_idx,
            (c.day_idx_60 % 10) as day_in_decade
        FROM calendar c
        LEFT JOIN LATERAL (
            SELECT solar_term_id 
            FROM t_solar_term_time 
            WHERE crossing_utc <= (c.date_val + time '12:00') AT TIME ZONE 'UTC'
            ORDER BY crossing_utc DESC 
            LIMIT 1
        ) st ON true
    ),
    calc_roots AS (
        SELECT 
            st.*,
            -- Xiu Men Palace from Sequence Table
            gs.palace_id as xiu_men_palace,
            
            -- Tai Yi Palace Calculation
            -- Formula using Start Palace from Table
            CASE WHEN st.run_type = 'YANG'
                 THEN ((ss.start_palace - 1 + st.day_in_decade) % 9) + 1
                 ELSE ((ss.start_palace - 1 - st.day_in_decade + 90) % 9) + 1
            END as tai_yi_palace,
            
            -- Xi Shen Palace from Table
            xs.palace_id as xi_shen_palace
            
        FROM solar_terms st
        LEFT JOIN spr_taiyi_gate_seq gs ON gs.cycle_type = st.run_type AND gs.seq_idx = st.xiu_seq_idx
        LEFT JOIN spr_taiyi_star_start ss ON ss.cycle_type = st.run_type AND ss.decade_idx = st.decade_idx
        LEFT JOIN spr_taiyi_xi_shen xs ON xs.day_stem_id = st.day_stem
    ),
    palace_calc AS (
        SELECT 
            cr.*,
            p.palace_id,
            -- Gate ID Calculation
            -- Yang Stem (odd): (P_idx - Start_idx) % 8
            -- Yin Stem (even): (Start_idx - P_idx) % 8
            -- We need Ring Index for P and StartP
            (CASE WHEN (cr.day_stem % 2) != 0 
                 THEN (p.ring_idx - pr_start.ring_idx + 8) % 8
                 ELSE (pr_start.ring_idx - p.ring_idx + 8) % 8
            END) as gate_seq_id, -- This maps to 0..7 index in spr_taiyi_gates order (id)
            
            -- Star ID Calculation
            -- (P - TaiYi + 9) % 9 + 1
            ((p.palace_id - cr.tai_yi_palace + 9) % 9) + 1 as star_id
            
        FROM calc_roots cr
        CROSS JOIN spr_taiyi_palace_ring p
        JOIN spr_taiyi_palace_ring pr_start ON pr_start.palace_id = cr.xiu_men_palace
    ),
    day_insert AS (
        INSERT INTO t_taiyi_day (
            date_val, day_ganzhi_idx, day_stem, day_branch, solar_term_id, run_type,
            xiu_men_palace, tai_yi_palace, xi_shen_palace,
            palace_1_score, palace_2_score, palace_3_score, palace_4_score, 
            palace_5_score, palace_6_score, palace_7_score, palace_8_score, palace_9_score,
            chart_data
        )
        SELECT 
            pc.date_val,
            max(pc.day_idx_60), max(pc.day_stem), max(pc.day_branch), max(pc.solar_term_id), max(pc.run_type),
            max(pc.xiu_men_palace), max(pc.tai_yi_palace), max(pc.xi_shen_palace),
            
            max(CASE WHEN pc.palace_id=1 THEN g.lucky_score + s.lucky_score + (CASE WHEN pc.palace_id = pc.xi_shen_palace THEN 1 ELSE 0 END) END),
            max(CASE WHEN pc.palace_id=2 THEN g.lucky_score + s.lucky_score + (CASE WHEN pc.palace_id = pc.xi_shen_palace THEN 1 ELSE 0 END) END),
            max(CASE WHEN pc.palace_id=3 THEN g.lucky_score + s.lucky_score + (CASE WHEN pc.palace_id = pc.xi_shen_palace THEN 1 ELSE 0 END) END),
            max(CASE WHEN pc.palace_id=4 THEN g.lucky_score + s.lucky_score + (CASE WHEN pc.palace_id = pc.xi_shen_palace THEN 1 ELSE 0 END) END),
            max(CASE WHEN pc.palace_id=5 THEN g.lucky_score + s.lucky_score + (CASE WHEN pc.palace_id = pc.xi_shen_palace THEN 1 ELSE 0 END) END),
            max(CASE WHEN pc.palace_id=6 THEN g.lucky_score + s.lucky_score + (CASE WHEN pc.palace_id = pc.xi_shen_palace THEN 1 ELSE 0 END) END),
            max(CASE WHEN pc.palace_id=7 THEN g.lucky_score + s.lucky_score + (CASE WHEN pc.palace_id = pc.xi_shen_palace THEN 1 ELSE 0 END) END),
            max(CASE WHEN pc.palace_id=8 THEN g.lucky_score + s.lucky_score + (CASE WHEN pc.palace_id = pc.xi_shen_palace THEN 1 ELSE 0 END) END),
            max(CASE WHEN pc.palace_id=9 THEN g.lucky_score + s.lucky_score + (CASE WHEN pc.palace_id = pc.xi_shen_palace THEN 1 ELSE 0 END) END),
            
            jsonb_object_agg(pc.palace_id, jsonb_build_object(
                'gate', g.code, 
                'gate_score', g.lucky_score,
                'star', s.code,
                'star_score', s.lucky_score,
                'total_score', g.lucky_score + s.lucky_score + (CASE WHEN pc.palace_id = pc.xi_shen_palace THEN 1 ELSE 0 END)
            ))
        FROM palace_calc pc
        JOIN spr_taiyi_gates g ON g.id = pc.gate_seq_id
        JOIN spr_taiyi_stars s ON s.id = pc.star_id
        GROUP BY pc.date_val
        RETURNING 1
    )
    INSERT INTO t_taiyi_hours (
        date_val, hour_branch, spirit_name, spirit_score, is_noble, is_kong_wang
    )
    SELECT 
        cr.date_val,
        h.h_idx,
        sp.code,
        -- Score adjustment: +1 if noble, -1 if kong wang
        sp.lucky_score + (CASE WHEN (nh.day_stem_id IS NOT NULL) THEN 1 ELSE 0 END) - (CASE WHEN (kw.day_stem_id IS NOT NULL) THEN 1 ELSE 0 END),
        (nh.day_stem_id IS NOT NULL),
        (kw.day_stem_id IS NOT NULL)
    FROM calc_roots cr
    CROSS JOIN generate_series(1, 12) as h(h_idx)
    JOIN spr_taiyi_qing_long_start qls ON qls.day_branch_id = cr.day_branch
    JOIN spr_taiyi_spirits sp ON sp.id = ((h.h_idx - qls.start_hour_idx + 12) % 12)
    LEFT JOIN spr_taiyi_noble nh ON nh.day_stem_id = cr.day_stem AND nh.hour_branch_id = h.h_idx
    LEFT JOIN spr_taiyi_kong_wang kw ON kw.day_stem_id = cr.day_stem AND kw.hour_branch_id = h.h_idx;
    """
    
    with db.get_cursor(commit=True) as cursor:
        cursor.execute(sql_logic)
        
    duration = time.time() - start_time
    print(f"Tai Yi (SQL Optimized) completed in {duration:.4f} seconds.")

if __name__ == "__main__":
    run_update()
