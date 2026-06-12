import time
import sys
import os

# Enable unbuffered output
sys.stdout.reconfigure(line_buffering=True)

# Ensure we can import from code/
sys.path.insert(0, os.getcwd())

from code.qimen.run_update_zhirun_optimized import run_update as run_zhirun
from code.qimen.run_update_chauby_optimized import run_update as run_chauby
from code.bazi_calendar.run_update_optimized import run_update as run_bazi_calendar
from code.feng_shui.run_update import run_update as run_flying_stars
from code.analysis.run_analysis import run_analysis
from code.common.logger import CalculationLogger
from code.tests.control_data import verify_all_tables
from code.bazi_calendar.db import vacuum_analyze_db, backup_db


def optimize_db(logger=None):
    log_id = None
    if logger:
        log_id = logger.start_stage("Database Maintenance")

    try:
        vacuum_analyze_db()

        if logger and log_id:
            logger.end_stage(log_id)

    except Exception as e:
        print(f"Error during maintenance: {e}")
        if logger and log_id:
            logger.fail_stage(log_id, str(e))


def main():
    print("=== Starting Full Update Cycle ===")

    # 0. Backup before start
    print("\n--- 0. Creating Backup ---")
    try:
        backup_path = backup_db()
        print(f"Backup created: {backup_path}")
    except Exception as e:
        print(f"WARNING: Backup failed: {e}")

    # Init Logger
    logger = CalculationLogger("postgres")
    logger.cleanup_old_logs(days=90)

    print("\n--- 1. Updating Bazi Calendar (Hourly) ---")
    try:
        run_bazi_calendar()
    except Exception as e:
        print(f"Error updating Bazi Calendar: {e}")

    print("\n--- 2. Updating Zhi Run ---")
    try:
        run_zhirun(logger=logger)
    except Exception as e:
        print(f"Error updating Zhi Run: {e}")

    print("\n--- 3. Updating Chai Bu ---")
    try:
        run_chauby(logger=logger)
    except Exception as e:
        print(f"Error updating Chai Bu: {e}")

    print("\n--- 4. Updating Flying Stars ---")
    try:
        run_flying_stars(logger=logger)
    except Exception as e:
        print(f"Error updating Flying Stars: {e}")

    print("\n--- 5. Running Qimen Walk Analysis ---")
    try:
        run_analysis(logger=logger)
    except Exception as e:
        print(f"Error running analysis: {e}")

    # Verify
    verify_all_tables(logger=logger)

    print("\n--- 6. Database Maintenance ---")
    optimize_db(logger=logger)

    print("\n=== All Done ===")


if __name__ == "__main__":
    main()
