"""Пакет расчёта бацзы‑календаря на базе PostgreSQL.

Состав подсистем:
- :mod:`code.bazi_calendar.db` — инфраструктура работы с PostgreSQL;
- :mod:`code.bazi_calendar.solar_terms` — чтение и поиск солнечных терминов
  (приоритет за данными Гонконгской обсерватории, при их отсутствии
  используются астрономические расчёты);
- :mod:`code.bazi_calendar.pillars` — вычисление столпов года, месяца,
  дня и часа с учётом локального сдвига времени;
- :mod:`code.bazi_calendar.hourly` — массовое заполнение таблицы
  `t_bazi_hourly` и создание представлений по часовым поясам.

Последнее обновление: 2026-06-05.
"""

from .db import (  # noqa: F401
    PROJECT_ROOT,
    backup_db,
    ensure_utc,
    parse_timestamp,
)
from .hourly import (  # noqa: F401
    create_bazi_hourly_views,
    ensure_bazi_hourly_table,
    populate_bazi_hourly_for_years,
    populate_bazi_hourly_table,
)
from .pillars import (  # noqa: F401
    FourPillars,
    Pillar,
    calc_day_pillar,
    calc_four_pillars,
    calc_hour_pillar,
    calc_month_pillar,
    calc_year_pillar,
)
from .lunar import (  # noqa: F401
    LunarDate,
    LunarDateNotExist,
    calc_lunar_components,
    calc_lunar_date,
    convert_lunar_to_solar,
    convert_solar_to_lunar,
)
from .solar_terms import (  # noqa: F401
    fetch_solar_term_crossings,
    get_prev_solar_term,
    get_solar_term_crossing,
    tz_from_offset,
)

__all__ = [
    "PROJECT_ROOT",
    "backup_db",
    "ensure_utc",
    "parse_timestamp",
    "create_bazi_hourly_views",
    "ensure_bazi_hourly_table",
    "populate_bazi_hourly_for_years",
    "populate_bazi_hourly_table",
    "FourPillars",
    "Pillar",
    "calc_day_pillar",
    "calc_four_pillars",
    "calc_hour_pillar",
    "calc_month_pillar",
    "calc_year_pillar",
    "LunarDate",
    "LunarDateNotExist",
    "calc_lunar_components",
    "calc_lunar_date",
    "convert_lunar_to_solar",
    "convert_solar_to_lunar",
    "fetch_solar_term_crossings",
    "get_prev_solar_term",
    "get_solar_term_crossing",
    "tz_from_offset",
]
