import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List
import sys
import os

# Ensure imports work
sys.path.insert(0, os.getcwd())

from code.bazi_calendar.db import get_connection, ensure_utc, get_placeholder
from code.bazi_calendar.engine import BaziEngine
from code.bazi_calendar.hourly import ensure_bazi_hourly_table, SLOT_START_HOURS, SLOT_DURATION, _align_to_slot_start, _format_date, _format_time, WEEKDAY_SHORT_RU, _format_iso_minute
from code.bazi_calendar.solar_terms import tz_from_offset

DEFAULT_YEAR_START = 2025
DEFAULT_YEAR_END = 2027
DEFAULT_TZ_OFFSETS = range(-12, 15)
DEFAULT_BATCH_SIZE = 50000


def run_update(
    year_start=DEFAULT_YEAR_START,
    year_end=DEFAULT_YEAR_END,
    tz_offsets=DEFAULT_TZ_OFFSETS,
    batch_size=DEFAULT_BATCH_SIZE,
):
    print("Initializing Bazi Engine...")
    conn = get_connection()
    engine = BaziEngine(conn)
    
    print("Ensuring table schema...")
    ensure_bazi_hourly_table(conn)
    
    cursor = conn.cursor()
    print("Truncating t_bazi_hourly to ensure clean state...")
    cursor.execute("TRUNCATE TABLE t_bazi_hourly CASCADE")
    conn.commit()
    
    ph = get_placeholder()
    
    print(f"Generating data for years {year_start}-{year_end}...")
    
    data_batch = []
    total_count = 0
    
    for offset in tz_offsets:
        # Определение локального диапазона
        local_tz = tz_from_offset(offset)
        
        start_local = datetime(year_start, 1, 1, 0, 0, tzinfo=local_tz)
        end_local = datetime(year_end + 1, 1, 1, 0, 0, tzinfo=local_tz)
        
        # Выравнивание начала (Align BEFORE calculating UTC for delete range)
        curr_local = _align_to_slot_start(start_local)
        
        start_utc = ensure_utc(curr_local) # Use aligned start
        end_utc = ensure_utc(end_local)
        
        # Clear existing data for this range to allow simple INSERT
        print(f"Clearing existing data for offset {offset} (Start: {_format_iso_minute(start_utc)})...")
        cursor.execute(
            f"""
            DELETE FROM t_bazi_hourly
            WHERE tz_offset_hours = {ph}
              AND slot_start_date_utc >= {ph}
              AND slot_start_date_utc < {ph}
            """,
            (offset, _format_date(start_utc), _format_date(end_utc)),
        )
        conn.commit()
        
        # Состояние для лунных полей _zi
        prev_month_str = None
        prev_day_str = None
        lunar_m_zi = 0
        lunar_d_zi = 0
        lunar_leap_zi = 0
        
        while True:
            # Цикл до конца
            slot_end_local = curr_local + SLOT_DURATION
            
            # Проверка, прошли ли мы end_local
            if curr_local >= end_local:
                break
                
            curr_utc = ensure_utc(curr_local)
            slot_end_utc = ensure_utc(slot_end_local)
            
            res = engine.calc_pillars(curr_utc, offset)
            
            # Распаковка
            y = res['year']
            m = res['month']
            d = res['day']
            h = res['hour']
            
            y_str = str(y)
            m_str = str(m)
            d_str = str(d)
            h_str = str(h)
            
            lunar = res['lunar']
            lunar_m, lunar_d, lunar_leap = lunar
            
            # Логика Zi
            if prev_month_str is None or m_str != prev_month_str:
                lunar_m_zi = lunar_m
                lunar_leap_zi = int(lunar_leap)
            
            if prev_day_str is None or d_str != prev_day_str:
                lunar_d_zi = lunar_d
                
            prev_month_str = m_str
            prev_day_str = d_str
            
            # Hash ID
            # hash_source: tz|start_d|start_t|end_d|end_t (local)
            s_d_loc = _format_date(curr_local)
            s_t_loc = _format_time(curr_local)
            e_d_loc = _format_date(slot_end_local)
            e_t_loc = _format_time(slot_end_local)
            
            hash_src = f"{offset}|{s_d_loc}|{s_t_loc}|{e_d_loc}|{e_t_loc}"
            hour_id = hashlib.sha1(hash_src.encode('utf-8')).hexdigest()
            
            weekday = WEEKDAY_SHORT_RU[curr_local.weekday()]
            
            # Офицер и Мастер
            # REMOVED: mst = res['master'] 
            
            row = (
                hour_id,
                offset,
                _format_date(curr_utc), _format_time(curr_utc),
                _format_date(slot_end_utc), _format_time(slot_end_utc),
                s_d_loc, s_t_loc,
                e_d_loc, e_t_loc,
                weekday,
                res['solar_term_id'],
                # Removed solar_term_name column from schema in previous steps
                y_str, m_str, d_str, h_str,
                y.stem, y.branch,
                m.stem, m.branch,
                d.stem, d.branch,
                h.stem, h.branch,
                lunar_m, lunar_d, int(lunar_leap),
                lunar_m_zi, lunar_d_zi, lunar_leap_zi
                # REMOVED: mst[0], mst[2]
            )
            
            data_batch.append(row)
            
            if len(data_batch) >= batch_size:
                values_ph = ",".join([ph] * 30)
                cursor.executemany(f"""
                    INSERT INTO t_bazi_hourly (
                        hour_id, tz_offset_hours,
                        slot_start_date_utc, slot_start_time_utc,
                        slot_end_date_utc, slot_end_time_utc,
                        slot_start_date_local, slot_start_time_local,
                        slot_end_date_local, slot_end_time_local,
                        weekday_local, solar_term_id,
                        year_pillar, month_pillar, day_pillar, hour_pillar,
                        year_stem, year_branch, month_stem, month_branch,
                        day_stem, day_branch, hour_stem, hour_branch,
                        lunar_month, lunar_day, lunar_is_leap,
                        lunar_month_zi, lunar_day_zi, lunar_is_leap_zi
                    ) VALUES ({values_ph})
                """, data_batch)
                conn.commit()
                total_count += len(data_batch)
                data_batch = []
                print(f"Processed {total_count} rows...")
            
            # Next slot
            curr_local = slot_end_local

    if data_batch:
        values_ph = ",".join([ph] * 30)
        cursor.executemany(f"""
            INSERT INTO t_bazi_hourly (
                hour_id, tz_offset_hours,
                slot_start_date_utc, slot_start_time_utc,
                slot_end_date_utc, slot_end_time_utc,
                slot_start_date_local, slot_start_time_local,
                slot_end_date_local, slot_end_time_local,
                weekday_local, solar_term_id,
                year_pillar, month_pillar, day_pillar, hour_pillar,
                year_stem, year_branch, month_stem, month_branch,
                day_stem, day_branch, hour_stem, hour_branch,
                lunar_month, lunar_day, lunar_is_leap,
                lunar_month_zi, lunar_day_zi, lunar_is_leap_zi
            ) VALUES ({values_ph})
        """, data_batch)
        conn.commit()
        total_count += len(data_batch)
        
    print(f"Finished. Total rows: {total_count}")
    
    # Recreate views (using hourly.py logic)
    from code.bazi_calendar.hourly import create_bazi_hourly_views
    print("Recreating views...")
    create_bazi_hourly_views(conn, default_offset_hours=3)
    conn.commit()
    
    conn.close()

if __name__ == "__main__":
    run_update()
