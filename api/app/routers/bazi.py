from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database.db import get_db

router = APIRouter()


class BaziPillar(BaseModel):
    """Один столп Ба Цзы"""

    stem: str
    branch: str
    pillar: str

    class Config:
        orm_mode = True


class BaziChart(BaseModel):
    """Полная карта Ба Цзы"""

    date: datetime
    year_pillar: BaziPillar
    month_pillar: BaziPillar
    day_pillar: BaziPillar
    hour_pillar: Optional[BaziPillar] = None
    lunar_day: Optional[int] = None
    lunar_month: Optional[int] = None
    solar_term: Optional[str] = None

    class Config:
        orm_mode = True


@router.get("/chart", response_model=BaziChart)
def get_bazi_chart(
    target_date: date = Query(None, description="Дата для расчета (YYYY-MM-DD)"),
    hour: Optional[int] = Query(None, description="Час (0-23)"),
    db: Session = Depends(get_db),
):
    """
    Получить карту Ба Цзы на указанную дату и час.
    Заглушка — требуется реализация сервиса.
    """
    raise HTTPException(
        status_code=501,
        detail="Модуль Ба Цзы находится в разработке. Используйте /api/tongshu для календарных данных.",
    )


@router.get("/daily", response_model=BaziChart)
def get_daily_bazi(
    target_date: date = Query(None, description="Дата для расчета (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """
    Получить дневную карту Ба Цзы (без часового столпа).
    Заглушка — требуется реализация сервиса.
    """
    raise HTTPException(
        status_code=501,
        detail="Модуль Ба Цзы находится в разработке. Используйте /api/tongshu для календарных данных.",
    )
