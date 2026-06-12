
import sys
import os
import io

# Set stdout to utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def check_years():
    print("Checking Analysis Data for 2025, 2026, 2027...")
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        years = [2025, 2026, 2027]
        tables = [
            "t_analysis_year", 
            "t_analysis_month", 
            "t_analysis_day", 
            "t_analysis_hour",
            "t_analysis_direction_year", 
            "t_analysis_direction_month", 
            "t_analysis_direction_day", 
            "t_analysis_direction_hour"
        ]
        
        # Check t_bazi_hourly first
        print("\n> Source Data (t_bazi_hourly):")
        for y in years:
            cursor.execute(f"SELECT COUNT(*) FROM t_bazi_hourly WHERE substring(slot_start_date_utc, 1, 4) = '{y}'")
            count = cursor.fetchone()[0]
            print(f"  {y}: {count} records")

        print("\n> Analysis Tables:")
        for t in tables:
            print(f"  Table: {t}")
            for y in years:
                count = 0
                if "hour" in t and "direction" not in t:
                     # t_analysis_hour joined with t_bazi_hourly
                     query = f"""
                        SELECT COUNT(a.hour_id) 
                        FROM {t} a 
                        JOIN t_bazi_hourly b ON a.hour_id = b.hour_id 
                        WHERE substring(b.slot_start_date_utc, 1, 4) = '{y}'
                     """
                     cursor.execute(query)
                elif "direction_hour" in t:
                     # t_analysis_direction_hour joined with t_bazi_hourly
                     query = f"""
                        SELECT COUNT(a.hour_id) 
                        FROM {t} a 
                        JOIN t_bazi_hourly b ON a.hour_id = b.hour_id 
                        WHERE substring(b.slot_start_date_utc, 1, 4) = '{y}'
                     """
                     cursor.execute(query)
                elif "day" in t or "direction_day" in t:
                     # date_val year
                     cursor.execute(f"SELECT COUNT(*) FROM {t} WHERE extract(year from date_val) = {y}")
                else:
                     # year column
                     cursor.execute(f"SELECT COUNT(*) FROM {t} WHERE year = {y}")
                
                count = cursor.fetchone()[0]
                print(f"    {y}: {count}")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Check failed: {e}")

if __name__ == "__main__":
    check_years()
