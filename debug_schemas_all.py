
import sys
import os

sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def check_all_schemas():
    tables = [
        'spr_indicator_value',
        'spr_tongshu_guigu_outcome',
        'spr_tongshu_stem_combo_rule',
        'spr_tongshu_branch_combo_rule',
        'spr_bazi_qi_phase',
        'spr_black_rabbit_scores',
        'spr_yellow_black_stars',
        't_rule_registry'
    ]
    
    print("Checking schemas...")
    for t in tables:
        print(f"Table: {t}")
        try:
            cols = db.fetch_all(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{t}' 
                AND column_name IN ('numeric_score', 'score', 'score_base')
            """)
            for c in cols:
                print(f"  {c[0]}: {c[1]}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    check_all_schemas()
