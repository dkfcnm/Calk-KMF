
import os
from typing import Dict, Any
from pathlib import Path

def load_env_file():
    """Simple .env loader to avoid external dependencies."""
    env_path = Path(__file__).resolve().parents[2] / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env_file()

# PostgreSQL Configuration
PG_CONFIG: Dict[str, Any] = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 5432)),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'calk_kmf')
}

# Path to PostgreSQL Binaries (pg_dump)
PG_BIN_PATH = os.environ.get('PG_BIN_PATH', r"d:\Program Files\PostgreSQL\18\bin")


def get_connection_params() -> Dict[str, Any]:
    """Returns connection parameters for PostgreSQL."""
    return PG_CONFIG
