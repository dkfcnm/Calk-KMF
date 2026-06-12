import sys
import os

# Ensure imports work - MUST BE FIRST
sys.path.insert(0, os.getcwd())

from code.common.db_manager import db

def generate_flying_star_map():
    """
    Generates the mapping of Center Star -> Palace -> Resident Star.
    Based on the logic:
    - Center 5: Palaces 6,7,8,9,1,2,3,4 get stars 6,7,8,9,1,2,3,4
    - Sequence is always forward in the fixed palace order:
      PALACE_SEQUENCE = [6, 7, 8, 9, 1, 2, 3, 4]
    """
    
    PALACE_SEQUENCE = [6, 7, 8, 9, 1, 2, 3, 4]
    seq = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    
    mapping = []
    
    for center_star in range(1, 10):
        # Center always gets the center star
        mapping.append((center_star, 5, center_star))
        
        # Calculate stars for other palaces
        idx = center_star - 1 # 0-based index of center star in seq
        # The star sequence starting from the one *after* center
        star_list = seq[idx+1:] + seq[:idx]
        
        for palace, star in zip(PALACE_SEQUENCE, star_list):
            mapping.append((center_star, palace, star))
            
    return mapping

def migrate():
    print("Migrating Feng Shui Constants...")
    
    # 1. spr_flying_star_map
    print("Creating spr_flying_star_map...")
    db.execute_query("DROP TABLE IF EXISTS spr_flying_star_map")
    db.execute_query("""
        CREATE TABLE spr_flying_star_map (
            center_star INTEGER,
            palace INTEGER,
            resident_star INTEGER,
            PRIMARY KEY (center_star, palace)
        )
    """)
    
    data = generate_flying_star_map()
    db.execute_batch("INSERT INTO spr_flying_star_map VALUES (%s, %s, %s)", data)
    print(f"Inserted {len(data)} rows into spr_flying_star_map.")
    
    # Check if spr_month_stars and spr_hour_stars exist (they should, but ensure)
    # If not, we would need to recreate them, but they are referenced in config.py so likely exist.
    # Just validation
    
    try:
        c = db.fetch_all("SELECT count(*) FROM spr_month_stars")[0][0]
        print(f"spr_month_stars exists with {c} rows.")
    except Exception as e:
        print(f"Warning: spr_month_stars issue: {e}")
        
    try:
        c = db.fetch_all("SELECT count(*) FROM spr_hour_stars")[0][0]
        print(f"spr_hour_stars exists with {c} rows.")
    except Exception as e:
        print(f"Warning: spr_hour_stars issue: {e}")

    print("Feng Shui constants migration completed.")

if __name__ == "__main__":
    migrate()
