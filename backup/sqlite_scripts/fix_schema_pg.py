
import sys
import os

sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def fix_schema_types():
    print("Fixing schema types...")
    try:
        # spr_indicator_value.numeric_score -> DOUBLE PRECISION
        print("Altering spr_indicator_value.numeric_score to DOUBLE PRECISION...")
        db.execute_query("""
            ALTER TABLE spr_indicator_value 
            ALTER COLUMN numeric_score TYPE DOUBLE PRECISION 
            USING NULLIF(numeric_score, '')::DOUBLE PRECISION
        """)
        
        # spr_tongshu_guigu_outcome.numeric_score -> DOUBLE PRECISION
        # Check if table exists first (it should)
        print("Altering spr_tongshu_guigu_outcome.numeric_score to DOUBLE PRECISION...")
        db.execute_query("""
            ALTER TABLE spr_tongshu_guigu_outcome
            ALTER COLUMN numeric_score TYPE DOUBLE PRECISION 
            USING NULLIF(numeric_score, '')::DOUBLE PRECISION
        """)
        
        # spr_tongshu_branch_combo_rule.numeric_score -> DOUBLE PRECISION
        print("Altering spr_tongshu_branch_combo_rule.numeric_score to DOUBLE PRECISION...")
        db.execute_query("""
            ALTER TABLE spr_tongshu_branch_combo_rule
            ALTER COLUMN numeric_score TYPE DOUBLE PRECISION 
            USING NULLIF(numeric_score, '')::DOUBLE PRECISION
        """)

        # spr_tongshu_stem_combo_rule.numeric_score -> DOUBLE PRECISION
        print("Altering spr_tongshu_stem_combo_rule.numeric_score to DOUBLE PRECISION...")
        db.execute_query("""
            ALTER TABLE spr_tongshu_stem_combo_rule
            ALTER COLUMN numeric_score TYPE DOUBLE PRECISION 
            USING NULLIF(numeric_score, '')::DOUBLE PRECISION
        """)
        
        # spr_tongshu_phase.numeric_score -> DOUBLE PRECISION
        print("Altering spr_tongshu_phase.numeric_score to DOUBLE PRECISION...")
        db.execute_query("""
            ALTER TABLE spr_tongshu_phase
            ALTER COLUMN numeric_score TYPE DOUBLE PRECISION 
            USING NULLIF(numeric_score, '')::DOUBLE PRECISION
        """)
        
        # spr_bazi_qi_phase.numeric_score (if exists, checking setup_db.py it wasn't there but might be in SQLite)
        # Assuming it might be there if migrated.
        try:
             db.execute_query("""
                ALTER TABLE spr_bazi_qi_phase
                ALTER COLUMN numeric_score TYPE DOUBLE PRECISION 
                USING NULLIF(numeric_score, '')::DOUBLE PRECISION
            """)
        except Exception as e:
            print(f"Skipping spr_bazi_qi_phase (might not exist or no col): {e}")

        # spr_black_rabbit_scores.numeric_score
        try:
             db.execute_query("""
                ALTER TABLE spr_black_rabbit_scores
                ALTER COLUMN numeric_score TYPE DOUBLE PRECISION 
                USING NULLIF(numeric_score, '')::DOUBLE PRECISION
            """)
        except Exception as e:
            print(f"Skipping spr_black_rabbit_scores: {e}")

        # spr_yellow_black_stars.score -> numeric_score? In run_analysis it uses s.score
        try:
             db.execute_query("""
                ALTER TABLE spr_yellow_black_stars
                ALTER COLUMN score TYPE DOUBLE PRECISION 
                USING NULLIF(score, '')::DOUBLE PRECISION
            """)
        except Exception as e:
            print(f"Skipping spr_yellow_black_stars: {e}")

        print("Schema types fixed.")
        
    except Exception as e:
        print(f"Error fixing schema: {e}")

if __name__ == "__main__":
    fix_schema_types()
