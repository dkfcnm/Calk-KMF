import sqlite3
import pg8000.native
import sys
import os
import json
from datetime import datetime

# Ensure we can import from code/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from code.common.db_config import PG_CONFIG

def get_sqlite_connection(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_postgres_connection():
    return pg8000.native.Connection(
        user=PG_CONFIG['user'],
        password=PG_CONFIG['password'],
        host=PG_CONFIG['host'],
        port=PG_CONFIG['port'],
        database=PG_CONFIG['database']
    )

def migrate_table(sqlite_conn, pg_conn, table_name):
    print(f"Migrating table: {table_name}...")
    
    # Get data from SQLite
    cursor_sqlite = sqlite_conn.cursor()
    try:
        cursor_sqlite.execute(f"SELECT * FROM {table_name}")
        rows = cursor_sqlite.fetchall()
    except Exception as e:
        print(f"Error reading from SQLite table {table_name}: {e}")
        return

    if not rows:
        print(f"Table {table_name} is empty. Skipping data migration.")
        return

    # Get column names
    columns = [description[0] for description in cursor_sqlite.description]
    
    # Prepare data for insertion
    # pg8000.native expects python types. 
    # We need to construct the INSERT statement.
    cols_str = ', '.join([f'"{c}"' for c in columns])
    # Placeholders for pg8000 are :name or just construct string if safe (but better use params)
    # pg8000.native run method takes SQL and params.
    # For bulk insert, we might need loop or construct a large VALUES string.
    # Given it's reference data, it shouldn't be huge. Loop is safer/easier with pg8000.native for now.
    
    placeholders = ", ".join(["%s"] * len(columns)) # pg8000 uses %s for dbapi, but native uses :p or literal
    # Wait, using pg8000.native, we should use identifiers.
    # Actually, let's use the DBAPI interface from pg8000 which is easier for migration compatibility
    # But wait, I imported pg8000.native. Let's switch to pg8000.dbapi to match DBManager style if needed, 
    # or just use native properly. Native is faster.
    # Let's use native. params are passed as a list.
    
    # However, native `run` executes one statement.
    # For bulk, we can construct a multi-value insert: INSERT INTO table (c1, c2) VALUES (v1, v2), (v3, v4)...
    # But we need to handle quoting/escaping.
    
    # Simplest reliable way: Loop inserts.
    
    success_count = 0
    try:
        # We'll use a transaction
        pg_conn.run("BEGIN")
        
        insert_sql = f'INSERT INTO "{table_name}" ({cols_str}) VALUES ({", ".join([f":v{i}" for i in range(len(columns))])}) ON CONFLICT DO NOTHING'
        
        for row in rows:
            # Create a dict for parameters if using named params, or list if positional
            # pg8000.native uses named parameters like :name if a dict is passed, or positional if list?
            # actually checking pg8000 docs (memory): native uses :p1, :p2 etc or name.
            # Let's use list of values and slightly different SQL generation or just simple parameter binding.
            
            # Re-reading pg8000 native docs logic (simulated):
            # run(sql, **params) or run(sql, params_list)
            # Let's stick to simple individual inserts to be safe with types.
            
            # mapping row to dict for named parameters
            params = {f"v{i}": val for i, val in enumerate(row)}
            pg_conn.run(insert_sql, **params)
            success_count += 1
            
        pg_conn.run("COMMIT")
        print(f"Successfully migrated {success_count} rows to {table_name}.")
        
    except Exception as e:
        pg_conn.run("ROLLBACK")
        print(f"Error inserting into PostgreSQL table {table_name}: {e}")

def create_table_ddl(sqlite_conn, pg_conn, table_name):
    cursor = sqlite_conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    
    pg_cols = []
    primary_keys = []
    
    for col in columns_info:
        cid, name, type_name, notnull, dflt_value, pk = col
        
        type_upper = type_name.upper() if type_name else "TEXT"
        pg_type = "TEXT"
        if "INT" in type_upper:
            pg_type = "INTEGER"
        elif "CHAR" in type_upper or "TEXT" in type_upper or "CLOB" in type_upper:
            pg_type = "TEXT"
        elif "BLOB" in type_upper:
            pg_type = "BYTEA"
        elif "REAL" in type_upper or "FLOA" in type_upper or "DOUB" in type_upper:
            pg_type = "DOUBLE PRECISION"
        elif "BOOLEAN" in type_upper:
            pg_type = "BOOLEAN"
            
        nullable = "NOT NULL" if notnull else "NULL"
        default = ""
        if dflt_value is not None:
             # handle quotes in default value if string
             default = f"DEFAULT {dflt_value}"
        
        pg_cols.append(f'"{name}" {pg_type} {nullable} {default}')
        
        if pk:
            primary_keys.append(f'"{name}"')
            
    ddl = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(pg_cols)}"
    if primary_keys:
        ddl += f", PRIMARY KEY ({', '.join(primary_keys)})"
    ddl += ")"
    
    try:
        pg_conn.run(ddl)
        print(f"Table structure created/verified for {table_name}.")
    except Exception as e:
        print(f"Error creating table {table_name}: {e}")

def main():
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sqlite_db_path = os.path.join(PROJECT_ROOT, "calk_kmf.sqlite")
    if not os.path.exists(sqlite_db_path):
        print(f"SQLite DB not found at {sqlite_db_path}")
        return

    sqlite_conn = get_sqlite_connection(sqlite_db_path)
    try:
        pg_conn = get_postgres_connection()
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")
        return
    
    # Get all tables starting with spr_
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'spr_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"Found {len(tables)} reference tables to migrate.")
    
    for table in tables:
        create_table_ddl(sqlite_conn, pg_conn, table)
        migrate_table(sqlite_conn, pg_conn, table)
        
    sqlite_conn.close()
    pg_conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    main()
