
import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def analyze_structure():
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # 1. Get unique stars
    cursor.execute("SELECT DISTINCT star_name FROM spr_black_rabbit_day_joey")
    stars = [row[0] for row in cursor.fetchall()]
    print("Unique Stars:", stars)
    
    # 2. Determine Sequence
    # We look at a sequence where we know it's forward (e.g. 1st Day Stem is Yang)
    # 2026-10-01 is Fire (9). 2026-10-02 is Water (1).
    # 2026-10-10 (1st Day) is Ding Si (Yin Fire). Wait.
    # If 2026-10-02 is Water, and 2026-10-01 is Fire.
    # Let's check a known Yang month.
    # 2026-06-15 (1st Day) is Geng Shen (Yang Metal). L.Mon 5.
    # Let's check dates 2026-06-15, 16, 17.
    
    print("\nChecking Sequence in Month 5 (Yang 1st Day - Geng):")
    sql = """
    SELECT slot_start_date_local, r.result_value
    FROM t_bazi_hourly h
    JOIN t_analysis_day r ON h.slot_start_date_local = r.date_val::text 
        AND r.rule_id = '5de066e318b1e50058d92807d6d49e30'
    WHERE h.lunar_month = 5 AND h.lunar_day BETWEEN 1 AND 5
    ORDER BY h.slot_start_date_local
    """
    cursor.execute(sql)
    for row in cursor.fetchall():
        print(row)
        
    print("\nChecking Sequence in Month 6 (Yin 1st Day - Ji):")
    sql = """
    SELECT slot_start_date_local, r.result_value
    FROM t_bazi_hourly h
    JOIN t_analysis_day r ON h.slot_start_date_local = r.date_val::text 
        AND r.rule_id = '5de066e318b1e50058d92807d6d49e30'
    WHERE h.lunar_month = 6 AND h.lunar_day BETWEEN 1 AND 5
    ORDER BY h.slot_start_date_local
    """
    cursor.execute(sql)
    for row in cursor.fetchall():
        print(row)

    conn.close()

if __name__ == "__main__":
    analyze_structure()
