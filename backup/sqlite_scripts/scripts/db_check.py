#!/usr/bin/env python3
"""
Унифицированный скрипт диагностики базы данных Calk_KMF.
Заменяет набор check_*.py скриптов.

Использование:
    python scripts/db_check.py --db-type sqlite --check tables
    python scripts/db_check.py --db-type postgres --check indexes
    python scripts/db_check.py --db-type sqlite --check schema --table t_bazi_hourly
    python scripts/db_check.py --db-type postgres --check stats
"""

import argparse
import os
import sqlite3
import sys
from pathlib import Path

# Добавляем корень проекта в путь
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def get_sqlite_connection(db_path=None):
    """Подключение к SQLite."""
    if db_path is None:
        db_path = PROJECT_ROOT / "calk_kmf.sqlite"
    return sqlite3.connect(str(db_path))


def get_postgres_connection():
    """Подключение к PostgreSQL через DBManager."""
    try:
        from code.common.db_manager import db
        return db
    except ImportError:
        print("ERROR: Cannot import DBManager. Make sure code/common/db_manager.py exists.")
        sys.exit(1)


def check_tables_sqlite(conn):
    """Список таблиц SQLite с примерным количеством строк."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()

    print(f"{'Table Name':<50} {'Rows (approx)':>15}")
    print("-" * 67)
    for (name,) in tables:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM "{name}"')
            count = cursor.fetchone()[0]
        except Exception:
            count = "N/A"
        print(f"{name:<50} {count:>15}")


def check_indexes_sqlite(conn):
    """Список индексов SQLite."""
    cursor = conn.cursor()
    cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' ORDER BY tbl_name, name")
    indexes = cursor.fetchall()

    print(f"{'Table':<40} {'Index Name':<50} {'SQL':<30}")
    print("-" * 120)
    for name, tbl_name, sql in indexes:
        print(f"{tbl_name:<40} {name:<50} {str(sql)[:30]:<30}")


def check_schema_sqlite(conn, table_name=None):
    """Схема таблиц SQLite."""
    cursor = conn.cursor()
    if table_name:
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        columns = cursor.fetchall()
        print(f"\nSchema for table: {table_name}")
        print(f"{'CID':>5} {'Name':<30} {'Type':<15} {'NotNull':>8} {'Default':<15} {'PK':>3}")
        print("-" * 80)
        for col in columns:
            print(f"{col[0]:>5} {col[1]:<30} {col[2]:<15} {col[3]:>8} {str(col[4]):<15} {col[5]:>3}")
    else:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        for (name,) in tables:
            print(f"\n{'='*60}")
            check_schema_sqlite(conn, name)


def check_stats_sqlite(conn):
    """Статистика SQLite БД."""
    cursor = conn.cursor()
    cursor.execute("PRAGMA page_count")
    page_count = cursor.fetchone()[0]
    cursor.execute("PRAGMA page_size")
    page_size = cursor.fetchone()[0]
    size_mb = (page_count * page_size) / (1024 * 1024)

    print(f"Database file size: {size_mb:.2f} MB")
    print(f"Page count: {page_count}")
    print(f"Page size: {page_size} bytes")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    total_rows = 0
    for (name,) in tables:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM "{name}"')
            count = cursor.fetchone()[0]
            total_rows += count
        except Exception:
            pass
    print(f"Total rows across all tables: {total_rows:,}")


def check_tables_postgres(db):
    """Список таблиц PostgreSQL."""
    query = """
    SELECT schemaname, tablename,
           (SELECT COUNT(*) FROM information_schema.columns c WHERE c.table_name = t.tablename) as col_count
    FROM pg_tables t
    WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
    ORDER BY schemaname, tablename;
    """
    results = db.execute_query(query)
    print(f"{'Schema':<20} {'Table':<50} {'Columns':>10}")
    print("-" * 82)
    for row in results:
        print(f"{row[0]:<20} {row[1]:<50} {row[2]:>10}")


def check_indexes_postgres(db):
    """Список индексов PostgreSQL."""
    query = """
    SELECT schemaname, tablename, indexname, indexdef
    FROM pg_indexes
    WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
    ORDER BY tablename, indexname;
    """
    results = db.execute_query(query)
    print(f"{'Table':<40} {'Index':<50}")
    print("-" * 90)
    for row in results:
        print(f"{row[1]:<40} {row[2]:<50}")


def check_schema_postgres(db, table_name=None):
    """Схема таблиц PostgreSQL."""
    if table_name:
        query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;
        """
        results = db.execute_query(query, (table_name,))
        print(f"\nSchema for table: {table_name}")
        print(f"{'Column':<30} {'Type':<25} {'Nullable':>10} {'Default':<30}")
        print("-" * 95)
        for row in results:
            print(f"{row[0]:<30} {row[1]:<25} {row[2]:>10} {str(row[3]):<30}")
    else:
        query = """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' ORDER BY table_name;
        """
        results = db.execute_query(query)
        for (name,) in results:
            check_schema_postgres(db, name)


def check_stats_postgres(db):
    """Статистика PostgreSQL БД."""
    query = """
    SELECT pg_size_pretty(pg_database_size(current_database())) as db_size;
    """
    result = db.execute_query(query)
    print(f"Database size: {result[0][0]}")

    query = """
    SELECT relname, n_live_tup, pg_size_pretty(pg_total_relation_size(relid))
    FROM pg_stat_user_tables
    ORDER BY n_live_tup DESC LIMIT 20;
    """
    results = db.execute_query(query)
    print(f"\n{'Table':<40} {'Rows':>15} {'Size':>15}")
    print("-" * 70)
    for row in results:
        print(f"{row[0]:<40} {row[1]:>15,} {row[2]:>15}")


def main():
    parser = argparse.ArgumentParser(description="Database diagnostic tool for Calk_KMF")
    parser.add_argument("--db-type", choices=["sqlite", "postgres"], default="sqlite",
                        help="Database type (default: sqlite)")
    parser.add_argument("--check", choices=["tables", "indexes", "schema", "stats", "all"],
                        default="all", help="What to check")
    parser.add_argument("--table", type=str, default=None,
                        help="Specific table name for schema check")
    parser.add_argument("--db-path", type=str, default=None,
                        help="Path to SQLite database (default: calk_kmf.sqlite)")
    args = parser.parse_args()

    if args.db_type == "sqlite":
        conn = get_sqlite_connection(args.db_path)
        checks = {
            "tables": check_tables_sqlite,
            "indexes": check_indexes_sqlite,
            "schema": lambda c: check_schema_sqlite(c, args.table),
            "stats": check_stats_sqlite,
        }
    else:
        db = get_postgres_connection()
        checks = {
            "tables": check_tables_postgres,
            "indexes": check_indexes_postgres,
            "schema": lambda d: check_schema_postgres(d, args.table),
            "stats": check_stats_postgres,
        }

    if args.check == "all":
        for name, func in checks.items():
            print(f"\n{'='*60}")
            print(f"CHECK: {name.upper()}")
            print("=" * 60)
            func(conn if args.db_type == "sqlite" else db)
    else:
        func = checks[args.check]
        func(conn if args.db_type == "sqlite" else db)

    if args.db_type == "sqlite":
        conn.close()


if __name__ == "__main__":
    main()
