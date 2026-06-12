import uuid
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

from sqlalchemy import text

from code.common.config import load_config_from_db
from code.qimen.engine import QimenEngine

from . import qimen_pg_service


def list_charts(
    db,
    method: Literal["zhirun", "chauby"],
    start_date: date,
    end_date: date,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """
    Получить список доступных раскладов Ци Мэнь для указанной методологии.
    Единый SQL-запрос вместо посуточного цикла.
    """
    table = "t_qumen_dgiren_hourly" if method == "zhirun" else "t_qumen_chauby_hourly"
    query = text(f"""
        SELECT DISTINCT q.hour_id, q.rasklad_id, h.slot_start_date_local, h.slot_start_time_local, h.hour_pillar
        FROM {table} q
        JOIN t_bazi_hourly h ON q.hour_id = h.hour_id
        WHERE h.slot_start_date_local >= :start_date
          AND h.slot_start_date_local <= :end_date
          AND h.tz_offset_hours = 0
        ORDER BY h.slot_start_date_local, h.slot_start_time_local
        LIMIT :limit OFFSET :offset
    """)
    rows = db.execute(query, {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "limit": limit + offset,
        "offset": 0,
    }).fetchall()

    result = []
    for row in rows[offset:offset + limit]:
        hour_id, rasklad_id, date_val, time_str, hour_pillar = row
        date_str = str(date_val)
        parts = rasklad_id.split("_")
        ju_num = int(parts[1]) if len(parts) >= 2 else 1
        yin_yang = parts[0] if parts else "Yang"
        result.append({
            "chart_id": f"{method}_{date_str}_{time_str}",
            "date_time": f"{date_str} {time_str}",
            "chart_num": ju_num,
            "yin_yang": yin_yang,
            "method": method,
        })
    return result


def get_chart_by_id(db, chart_id: str) -> Dict[str, Any]:
    """
    Получить полные данные расклада Ци Мэнь по его ID.
    Парсит ID и делегирует qimen_pg_service.
    """
    parts = chart_id.split("_")
    if len(parts) < 3:
        return None

    method = parts[0]

    # daily:  method_day_YYYY-MM-DD
    if parts[1] == "day" and len(parts) >= 3:
        try:
            target_date = date.fromisoformat(parts[2])
            return qimen_pg_service.get_daily_chart(target_date, method)
        except Exception:
            return None

    # monthly:  method_month_YYYY_M
    if parts[1] == "month" and len(parts) >= 4:
        try:
            year, month = int(parts[2]), int(parts[3])
            return qimen_pg_service.get_monthly_chart(year, month, method)
        except Exception:
            return None

    # yearly:  method_year_YYYY
    if parts[1] == "year" and len(parts) >= 3:
        try:
            year = int(parts[2])
            return qimen_pg_service.get_yearly_chart(year, method)
        except Exception:
            return None

    # hourly:  method_YYYY-MM-DD_HH:MM  (no level keyword)
    try:
        target_date = date.fromisoformat(parts[1])
        time_str = parts[2]
        charts = qimen_pg_service.get_hourly_charts(target_date, method)
        for c in charts:
            if time_str in c["chart_id"]:
                return c
        return charts[0] if charts else None
    except Exception:
        return None

    return None


def calculate_chart(
    db, method: Literal["zhirun", "chauby"], datetime_obj: datetime
) -> Dict[str, Any]:
    """
    Рассчитать расклад Ци Мэнь на указанную дату и время по выбранной методологии.
    Использует движок QimenEngine и данные t_bazi_hourly из PostgreSQL.
    """
    bazi_query = """
    SELECT
        year_stem,
        year_branch,
        month_stem,
        month_branch,
        day_stem,
        day_branch,
        hour_stem,
        hour_branch,
        solar_term_id,
        hour_id
    FROM
        t_bazi_hourly
    WHERE
        slot_start_date_local <= :date_str
    ORDER BY
        slot_start_date_local DESC, slot_start_time_local DESC
    LIMIT 1
    """

    bazi_result = db.execute(
        text(bazi_query),
        {"date_str": datetime_obj.strftime("%Y-%m-%d")},
    ).fetchone()

    if not bazi_result:
        raise ValueError("Не удалось найти данные базы для указанной даты и времени")

    config = load_config_from_db()
    engine = QimenEngine(config)

    qimen_chart = engine.compute_chart(
        hour_id=bazi_result.hour_id,
        solar_term_id=bazi_result.solar_term_id,
        day_stem=bazi_result.day_stem,
        day_branch=bazi_result.day_branch,
        hour_stem=bazi_result.hour_stem,
        hour_branch=bazi_result.hour_branch,
        chart_type="Часовой",
    )

    chart_id = str(uuid.uuid4())

    chart = {
        "chart_id": chart_id,
        "date_time": datetime_obj,
        "chart_num": qimen_chart.chart_num,
        "yin_yang": qimen_chart.yin_yang,
        "method": method,
    }

    palaces = {}
    for palace_no, palace_data in qimen_chart.palaces.items():
        palace = {
            "palace_no": palace_data.palace_no,
            "earth_stem": palace_data.earth_stem,
            "is_fou_tou_earth": palace_data.is_fou_tou_earth,
            "heaven_stem": palace_data.heaven_stem,
            "is_fou_tou_heaven": palace_data.is_fou_tou_heaven,
            "star": palace_data.star,
            "is_main_star": palace_data.is_main_star,
            "gate": palace_data.gate,
            "is_main_gate": palace_data.is_main_gate,
            "spirit": palace_data.spirit,
        }
        palaces[str(palace_no)] = palace

    chart["palaces"] = palaces
    return chart


def get_palace_data(db, chart_id: str, palace_no: int) -> Dict[str, Any]:
    """
    Получить данные конкретного дворца в раскладе Ци Мэнь.
    Делегирует qimen_pg_service для получения полного расклада.
    """
    chart = get_chart_by_id(db, chart_id)
    if not chart:
        return None
    return chart.get("palaces", {}).get(str(palace_no))
