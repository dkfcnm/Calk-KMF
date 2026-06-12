
import sys
import subprocess
import time

def install_package(package_name):
    print(f"Installing '{package_name}'...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"Package '{package_name}' installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install '{package_name}': {e}")
        sys.exit(1)

try:
    import pg8000.native
    print("pg8000 is already installed.")
except ImportError:
    install_package('pg8000')
    import pg8000.native

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': '1Dct,eltn!',
    'database': 'postgres'
}

def check_connection_and_create_db():
    print("Connecting to PostgreSQL...")
    try:
        # Connect to 'postgres' db to check/create target db
        conn = pg8000.native.Connection(**DB_CONFIG)
        print("Successfully connected to PostgreSQL 'postgres' database.")
        
        # Check if calk_kmf exists
        # pg8000 native run returns rows as lists
        results = conn.run("SELECT 1 FROM pg_database WHERE datname = 'calk_kmf'")
        
        if not results:
            print("Database 'calk_kmf' does not exist. Creating...")
            # pg8000 auto-commits DDL if autocommit is on, but native interface might behave differently.
            # In native mode, commands are executed directly. CREATE DATABASE cannot run in a transaction block.
            # pg8000.native.Connection doesn't have autocommit property like DB-API 2.0.
            # It runs queries immediately.
            conn.run("CREATE DATABASE calk_kmf")
            print("Database 'calk_kmf' created.")
        else:
            print("Database 'calk_kmf' already exists.")
            
        conn.close()
        
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_connection_and_create_db()
