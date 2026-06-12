from code.common.db_manager import db
import sys

def check_schema():
    print("Checking schema...")
    try:
        # Check t_rule_registry columns
        if 'sqlite' in str(db.conn):
            cols = db.fetch_all("PRAGMA table_info(t_rule_registry)")
            print("t_rule_registry columns (SQLite):", [c[1] for c in cols])
        else:
            cols = db.fetch_all("SELECT column_name FROM information_schema.columns WHERE table_name = 't_rule_registry'")
            print("t_rule_registry columns (PG):", [c[0] for c in cols])
            
        # Check spr_rule_registry columns
        if 'sqlite' in str(db.conn):
            cols = db.fetch_all("PRAGMA table_info(spr_rule_registry)")
            print("spr_rule_registry columns (SQLite):", [c[1] for c in cols])
        else:
            cols = db.fetch_all("SELECT column_name FROM information_schema.columns WHERE table_name = 'spr_rule_registry'")
            print("spr_rule_registry columns (PG):", [c[0] for c in cols])

    except Exception as e:
        print(f"Error checking schema: {e}")

if __name__ == "__main__":
    check_schema()
