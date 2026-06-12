import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('calk_kmf.sqlite')
cursor = conn.cursor()

# Check sample data for April 2026
cursor.execute("""
SELECT DISTINCT slot_start_date_local, slot_start_date_utc, tz_offset_hours, hour_stem, hour_branch, day_stem, day_branch
FROM t_bazi_hourly
WHERE slot_start_date_local LIKE '2026-04-01%'
ORDER BY tz_offset_hours, slot_start_time_local
LIMIT 5
""")
for row in cursor.fetchall():
    print(row)

print('---')
# Check how many tz offsets for 2026-04-01
cursor.execute("SELECT DISTINCT tz_offset_hours FROM t_bazi_hourly WHERE slot_start_date_local LIKE '2026-04-01%'")
print('TZ offsets for 2026-04-01:', [r[0] for r in cursor.fetchall()])

conn.close()
