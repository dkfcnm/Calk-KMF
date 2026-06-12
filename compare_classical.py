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

# Получаем данные из БД
# Для каждой LOCAL даты получаем day_pillar из 子 часа
cur.execute('''
WITH zi_pillars AS (
    SELECT DISTINCT ON (slot_start_date_local::DATE, tz_offset_hours)
        slot_start_date_local::DATE as date,
        tz_offset_hours,
        day_stem, day_branch
    FROM t_bazi_hourly
    WHERE hour_branch = '子'
    ORDER BY slot_start_date_local::DATE, tz_offset_hours, slot_start_time_local
)
SELECT 
    h.slot_start_date_local::DATE as date,
    h.hour_branch,
    h.day_stem, h.day_branch,
    h.hour_stem, h.hour_branch as hb,
    zi.day_stem as zi_stem, zi.day_branch as zi_branch
FROM t_bazi_hourly h
LEFT JOIN zi_pillars zi ON zi.date = h.slot_start_date_local::DATE AND zi.tz_offset_hours = h.tz_offset_hours
WHERE h.tz_offset_hours = 3
  AND h.slot_start_date_local::DATE BETWEEN '2026-01-01' AND '2026-12-31'
''')
rows = cur.fetchall()
conn.close()

df_db = pd.DataFrame(rows, columns=['date', 'hour_branch', 'day_stem', 'day_branch', 'hour_stem', 'hb', 'zi_stem', 'zi_branch'])

# Пересчитываем ju_num с использованием day_pillar из 子 часа
# Для этого нужен доступ к spr_solar_term
# Но это сложно в pandas. Давайте просто посмотрим, изменится ли day_stem для 丑-亥.

with open('classical_comparison.txt', 'w', encoding='utf-8') as f:
    f.write('Sample of day_pillars:\n')
    sample = df_db[df_db['date'] == pd.to_datetime('2026-01-05').date()].head(5)
    for _, row in sample.iterrows():
        f.write(f"{row['date']} {row['hour_branch']}: day={row['day_stem']}{row['day_branch']}, zi_day={row['zi_stem']}{row['zi_branch']}\n")
    
    # Сколько записей имеют day_pillar != zi_day_pillar?
    diff = df_db[(df_db['day_stem'] != df_db['zi_stem']) | (df_db['day_branch'] != df_db['zi_branch'])]
    f.write(f'\nRecords with different day_pillar: {len(diff)} out of {len(df_db)}\n')

print('Done')
