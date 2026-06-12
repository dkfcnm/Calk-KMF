import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.getcwd())
from code.bazi_calendar.lunar import calc_lunar_components

def test_lunar(local_dt_str, tz_offset):
    # Parse local time
    local_dt = datetime.strptime(local_dt_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=tz_offset)))
    # Convert to UTC for the function call
    utc_dt = local_dt.astimezone(timezone.utc)
    
    # Call calc_lunar_components
    try:
        m, d, leap = calc_lunar_components(utc_dt, tz_offset_hours=tz_offset)
        print(f"Local: {local_dt_str} (UTC+3), Offset: {tz_offset} -> Lunar: {m}-{d} (Leap: {leap})")
    except Exception as e:
        print(f"Error for {local_dt_str}: {e}")

print("--- Checking August 2026 (Moscow +3) ---")
# 12 августа
test_lunar("2026-08-12 22:59:00", 3) # До Крысы
test_lunar("2026-08-12 23:01:00", 3) # Час Крысы (считается следующим днем?)

# 13 августа
test_lunar("2026-08-13 00:00:00", 3)
test_lunar("2026-08-13 12:00:00", 3)
test_lunar("2026-08-13 23:01:00", 3) # Час Крысы следующего дня

# 14 августа
test_lunar("2026-08-14 00:00:00", 3)
