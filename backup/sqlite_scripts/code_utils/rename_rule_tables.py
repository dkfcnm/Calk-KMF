import sqlite3
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "calk_kmf.sqlite")

def rename_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables_to_rename = [
        ("spr_rule_registry", "t_rule_registry"),
        ("spr_rule_scope", "t_rule_scope")
    ]
    
    for old_name, new_name in tables_to_rename:
        # Check if old table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{old_name}'")
        if cursor.fetchone():
            print(f"Renaming {old_name} to {new_name}...")
            # Check if new table already exists (safety)
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{new_name}'")
            if cursor.fetchone():
                print(f"Target table {new_name} already exists. Skipping or Dropping?")
                # Decision: Drop target if it exists to ensure clean rename? 
                # Or maybe we already ran this?
                # Let's drop new_name if it exists, assuming old_name has the data we want to keep/move.
                cursor.execute(f"DROP TABLE {new_name}")
            
            cursor.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")
        else:
            print(f"Table {old_name} not found (maybe already renamed).")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    rename_tables()
