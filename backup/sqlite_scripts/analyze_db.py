import sqlite3
import os

db_path = 'e:/Project/Calk_KMF/calk_kmf.sqlite'

def analyze():
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=== INDEXES ===")
    cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
    for row in cursor.fetchall():
        print(f"Index: {row[0]} ON {row[1]}")
        print(f"  SQL: {row[2]}")
        print("-" * 20)

    print("\n=== TABLE ROW COUNTS ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [r[0] for r in cursor.fetchall()]
    for tbl in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
            cnt = cursor.fetchone()[0]
            print(f"{tbl}: {cnt}")
        except Exception as e:
            print(f"{tbl}: Error {e}")

    conn.close()

if __name__ == "__main__":
    analyze()
