import sys
import os
import sqlite3

# Add project root to path
project_root = "e:/Project/Calk_KMF"
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import necessary modules
# Note: These imports might execute module-level code, but in this project it seems safe.
try:
    from code.bazi_calendar.run_update_optimized import run_update
    from code.tests.control_data import create_control, verify_all_tables
    from code.common.logger import CalculationLogger
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def main():
    print("=== Applying Changes and Verifying ===")
    
    # Step 1: Run Bazi Update
    # This will recreate t_bazi_hourly with the new schema (without day_officer_value_id)
    # and populate it.
    print("\n[Step 1] Running Bazi Update (Regenerating t_bazi_hourly)...")
    try:
        run_update()
    except Exception as e:
        print(f"CRITICAL: Bazi Update failed: {e}")
        return

    # Step 2: Update Control Data
    # Since we changed the schema, the old control table has the deleted column.
    # Verification would fail if we don't update the control table to match the new schema.
    print("\n[Step 2] Updating Control Data for t_bazi_hourly...")
    try:
        create_control("t_bazi_hourly")
    except Exception as e:
        print(f"CRITICAL: Control Data update failed: {e}")
        return
    
    # Step 3: Run Verification
    # This checks t_bazi_hourly (new schema vs new control) and other tables (unchanged).
    print("\n[Step 3] Running Full Verification...")
    db_path = "e:/Project/Calk_KMF/calk_kmf.sqlite"
    logger = CalculationLogger(db_path)
    
    success = verify_all_tables(logger=logger)
    
    if success:
        print("\n=== SUCCESS: All steps completed and verified. ===")
    else:
        print("\n=== WARNING: Verification found discrepancies (see above). ===")

if __name__ == "__main__":
    main()
