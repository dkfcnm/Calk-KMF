#!/usr/bin/env python3
"""
Детальный аудит SQLite БД проекта Calk_KMF
Только чтение, без модификаций
"""

import sqlite3
import json
import os
from collections import defaultdict

DB_PATH = "calk_kmf.sqlite"
OUTPUT_PATH = "db_audit_result.json"

def connect():
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn

def get_tables(conn):
    """Все таблицы (исключая sqlite_*)"""
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )
    return [row["name"] for row in cur.fetchall()]

def get_views(conn):
    """Все views"""
    cur = conn.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='view' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )
    return [{"name": row["name"], "sql": row["sql"]} for row in cur.fetchall()]

def get_indexes(conn):
    """Все индексы"""
    cur = conn.execute(
        "SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%' ORDER BY tbl_name, name"
    )
    return [{"name": row["name"], "table": row["tbl_name"], "sql": row["sql"]} for row in cur.fetchall()]

def get_table_info(conn, table):
    """PRAGMA table_info"""
    cur = conn.execute(f'PRAGMA table_info("{table}")')
    return [{"cid": row["cid"], "name": row["name"], "type": row["type"],
             "notnull": row["notnull"], "dflt_value": row["dflt_value"], "pk": row["pk"]} for row in cur.fetchall()]

def get_table_size(conn, table):
    """Приблизительное количество строк"""
    try:
        cur = conn.execute(f'SELECT COUNT(*) as cnt FROM "{table}"')
        return cur.fetchone()["cnt"]
    except Exception as e:
        return str(e)

def get_foreign_keys(conn, table):
    cur = conn.execute(f'PRAGMA foreign_key_list("{table}")')
    return [{"id": row["id"], "seq": row["seq"], "table": row["table"],
             "from": row["from"], "to": row["to"], "on_update": row["on_update"], "on_delete": row["on_delete"]} for row in cur.fetchall()]

def categorize_table(name):
    if name.startswith("v_"):
        return "view"
    if name.startswith("t_control_"):
        return "control"
    if name.startswith("spr_"):
        return "reference"
    if name.startswith("t_"):
        return "main"
    return "other"

def main():
    if not os.path.exists(DB_PATH):
        print(f"DB not found: {DB_PATH}")
        return

    conn = connect()
    tables = get_tables(conn)
    views = get_views(conn)
    indexes = get_indexes(conn)

    result = {
        "db_path": DB_PATH,
        "db_size_mb": round(os.path.getsize(DB_PATH) / (1024*1024), 2),
        "total_tables": len(tables),
        "total_views": len(views),
        "total_indexes": len(indexes),
        "tables": {},
        "views": views,
        "indexes_by_table": defaultdict(list),
        "summary": {
            "main": [],
            "reference": [],
            "control": [],
            "other": [],
        },
        "problems": []
    }

    # Categorize tables
    for t in tables:
        cat = categorize_table(t)
        result["summary"][cat].append(t)

    # Gather table details
    for t in tables:
        info = get_table_info(conn, t)
        size = get_table_size(conn, t)
        fks = get_foreign_keys(conn, t)
        result["tables"][t] = {
            "category": categorize_table(t),
            "columns": info,
            "row_count": size,
            "foreign_keys": fks,
        }

    # Index mapping
    for idx in indexes:
        result["indexes_by_table"][idx["table"]].append(idx)

    conn.close()

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Audit complete. Results saved to {OUTPUT_PATH}")
    print(f"Tables: {len(tables)}, Views: {len(views)}, Indexes: {len(indexes)}")

if __name__ == "__main__":
    main()
