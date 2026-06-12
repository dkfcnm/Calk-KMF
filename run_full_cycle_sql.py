import sys
import os
import time
import traceback
from datetime import datetime

# Ensure we can import from code/
sys.path.insert(0, os.getcwd())

# Import modules
from code.common.db_manager import db
from code.common.logger import CalculationLogger

# Import update scripts
# We use the new SQL-centric/Optimized versions
try:
    from code.bazi_calendar.run_update_optimized import run_update as run_bazi
    from code.taiyi.run_update import run_update as run_taiyi
    from code.qimen.run_update_zhirun import run_update as run_qimen_zhirun
    from code.qimen.run_update_chauby import run_update as run_qimen_chauby
    from code.feng_shui.run_update import run_update as run_feng_shui
    from code.analysis.run_analysis import run_analysis
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import one or more modules: {e}")
    sys.exit(1)

def main():
    start_total = time.time()
    logger = CalculationLogger(db_path="postgres") # Path ignored for PG usually, but logger might use it for file logging
    
    print("\n" + "="*60)
    print(f"STARTING FULL SQL CALCULATION CYCLE")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*60 + "\n")

    stages = [
        ("Bazi Calendar", run_bazi),
        ("Tai Yi", run_taiyi),
        ("Qimen Zhi Run", run_qimen_zhirun),
        ("Qimen Chai Bu", run_qimen_chauby),
        ("Feng Shui", run_feng_shui),
        ("Analysis", run_analysis)
    ]

    success_count = 0
    
    for name, func in stages:
        print(f"\n--- Stage: {name} ---")
        st_start = time.time()
        try:
            # Pass logger if the function accepts it
            # Inspecting signatures previously: most accepted logger=None
            # run_bazi doesn't seem to take logger in the version I read, but let's check.
            # actually run_update_optimized.py for bazi: def run_update(): ... (no args)
            # others take logger.
            
            if name == "Bazi Calendar":
                func()
            else:
                func(logger=logger)
                
            elapsed = time.time() - st_start
            print(f"[OK] {name} completed in {elapsed:.2f}s")
            success_count += 1
        except Exception as e:
            print(f"[FAIL] {name} FAILED: {e}")
            traceback.print_exc()
            # We continue to next stage? Or stop?
            # User request "Run full cycle". Usually implies stop on critical error, but we want to see what works.
            # Bazi is critical. If Bazi fails, others fail.
            if name == "Bazi Calendar":
                print("CRITICAL: Bazi failed. Aborting cycle.")
                break

    print("\n" + "="*60)
    total_elapsed = time.time() - start_total
    print(f"CYCLE COMPLETED")
    print(f"Successful Stages: {success_count} / {len(stages)}")
    print(f"Total Duration: {total_elapsed:.2f}s")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
