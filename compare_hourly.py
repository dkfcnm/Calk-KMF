import pandas as pd
import re
import sys
sys.path.insert(0, '.')
from code.common.db_manager import DBManager

# Загружаем Excel данные
df_excel = pd.read_csv('smart_tablica_extracted.csv')
df_excel['date'] = pd.to_datetime(df_excel['date']).dt.date

# Извлекаем ju_num и yy из Excel
def parse_excel_chart(chart):
    # "4 ян" → ju=4, yy='Yang'
    # "8 инь" → ju=8, yy='Yin'
    match = re.match(r'(\d+)\s+(ян|инь)', chart)
    if match:
        ju = int(match.group(1))
        yy = 'Yang' if match.group(2) == 'ян' else 'Yin'
        return ju, yy
    return None, None

df_excel[['excel_ju', 'excel_yy']] = df_excel['hour_chart'].apply(
    lambda x: pd.Series(parse_excel_chart(x))
)

# Подключаемся к БД
db = DBManager()
conn = db.get_connection()
cur = conn.cursor()

# Получаем данные из БД
cur.execute('''
SELECT DISTINCT
    h.slot_start_date_local::DATE as date,
    h.hour_branch,
    r.rasklad_id,
    h.hour_stem,
    h.hour_branch as hb,
    h.day_stem,
    h.day_branch
FROM t_bazi_hourly h
JOIN t_qumen_dgiren_hourly r ON r.hour_id = h.hour_id
WHERE h.tz_offset_hours = 3
  AND h.slot_start_date_local::DATE BETWEEN '2026-01-01' AND '2026-12-31'
''')
df_db = pd.DataFrame(cur.fetchall(), columns=['date', 'hour_branch', 'rasklad_id', 'hour_stem', 'hb', 'day_stem', 'day_branch'])
conn.close()

# Извлекаем ju_num и yy из DB rasklad_id
def parse_db_rasklad(rid):
    # "Yang_4_丁丑" → yy='Yang', ju=4
    parts = rid.split('_')
    if len(parts) >= 2:
        return parts[0], int(parts[1])
    return None, None

df_db[['db_yy', 'db_ju']] = df_db['rasklad_id'].apply(
    lambda x: pd.Series(parse_db_rasklad(x))
)

# Сравниваем ju_num
merged = df_excel.merge(df_db, on=['date', 'hour_branch'], how='inner')
merged['ju_match'] = merged['excel_ju'] == merged['db_ju']
merged['yy_match'] = merged['excel_yy'] == merged['db_yy']
merged['full_match'] = merged['ju_match'] & merged['yy_match']

total = len(merged)
ju_matched = merged['ju_match'].sum()
yy_matched = merged['yy_match'].sum()
full_matched = merged['full_match'].sum()

with open('comparison_result.txt', 'w', encoding='utf-8') as f:
    f.write(f'Total records: {total}\n')
    f.write(f'Ju match: {ju_matched} ({ju_matched/total*100:.2f}%)\n')
    f.write(f'YY match: {yy_matched} ({yy_matched/total*100:.2f}%)\n')
    f.write(f'Full match (ju+yy): {full_matched} ({full_matched/total*100:.2f}%)\n')
    f.write('\nFirst 30 ju mismatches:\n')
    mismatches = merged[~merged['ju_match']].head(30)
    for _, row in mismatches.iterrows():
        f.write(f"{row['date']} {row['hour_branch']}: Excel={row['hour_chart']} DB={row['rasklad_id']} "
                f"day={row['day_stem']}{row['day_branch']} hour={row['hour_stem']}{row['hour_branch']}\n")

print(f'Total: {total}, Ju match: {int(ju_matched)} ({ju_matched/total*100:.2f}%), Full: {int(full_matched)} ({full_matched/total*100:.2f}%)')
