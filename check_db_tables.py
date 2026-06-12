import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "calk_kmf")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "postgres")

print(f"Connecting to postgresql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

try:
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )
        ).fetchall()
        print(f"Found {len(result)} tables:")
        for row in result:
            print(f" - {row[0]}")
except Exception as e:
    print(f"Error: {e}")
