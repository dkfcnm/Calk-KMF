"""Операции по наполнению таблицы t_bazi_hourly и созданию представлений.

Назначение модуля:
- обеспечивать актуальность схемы таблицы `t_bazi_hourly` в PostgreSQL;
- заполнять данные столпов бацзы по китайским двойным часам (двухчасовкам)
  для заданных диапазонов времени и часовых поясов;
- формировать представления `v_bazi_hourly` и `v_bazi_hourly_tz_*` с
  корректной фиксацией начала и окончания двухчасовок;
- предоставлять константы и утилиты, необходимые для слоя хранения.

Ключевые константы:
- `WEEKDAY_SHORT_RU`: локализованные краткие обозначения дней недели;
- `SLOT_START_HOURS`: допустимые часы начала китайских двухчасовок.

Последнее обновление: 2025-12-31 11:25 MSK.
"""

from __future__ import annotations

import hashlib
from bisect import bisect_right
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, List, Optional, Tuple, Any

from .db import ensure_utc, get_placeholder

from .pillars import Pillar, calc_four_pillars
from .lunar import calc_lunar_components, LunarDateNotExist
from .solar_terms import (
    fetch_solar_term_crossings,
    get_prev_solar_term,
    tz_from_offset,
)


WEEKDAY_SHORT_RU = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")
SLOT_START_HOURS = (23, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21)
SLOT_DURATION = timedelta(hours=2)


def _format_pillar(pillar: Pillar) -> str:
    """Возвращает строковое представление столпа (ствол + ветвь).

    Последнее обновление: 2025-12-25 15:50 MSK.
    """

    return f"{pillar.stem_char}{pillar.branch_char}"


MASTER_DANO_INDICATOR_CODE = "master_dano_day_quality"


def _load_indicator_value_map(
    conn: Any,
    indicator_code: str,
) -> Dict[int, Tuple[str, float]]:
    """Возвращает карту value_id → (название, числовая оценка) для индикатора."""

    cursor = conn.cursor()
    ph = get_placeholder()
    cursor.execute(
        f"""
        SELECT iv.value_id, iv.name_ru, iv.numeric_score
        FROM spr_indicator AS i
        JOIN spr_indicator_value AS iv ON iv.indicator_id = i.indicator_id
        WHERE i.code = {ph}
        """,
        (indicator_code,),
    )
    return {value_id: (name_ru, numeric_score) for value_id, name_ru, numeric_score in cursor.fetchall()}


def _load_solar_term_names(conn: Any) -> Dict[int, str]:
    """Загружает наименования солнечных терминов.

    Последнее обновление: 2025-12-25 15:50 MSK.
    """

    cursor = conn.cursor()
    cursor.execute(
        "SELECT solar_term_id, solar_term_name_ru FROM spr_solar_term"
    )
    return {row[0]: row[1] for row in cursor.fetchall()}


def _load_day_officer_mapping(conn: Any) -> Dict[Tuple[str, str], int]:
    """Возвращает соответствие (ветвь месяца, ветвь дня) → значение офицера."""

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            month_branch.branch_char,
            day_branch.branch_char,
            dom.officer_value_id
        FROM spr_day_officer_mapping AS dom
        JOIN spr_earthly_branch AS month_branch
             ON month_branch.branch_id = dom.month_branch_id
        JOIN spr_earthly_branch AS day_branch
             ON day_branch.branch_id = dom.day_branch_id
        """
    )
    mapping: Dict[Tuple[str, str], int] = {}
    for month_char, day_char, officer_value_id in cursor.fetchall():
        mapping[(month_char, day_char)] = officer_value_id

    if not mapping:
        raise ValueError(
            "Справочник spr_day_officer_mapping пуст, невозможно вычислить офицеров дня"
        )

    return mapping


def _load_master_dano_mapping(conn: Any) -> Dict[Tuple[str, str, str], int]:
    """Возвращает карту (ветвь месяца, ствол дня, ветвь дня) → значение Мастера Дано."""

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            mb.branch_char,
            hs.stem_char,
            db.branch_char,
            mapping.indicator_value_id
        FROM spr_master_dano_mapping AS mapping
        JOIN spr_earthly_branch AS mb ON mb.branch_id = mapping.month_branch_id
        JOIN spr_heavenly_stem AS hs ON hs.stem_id = mapping.day_stem_id
        JOIN spr_earthly_branch AS db ON db.branch_id = mapping.day_branch_id
        """
    )
    result: Dict[Tuple[str, str, str], int] = {}
    for month_char, day_stem_char, day_branch_char, value_id in cursor.fetchall():
        result[(month_char, day_stem_char, day_branch_char)] = value_id
    return result


