from code.common.db_manager import db

def check_qimen_schema():
    print("Checking Qimen tables schema...")
    tables = [
        't_qumen_dgiren_hourly', 
        't_qumen_chauby_hourly',
        't_qumen_dgiren_day',
        't_qumen_chauby_day'
    ]
    for t in tables:
        print(f"\n--- {t} ---")
        try:
            rows = db.fetch_all(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{t}' ORDER BY ordinal_position")
            for r in rows:
                print(f"{r[0]}: {r[1]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_qimen_schema()
