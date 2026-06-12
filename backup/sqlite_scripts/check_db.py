import sqlite3
import os

db_path = "e:/Project/Calk_KMF/calk_kmf.sqlite"
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cursor.fetchall()]
    print(f"Found {len(tables)} tables.")
    print("Tables:", tables)
    
    # Check key tables for row counts
    key_tables = ['spr_heavenly_stem', 't_qumen_dgiren_hourly', 't_flying_stars', 'spr_qimen_templates']
    for t in key_tables:
        if t in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {t}")
            count = cursor.fetchone()[0]
            print(f"{t}: {count} rows")
        else:
            print(f"{t}: MISSING")
            
    conn.close()
