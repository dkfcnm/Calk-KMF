
import sys
import os
sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def reset_analysis_tables():
    tables = [
        "t_analysis_year", "t_analysis_month", "t_analysis_day", "t_analysis_hour",
        "t_analysis_direction_year", "t_analysis_direction_month", 
        "t_analysis_direction_day", "t_analysis_direction_hour",
        "t_analysis_activation"
    ]
    print("Dropping analysis tables to update schema...")
    for t in tables:
        try:
            db.execute_query(f"DROP TABLE IF EXISTS {t}")
            print(f"Dropped {t}.")
        except Exception as e:
            print(f"Error dropping {t}: {e}")

if __name__ == "__main__":
    reset_analysis_tables()
