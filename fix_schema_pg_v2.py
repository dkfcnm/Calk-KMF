
import sys
import os

sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def fix_schema_types_v2():
    print("Fixing schema types (Robust version)...")
    
    tables_cols = [
        ('spr_indicator_value', 'numeric_score'),
        ('spr_tongshu_guigu_outcome', 'numeric_score'),
        ('spr_tongshu_branch_combo_rule', 'numeric_score'),
        ('spr_tongshu_stem_combo_rule', 'numeric_score'),
        ('spr_tongshu_phase', 'numeric_score'),
        ('spr_black_rabbit_scores', 'numeric_score'),
        ('spr_yellow_black_stars', 'score')
    ]
    
    for t, col in tables_cols:
        print(f"Processing {t}.{col}...")
        try:
            # 1. Check if table exists
            db.fetch_all(f"SELECT 1 FROM {t} LIMIT 1")
            
            # 2. Update empty/whitespace to NULL
            print(f"  Nullifying empty strings in {t}.{col}...")
            db.execute_query(f"UPDATE {t} SET {col} = NULL WHERE TRIM({col}) = ''")
            
            # 3. Alter type
            print(f"  Altering {t}.{col} to DOUBLE PRECISION...")
            db.execute_query(f"""
                ALTER TABLE {t} 
                ALTER COLUMN {col} TYPE DOUBLE PRECISION 
                USING {col}::DOUBLE PRECISION
            """)
            print(f"  Success for {t}.")
            
        except Exception as e:
            print(f"  Error processing {t}: {e}")

if __name__ == "__main__":
    fix_schema_types_v2()
