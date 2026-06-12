
import sys
import os
import io

# Set stdout to utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def check_base_tables():
    print("Checking Base Metaphysical Data for 2025-2027...")
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        years = [2025, 2026, 2027]
        # Tables that should have data for these years
        tables_to_check = [
            # Qimen ZhiRun
            "t_qumen_dgiren_year",
            "t_qumen_dgiren_month",
            "t_qumen_dgiren_day",
            "t_qumen_dgiren_hourly",
            # Flying Stars
            "t_flying_stars"
        ]
        
        for t in tables_to_check:
            print(f"\nTable: {t}")
            for y in years:
                count = 0
                if "hourly" in t or "flying_stars" in t:
                    # hour_id based check (assumes hour_id starts with YYYY)
                    # Note: t_flying_stars has hour_id
                    cursor.execute(f"SELECT COUNT(*) FROM {t} WHERE hour_id LIKE '{y}%'")
                elif "day" in t:
                    # day_pillar doesn't help with year directly without join or if there is a date column?
                    # t_qumen_dgiren_day: chart_id, day_pillar, month_pillar, year_pillar... no date column usually, it's a mapping?
                    # Wait, t_qumen_dgiren_day links chart_id to pillars.
                    # Actually run_analysis joins t_bazi_hourly with t_qumen_dgiren_day on pillars.
                    # So t_qumen_dgiren_day is a lookup table of unique pillar combos?
                    # Let's check schema.
                    pass 
                elif "year" in t and "qumen" in t:
                     # t_qumen_dgiren_year: year_pillar -> chart_id. 
                     # It likely doesn't have a 'year' column, just pillars.
                     pass
                
                # Actually, Qimen tables in this project (optimized) might be lookups or actual timeseries.
                # In Architecture v2: 
                # "t_qumen_dgiren_hourly: Часовые расклады." -> Time series?
                # "t_qumen_dgiren_year... Все таблицы имеют chart_id (PK, хэш-код параметров)." -> These sound like lookups.
                
                # If they are lookups, we can't check by 'year' easily.
                # But t_qumen_dgiren_hourly MUST be time series to support "Hourly" charts over time?
                # Or does it link hour_pillar to chart?
                
                # Let's check t_qumen_dgiren_hourly columns.
                try:
                    cursor.execute(f"SELECT * FROM {t} LIMIT 1")
                    cols = [desc[0] for desc in cursor.description]
                    # print(f"  Cols: {cols}")
                    
                    if 'hour_id' in cols:
                        cursor.execute(f"SELECT COUNT(*) FROM {t} WHERE hour_id LIKE '{y}%'")
                        count = cursor.fetchone()[0]
                        print(f"  {y}: {count}")
                    elif 'year' in cols:
                        cursor.execute(f"SELECT COUNT(*) FROM {t} WHERE year = {y}")
                        count = cursor.fetchone()[0]
                        print(f"  {y}: {count}")
                    else:
                        print(f"  (Skipping year check, likely lookup table)")
                        break
                except Exception as e:
                    print(f"  Error checking {t}: {e}")
                    break

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Check failed: {e}")

if __name__ == "__main__":
    check_base_tables()
