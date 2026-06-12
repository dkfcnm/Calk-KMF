from code.common.db_manager import db

def list_tables():
    print("Listing tables in public schema:")
    try:
        rows = db.fetch_all("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
        for r in rows:
            print(r[0])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_tables()
