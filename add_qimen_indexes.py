
import sys
import os

sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def add_qimen_indexes():
    print("Adding indexes for Qimen tables...")
    try:
        # t_qumen_dgiren_hourly
        print("  t_qumen_dgiren_hourly indexes...")
        db.execute_query("CREATE INDEX IF NOT EXISTS idx_qumen_dgiren_hourly_hour_id ON t_qumen_dgiren_hourly(hour_id)")
        db.execute_query("CREATE INDEX IF NOT EXISTS idx_qumen_dgiren_hourly_rasklad ON t_qumen_dgiren_hourly(rasklad_id, palace_no)")
        
        # spr_qimen_templates
        print("  spr_qimen_templates indexes...")
        db.execute_query("CREATE INDEX IF NOT EXISTS idx_qimen_templates_rasklad ON spr_qimen_templates(rasklad_id, palace_no)")
        db.execute_query("CREATE INDEX IF NOT EXISTS idx_qimen_templates_stems ON spr_qimen_templates(heaven_stem, earth_stem)")
        
        # t_bazi_hourly additional indexes for analysis
        print("  t_bazi_hourly additional indexes...")
        db.execute_query("CREATE INDEX IF NOT EXISTS idx_bazi_hourly_analysis_join ON t_bazi_hourly(hour_id)")
        
        print("Indexes created.")
        
    except Exception as e:
        print(f"Error adding indexes: {e}")

if __name__ == "__main__":
    add_qimen_indexes()
