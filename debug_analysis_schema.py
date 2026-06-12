
import sys
import os

sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def check_analysis_schema():
    tables = ['spr_indicator_value', 't_analysis_date']
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
    check_analysis_schema()
