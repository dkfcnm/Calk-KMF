
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.getcwd())

from code.common.db_manager import db

def check_schema():
    tables = ['t_bazi_hourly', 'spr_solar_term']
    for t in tables:
        print(f"Checking {t} schema...")
        try:
            res = db.fetch_all(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{t}'
            """)
            for r in res:
                print(f"  {r[0]}: {r[1]}")
        except Exception as e:
            print(f"Error checking schema for {t}: {e}")

if __name__ == "__main__":
    check_schema()
