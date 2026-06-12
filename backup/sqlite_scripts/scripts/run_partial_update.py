
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code.bazi_calendar.run_update_optimized import run_update as run_bazi
from code.analysis.run_analysis import run_analysis
from code.common.logger import CalculationLogger

DB_PATH = "e:/Project/Calk_KMF/calk_kmf.sqlite"

def main():
    print("=== Partial Update: Bazi + Analysis ===")
    logger = CalculationLogger(DB_PATH)
    
    print("1. Updating Bazi Calendar (with new Lunar logic)...")
    try:
        run_bazi()
    except Exception as e:
        print(f"Error in Bazi: {e}")
        return

    print("2. Running Analysis (re-evaluating rules)...")
    try:
        run_analysis(logger=logger)
    except Exception as e:
        print(f"Error in Analysis: {e}")

if __name__ == "__main__":
    main()
