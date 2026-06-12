import sys
import os
import time
import traceback

# Setup path
project_root = os.getcwd()
sys.path.insert(0, project_root)

# Redirect stdout/stderr to file for reliability
log_file = open("full_cycle_2026.log", "w", encoding="utf-8")
sys.stdout = log_file
sys.stderr = log_file

print(f"Starting Full Calculation Cycle for 2026 at {time.ctime()}")

try:
    print("\n" + "="*50)
    print("STEP 1: Bazi Calendar (2026)")
    print("="*50)
    from code.bazi_calendar.run_update_optimized import run_update as run_bazi
    run_bazi()
    print("STEP 1 COMPLETED.")

    print("\n" + "="*50)
    print("STEP 2: Qimen Zhi Run (2026)")
    print("="*50)
    from code.qimen.run_update_zhirun_optimized import run_update as run_zhirun
    run_zhirun()
    print("STEP 2 COMPLETED.")

    print("\n" + "="*50)
    print("STEP 3: Qimen Chai Bu (2026)")
    print("="*50)
    from code.qimen.run_update_chauby_optimized import run_update as run_chaibu
    run_chaibu()
    print("STEP 3 COMPLETED.")

    print("\n" + "="*50)
    print("STEP 4: Flying Stars (2026)")
    print("="*50)
    from code.feng_shui.run_update import run_update as run_fs
    run_fs()
    print("STEP 4 COMPLETED.")

    print("\n" + "="*50)
    print("STEP 5: Analysis Engine")
    print("="*50)
    from code.analysis.run_analysis import run_analysis
    run_analysis(target_year=2026)
    print("STEP 5 COMPLETED.")

    print("\n" + "="*50)
    print("STEP 6: Tai Yi Shen Shu (2026)")
    print("="*50)
    from code.taiyi.run_update import run_update as run_taiyi
    run_taiyi()
    print("STEP 6 COMPLETED.")

    print("\n" + "="*50)
    print("ALL STEPS FINISHED SUCCESSFULLY.")
    
except Exception as e:
    print("\nCRITICAL ERROR:")
    traceback.print_exc()

finally:
    print(f"Finished at {time.ctime()}")
    log_file.close()
