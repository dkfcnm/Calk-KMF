"""Расчёт столпов бацзы на основе данных PostgreSQL.

Назначение модуля:
- определить структуры данных для отдельных столпов и набора из четырёх столпов;
- предоставить функции расчёта столпов года, месяца, дня и часа с учётом локального времени;
- агрегировать расчёт всех четырёх столпов в одной функции.

Последнее обновление: 2025-12-25 15:45 MSK.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Any

from .db import ensure_utc, get_connection, get_placeholder
from .solar_terms import (
    get_prev_solar_term,
    get_solar_term_crossing,
    tz_from_offset,
)


__all__ = [
    "Pillar",
    "FourPillars",
    "calc_year_pillar",
    "calc_month_pillar",
    "calc_day_pillar",
    "calc_hour_pillar",
    "calc_four_pillars",
]


@dataclass
class Pillar:
    """Небесный ствол и земная ветвь одного столпа.

    Последнее обновление: 2025-12-25 15:45 MSK.
    """

    stem_char: str
    branch_char: str


@dataclass
class FourPillars:
    """Четыре столпа бацзы (год, месяц, день, час).

    Последнее обновление: 2025-12-25 15:45 MSK.
    """

    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar


def calc_year_pillar(
    dt_utc: datetime,
    conn: Any,
    tz_offset_hours: int = 0,
) -> Pillar:
    """Возвращает столп года, используя термин Ли Чунь (315°).

    Параметры:
    - dt_utc: момент времени в UTC;
    - conn: активное соединение (DBManager / pg8000);
    - tz_offset_hours: локальный сдвиг времени относительно UTC.

    Правила:
    - при наличии данных HKO время начала сезона берётся из `t_solar_term_time_hko`;
    - иначе используется расчётное значение из `t_solar_term_time`.

    Последнее обновление: 2025-12-25 15:45 MSK.
    """

    dt_utc = ensure_utc(dt_utc)
    local_tz = tz_from_offset(tz_offset_hours)
    dt_local = dt_utc.astimezone(local_tz)
    year_local = dt_local.year
    cursor = conn.cursor()
    ph = get_placeholder()

    cursor.execute(
        f"SELECT solar_term_id FROM spr_solar_term WHERE longitude_deg = 315"
    )
    row_term = cursor.fetchone()
    if row_term is None:
        raise ValueError("В spr_solar_term отсутствует сезон с долготой 315°")
    solar_term_id = row_term[0]

    li_chun_dt_utc = get_solar_term_crossing(conn, year_local, solar_term_id)
    li_chun_dt_local = li_chun_dt_utc.astimezone(local_tz)
    bazi_year = year_local - 1 if dt_local < li_chun_dt_local else year_local

    base_year = 1864  # 甲子
    cycle_index = (bazi_year - base_year) % 60

    cursor.execute(
        f"""
        SELECT hs.stem_char, eb.branch_char
        FROM spr_pillar_cycle pc
        JOIN spr_heavenly_stem hs ON hs.stem_id = pc.stem_id
        JOIN spr_earthly_branch eb ON eb.branch_id = pc.branch_id
        WHERE pc.cycle_index = {ph}
        """,
        (cycle_index,),
    )
    row = cursor.fetchone()
    if row is None:
        raise ValueError(f"Не найден столп года для индекса {cycle_index}")

    return Pillar(*row)


def calc_month_pillar(
    dt_utc: datetime,
    conn: Any,
    tz_offset_hours: int = 0,
) -> Pillar:
    """Возвращает столп месяца, основываясь на текущем солнечном термине.

    Последнее обновление: 2025-12-25 15:45 MSK.
    """

    dt_utc = ensure_utc(dt_utc)
    cursor = conn.cursor()
    ph = get_placeholder()

    solar_term_id, _ = get_prev_solar_term(
        dt_utc,
        conn,
        tz_offset_hours=tz_offset_hours,
    )
    month_index = (solar_term_id + 1) // 2

    cursor.execute(
        f"""
        SELECT st.month_branch_id, eb.branch_char
        FROM spr_solar_term st
        JOIN spr_earthly_branch eb ON eb.branch_id = st.month_branch_id
        WHERE st.solar_term_id = {ph}
        """,
        (solar_term_id,),
    )
    row_branch = cursor.fetchone()
    if row_branch is None:
        raise ValueError(f"Нет данных для сезона {solar_term_id}")

    month_branch_id, month_branch_char = row_branch

    year_pillar = calc_year_pillar(
        dt_utc,
        conn,
        tz_offset_hours=tz_offset_hours,
    )
    cursor.execute(
        f"SELECT stem_id FROM spr_heavenly_stem WHERE stem_char = {ph}",
        (year_pillar.stem_char,),
    )
    row_year_stem = cursor.fetchone()
    if row_year_stem is None:
        raise ValueError(f"Ствол года {year_pillar.stem_char} не найден")
    year_stem_id = row_year_stem[0]

    cursor.execute(
        f"""
        SELECT hs.stem_char
        FROM spr_pillar_month_rule pmr
        JOIN spr_heavenly_stem hs ON hs.stem_id = pmr.month_stem_id
        WHERE pmr.year_stem_id = {ph} AND pmr.month_index = {ph}
        """,
        (year_stem_id, month_index),
    )
    row_month_stem = cursor.fetchone()
    if row_month_stem is None:
        raise ValueError(
            f"Нет правила для year_stem_id={year_stem_id}, month_index={month_index}"
        )

    month_stem_char = row_month_stem[0]
    return Pillar(month_stem_char, month_branch_char)


def calc_day_pillar(
    dt_utc: datetime,
    conn: Any,
    tz_offset_hours: int = 0,
) -> Pillar:
    """Возвращает столп дня с учётом смены суток в час 子 (23:00 локально).

    Последнее обновление: 2025-12-25 15:45 MSK.
    """

    dt_utc = ensure_utc(dt_utc)
    dt_local = dt_utc + timedelta(hours=tz_offset_hours)
    effective_date = (dt_local + timedelta(hours=1)).date()

    anchor_date = datetime(1864, 2, 5).date()  # 庚子

    cursor = conn.cursor()
    # Assuming standard cycle setup, just fetching from cycle table based on calculated index
    # We don't need to query for anchor every time if we know it.
    # But let's keep logic similar to original but check anchor if needed.
    # Original logic queried anchor cycle index.
    
    # Optimizing: 1864-02-05 is Geng Zi (36).
    anchor_cycle = 36 
    
    delta_days = (effective_date - anchor_date).days
    cycle_index = (anchor_cycle + delta_days) % 60

    ph = get_placeholder()
    cursor.execute(
        f"""
        SELECT hs.stem_char, eb.branch_char
        FROM spr_pillar_cycle pc
        JOIN spr_heavenly_stem hs ON hs.stem_id = pc.stem_id
        JOIN spr_earthly_branch eb ON eb.branch_id = pc.branch_id
        WHERE pc.cycle_index = {ph}
        """,
        (cycle_index,),
    )
    row = cursor.fetchone()
    if row is None:
        raise ValueError(f"Не найден столп дня для cycle_index={cycle_index}")

    return Pillar(*row)


def calc_hour_pillar(
    dt_utc: datetime,
    conn: Any,
    tz_offset_hours: int = 0,
) -> Pillar:
    """Возвращает столп часа, используя правила spr_earthly_branch и spr_pillar_hour_rule.

    Последнее обновление: 2026-02-08 MSK.
    """

    dt_utc = ensure_utc(dt_utc)
    dt_local = dt_utc + timedelta(hours=tz_offset_hours)
    hour_val = dt_local.hour
    cursor = conn.cursor()
    ph = get_placeholder()

    cursor.execute(
        "SELECT branch_id, start_hour, end_hour FROM spr_earthly_branch"
    )
    rows = cursor.fetchall()
    if not rows:
        raise ValueError("Таблица spr_earthly_branch пуста")

    hour_branch_id = None
    for branch_id, start_h, end_h in rows:
        if start_h is None: # Handle None values if any
             continue
        if start_h < end_h:
            if start_h <= hour_val < end_h:
                hour_branch_id = branch_id
                break
        else:
            if hour_val >= start_h or hour_val < end_h:
                hour_branch_id = branch_id
                break

    if hour_branch_id is None:
        raise ValueError(f"Не удалось определить ветвь часа для H={hour_val}")

    cursor.execute(
        f"SELECT branch_char FROM spr_earthly_branch WHERE branch_id = {ph}",
        (hour_branch_id,),
    )
    row_branch = cursor.fetchone()
    if row_branch is None:
        raise ValueError(
            f"Не найдена земная ветвь для branch_id={hour_branch_id}"
        )
    hour_branch_char = row_branch[0]

    day_pillar = calc_day_pillar(dt_utc, conn, tz_offset_hours=tz_offset_hours)
    cursor.execute(
        f"SELECT stem_id FROM spr_heavenly_stem WHERE stem_char = {ph}",
        (day_pillar.stem_char,),
    )
    row_day_stem = cursor.fetchone()
    if row_day_stem is None:
        raise ValueError(
            f"Не найден stem_id для ствола дня '{day_pillar.stem_char}'"
        )
    day_stem_id = row_day_stem[0]

    cursor.execute(
        f"""
        SELECT hs.stem_char
        FROM spr_pillar_hour_rule phr
        JOIN spr_heavenly_stem hs ON hs.stem_id = phr.hour_stem_id
        WHERE phr.day_stem_id = {ph} AND phr.hour_branch_id = {ph}
        """,
        (day_stem_id, hour_branch_id),
    )
    row_hour_stem = cursor.fetchone()
    if row_hour_stem is None:
        raise ValueError(
            "Не найдено правило spr_pillar_hour_rule для day_stem_id="
            f"{day_stem_id}, hour_branch_id={hour_branch_id}"
        )
    hour_stem_char = row_hour_stem[0]

    return Pillar(hour_stem_char, hour_branch_char)


def calc_four_pillars(
    dt: datetime,
    conn: Optional[Any] = None,
    tz_offset_hours: int = 0,
) -> FourPillars:
    """Возвращает четыре столпа для переданного момента времени (в UTC).

    Последнее обновление: 2025-12-25 15:45 MSK.
    """

    dt_utc = ensure_utc(dt)

    created_conn = False
    if conn is None:
        conn = get_connection()
        created_conn = True

    try:
        year = calc_year_pillar(dt_utc, conn, tz_offset_hours=tz_offset_hours)
        month = calc_month_pillar(dt_utc, conn, tz_offset_hours=tz_offset_hours)
        day = calc_day_pillar(dt_utc, conn, tz_offset_hours=tz_offset_hours)
        hour = calc_hour_pillar(dt_utc, conn, tz_offset_hours=tz_offset_hours)
        return FourPillars(year=year, month=month, day=day, hour=hour)
    finally:
        if created_conn:
            conn.close()
