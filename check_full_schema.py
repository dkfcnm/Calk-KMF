
import sys
import os
sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def check_schema(table_name):
    print(f"Checking {table_name}...")
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get columns
        cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
        cols = [r[0] for r in cursor.fetchall()]
        print(f"  Columns: {cols}")
        
        # Get PK
        cursor.execute(f"""
            SELECT a.attname
            FROM   pg_index i
            JOIN   pg_attribute a ON a.attrelid = i.indrelid
                                 AND a.attnum = ANY(i.indkey)
            WHERE  i.indrelid = '{table_name}'::regclass
            AND    i.indisprimary
        """)
        pk = [r[0] for r in cursor.fetchall()]
        print(f"  PK: {pk}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    tables = [
        "t_analysis_year", 
        "t_analysis_month", 
        "t_analysis_day", 
        "t_analysis_hour",
        "t_analysis_direction_year",
        "t_analysis_direction_month",
        "t_analysis_direction_day",
        "t_analysis_direction_hour"
    ]
    for t in tables:
        check_schema(t)
