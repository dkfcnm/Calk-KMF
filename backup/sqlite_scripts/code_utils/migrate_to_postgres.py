
import sqlite3
import sys
import os
import pg8000.dbapi
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from code.common.db_config import PG_CONFIG, SQLITE_DB_PATH

def get_sqlite_tables(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    return [row[0] for row in cursor.fetchall()]

def get_table_schema(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = []
    pks = []
    for row in cursor.fetchall():
        # cid, name, type, notnull, dflt_value, pk
        col_name = row[1]
        col_type = row[2].upper()
        not_null = row[3]
        pk = row[5]
        
        pg_type = 'TEXT' # Default
        if 'INT' in col_type:
            pg_type = 'BIGINT'
        elif 'REAL' in col_type or 'FLOAT' in col_type or 'DOUBLE' in col_type:
            pg_type = 'DOUBLE PRECISION'
        elif 'BLOB' in col_type:
            pg_type = 'BYTEA'
        elif 'BOOL' in col_type:
            pg_type = 'BOOLEAN'
        
        columns.append({
            'name': col_name,
            'type': pg_type,
            'not_null': not_null,
            'pk': pk
        })
        if pk > 0:
            pks.append(col_name)
            
    return columns, pks

def migrate_table(table_name, sqlite_curr, pg_conn):
    print(f"Migrating table: {table_name}...")
    
    # Get Schema
    columns, pks = get_table_schema(sqlite_curr, table_name)
    
    # Build CREATE TABLE
    create_cols = []
    for col in columns:
        line = f'"{col["name"]}" {col["type"]}'
        if col['not_null']:
            line += ' NOT NULL'
        create_cols.append(line)
    
    if pks:
        pk_str = ', '.join([f'"{pk}"' for pk in pks])
        create_cols.append(f'PRIMARY KEY ({pk_str})')
        
    create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(create_cols)})'
    
    pg_curr = pg_conn.cursor()
    try:
        pg_curr.execute(create_sql)
        pg_conn.commit()
    except Exception as e:
        print(f"Error creating table {table_name}: {e}")
        pg_conn.rollback()
        return

    # Clear Postgres table to avoid dupes during retry
    pg_curr.execute(f'TRUNCATE TABLE "{table_name}"')
    pg_conn.commit()

    # Migrate Data
    sqlite_curr.execute(f'SELECT * FROM "{table_name}"')
    
    batch_size = 10000
    total_rows = 0
    
    insert_sql = f'INSERT INTO "{table_name}" VALUES ({", ".join(["%s"] * len(columns))})'
    
    while True:
        rows = sqlite_curr.fetchmany(batch_size)
        if not rows:
            break
            
        try:
            pg_curr.executemany(insert_sql, rows)
            pg_conn.commit()
            total_rows += len(rows)
            print(f"  Transferred {total_rows} rows...", end='\r')
        except Exception as e:
            print(f"\nError inserting batch into {table_name}: {e}")
            pg_conn.rollback()
            break
            
    print(f"\nFinished {table_name}. Total: {total_rows} rows.")
    pg_curr.close()

def main():
    print("Starting migration from SQLite to PostgreSQL...")
    print(f"SQLite DB: {SQLITE_DB_PATH}")
    print(f"Postgres DB: {PG_CONFIG['database']} on {PG_CONFIG['host']}")
    
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
        sqlite_curr = sqlite_conn.cursor()
        
        pg_conn = pg8000.dbapi.connect(
            user=PG_CONFIG['user'],
            password=PG_CONFIG['password'],
            host=PG_CONFIG['host'],
            port=PG_CONFIG['port'],
            database=PG_CONFIG['database']
        )
        
        tables = get_sqlite_tables(sqlite_curr)
        print(f"Found {len(tables)} tables to migrate.")
        
        # Disable constraints check/triggers? 
        # Postgres doesn't have a simple global switch like sqlite's foreign_keys off for session, 
        # but we can set session_replication_role for current session if superuser.
        # pg_conn.cursor().execute("SET session_replication_role = 'replica';")
        
        for table in tables:
            migrate_table(table, sqlite_curr, pg_conn)
            
        sqlite_conn.close()
        pg_conn.close()
        print("\nMigration completed successfully.")
        
    except Exception as e:
        print(f"\nCritical Error during migration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
