"""Расчёт Ци Мэнь Чай Бу (только часовой расклад).
Годовой, месячный и дневной Чай Бу удалены — для этих периодов используется метод Джи Рэн.
Обновлено: 2026-03-09
"""
import sys
import os
import time
import traceback

# Ensure we can import from code/ - MUST BE FIRST
sys.path.insert(0, os.getcwd())

try:
    from code.common.db_manager import db
    from code.common.config import load_config_from_db
except ImportError as e:
    print(f"Import Error: {e}")
    traceback.print_exc()
    sys.exit(1)

def run_update(logger=None):
    log_id = None
    if logger:
        log_id = logger.start_stage("Qimen Chai Bu Hourly (SQL-Centric)")

    print("Starting Qimen Chai Bu Hourly Calculation...")
    start_time = time.time()

    try:
        # Инициализация таблицы (только hourly)
        print("Recreating t_qumen_chauby_hourly...")
        db.execute_query("DROP TABLE IF EXISTS t_qumen_chauby_hourly CASCADE")
        db.execute_query("""
            CREATE TABLE t_qumen_chauby_hourly (
                chart_id TEXT PRIMARY KEY,
                hour_id TEXT NOT NULL,
                rasklad_id TEXT,
                palace_no INTEGER,
                chart_type TEXT
            )
        """)

        # Hourly Charts
        print("Calculating Hourly Charts (Chai Bu)...")
        sql_hour = """
        INSERT INTO t_qumen_chauby_hourly (chart_id, hour_id, rasklad_id, palace_no, chart_type)
        WITH base_data AS (
            SELECT 
                h.hour_id,
                h.solar_term_id,
                h.day_stem, h.day_branch,
                h.hour_stem, h.hour_branch,
                hs.stem_id as d_stem_id,
                hb.branch_id as d_branch_id
            FROM t_bazi_hourly h
            JOIN spr_heavenly_stem hs ON hs.stem_char = h.day_stem
            JOIN spr_earthly_branch hb ON hb.branch_char = h.day_branch
        ),
        calc_yuan AS (
            SELECT
                hour_id, solar_term_id, hour_stem, hour_branch,
                -- JiaZi Index for Day Pillar
                -- (6 * (s-1) - 5 * (b-1) + 60) % 60
                (6 * (d_stem_id - 1) - 5 * (d_branch_id - 1) + 60) % 60 as jiazi_idx
            FROM base_data
        ),
        calc_ju AS (
            SELECT
                c.hour_id, c.hour_stem, c.hour_branch,
                c.solar_term_id,
                (c.jiazi_idx / 5)::INT % 3 as yuan_idx, -- 0, 1, 2
                (CASE WHEN c.solar_term_id BETWEEN 10 AND 21 THEN 'Yin' ELSE 'Yang' END) as yy_str,
                (CASE WHEN c.solar_term_id BETWEEN 10 AND 21 THEN 'yin' ELSE 'yang' END) as yy_key
            FROM calc_yuan c
        ),
        lookup_ju AS (
            SELECT
                c.hour_id, c.hour_stem, c.hour_branch, c.yy_str,
                (CASE 
                    WHEN c.yuan_idx = 0 THEN st.upper_ju
                    WHEN c.yuan_idx = 1 THEN st.middle_ju
                    ELSE st.lower_ju
                 END) as ju_num
            FROM calc_ju c
            JOIN spr_solar_term st ON st.solar_term_id = c.solar_term_id
        ),
        rasklads AS (
            SELECT
                hour_id,
                yy_str || '_' || ju_num || '_' || hour_stem || hour_branch as rasklad_id
            FROM lookup_ju
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
        db.execute_query(sql_hour)

        # Индексы
        print("Creating Indexes...")
        db.execute_query("CREATE INDEX idx_qimen_cb_hr_hour ON t_qumen_chauby_hourly(hour_id)")

        duration = time.time() - start_time
        print(f"Qimen Chai Bu Hourly completed in {duration:.4f} seconds.")

        if logger and log_id:
            logger.end_stage(log_id)
            
    except Exception as e:
        print(f"Error in Chai Bu Calculation: {e}")
        traceback.print_exc()
        if logger and log_id:
            logger.fail_stage(log_id, str(e))
        sys.exit(1)

if __name__ == "__main__":
    run_update()
