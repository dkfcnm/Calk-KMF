
import sys
import os

sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def check_views():
    try:
        res = db.fetch_all("SELECT table_name FROM information_schema.views WHERE table_schema = 'public'")
        print("Views found:")
        for r in res:
            print(f" - {r[0]}")
    except Exception as e:
        print(f"Error checking views: {e}")

if __name__ == "__main__":
    check_views()
