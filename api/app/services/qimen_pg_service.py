#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qi Men PostgreSQL service.
Reads chart data (year/month/day/hour levels) and reference data from PostgreSQL.
"""
from datetime import date
from typing import Dict, List, Optional

from code.common.db_manager import db


def _parse_rasklad(rasklad_id: str) -> dict:
    """Parse rasklad_id like 'Yang_4_壬子' into components."""
    parts = rasklad_id.split("_")
    if len(parts) >= 3:
        return {
            "yin_yang": parts[0],
            "ju_num": int(parts[1]),
            "hour_stem_branch": parts[2],
        }
    return {"yin_yang": "Yang", "ju_num": 1, "hour_stem_branch": ""}


def _get_palaces_from_rasklad(rasklad_id: str) -> Dict[str, dict]:
    """Get all 9 palaces for a rasklad_id from spr_qimen_templates."""
    rows = db.fetch_all(
        """
        SELECT palace_no, heaven_stem, is_fou_tou_heaven, earth_stem,
               is_fou_tou_earth, star, is_main_star, gate, is_main_gate, spirit
        FROM spr_qimen_templates
        WHERE rasklad_id = %s
        ORDER BY palace_no
        """,
        [rasklad_id],
    )
    palaces = {}
    for row in rows:
        palaces[str(row[0])] = {
            "palace_no": row[0],
            "heaven_stem": row[1],
            "is_fou_tou_heaven": row[2],
            "earth_stem": row[3],
            "is_fou_tou_earth": row[4],
            "star": row[5],
            "is_main_star": row[6],
            "gate": row[7],
            "is_main_gate": row[8],
            "spirit": row[9],
        }
    return palaces


def get_hourly_charts(target_date: date, method: str = "zhirun") -> List[dict]:
    """Get all hourly charts for a specific day."""
    table = "t_qumen_dgiren_hourly" if method == "zhirun" else "t_qumen_chauby_hourly"
    rows = db.fetch_all(
        f"""
        SELECT DISTINCT q.hour_id, q.rasklad_id, h.slot_start_time_local, h.hour_pillar
        FROM {table} q
        JOIN t_bazi_hourly h ON q.hour_id = h.hour_id
        WHERE h.slot_start_date_local = %s AND h.tz_offset_hours = 0
        ORDER BY h.slot_start_time_local
        """,
        [target_date.isoformat()],
    )
    if not rows:
        return []

    rasklad_ids = list(set(row[1] for row in rows))
    palaces_rows = db.fetch_all(
        """
        SELECT rasklad_id, palace_no, heaven_stem, is_fou_tou_heaven, earth_stem,
               is_fou_tou_earth, star, is_main_star, gate, is_main_gate, spirit
        FROM spr_qimen_templates
        WHERE rasklad_id = ANY(%s)
        ORDER BY rasklad_id, palace_no
        """,
        [rasklad_ids],
    )
    palaces_map: Dict[str, Dict[str, dict]] = {}
    for row in palaces_rows:
        rid = row[0]
        if rid not in palaces_map:
            palaces_map[rid] = {}
        palaces_map[rid][str(row[1])] = {
            "palace_no": row[1],
            "heaven_stem": row[2],
            "is_fou_tou_heaven": row[3],
            "earth_stem": row[4],
            "is_fou_tou_earth": row[5],
            "star": row[6],
            "is_main_star": row[7],
            "gate": row[8],
            "is_main_gate": row[9],
            "spirit": row[10],
        }

    charts = []
    for row in rows:
        hour_id, rasklad_id, time_str, hour_pillar = row
        meta = _parse_rasklad(rasklad_id)
        charts.append(
            {
                "chart_id": f"{method}_{target_date.isoformat()}_{time_str}",
                "date_time": f"{target_date.isoformat()} {time_str}",
                "chart_num": meta["ju_num"],
                "yin_yang": meta["yin_yang"],
                "hour_pillar": hour_pillar,
                "method": method,
                "level": "hour",
                "palaces": palaces_map.get(rasklad_id, {}),
            }
        )
    return charts


def get_daily_chart(target_date: date, method: str = "zhirun") -> Optional[dict]:
    """Get daily chart for a specific day."""
    table = "t_qumen_dgiren_day" if method == "zhirun" else "t_qumen_chauby_day"
    bazi_row = db.fetch_one(
        """
        SELECT DISTINCT year_pillar, month_pillar, day_pillar
        FROM t_bazi_hourly
        WHERE slot_start_date_local = %s AND tz_offset_hours = 0
        LIMIT 1
        """,
        [target_date.isoformat()],
    )
    if not bazi_row:
        return None
    year_pillar, month_pillar, day_pillar = bazi_row
    row = db.fetch_one(
        f"""
        SELECT DISTINCT chart_id, rasklad_id
        FROM {table}
        WHERE year_pillar = %s AND month_pillar = %s AND day_pillar = %s
        LIMIT 1
        """,
        [year_pillar, month_pillar, day_pillar],
    )
    if not row:
        return None
    chart_id, rasklad_id = row
    meta = _parse_rasklad(rasklad_id)
    palaces = _get_palaces_from_rasklad(rasklad_id)
    return {
        "chart_id": f"{method}_day_{target_date.isoformat()}",
        "date_time": target_date.isoformat(),
        "chart_num": meta["ju_num"],
        "yin_yang": meta["yin_yang"],
        "year_pillar": year_pillar,
        "month_pillar": month_pillar,
        "day_pillar": day_pillar,
        "method": method,
        "level": "day",
        "palaces": palaces,
    }


def get_monthly_chart(year: int, month: int, method: str = "zhirun") -> Optional[dict]:
    """Get monthly chart."""
    table = "t_qumen_dgiren_month" if method == "zhirun" else "t_qumen_chauby_month"
    bazi_row = db.fetch_one(
        """
        SELECT DISTINCT year_pillar, month_pillar
        FROM t_bazi_hourly
        WHERE slot_start_date_local = %s AND tz_offset_hours = 0
        LIMIT 1
        """,
        [date(year, month, 15).isoformat()],
    )
    if not bazi_row:
        return None
    year_pillar, month_pillar = bazi_row
    row = db.fetch_one(
        f"""
        SELECT DISTINCT chart_id, rasklad_id
        FROM {table}
        WHERE year_pillar = %s AND month_pillar = %s
        LIMIT 1
        """,
        [year_pillar, month_pillar],
    )
    if not row:
        return None
    chart_id, rasklad_id = row
    meta = _parse_rasklad(rasklad_id)
    palaces = _get_palaces_from_rasklad(rasklad_id)
    return {
        "chart_id": f"{method}_month_{year}_{month}",
        "date_time": f"{year}-{month:02d}",
        "chart_num": meta["ju_num"],
        "yin_yang": meta["yin_yang"],
        "year_pillar": year_pillar,
        "month_pillar": month_pillar,
        "method": method,
        "level": "month",
        "palaces": palaces,
    }


def get_yearly_chart(year: int, method: str = "zhirun") -> Optional[dict]:
    """Get yearly chart."""
    table = "t_qumen_dgiren_year" if method == "zhirun" else "t_qumen_chauby_year"
    bazi_row = db.fetch_one(
        """
        SELECT DISTINCT year_pillar
        FROM t_bazi_hourly
        WHERE slot_start_date_local = %s AND tz_offset_hours = 0
        LIMIT 1
        """,
        [date(year, 1, 1).isoformat()],
    )
    if not bazi_row:
        return None
    year_pillar = bazi_row[0]
    row = db.fetch_one(
        f"""
        SELECT DISTINCT chart_id, rasklad_id
        FROM {table}
        WHERE year_pillar = %s
        LIMIT 1
        """,
        [year_pillar],
    )
    if not row:
        return None
    chart_id, rasklad_id = row
    meta = _parse_rasklad(rasklad_id)
    palaces = _get_palaces_from_rasklad(rasklad_id)
    return {
        "chart_id": f"{method}_year_{year}",
        "date_time": str(year),
        "chart_num": meta["ju_num"],
        "yin_yang": meta["yin_yang"],
        "year_pillar": year_pillar,
        "method": method,
        "level": "year",
        "palaces": palaces,
    }


def get_all_levels(target_date: date, method: str = "zhirun") -> dict:
    """Get year, month, day, and all hourly charts for a date."""
    year = target_date.year
    month = target_date.month
    return {
        "year": get_yearly_chart(year, method),
        "month": get_monthly_chart(year, month, method),
        "day": get_daily_chart(target_date, method),
        "hours": get_hourly_charts(target_date, method),
    }


# ---------------------------------------------------------------------------
# Reference data queries
# ---------------------------------------------------------------------------

def get_stars() -> List[dict]:
    """Get all Qi Men stars with descriptions."""
    rows = db.fetch_all(
        """
        SELECT id AS star_id, star_char, name_ru AS star_name_ru, name_en AS star_name_en,
               star_pinyin AS star_name_zh, palace_orig, element, nature, description_ru
        FROM spr_stars
        ORDER BY id
        """
    )
    cols = [
        "star_id", "star_char", "star_name_ru", "star_name_en", "star_name_zh",
        "palace_orig", "element", "nature", "description_ru",
    ]
    return [dict(zip(cols, row)) for row in rows]


def get_gates() -> List[dict]:
    """Get all Qi Men gates with descriptions."""
    rows = db.fetch_all(
        """
        SELECT id AS gate_id, gate_char, name_ru AS gate_name_ru, name_en AS gate_name_en,
               gate_pinyin AS gate_name_zh, palace_orig, element, nature, description_ru
        FROM spr_gates
        ORDER BY id
        """
    )
    cols = [
        "gate_id", "gate_char", "gate_name_ru", "gate_name_en", "gate_name_zh",
        "palace_orig", "element", "nature", "description_ru",
    ]
    return [dict(zip(cols, row)) for row in rows]


def get_spirits() -> List[dict]:
    """Get all Qi Men spirits with descriptions."""
    rows = db.fetch_all(
        """
        SELECT id AS spirit_id, spirit_char, name_ru AS spirit_name_ru, name_en AS spirit_name_en,
               spirit_pinyin AS spirit_name_zh, element, nature, description_ru
        FROM spr_gods
        ORDER BY id
        """
    )
    cols = [
        "spirit_id", "spirit_char", "spirit_name_ru", "spirit_name_en", "spirit_name_zh",
        "element", "nature", "description_ru",
    ]
    return [dict(zip(cols, row)) for row in rows]


def get_stem_combos() -> List[dict]:
    """Get all 100 stem combinations."""
    rows = db.fetch_all(
        """
        SELECT combo_id, stem_top, stem_bottom, combo_char, favorability, name_ru, description_ru
        FROM spr_qimen_stem_combos
        ORDER BY combo_id
        """
    )
    cols = ["combo_id", "stem_top", "stem_bottom", "combo_char", "favorability", "name_ru", "description_ru"]
    return [dict(zip(cols, row)) for row in rows]


def get_stem_combo(stem_top: str, stem_bottom: str) -> Optional[dict]:
    """Get a specific stem combination."""
    row = db.fetch_one(
        """
        SELECT combo_id, stem_top, stem_bottom, combo_char, favorability, name_ru, description_ru
        FROM spr_qimen_stem_combos
        WHERE stem_top = %s AND stem_bottom = %s
        """,
        [stem_top, stem_bottom],
    )
    if not row:
        return None
    cols = ["combo_id", "stem_top", "stem_bottom", "combo_char", "favorability", "name_ru", "description_ru"]
    return dict(zip(cols, row))


def get_trigrams() -> List[dict]:
    """Get all Ba Gua trigrams."""
    rows = db.fetch_all(
        """
        SELECT trigram_id, trigram_char, trigram_name_ru, trigram_name_en, trigram_name_zh,
               palace_nos, element, nature, description_ru
        FROM spr_qimen_trigrams
        ORDER BY trigram_id
        """
    )
    cols = [
        "trigram_id", "trigram_char", "trigram_name_ru", "trigram_name_en",
        "trigram_name_zh", "palace_nos", "element", "nature", "description_ru",
    ]
    return [dict(zip(cols, row)) for row in rows]
