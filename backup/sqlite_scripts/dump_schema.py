import sqlite3
import sys

def dump_schema():
    conn = sqlite3.connect('e:/Project/Calk_KMF/calk_kmf.sqlite')
    cursor = conn.cursor()
    
    print("=== TABLES ===")
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    for name, sql in cursor.fetchall():
        print(f"--- {name} ---")
        print(sql)
        print("\n")

    print("=== INDEXES ===")
    cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
    for name, tbl_name, sql in cursor.fetchall():
        print(f"--- {name} on {tbl_name} ---")
        print(sql)
        print("\n")
        
    conn.close()

if __name__ == "__main__":
    dump_schema()
