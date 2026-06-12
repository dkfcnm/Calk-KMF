from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..schemas.tongshu import TongshuDayData, TongshuDailyData, TongshuHourData
from ..services import tongshu_service
from ..services.personalized_service import get_personalized_day_data
from ..services.profile_service import ProfileService

router = APIRouter()


# Маршруты API


@router.get("/calendar/day", response_model=TongshuDailyData)
def get_tongshu_day(
    target_date: date = Query(
        None, description="Дата для получения информации (YYYY-MM-DD)"
    ),
    db: Session = Depends(get_db),
):
    """
    Получить данные календаря Тун Шу на конкретный день.
    Если дата не указана, используется текущая дата.
    """
    if target_date is None:
        target_date = date.today()

    try:
        day_data = tongshu_service.get_day_data(db, target_date)
        if not day_data:
            raise HTTPException(
                status_code=404, detail="Данные на указанную дату не найдены"
            )
        return day_data
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка получения данных: {str(e)}"
        )


@router.get("/calendar/month", response_model=List[TongshuDailyData])
def get_tongshu_month(
    year: int = Query(..., description="Год (YYYY)"),
    month: int = Query(..., description="Месяц (1-12)"),
    db: Session = Depends(get_db),
):
    """
    Получить данные календаря Тун Шу на весь месяц.
    """
    try:
        if not (1 <= month <= 12):
            raise HTTPException(
                status_code=400, detail="Неверный месяц. Должен быть от 1 до 12."
            )

        month_data = tongshu_service.get_month_data(db, year, month)
        return month_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка получения данных: {str(e)}"
        )


@router.get("/calendar/week", response_model=List[TongshuDailyData])
def get_tongshu_week(
    start_date: date = Query(None, description="Начальная дата недели (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """
    Получить данные календаря Тун Шу на неделю, начиная с указанной даты.
    Если дата не указана, используется текущая дата.
    """
    if start_date is None:
        # Если дата не указана, берем текущую дату и начало недели (понедельник)
        today = date.today()
        start_date = today - timedelta(days=today.weekday())

    try:
        week_data = tongshu_service.get_week_data(db, start_date)
        return week_data
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка получения данных: {str(e)}"
        )


@router.get("/hours/{date_str}", response_model=List[TongshuHourData])
def get_tongshu_hours(
    date_str: str = Path(
        ..., description="Дата для получения часовых данных (YYYY-MM-DD)"
    ),
    db: Session = Depends(get_db),
):
    """
    Получить часовые данные Тун Шу для конкретного дня.
    """
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        hours_data = tongshu_service.get_hours_data(db, target_date)
        return hours_data
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Неверный формат даты. Используйте формат YYYY-MM-DD.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка получения данных: {str(e)}"
        )


@router.get("/calendar/year", response_model=List[TongshuDayData])
def get_tongshu_year(
    year: int = Query(..., description="Год (YYYY)"), db: Session = Depends(get_db)
):
    """
    Получить данные календаря Тун Шу на весь год.
    """
    try:
        year_data = tongshu_service.get_year_data(db, year)
        return year_data
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка получения данных: {str(e)}"
        )


# ---------------------------------------------------------------------------
# Daily endpoints using t_tung_shu_daily (PostgreSQL via SQLAlchemy)
# ---------------------------------------------------------------------------

@router.get("/daily/day", response_model=TongshuDailyData)
def get_tongshu_daily_day(
    target_date: date = Query(None, description="Дата (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """
    Получить данные Тун Шу на конкретный день из агрегатной таблицы.
    """
    if target_date is None:
        target_date = date.today()

    day_data = tongshu_service.get_day_data(db, target_date)
    if not day_data:
        raise HTTPException(status_code=404, detail="Данные не найдены")
    return day_data


@router.get("/daily/month", response_model=List[TongshuDailyData])
def get_tongshu_daily_month(
    year: int = Query(..., description="Год (YYYY)"),
    month: int = Query(..., description="Месяц (1-12)"),
    db: Session = Depends(get_db),
):
    """
    Получить данные Тун Шу на весь месяц из агрегатной таблицы.
    """
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="Неверный месяц")

    return tongshu_service.get_month_data(db, year, month)


@router.get("/daily/week", response_model=List[TongshuDailyData])
def get_tongshu_daily_week(
    start_date: date = Query(None, description="Начальная дата недели (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """
    Получить данные Тун Шу на неделю из агрегатной таблицы.
    """
    if start_date is None:
        today = date.today()
        start_date = today - timedelta(days=today.weekday())

    return tongshu_service.get_week_data(db, start_date)


@router.get("/daily/year", response_model=None)
def get_tongshu_daily_year(
    year: int = Query(..., description="Год (YYYY)"),
    page: Optional[int] = Query(None, ge=1, description="Номер страницы"),
    page_size: Optional[int] = Query(None, ge=1, le=365, description="Размер страницы"),
    db: Session = Depends(get_db),
):
    """
    Получить данные Тун Шу на весь год из агрегатной таблицы.
    Поддерживает пагинацию. Если параметры пагинации не указаны, возвращает все данные.
    """
    try:
        if page is not None or page_size is not None:
            current_page = page if page is not None else 1
            current_page_size = page_size if page_size is not None else 31
            return tongshu_service.get_year_data_paginated(db, year, current_page, current_page_size)
        return tongshu_service.get_year_data(db, year)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка получения данных: {str(e)}"
        )


@router.get("/personalized/day")
def get_personalized_day(
    target_date: date = Query(None, description="Дата (YYYY-MM-DD)"),
    profile_id: int = Query(..., description="ID профиля"),
    db: Session = Depends(get_db),
):
    """
    Получить полные персонализированные данные Тун Шу на день.
    Включает скрытые стволы, персонализированные 10 Богов и фазы Ци.
    """
    if target_date is None:
        target_date = date.today()

    profile_service = ProfileService(db)
    profile = profile_service.get_by_id(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Профиль не найден")

    day_master = profile.get('birth_chart', {}).get('day_master') if profile.get('birth_chart') else None

    try:
        data = get_personalized_day_data(db, target_date, profile_day_master=day_master)
        data['profile'] = {
            'id': profile['id'],
            'name': profile['name'],
            'day_master': day_master,
            'day_master_element': profile.get('birth_chart', {}).get('day_master_element'),
        }
        return data
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка получения данных: {str(e)}"
        )
