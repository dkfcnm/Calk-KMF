"""Инфраструктурные функции работы с базой данных проекта.

Назначение модуля:
- предоставить доступ к центральному менеджеру базы данных (DBManager);
- обеспечить функции получения соединения для легаси-кода;
- предоставить утилиты работы с временем (ensure_utc, parse_timestamp).

Ключевые константы:
- `PROJECT_ROOT`: корень репозитория;

Последнее обновление: 2026-06-05.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any

from code.common.db_config import PG_CONFIG, PG_BIN_PATH
from code.common.db_manager import db as db_manager
import subprocess
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def get_connection() -> Any:
    """Возвращает соединение с PostgreSQL."""
    return db_manager.get_connection()


def backup_db(backup_dir: Optional[Path] = None) -> Path:
    """Создаёт резервную копию базы данных PostgreSQL и возвращает путь к копии."""

    if backup_dir is None:
        backup_dir = PROJECT_ROOT / "backup"
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"calk_kmf_pg_backup_{timestamp}.sql"

    # pg_dump parameters
    pg_dump_exe = Path(PG_BIN_PATH) / "pg_dump.exe"
    if not pg_dump_exe.exists():
        # Fallback: try just 'pg_dump' if explicitly not found at path, or warn
        print(f"WARNING: pg_dump not found at {pg_dump_exe}. Trying system PATH.")
        pg_dump_exe = "pg_dump"

    env = os.environ.copy()
    env["PGPASSWORD"] = PG_CONFIG['password']

    cmd = [
        str(pg_dump_exe),
        "-h", PG_CONFIG['host'],
        "-p", str(PG_CONFIG['port']),
        "-U", PG_CONFIG['user'],
        "-F", "c",  # Custom format (compressed)
        "-b",       # Include large objects
        "-v",       # Verbose
        "-f", str(backup_file),
        PG_CONFIG['database']
    ]

    print(f"Starting PostgreSQL backup to {backup_file}...")
    try:
        subprocess.run(cmd, env=env, check=True)
        print("Backup completed successfully.")
        return backup_file
    except subprocess.CalledProcessError as e:
        print(f"Error during pg_dump: {e}")
        raise
    except FileNotFoundError:
        print(f"Error: pg_dump executable not found. Please check PG_BIN_PATH in config.")
        raise


def vacuum_analyze_db():
    """Выполняет обслуживание базы данных (VACUUM + ANALYZE)."""
    print("Starting Database Maintenance...")
    # pg8000 does not support VACUUM inside a transaction block easily via cursor.execute
    # VACUUM cannot run inside a transaction block.
    # We need a raw connection with autocommit.
    try:
        import pg8000.native
        conn = pg8000.native.Connection(
            user=PG_CONFIG['user'],
            password=PG_CONFIG['password'],
            host=PG_CONFIG['host'],
            port=PG_CONFIG['port'],
            database=PG_CONFIG['database']
        )
        print("Running VACUUM (FULL, ANALYZE)...")
        conn.run("VACUUM (ANALYZE)")
        conn.close()
        print("PostgreSQL Maintenance completed.")
    except Exception as e:
        print(f"Error during PG maintenance: {e}")


def ensure_utc(dt: datetime) -> datetime:
    """Возвращает `datetime` с tzinfo=UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_timestamp(raw_value: Any) -> datetime:
    """Парсит текстовое поле с временем или возвращает datetime без изменений."""
    if isinstance(raw_value, datetime):
        return ensure_utc(raw_value)

    if not isinstance(raw_value, str):
        # Fallback for unexpected types
        return raw_value

    dt = datetime.fromisoformat(raw_value)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def get_placeholder() -> str:
    """Возвращает символ плейсхолдера для PostgreSQL (%s)."""
    return "%s"
