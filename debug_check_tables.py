
import sys
import os

sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def check_tables():
    tables = ['t_rule_registry', 't_rule_scope', 't_qumen_dgiren_hourly']
    for t in tables:
        try:
            res = db.fetch_one(f"SELECT count(*) FROM {t}")
            print(f"{t}: {res[0]} rows")
        except Exception as e:
            print(f"{t}: Error/Missing ({e})")

if __name__ == "__main__":
    check_tables()
