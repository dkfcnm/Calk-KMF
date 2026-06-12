"""Работа с таблицами солнечных терминов в базе данных PostgreSQL.

Назначение модуля:
- читать времена пересечения солнечных терминов из таблиц `t_solar_term_time` и `t_solar_term_time_hko`;
- предоставлять функции для определения актуального сезона относительно локального времени;
- инкапсулировать перевод между смещением UTC и объектом таймзоны.

Ключевые константы отсутствуют – все параметры передаются извне.

Последнее обновление: 2025-12-25 15:35 MSK.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, List, Tuple

from typing import Any

from .db import ensure_utc, parse_timestamp, get_placeholder


SolarTermRecord = Tuple[int, int, datetime]


def tz_from_offset(tz_offset_hours: int) -> timezone:
    """Возвращает объект таймзоны для переданного смещения относительно UTC.

    Последнее обновление: 2025-12-25 15:35 MSK.
    """

    return timezone(timedelta(hours=tz_offset_hours))


def fetch_solar_term_crossings(
    conn: Any,
    years: Iterable[int],
) -> List[SolarTermRecord]:
    """Загружает времена наступления солнечных терминов для списка лет.

    Параметры:
    - conn: открытое соединение с БД (pg8000 или аналог);
    - years: последовательность интересующих лет.

    Возвращаемое значение:
    - список кортежей (год, идентификатор термина, момент наступления в UTC),
      отсортированный по времени, с учётом переопределений из таблицы HKO.

    Последнее обновление: 2025-12-25 15:35 MSK.
    """

    years = list(dict.fromkeys(years))
    if not years:
        return []

    ph = get_placeholder()
    placeholders = ",".join(ph for _ in years)
    cursor = conn.cursor()

    records: Dict[Tuple[int, int], datetime] = {}
    cursor.execute(
        f"""
        SELECT year, solar_term_id, crossing_utc
        FROM t_solar_term_time
        WHERE year IN ({placeholders})
        """,
        years,
    )
    for year, solar_term_id, crossing_utc in cursor.fetchall():
        records[(year, solar_term_id)] = parse_timestamp(crossing_utc)

    try:
        cursor.execute(
            f"""
            SELECT year, solar_term_id, crossing_utc
            FROM t_solar_term_time_hko
            WHERE year IN ({placeholders})
            """,
            years,
        )
    except Exception:
        # Catch generic Exception because pg8000 might raise DatabaseError, etc.
        override_rows = []
    else:
        override_rows = cursor.fetchall()

    for year, solar_term_id, crossing_utc in override_rows:
        records[(year, solar_term_id)] = parse_timestamp(crossing_utc)

    merged = [
        (year, solar_term_id, crossing_dt)
        for (year, solar_term_id), crossing_dt in records.items()
    ]
    merged.sort(key=lambda item: item[2])
    return merged


def get_solar_term_crossing(
    conn: Any,
    year: int,
    solar_term_id: int,
) -> datetime:
    """Возвращает момент наступления указанного термина, предпочитая данные HKO.

    Исключения:
    - ValueError, если запись отсутствует в обеих таблицах.

    Последнее обновление: 2025-12-25 15:35 MSK.
    """

    cursor = conn.cursor()
    ph = get_placeholder()
    try:
        cursor.execute(
            f"""
            SELECT crossing_utc
            FROM t_solar_term_time_hko
            WHERE year = {ph} AND solar_term_id = {ph}
            """,
            (year, solar_term_id),
        )
    except Exception:
        row = None
    else:
        row = cursor.fetchone()
    if row is not None:
        return parse_timestamp(row[0])

    cursor.execute(
        f"""
        SELECT crossing_utc
        FROM t_solar_term_time
        WHERE year = {ph} AND solar_term_id = {ph}
        """,
        (year, solar_term_id),
    )
    row_base = cursor.fetchone()
    if row_base is None:
        raise ValueError(
            f"Не найден сезон year={year}, solar_term_id={solar_term_id} ни в одной таблице"
        )
    return parse_timestamp(row_base[0])


def get_prev_solar_term(
    dt_utc: datetime,
    conn: Any,
    tz_offset_hours: int = 0,
) -> Tuple[int, datetime]:
    """Возвращает (solar_term_id, crossing_dt_utc) последнего термина до момента.

    Алгоритм учитывает локальное время: текущий термин определяется по времени,
    полученному после перевода `dt_utc` в таймзону `UTC+tz_offset_hours`.

    Последнее обновление: 2025-12-25 15:35 MSK.
    """

    dt_utc = ensure_utc(dt_utc)
    local_tz = tz_from_offset(tz_offset_hours)
    dt_local = dt_utc.astimezone(local_tz)
    years = [dt_local.year - 1, dt_local.year, dt_local.year + 1]
    records = fetch_solar_term_crossings(conn, years)

    for solar_year, solar_term_id, crossing_dt in reversed(records):
        crossing_local = crossing_dt.astimezone(local_tz)
        if crossing_local <= dt_local:
            return solar_term_id, crossing_dt

    raise ValueError(f"Не найден сезон до {dt_utc.isoformat()}")
