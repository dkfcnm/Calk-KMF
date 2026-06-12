
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.getcwd())

from code.common.db_manager import db

def check_count():
    try:
        res = db.fetch_one("SELECT count(*) FROM t_bazi_hourly")
        print(f"t_bazi_hourly count: {res[0]}")
    except Exception as e:
        print(f"Error checking count: {e}")

if __name__ == "__main__":
    check_count()
