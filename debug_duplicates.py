
import sys
import os

sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def check_duplicates():
    print("Checking for duplicates in reference tables...")
    
    checks = [
        ("spr_earthly_branch", "branch_char"),
        ("spr_heavenly_stem", "stem_char"),
        ("spr_day_officer_mapping", "month_branch_id, day_branch_id"),
        ("spr_master_dano_mapping", "month_branch_id, day_stem_id, day_branch_id"),
        ("spr_tongshu_guigu_outcome", "outcome_number"),
        ("spr_tongshu_stem_combo_rule", "item1, item2, combo_type_id"), 
        # Note: combo rules might not be unique on items if multiple rules apply? 
        # But for specific predicate/rule_id map?
        ("spr_jiazi_extended", "stem, branch"),
        ("spr_black_rabbit_matrix", "jiazi_id, lunar_day"),
        ("spr_yellow_black_matrix", "month_branch, day_branch")
    ]
    
    for table, cols in checks:
        print(f"Checking {table} ({cols})...")
        try:
            sql = f"""
                SELECT {cols}, count(*) 
                FROM {table} 
                GROUP BY {cols} 
                HAVING count(*) > 1
            """
            res = db.fetch_all(sql)
            if res:
                print(f"  Found {len(res)} duplicates in {table}!")
                print(f"  Sample: {res[0]}")
            else:
                print(f"  OK.")
        except Exception as e:
            print(f"  Error checking {table}: {e}")

if __name__ == "__main__":
    check_duplicates()
