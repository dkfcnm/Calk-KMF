import sys
import os
from code.common.db_manager import db

sys.path.insert(0, os.getcwd())

def check_content():
    print("Checking t_bazi_hourly content types...")
    try:
        # Fetch one row
        row = db.fetch_all("""
            SELECT 
                year_stem, year_branch, 
                month_stem, month_branch,
                day_stem, day_branch,
                hour_stem, hour_branch
            FROM t_bazi_hourly 
            LIMIT 1
        """)
        if row:
            r = row[0]
            print(f"Year: {r[0]!r}/{r[1]!r}")
            print(f"Month: {r[2]!r}/{r[3]!r}")
            print(f"Day: {r[4]!r}/{r[5]!r}")
            print(f"Hour: {r[6]!r}/{r[7]!r}")
        else:
            print("t_bazi_hourly is empty.")
            
        # Check stem IDs
        stems = db.fetch_all("SELECT stem_id, stem_char FROM spr_heavenly_stem ORDER BY stem_id")
        print(f"Stems: {[(s[0], s[1]) for s in stems]}") # Will print tuple structure even if char fails display

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_content()
