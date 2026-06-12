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

# Пересчитаем ju_num с использованием day_pillar из 子 часа для всех часов
cur.execute('''
WITH zi_pillars AS (
    SELECT DISTINCT ON (slot_start_date_local::DATE, tz_offset_hours)
        slot_start_date_local::DATE as date,
        tz_offset_hours,
        day_stem, day_branch,
        (SELECT stem_id FROM spr_heavenly_stem WHERE stem_char = t_bazi_hourly.day_stem) as d_stem_id,
        (SELECT branch_id FROM spr_earthly_branch WHERE branch_char = t_bazi_hourly.day_branch) as d_branch_id
    FROM t_bazi_hourly
    WHERE hour_branch = '子'
    ORDER BY slot_start_date_local::DATE, tz_offset_hours, slot_start_time_local
),
base_data AS (
    SELECT 
        h.hour_id,
        h.slot_start_date_local::DATE as curr_date,
        h.hour_stem, h.hour_branch,
        zi.day_stem as classical_day_stem,
        zi.day_branch as classical_day_branch,
        zi.d_stem_id,
        zi.d_branch_id
    FROM t_bazi_hourly h
    JOIN zi_pillars zi ON zi.date = h.slot_start_date_local::DATE AND zi.tz_offset_hours = h.tz_offset_hours
    WHERE h.tz_offset_hours = 3
      AND h.slot_start_date_local::DATE BETWEEN '2026-01-01' AND '2026-12-31'
),
calc_futou AS (
    SELECT
        hour_id, curr_date, classical_day_stem, classical_day_branch, hour_stem, hour_branch,
        d_stem_id, d_branch_id,
        ((d_stem_id - 1) % 5) as offset_days,
        (6 * (d_stem_id - 1) - 5 * (d_branch_id - 1) + 60) % 60 as jiazi_idx
    FROM base_data
),
futou_date AS (
    SELECT
        *,
        (curr_date - (offset_days || ' days')::INTERVAL)::DATE as f_date,
        (jiazi_idx / 5)::INT % 3 as yuan_idx
    FROM calc_futou
),
term_lookup AS (
    SELECT
        f.hour_id, f.hour_stem, f.hour_branch, f.yuan_idx,
        st.solar_term_id
    FROM futou_date f
    JOIN LATERAL (
        SELECT solar_term_id
        FROM t_solar_term_time
        WHERE crossing_utc::DATE <= f.f_date
        ORDER BY crossing_utc DESC
        LIMIT 1
    ) st ON TRUE
),
calc_ju AS (
    SELECT
        tl.hour_id, tl.hour_stem, tl.hour_branch,
        tl.solar_term_id,
        (CASE WHEN tl.solar_term_id BETWEEN 10 AND 21 THEN 'Yin' ELSE 'Yang' END) as yy_str,
        (CASE 
            WHEN tl.yuan_idx = 0 THEN st.upper_ju
            WHEN tl.yuan_idx = 1 THEN st.middle_ju
            ELSE st.lower_ju
         END) as ju_num
    FROM term_lookup tl
    JOIN spr_solar_term st ON st.solar_term_id = tl.solar_term_id
)
SELECT 
    h.slot_start_date_local::DATE as date,
    h.hour_branch,
    c.yy_str || '_' || c.ju_num || '_' || h.hour_stem || h.hour_branch as rasklad_id
FROM calc_ju c
JOIN t_bazi_hourly h ON h.hour_id = c.hour_id
''')
rows = cur.fetchall()
conn.close()

df_db = pd.DataFrame(rows, columns=['date', 'hour_branch', 'rasklad_id'])

def parse_db(rid):
    parts = rid.split('_')
    return parts[0], int(parts[1])

df_db[['db_yy', 'db_ju']] = df_db['rasklad_id'].apply(lambda x: pd.Series(parse_db(x)))

merged = df_excel.merge(df_db, on=['date', 'hour_branch'], how='inner')
merged['ju_match'] = merged['excel_ju'] == merged['db_ju']
merged['full_match'] = merged['ju_match'] & (merged['excel_yy'] == merged['db_yy'])

total = len(merged)
ju_matched = merged['ju_match'].sum()
full_matched = merged['full_match'].sum()

with open('zi_day_comparison.txt', 'w', encoding='utf-8') as f:
    f.write(f'Classical day pillar from Zi hour: Total={total}, Ju match={ju_matched} ({ju_matched/total*100:.1f}%), Full={full_matched} ({full_matched/total*100:.1f}%)\n')
    f.write('\nFirst 20 mismatches:\n')
    mismatches = merged[~merged['ju_match']].head(20)
    for _, row in mismatches.iterrows():
        f.write(f"{row['date']} {row['hour_branch']}: Excel={row['hour_chart']} DB={row['rasklad_id']}\n")

print(f'Done: Ju match={ju_matched} ({ju_matched/total*100:.1f}%)')
