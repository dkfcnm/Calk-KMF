import sqlite3
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "calk_kmf.sqlite")

def fix_and_rename():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Drop broken view
    print("Dropping broken view v_qimen_chaiby...")
    cursor.execute("DROP VIEW IF EXISTS v_qimen_chaiby")
    print("Dropping broken view v_good_walk...")
    cursor.execute("DROP VIEW IF EXISTS v_good_walk")
    
    # Drop Bazi Views causing lock
    print("Dropping bazi views...")
    cursor.execute("DROP VIEW IF EXISTS v_bazi_hourly_msk")
    cursor.execute("DROP VIEW IF EXISTS v_bazi_hourly")
    # Drop TZ views too? It's easier to drop them by pattern but python sql doesn't support wildcard drop.
    # We can iterate.
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name LIKE 'v_bazi_hourly%'")
    views = [row[0] for row in cursor.fetchall()]
    for v in views:
        cursor.execute(f"DROP VIEW IF EXISTS {v}")
        
    print("Dropping qimen views...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name LIKE 'v_qimen%'")
    views = [row[0] for row in cursor.fetchall()]
    for v in views:
        cursor.execute(f"DROP VIEW IF EXISTS {v}")
    
    # 2. Rename tables
    tables_to_rename = [
        ("spr_rule_registry", "t_rule_registry"),
        ("spr_rule_scope", "t_rule_scope")
    ]
    
    for old_name, new_name in tables_to_rename:
        # Check if old table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{old_name}'")
        if cursor.fetchone():
            print(f"Renaming {old_name} to {new_name}...")
            # Check if new table already exists
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{new_name}'")
            if cursor.fetchone():
                print(f"Target table {new_name} already exists. Dropping it.")
                cursor.execute(f"DROP TABLE {new_name}")
            
            cursor.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")
        else:
            print(f"Table {old_name} not found (maybe already renamed).")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix_and_rename()