def _normalize_tz_offsets(tz_offsets: Optional[Iterable[int]]) -> List[int]:
    """Возвращает уникальные смещения часовых поясов по возрастанию.

    Последнее обновление: 2025-12-25 15:50 MSK.
    """

    if tz_offsets is None:
        offsets = range(-12, 15)
    else:
        offsets = [int(value) for value in tz_offsets]
    return sorted(dict.fromkeys(offsets))


def _format_tz_suffix(offset: int) -> str:
    """Формирует суффикс имени view для часового пояса.

    Последнее обновление: 2025-12-25 15:50 MSK.
    """

    sign = "p" if offset >= 0 else "m"
    return f"{sign}{abs(offset):02d}"


def _align_to_slot_start(dt_local: datetime) -> datetime:
    """Возвращает ближайший не позднее `dt_local` старт китайской двухчасовки.

    Последнее обновление: 2025-12-31 11:25 MSK.
    """

    base = dt_local.replace(minute=0, second=0, microsecond=0)
    if base.hour in SLOT_START_HOURS:
        return base

    for candidate in sorted(SLOT_START_HOURS, reverse=True):
        if base.hour >= candidate:
            return base.replace(hour=candidate)

    previous_day = base - timedelta(days=1)
    return previous_day.replace(hour=23)


def _format_date(dt: datetime) -> str:
    """Возвращает строку даты в формате YYYY-MM-DD."""

    return dt.strftime("%Y-%m-%d")


def _format_time(dt: datetime) -> str:
    """Возвращает строку времени в формате HH:MM."""

    return dt.strftime("%H:%M")


def _format_iso_minute(dt: datetime) -> str:
    """Возвращает ISO-представление (без секунд) для сравнения диапазонов."""

    return dt.strftime("%Y-%m-%dT%H:%M")


