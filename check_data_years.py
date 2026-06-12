
import sys
import os
sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def check_years():
    print("Checking available years in t_bazi_hourly...")
    try:
        sql = "SELECT DISTINCT substring(slot_start_date_utc, 1, 4) as year FROM t_bazi_hourly ORDER BY 1"
        rows = db.fetch_all(sql)
        print(f"Years found: {[r[0] for r in rows]}")
        
        sql_count = "SELECT substring(slot_start_date_utc, 1, 4) as year, COUNT(*) FROM t_bazi_hourly GROUP BY 1 ORDER BY 1"
        rows_count = db.fetch_all(sql_count)
        for r in rows_count:
            print(f"Year {r[0]}: {r[1]} rows")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_years()
