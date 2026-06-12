
import sys
import os

sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def check_bad_data():
    tables = [
        'spr_indicator_value', 
        'spr_tongshu_guigu_outcome', 
        'spr_tongshu_branch_combo_rule',
        'spr_tongshu_stem_combo_rule',
        'spr_tongshu_phase',
        'spr_black_rabbit_scores',
        'spr_yellow_black_stars'
    ]
    
    for t in tables:
        print(f"Checking {t}...")
        col = 'numeric_score'
        if t == 'spr_yellow_black_stars':
            col = 'score'
            
        try:
            # Check if table exists
            db.fetch_all(f"SELECT 1 FROM {t} LIMIT 1")
            
            # Find distinct non-numeric values
            # We try to cast to double and catch errors? No, pg doesn't support that easily in select.
            # We can regex check.
            sql = f"""
                SELECT DISTINCT {col} 
                FROM {t} 
                WHERE {col} IS NOT NULL AND {col} != '' 
                AND {col} !~ '^-?[0-9]+(\.[0-9]+)?$'
            """
            res = db.fetch_all(sql)
            if res:
                print(f"  Found potential bad values in {t}.{col}: {res}")
            else:
                print(f"  No obvious bad values found (regex check).")
                
            # Check empty strings specifically
            res_empty = db.fetch_all(f"SELECT count(*) FROM {t} WHERE {col} = ''")
            print(f"  Empty strings count: {res_empty[0][0]}")
            
        except Exception as e:
            print(f"  Skipping {t}: {e}")

if __name__ == "__main__":
    check_bad_data()
