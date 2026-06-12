
import sys
import os

sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def check_qimen_indexes():
    table = 't_qumen_dgiren_hourly'
    print(f"Checking indexes for {table}...")
    try:
        indexes = db.fetch_all(f"""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = '{table}'
        """)
        if indexes:
            for idx in indexes:
                print(f"  {idx[0]}: {idx[1]}")
        else:
            print("  No indexes found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_qimen_indexes()
