import sqlite3
import os
import sys
import time

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

DB_PATH = os.path.join(project_root, "calk_kmf.sqlite")

def optimize_db():
    print("Starting Database Maintenance (VACUUM + ANALYZE)...")
    try:
        conn = sqlite3.connect(DB_PATH)
        start = time.time()
        
        # Get initial size
        initial_size = os.path.getsize(DB_PATH) / (1024*1024)
        print(f"Initial DB Size: {initial_size:.2f} MB")
        
        print("Running VACUUM...")
        conn.execute("VACUUM")
        
        print("Running ANALYZE...")
        conn.execute("ANALYZE")
        
        conn.close()
        
        # Get final size
        final_size = os.path.getsize(DB_PATH) / (1024*1024)
        print(f"Final DB Size: {final_size:.2f} MB")
        print(f"Freed: {initial_size - final_size:.2f} MB")
        
        duration = time.time() - start
        print(f"Maintenance completed in {duration:.2f} seconds.")
            
    except Exception as e:
        print(f"Error during maintenance: {e}")

if __name__ == "__main__":
    optimize_db()
