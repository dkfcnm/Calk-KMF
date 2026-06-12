
import sys
import os

sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def check_and_fix_schema_v3():
    print("Checking and Fixing schema types (V3)...")
    
    tables_cols = [
        ('spr_indicator_value', 'numeric_score'),
        ('spr_tongshu_guigu_outcome', 'numeric_score'),
        ('spr_tongshu_branch_combo_rule', 'numeric_score'),
        ('spr_tongshu_stem_combo_rule', 'numeric_score'),
        ('spr_tongshu_phase', 'numeric_score'),
        ('spr_bazi_qi_phase', 'numeric_score'),
        ('spr_black_rabbit_scores', 'numeric_score'),
        ('spr_yellow_black_stars', 'score')
    ]
    
    for t, col in tables_cols:
        print(f"Checking {t}.{col}...")
        try:
            # Check type
            res = db.fetch_all(f"""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = '{t}' AND column_name = '{col}'
            """)
            
            if not res:
                print(f"  Table or column does not exist: {t}.{col}")
                continue
                
            dtype = res[0][0]
            print(f"  Current type: {dtype}")
            
            if dtype in ('text', 'character varying'):
                print(f"  Fixing {t}.{col} (TEXT -> DOUBLE PRECISION)...")
                # Update empty/whitespace to NULL
                db.execute_query(f"UPDATE {t} SET {col} = NULL WHERE TRIM({col}) = ''")
                # Cast
                db.execute_query(f"""
                    ALTER TABLE {t} 
                    ALTER COLUMN {col} TYPE DOUBLE PRECISION 
                    USING {col}::DOUBLE PRECISION
                """)
                print("  Fixed.")
            else:
                print("  Type is already numeric-compatible. Skipping.")
                
        except Exception as e:
            print(f"  Error processing {t}: {e}")

if __name__ == "__main__":
    check_and_fix_schema_v3()
