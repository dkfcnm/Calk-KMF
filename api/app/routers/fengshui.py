from datetime import date, datetime
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..services import fengshui_service

router = APIRouter()


class PalaceStars(BaseModel):
    """Звезды для одного дворца"""
    palace: int
    year_star: int
    month_star: Optional[int] = None
    day_star: Optional[int] = None
    hour_star: Optional[int] = None
    direction_ru: str

    class Config:
        from_attributes = True


class FlyingStarsChart(BaseModel):
    """Карта Летящих Звезд"""
    date_time: str
    period: int
    palaces: Dict[str, PalaceStars]

    class Config:
        from_attributes = True


@router.get("/chart", response_model=FlyingStarsChart)
def get_flying_stars_chart(
    target_date: date = Query(None, description="Дата для расчета (YYYY-MM-DD)"),
    hour: Optional[int] = Query(None, description="Час (0-23), по умолчанию 0"),
    db: Session = Depends(get_db),
):
    """
    Получить карту Летящих Звезд на указанную дату и час.
    Возвращает 9 дворцов с годовой, месячной, дневной и часовой звездами.
    """
    if target_date is None:
        target_date = date.today()

    chart = fengshui_service.get_flying_stars_chart(db, target_date, hour)
    if not chart:
        raise HTTPException(
            status_code=404,
            detail=f"Данные Летящих Звезд не найдены для {target_date} {hour or 0}:00",
        )
    return chart


@router.get("/current", response_model=FlyingStarsChart)
def get_current_flying_stars(db: Session = Depends(get_db)):
    """
    Получить текущую карту Летящих Звезд (UTC).
    """
    chart = fengshui_service.get_current_flying_stars(db)
    if not chart:
        raise HTTPException(
            status_code=404,
            detail="Не удалось получить текущие данные Летящих Звезд",
        )
    return chart


@router.get("/directions")
def get_feng_shui_directions(
    target_date: date = Query(None, description="Дата для расчета (YYYY-MM-DD)"),
    hour: Optional[int] = Query(None, description="Час (0-23), по умолчанию 0"),
    db: Session = Depends(get_db),
):
    """
    Получить благоприятность направлений Фэн Шуй на указанную дату и час.
    Возвращает список направлений с текущей часовой звездой и оценкой.
    """
    if target_date is None:
        target_date = date.today()

    chart = fengshui_service.get_flying_stars_chart(db, target_date, hour)
    if not chart:
        raise HTTPException(
            status_code=404,
            detail=f"Данные не найдены для {target_date} {hour or 0}:00",
        )

    # Оценка направлений по часовой звезде
    # Звезды 1, 4, 6, 8, 9 — благоприятные
    # Звезды 2, 3, 5, 7 — неблагоприятные
    AUSPICIOUS_STARS = {1, 4, 6, 8, 9}
    INAUSPICIOUS_STARS = {2, 3, 5, 7}

    directions = []
    for direction, palace_data in chart["palaces"].items():
        hour_star = palace_data["hour_star"]
        if hour_star in AUSPICIOUS_STARS:
            rating = "auspicious"
            rating_ru = "Благоприятное"
        elif hour_star in INAUSPICIOUS_STARS:
            rating = "inauspicious"
            rating_ru = "Неблагоприятное"
        else:
            rating = "neutral"
            rating_ru = "Нейтральное"

        directions.append({
            "direction": direction,
            "direction_ru": palace_data["direction_ru"],
            "palace": palace_data["palace"],
            "hour_star": hour_star,
            "rating": rating,
            "rating_ru": rating_ru,
        })

    # Сортируем: сначала благоприятные
    directions.sort(key=lambda x: (
        0 if x["rating"] == "auspicious" else 1 if x["rating"] == "neutral" else 2,
        x["direction"],
    ))

    return {
        "date_time": chart["date_time"],
        "period": chart["period"],
        "directions": directions,
    }
