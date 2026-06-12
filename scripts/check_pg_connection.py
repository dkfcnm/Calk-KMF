
import sys
import os

# Добавляем корневую директорию в sys.path
sys.path.insert(0, os.getcwd())

from code.common.db_manager import db

def check_db():
    print("Checking DB connection...")
    try:
        # Пробуем получить список таблиц из public схемы PostgreSQL
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        tables = db.fetch_all(query)
        print(f"Connection successful. Found {len(tables)} tables.")
        for t in tables[:5]:
            print(f"- {t[0]}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check_db()
