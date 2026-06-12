from datetime import date, datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

# Маппинг дворцов Летящих Звезд на направления
PALACE_DIRECTIONS = {
    1: "N",
    2: "SW",
    3: "E",
    4: "SE",
    5: "C",
    6: "NW",
    7: "W",
    8: "NE",
    9: "S",
}

DIRECTION_NAMES_RU = {
    "N": "Север",
    "NE": "Северо-восток",
    "E": "Восток",
    "SE": "Юго-восток",
    "S": "Юг",
    "SW": "Юго-запад",
    "W": "Запад",
    "NW": "Северо-запад",
    "C": "Центр",
}


def _get_hour_id(db: Session, target_date: date, hour: Optional[int] = None) -> Optional[str]:
    """Получить hour_id из t_bazi_hourly по дате и часу (UTC+0 по умолчанию)."""
    if hour is None:
        hour = 0

    date_str = target_date.strftime("%Y-%m-%d")
    time_str = f"{hour:02d}:00"

    # Пробуем точное совпадение времени начала слота
    query = text("""
        SELECT hour_id
        FROM t_bazi_hourly
        WHERE slot_start_date_utc = :target_date
          AND tz_offset_hours = 0
          AND slot_start_time_utc = :time_str
        LIMIT 1
    """)
    result = db.execute(query, {"target_date": date_str, "time_str": time_str}).fetchone()
    if result:
        return result[0]

    # Если не найдено (например, 00:00), берем первый слот даты
    query = text("""
        SELECT hour_id
        FROM t_bazi_hourly
        WHERE slot_start_date_utc = :target_date
          AND tz_offset_hours = 0
        ORDER BY slot_start_time_utc
        LIMIT 1
    """)
    result = db.execute(query, {"target_date": date_str}).fetchone()
    return result[0] if result else None


def get_flying_stars_chart(
    db: Session,
    target_date: date,
    hour: Optional[int] = None,
) -> Optional[dict]:
    """
    Получить карту Летящих Звезд на указанную дату и час.

    Args:
        db: Сессия базы данных
        target_date: Дата для расчета
        hour: Час (0-23), по умолчанию 0

    Returns:
        Словарь с картой 9 дворцов или None
    """
    hour_id = _get_hour_id(db, target_date, hour)
    if not hour_id:
        return None

    query = text("""
        SELECT palace, year_star, month_star, day_star, hour_star
        FROM t_flying_stars
        WHERE hour_id = :hour_id
        ORDER BY palace
    """)
    rows = db.execute(query, {"hour_id": hour_id}).fetchall()

    if not rows:
        return None

    palaces = {}
    for row in rows:
        palace_num = row[0]
        direction = PALACE_DIRECTIONS.get(palace_num, str(palace_num))
        palaces[direction] = {
            "palace": palace_num,
            "year_star": row[1],
            "month_star": row[2],
            "day_star": row[3],
            "hour_star": row[4],
            "direction_ru": DIRECTION_NAMES_RU.get(direction, direction),
        }

    # Определяем период по году (Period = (Year % 9) или по таблицам)
    # Упрощенно: период для 2024-2043 = 9 (Li)
    year = target_date.year
    if 2024 <= year <= 2043:
        period = 9
    elif 2004 <= year <= 2023:
        period = 8
    elif 1984 <= year <= 2003:
        period = 7
    else:
        period = ((year - 4) % 9) + 1

    date_time = datetime(target_date.year, target_date.month, target_date.day, hour or 0)

    return {
        "date_time": date_time.isoformat(),
        "period": period,
        "palaces": palaces,
    }


def get_current_flying_stars(db: Session) -> Optional[dict]:
    """Получить текущую карту Летящих Звезд."""
    now = datetime.utcnow()
    return get_flying_stars_chart(db, now.date(), now.hour)
