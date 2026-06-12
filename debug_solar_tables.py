
import sys
import os

sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def check_solar_tables():
    tables = ['t_solar_term_time', 't_solar_term_time_hko']
    print("Checking solar term tables...")
    for t in tables:
        try:
            res = db.fetch_one(f"SELECT count(*) FROM {t}")
            print(f"  {t}: {res[0]} rows")
        except Exception as e:
            print(f"  {t}: Error ({e})")

if __name__ == "__main__":
    check_solar_tables()
