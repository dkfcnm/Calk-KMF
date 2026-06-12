from code.common.db_manager import db

def check_schemas():
    tables = ['t_rule_registry', 't_bazi_hourly']
    for t in tables:
        print(f"--- {t} ---")
        try:
            # pg8000 doesn't support dictionary cursor easily, so we query information_schema
            rows = db.fetch_all(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{t}' ORDER BY ordinal_position")
            for r in rows:
                print(f"{r[0]}: {r[1]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_schemas()
