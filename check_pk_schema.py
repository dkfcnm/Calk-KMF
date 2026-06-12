
import sys
import os
sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def check_schema_columns(table_name):
    print(f"Checking columns for {table_name}...")
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'")
        cols = cursor.fetchall()
        print(f"Columns: {[c[0] for c in cols]}")
        
        # Check PK
        cursor.execute(f"""
            SELECT a.attname
            FROM   pg_index i
            JOIN   pg_attribute a ON a.attrelid = i.indrelid
                                 AND a.attnum = ANY(i.indkey)
            WHERE  i.indrelid = '{table_name}'::regclass
            AND    i.indisprimary;
        """)
        pk_cols = cursor.fetchall()
        print(f"PK Columns: {[c[0] for c in pk_cols]}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema_columns("t_analysis_year")
    check_schema_columns("t_analysis_month")
