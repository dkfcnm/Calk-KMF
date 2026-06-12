
import sys
import os

sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def check_perf_info():
    tables = ['t_qumen_dgiren_hourly', 'spr_qimen_templates', 't_bazi_hourly']
    
    print("Checking Table Info...")
    for t in tables:
        print(f"\nTable: {t}")
        try:
            # Columns
            cols = db.fetch_all(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{t}'")
            print("  Columns:")
            for c in cols:
                print(f"    {c[0]}: {c[1]}")
                
            # Indexes
            indexes = db.fetch_all(f"""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = '{t}'
            """)
            print("  Indexes:")
            if indexes:
                for idx in indexes:
                    print(f"    {idx[0]}: {idx[1]}")
            else:
                print("    (No indexes found)")
                
        except Exception as e:
            print(f"  Error checking {t}: {e}")

if __name__ == "__main__":
    check_perf_info()
