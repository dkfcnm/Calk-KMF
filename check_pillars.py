
import sys
import os
sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def check_pillars():
    print("Checking pillars in t_bazi_hourly...")
    try:
        sql = """
        SELECT count(*) as total,
               count(year_pillar) as year_p,
               count(month_pillar) as month_p,
               count(day_pillar) as day_p,
               count(hour_pillar) as hour_p
        FROM t_bazi_hourly
        """
        row = db.fetch_one(sql)
        print(f"Total rows: {row[0]}")
        print(f"Year Pillars: {row[1]}")
        print(f"Month Pillars: {row[2]}")
        print(f"Day Pillars: {row[3]}")
        print(f"Hour Pillars: {row[4]}")
        
        if row[0] != row[1]:
            print("WARNING: Some rows are missing year_pillar!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_pillars()
