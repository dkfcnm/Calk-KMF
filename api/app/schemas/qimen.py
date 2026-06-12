from datetime import datetime
from typing import Dict

from pydantic import BaseModel


class PalaceData(BaseModel):
    """Данные дворца в раскладе Ци Мэнь"""

    palace_no: int
    earth_stem: str
    is_fou_tou_earth: int
    heaven_stem: str
    is_fou_tou_heaven: int
    star: str
    is_main_star: int
    gate: str
    is_main_gate: int
    spirit: str

    class Config:
        orm_mode = True


class QimenChart(BaseModel):
    """Полный расклад Ци Мэнь"""

    chart_id: str
    date_time: datetime
    chart_num: int
    yin_yang: str
    palaces: Dict[str, PalaceData]
    method: str

    class Config:
        orm_mode = True


class QimenChartSummary(BaseModel):
    """Краткая информация о раскладе Ци Мэнь для списков"""

    chart_id: str
    date_time: datetime
    chart_num: int
    yin_yang: str
    method: str

    class Config:
        orm_mode = True
