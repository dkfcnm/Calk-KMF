import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.getcwd())
import sqlite3
from code.bazi_calendar.engine import BaziEngine

def test_engine():
    conn = sqlite3.connect("e:/Project/Calk_KMF/calk_kmf.sqlite")
    engine = BaziEngine(conn)
    
    # 13 Aug 11:00 Local (+3) = 08:00 UTC
    dt_utc = datetime(2026, 8, 13, 8, 0, 0, tzinfo=timezone.utc)
    offset = 3
    res = engine.calc_pillars(dt_utc, offset)
    
    lunar = res['lunar']
    print(f"Engine Test for 13 Aug 11:00 Local (+3) [08:00 UTC]: {lunar}")

    # 13 Aug 01:00 Local (+3) = 12 Aug 22:00 UTC
    dt_utc2 = datetime(2026, 8, 12, 22, 0, 0, tzinfo=timezone.utc)
    res2 = engine.calc_pillars(dt_utc2, offset)
    lunar2 = res2['lunar']
    print(f"Engine Test for 13 Aug 01:00 Local (+3) [12 Aug 22:00 UTC]: {lunar2}")

    conn.close()

test_engine()
