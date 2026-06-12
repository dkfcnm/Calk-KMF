
import sys
import os
import time

sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def check_progress():
    tables = ['t_analysis_date', 't_analysis_direction', 't_analysis_activation']
    print(f"Checking analysis tables progress at {time.strftime('%H:%M:%S')}...")
    for t in tables:
        try:
            res = db.fetch_one(f"SELECT count(*) FROM {t}")
            print(f"  {t}: {res[0]} rows")
        except Exception as e:
            print(f"  {t}: Error ({e})")

if __name__ == "__main__":
    check_progress()
