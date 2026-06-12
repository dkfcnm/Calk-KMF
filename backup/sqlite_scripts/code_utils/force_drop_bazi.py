import sqlite3
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "calk_kmf.sqlite")

def force_recreate_bazi_table():
    print("Forcing recreation of t_bazi_hourly...")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = OFF") # Important to avoid constraint errors
    
    try:
        # 1. Drop Views that depend on it
        print("Dropping views...")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name LIKE 'v_bazi_hourly%'")
        views = [row[0] for row in cursor.fetchall()]
        for v in views:
            conn.execute(f"DROP VIEW IF EXISTS {v}")
            
        # 2. Drop Table
        print("Dropping table t_bazi_hourly...")
        conn.execute("DROP TABLE IF EXISTS t_bazi_hourly")
        
        # 3. Vacuum to clear schema cache
        print("Vacuuming...")
        conn.execute("VACUUM")
        
        conn.commit()
        print("Table dropped successfully.")
    except Exception as e:
        print(f"Error dropping table: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    force_recreate_bazi_table()
