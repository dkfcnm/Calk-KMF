from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database.db import get_db

router = APIRouter()


class TaiyiChart(BaseModel):
    """Расклад Тай И Шен Шу"""

    date_time: datetime
    palace: int
    star: str
    gate: Optional[str] = None
    spirit: Optional[str] = None
    deity: Optional[str] = None

    class Config:
        orm_mode = True


@router.get("/chart", response_model=TaiyiChart)
def get_taiyi_chart(
    target_date: date = Query(None, description="Дата для расчета (YYYY-MM-DD)"),
    hour: Optional[int] = Query(None, description="Час (0-23)"),
    db: Session = Depends(get_db),
):
    """
    Получить расклад Тай И Шен Шу на указанную дату и час.
    Заглушка — требуется реализация сервиса.
    """
    raise HTTPException(
        status_code=501,
        detail="Модуль Тай И находится в разработке.",
    )


@router.get("/current", response_model=TaiyiChart)
def get_current_taiyi(db: Session = Depends(get_db)):
    """
    Получить текущий расклад Тай И.
    Заглушка — требуется реализация сервиса.
    """
    raise HTTPException(
        status_code=501,
        detail="Модуль Тай И находится в разработке.",
    )
