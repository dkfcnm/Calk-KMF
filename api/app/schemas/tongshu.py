from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class TongshuDayData(BaseModel):
    """Данные по дню в календаре Тун Шу (legacy, from t_bazi_hourly)"""

    date: date
    year_stem: str
    year_branch: str
    month_stem: str
    month_branch: str
    day_stem: str
    day_branch: str
    lunar_day: int
    lunar_month: int
    lunar_year: int
    solar_term: Optional[str] = None
    ten_gods_day: dict
    day_rating: str
    suitable_activities: List[str]
    unsuitable_activities: List[str]

    class Config:
        orm_mode = True


class TongshuDailyData(BaseModel):
    """Данные по дню из агрегатной таблицы t_tung_shu_daily"""

    calendar_date: date
    year_pillar: Optional[str] = None
    month_pillar: Optional[str] = None
    day_pillar: Optional[str] = None
    year_stem: Optional[str] = None
    year_branch: Optional[str] = None
    month_stem: Optional[str] = None
    month_branch: Optional[str] = None
    day_stem: Optional[str] = None
    day_branch: Optional[str] = None
    solar_term_id: Optional[int] = None
    solar_term_char: Optional[str] = None
    solar_term_name_ru: Optional[str] = None
    nayin_element: Optional[str] = None
    nayin_name: Optional[str] = None
    year_nayin_element: Optional[str] = None
    year_nayin_name: Optional[str] = None
    month_nayin_element: Optional[str] = None
    month_nayin_name: Optional[str] = None
    day_nayin_element: Optional[str] = None
    day_nayin_name: Optional[str] = None
    year_period: Optional[int] = None
    month_period: Optional[int] = None
    day_period: Optional[int] = None
    year_element_num: Optional[int] = None
    month_element_num: Optional[int] = None
    day_element_num: Optional[int] = None
    hexagram_family_same: Optional[bool] = None
    production_chain: Optional[bool] = None
    lunar_day: Optional[int] = None
    day_officer_char: Optional[str] = None
    day_officer_name_ru: Optional[str] = None
    day_officer_category: Optional[str] = None
    constellation_char: Optional[str] = None
    constellation_name_ru: Optional[str] = None
    constellation_direction: Optional[str] = None
    constellation_nature: Optional[str] = None
    belt_type: Optional[str] = None
    belt_stars: Optional[List[str]] = None
    moon_phase_name: Optional[str] = None
    moon_phase_pct: Optional[float] = None
    tongshu_phase_name_ru: Optional[str] = None
    great_sun_mountain: Optional[str] = None
    great_sun_mountain_name: Optional[str] = None
    symbolic_stars: Optional[List[dict]] = None
    lunar_month: Optional[str] = None
    black_rabbit_star: Optional[str] = None
    black_rabbit_score: Optional[float] = None

    class Config:
        orm_mode = True


class TongshuHourData(BaseModel):
    """Данные по двухчасовому слоту в календаре Тун Шу"""

    time_str: Optional[str] = None
    hour_stem: Optional[str] = None
    hour_branch: Optional[str] = None
    hour_pillar: Optional[str] = None
    ten_god: Optional[str] = None
    qi_phase: Optional[str] = None
    qi_phase_score: Optional[float] = None
    hidden_stems: Optional[List[dict]] = None
    symbolic_stars: Optional[List[dict]] = None

    class Config:
        orm_mode = True
