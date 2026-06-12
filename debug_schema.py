
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.getcwd())

from code.common.db_manager import db

def check_schema():
    print("Checking spr_solar_term schema...")
    try:
        # Check columns in spr_solar_term
        res = db.fetch_all("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'spr_solar_term'
        """)
        print("Columns in spr_solar_term:")
        for r in res:
            print(f"  {r[0]}: {r[1]}")
            
        # Check constraints
        res = db.fetch_all("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints
            WHERE table_name = 'spr_solar_term'
        """)
        print("Constraints on spr_solar_term:")
        for r in res:
            print(f"  {r[0]}: {r[1]}")

    except Exception as e:
        print(f"Error checking schema: {e}")

if __name__ == "__main__":
    check_schema()