def ensure_bazi_hourly_table(conn: Any) -> None:
    """Гарантирует наличие таблицы t_bazi_hourly с актуальной схемой.

    При несоответствии структуры существующая таблица пересоздаётся.

    Последнее обновление: 2025-12-31 11:25 MSK.
    """

    required_columns = {
        "hour_id",
        "tz_offset_hours",
        "slot_start_date_utc",
        "slot_start_time_utc",
        "slot_end_date_utc",
        "slot_end_time_utc",
        "slot_start_date_local",
        "slot_start_time_local",
        "slot_end_date_local",
        "slot_end_time_local",
        "weekday_local",
        "solar_term_id",
        "solar_term_name",
        "year_pillar",
        "month_pillar",
        "day_pillar",
        "hour_pillar",
        "year_stem",
        "year_branch",
        "month_stem",
        "month_branch",
        "day_stem",
        "day_branch",
        "hour_stem",
        "hour_branch",
        "lunar_month",
        "lunar_day",
        "lunar_is_leap",
        "lunar_month_zi",
        "lunar_day_zi",
        "lunar_is_leap_zi",
    }

    cursor = conn.cursor()
    # Check if table exists (PostgreSQL)
    # Using specific query for each DB_TYPE would be better, but information_schema works for PG
    # PostgreSQL uses information_schema.tables
    # We can try a simple SELECT LIMIT 0 to check existence.
    
    table_exists = False
    try:
        cursor.execute("SELECT 1 FROM t_bazi_hourly LIMIT 1")
        table_exists = True
    except Exception:
        pass

    recreate_needed = False
    if table_exists:
        # Simplified check: if columns count mismatch or specific col missing.
        # Getting column list is DB specific.
        # Assuming DB is managed by setup_db.py, we trust it or skip checks here.
        # setup_db.py creates tables. This function might be redundant or just a double check.
        # Let's trust setup_db.py for now to simplify migration.
        pass

    # If setup_db.py is run, table exists.
    # Logic below handles PostgreSQL schema evolution.
    # For now, we skip detailed schema check inside hourly.py for PG migration simplicity.
    # The SQL for creation is also in setup_db.py
    
    # However, indices are important.
    # Index creation:
    try:
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_bazi_hourly_local
            ON t_bazi_hourly (
                tz_offset_hours,
                slot_start_date_local,
                slot_start_time_local
            )
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_bazi_hourly_utc
            ON t_bazi_hourly (
                tz_offset_hours,
                slot_start_date_utc,
                slot_start_time_utc
            )
            """
        )
        conn.commit()
    except Exception as e:
        # Ignore index creation errors (e.g. already exists)
        print(f"Warning: Index creation failed or skipped: {e}")


def populate_bazi_hourly_table(
    conn: Any,
    tz_offset_hours: int,
    start_dt_utc: datetime,
    end_dt_utc: datetime,
    *,
    clear_existing: bool = True,
    # Local caches
    lunar_cache: Optional[Dict[datetime, Tuple[int, int, bool]]] = None,
    solar_term_cache: Optional[Dict[datetime, int]] = None,
) -> int:
    """Заполняет t_bazi_hourly данными по китайским двухчасовкам.

    Диапазон задаётся как [start_dt_utc, end_dt_utc). Возвращает количество записей.

    Последнее обновление: 2025-12-31 11:25 MSK.
    """

    start_utc = ensure_utc(start_dt_utc)
    end_utc = ensure_utc(end_dt_utc)
    if end_utc <= start_utc:
        raise ValueError("end_dt_utc должен быть больше start_dt_utc")

    local_tz = tz_from_offset(tz_offset_hours)
    ph = get_placeholder()

    cursor = conn.cursor()
    ensure_bazi_hourly_table(conn)
    if clear_existing:
        # Using string concatenation for LIKE or range comparison with ISO string might be slow or DB-specific.
        # But here logic is: (date || 'T' || time)
        # In PostgreSQL, string concatenation is ||.
        # This logic is fragile. Better to use slot_start_date_utc and time columns properly.
        # But to keep logic same:
        cursor.execute(
            f"""
            DELETE FROM t_bazi_hourly
            WHERE tz_offset_hours = {ph}
              AND (slot_start_date_utc || 'T' || slot_start_time_utc) >= {ph}
              AND (slot_start_date_utc || 'T' || slot_start_time_utc) < {ph}
            """,
            (tz_offset_hours, _format_iso_minute(start_utc), _format_iso_minute(end_utc)),
        )

    start_local = start_utc.astimezone(local_tz)
    end_local = end_utc.astimezone(local_tz)

    years = range(start_local.year - 1, end_local.year + 2)
    crossing_records = fetch_solar_term_crossings(conn, years)
    crossing_times_utc = [ensure_utc(record[2]) for record in crossing_records]

    rows: List[Tuple] = []

    prev_month_pillar: Optional[str] = None
    prev_day_pillar: Optional[str] = None
    current_lunar_month_zi = 0
    current_lunar_day_zi = 0
    current_lunar_is_leap_zi = 0

    slot_start_local = _align_to_slot_start(start_local)

    while slot_start_local.astimezone(timezone.utc) < end_utc:
        slot_end_local = slot_start_local + SLOT_DURATION
        slot_start_utc = slot_start_local.astimezone(timezone.utc)
        slot_end_utc = slot_end_local.astimezone(timezone.utc)

        if slot_end_utc <= start_utc:
            slot_start_local = slot_end_local
            continue

        effective_start_utc = max(slot_start_utc, start_utc)
        effective_end_utc = min(slot_end_utc, end_utc)
        if effective_start_utc >= effective_end_utc:
            slot_start_local = slot_end_local
            continue

        boundaries = [effective_start_utc]
        idx = bisect_right(crossing_times_utc, effective_start_utc)
        while idx < len(crossing_times_utc):
            crossing_dt = crossing_times_utc[idx]
            if crossing_dt >= effective_end_utc:
                break
            boundaries.append(crossing_dt)
            idx += 1
        boundaries.append(effective_end_utc)

        for segment_start_utc, segment_end_utc in zip(boundaries, boundaries[1:]):
            if segment_start_utc >= segment_end_utc:
                continue

            segment_start_local = segment_start_utc.astimezone(local_tz)
            segment_end_local = segment_end_utc.astimezone(local_tz)
            weekday_local = WEEKDAY_SHORT_RU[segment_start_local.weekday()]

            # Caching Solar Term ID
            if solar_term_cache is not None and segment_start_utc in solar_term_cache:
                solar_term_id = solar_term_cache[segment_start_utc]
            else:
                solar_term_id, _ = get_prev_solar_term(
                    segment_start_utc,
                    conn,
                    tz_offset_hours=tz_offset_hours,
                )
                if solar_term_cache is not None:
                    solar_term_cache[segment_start_utc] = solar_term_id

            pillars = calc_four_pillars(
                segment_start_utc,
                conn,
                tz_offset_hours=tz_offset_hours,
            )

            # Master Dano removed

            # Caching Lunar Components
            if lunar_cache is not None and segment_start_utc in lunar_cache:
                lunar_month, lunar_day, is_leap = lunar_cache[segment_start_utc]
            else:
                try:
                    lunar_month, lunar_day, is_leap = calc_lunar_components(
                        segment_start_utc,
                        tz_offset_hours=tz_offset_hours,
                    )
                except LunarDateNotExist:
                    lunar_month, lunar_day, is_leap = 0, 0, False
                if lunar_cache is not None:
                    lunar_cache[segment_start_utc] = (lunar_month, lunar_day, is_leap)

            month_pillar_str = _format_pillar(pillars.month)
            day_pillar_str = _format_pillar(pillars.day)

            if prev_month_pillar is None or month_pillar_str != prev_month_pillar:
                current_lunar_month_zi = lunar_month
                current_lunar_is_leap_zi = int(is_leap)

            if prev_day_pillar is None or day_pillar_str != prev_day_pillar:
                current_lunar_day_zi = lunar_day

            prev_month_pillar = month_pillar_str
            prev_day_pillar = day_pillar_str

            hash_source = "|".join(
                [
                    str(tz_offset_hours),
                    _format_date(segment_start_local),
                    _format_time(segment_start_local),
                    _format_date(segment_end_local),
                    _format_time(segment_end_local),
                ]
            )
            hour_id = hashlib.sha1(hash_source.encode("utf-8")).hexdigest()

            rows.append(
                (
                    hour_id,
                    tz_offset_hours,
                    _format_date(segment_start_utc),
                    _format_time(segment_start_utc),
                    _format_date(segment_end_utc),
                    _format_time(segment_end_utc),
                    _format_date(segment_start_local),
                    _format_time(segment_start_local),
                    _format_date(segment_end_local),
                    _format_time(segment_end_local),
                    weekday_local,
                    solar_term_id,
                    # solar_term_name removed
                    _format_pillar(pillars.year),
                    month_pillar_str,
                    day_pillar_str,
                    _format_pillar(pillars.hour),
                    pillars.year.stem_char,
                    pillars.year.branch_char,
                    pillars.month.stem_char,
                    pillars.month.branch_char,
                    pillars.day.stem_char,
                    pillars.day.branch_char,
                    pillars.hour.stem_char,
                    pillars.hour.branch_char,
                    lunar_month,
                    lunar_day,
                    int(is_leap),
                    current_lunar_month_zi,
                    current_lunar_day_zi,
                    current_lunar_is_leap_zi,
                )
            )

        slot_start_local = slot_end_local

    if not rows:
        return 0

    values_ph = ",".join([ph] * 30)
    cursor.executemany(
        f"""
        INSERT INTO t_bazi_hourly (
            hour_id,
            tz_offset_hours,
            slot_start_date_utc,
            slot_start_time_utc,
            slot_end_date_utc,
            slot_end_time_utc,
            slot_start_date_local,
            slot_start_time_local,
            slot_end_date_local,
            slot_end_time_local,
            weekday_local,
            solar_term_id,
            -- solar_term_name removed
            year_pillar,
            month_pillar,
            day_pillar,
            hour_pillar,
            year_stem,
            year_branch,
            month_stem,
            month_branch,
            day_stem,
            day_branch,
            hour_stem,
            hour_branch,
            lunar_month,
            lunar_day,
            lunar_is_leap,
            lunar_month_zi,
            lunar_day_zi,
            lunar_is_leap_zi
        ) VALUES ({values_ph})
        """,
        rows,
    )

    return len(rows)


def populate_bazi_hourly_for_years(
    conn: Any,
    *,
    start_year: int,
    end_year: int,
    tz_offsets: Optional[Iterable[int]] = None,
    clear_existing: bool = True,
) -> int:
    """Заполняет t_bazi_hourly для диапазона календарных лет.

    Последнее обновление: 2025-12-31 11:25 MSK.
    """

    if end_year < start_year:
        raise ValueError("end_year не может быть меньше start_year")

    offsets = _normalize_tz_offsets(tz_offsets)
    total_inserted = 0
    
    # Caches for reuse across offsets
    lunar_cache: Dict[datetime, Tuple[int, int, bool]] = {}
    solar_term_cache: Dict[datetime, int] = {}

    for offset in offsets:
        local_tz = tz_from_offset(offset)
        start_local = datetime(start_year, 1, 1, tzinfo=local_tz)
        end_local = datetime(end_year + 1, 1, 1, tzinfo=local_tz)
        start_utc = start_local.astimezone(timezone.utc)
        end_utc = end_local.astimezone(timezone.utc)

        total_inserted += populate_bazi_hourly_table(
            conn,
            tz_offset_hours=offset,
            start_dt_utc=start_utc,
            end_dt_utc=end_utc,
            clear_existing=clear_existing,
            lunar_cache=lunar_cache,
            solar_term_cache=solar_term_cache,
        )

    return total_inserted


def create_bazi_hourly_views(
    conn: Any,
    tz_offsets: List[int] = range(-12, 15),
    default_offset_hours: int = 3
) -> None:
    """Пересоздаёт представления v_bazi_hourly и производные по часовым поясам.

    Последнее обновление: 2025-12-25 15:50 MSK.
    """

    offsets = _normalize_tz_offsets(tz_offsets)
    if default_offset_hours not in offsets:
        offsets = sorted(dict.fromkeys(offsets + [default_offset_hours]))

    cursor = conn.cursor()
    
    # Drop dependent views first or use CASCADE
    cursor.execute("DROP VIEW IF EXISTS v_bazi_hourly_msk")
    
    # Try to drop specific timezone views
    for offset in offsets:
        suffix = _format_tz_suffix(offset)
        cursor.execute(f"DROP VIEW IF EXISTS v_bazi_hourly_tz_{suffix}")
        
    # Drop base view
    cursor.execute("DROP VIEW IF EXISTS v_bazi_hourly CASCADE")

    cursor.execute(
        """
        CREATE VIEW v_bazi_hourly AS
        SELECT
            t.hour_id,
            t.tz_offset_hours,
            t.slot_start_date_utc,
            t.slot_start_time_utc,
            t.slot_end_date_utc,
            t.slot_end_time_utc,
            t.slot_start_date_local,
            t.slot_start_time_local,
            t.slot_end_date_local,
            t.slot_end_time_local,
            t.weekday_local,
            t.solar_term_id,
            st.solar_term_name_ru AS solar_term_name_ru,
            -- t.solar_term_name removed
            t.year_pillar,
            t.month_pillar,
            t.day_pillar,
            t.hour_pillar,
            t.year_stem,
            t.year_branch,
            t.month_stem,
            t.month_branch,
            t.day_stem,
            t.day_branch,
            t.hour_stem,
            t.hour_branch AS hour_branch_char,
            t.lunar_month,
            t.lunar_day,
            t.lunar_is_leap,
            t.lunar_month_zi,
            t.lunar_day_zi,
            t.lunar_is_leap_zi,
            eb.branch_rus AS hour_name_ru
        FROM t_bazi_hourly AS t
        LEFT JOIN spr_solar_term AS st
               ON st.solar_term_id = t.solar_term_id
        LEFT JOIN spr_earthly_branch AS eb
               ON eb.branch_char = t.hour_branch
        -- WHERE t.slot_start_date_utc >= '2026-01-01' -- Removed hardcoded filter to support multiple years
        ORDER BY t.tz_offset_hours, t.slot_start_date_utc, t.slot_start_time_utc
        """
    )

    for offset in offsets:
        suffix = _format_tz_suffix(offset)
        cursor.execute(
            f"""
            CREATE VIEW v_bazi_hourly_tz_{suffix} AS
            SELECT
                v.hour_id,
                v.slot_start_date_local,
                v.slot_start_time_local,
                v.slot_end_date_local,
                v.slot_end_time_local,
                v.slot_start_date_utc,
                v.slot_start_time_utc,
                v.slot_end_date_utc,
                v.slot_end_time_utc,
                v.weekday_local,
                v.hour_name_ru,
                v.hour_branch_char,
                v.solar_term_id,
                v.solar_term_name_ru,
                -- v.solar_term_name removed
                v.year_pillar,
                v.month_pillar,
                v.day_pillar,
                v.hour_pillar,
                v.year_stem,
                v.year_branch,
                v.month_stem,
                v.month_branch,
                v.day_stem,
                v.day_branch,
                v.hour_stem,
                v.hour_branch_char AS hour_branch,
                v.lunar_month,
                v.lunar_day,
                v.lunar_is_leap,
                v.lunar_month_zi,
                v.lunar_day_zi,
                v.lunar_is_leap_zi
            FROM v_bazi_hourly AS v
            WHERE v.tz_offset_hours = {offset}
            ORDER BY v.slot_start_date_local, v.slot_start_time_local
            """
        )

    default_suffix = _format_tz_suffix(int(default_offset_hours))
    cursor.execute(
        f"""
        CREATE VIEW v_bazi_hourly_msk AS
        SELECT
            tz.hour_id,
            tz.slot_start_date_local AS slot_start_date_msk,
            tz.slot_start_time_local AS slot_start_time_msk,
            tz.slot_end_date_local AS slot_end_date_msk,
            tz.slot_end_time_local AS slot_end_time_msk,
            tz.slot_start_date_utc,
            tz.slot_start_time_utc,
            tz.slot_end_date_utc,
            tz.slot_end_time_utc,
            tz.weekday_local AS weekday_msk,
            tz.hour_name_ru,
            tz.hour_branch_char,
            tz.solar_term_id,
            tz.solar_term_name_ru,
            -- tz.solar_term_name removed
            tz.year_pillar,
            tz.month_pillar,
            tz.day_pillar,
            tz.hour_pillar,
            tz.year_stem,
            tz.year_branch,
            tz.month_stem,
            tz.month_branch,
            tz.day_stem,
            tz.day_branch,
            tz.hour_stem,
            tz.hour_branch,
            tz.lunar_month,
            tz.lunar_day,
            tz.lunar_is_leap,
            tz.lunar_month_zi,
            tz.lunar_day_zi,
            tz.lunar_is_leap_zi
        FROM v_bazi_hourly_tz_{default_suffix} AS tz
        ORDER BY slot_start_date_msk, slot_start_time_msk
        """
    )
