import pandas as pd
import re
import sys
sys.path.insert(0, '.')
from code.common.db_manager import DBManager

df_excel = pd.read_csv('smart_tablica_extracted.csv')
df_excel['date'] = pd.to_datetime(df_excel['date']).dt.date

def parse_excel_chart(chart):
    match = re.match(r'(\d+)\s+(ян|инь)', chart)
    if match:
        return int(match.group(1)), 'Yang' if match.group(2) == 'ян' else 'Yin'
    return None, None

df_excel[['excel_ju', 'excel_yy']] = df_excel['hour_chart'].apply(lambda x: pd.Series(parse_excel_chart(x)))

db = DBManager()
conn = db.get_connection()
cur = conn.cursor()
cur.execute('''
SELECT DISTINCT
    h.slot_start_date_local::DATE as date,
    h.hour_branch,
    r.rasklad_id,
    h.day_stem, h.day_branch, h.hour_stem, h.hour_branch
FROM t_bazi_hourly h
JOIN t_qumen_dgiren_hourly r ON r.hour_id = h.hour_id
WHERE h.tz_offset_hours = 3
  AND h.slot_start_date_local::DATE BETWEEN '2026-01-01' AND '2026-12-31'
''')
df_db = pd.DataFrame(cur.fetchall(), columns=['date', 'hour_branch', 'rasklad_id', 'day_stem', 'day_branch', 'hour_stem', 'hb'])
conn.close()

def parse_db(rid):
    parts = rid.split('_')
    return parts[0], int(parts[1])

df_db[['db_yy', 'db_ju']] = df_db['rasklad_id'].apply(lambda x: pd.Series(parse_db(x)))

merged = df_excel.merge(df_db, on=['date', 'hour_branch'], how='inner')
merged['ju_match'] = merged['excel_ju'] == merged['db_ju']

# Несовпадения для 丑
chou_mismatch = merged[(merged['hour_branch'] == '丑') & ~merged['ju_match']]

with open('mismatch_analysis.txt', 'w', encoding='utf-8') as f:
    f.write(f'Total 丑 mismatches: {len(chou_mismatch)}\n')
    f.write('\nAll 丑 mismatches:\n')
    for _, row in chou_mismatch.iterrows():
        f.write(f"{row['date']}: Excel={row['hour_chart']} DB={row['rasklad_id']} day={row['day_stem']}{row['day_branch']}\n")
    
    # Несовпадения для 子
    zi_mismatch = merged[(merged['hour_branch'] == '子') & ~merged['ju_match']]
    f.write(f'\nTotal 子 mismatches: {len(zi_mismatch)}\n')

print('Done')
