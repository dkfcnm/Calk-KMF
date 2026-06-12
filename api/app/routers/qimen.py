from datetime import date, datetime
from typing import List, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..schemas.qimen import QimenChart, QimenChartSummary, PalaceData
from ..services import qimen_service
from ..services.qimen_pg_service import (
    get_all_levels, get_hourly_charts, get_daily_chart,
    get_monthly_chart, get_yearly_chart,
    get_stars, get_gates, get_spirits, get_stem_combos, get_stem_combo,
    get_trigrams,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Chart endpoints
# ---------------------------------------------------------------------------

@router.get("/charts/{method}", response_model=List[QimenChartSummary])
def list_qimen_charts(
    method: Literal["zhirun", "chauby"] = Path(
        ..., description="Методология расчета (zhirun или chauby)"
    ),
    start_date: date = Query(None, description="Начальная дата выборки (YYYY-MM-DD)"),
    end_date: date = Query(None, description="Конечная дата выборки (YYYY-MM-DD)"),
    limit: int = Query(100, description="Максимальное количество результатов"),
    offset: int = Query(0, description="Смещение для пагинации"),
    db: Session = Depends(get_db),
):
    """
    Получить список доступных раскладов Ци Мэнь для указанной методологии.
    Можно фильтровать по диапазону дат.
    """
    try:
        if start_date is None:
            start_date = date.today()
        if end_date is None:
            end_date = start_date

        charts = qimen_service.list_charts(
            db, method, start_date, end_date, limit, offset
        )
        return charts
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка получения данных: {str(e)}"
        )


@router.get("/chart/{chart_id}", response_model=QimenChart)
def get_qimen_chart(
    chart_id: str = Path(..., description="ID расклада Ци Мэнь"),
    db: Session = Depends(get_db),
):
    """
    Получить полные данные расклада Ци Мэнь по его ID.
    """
    try:
        chart = qimen_service.get_chart_by_id(db, chart_id)
        if not chart:
            raise HTTPException(status_code=404, detail="Расклад не найден")
        return chart
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка получения данных: {str(e)}"
        )


@router.get("/calculate/{method}", response_model=QimenChart)
def calculate_qimen_chart(
    method: Literal["zhirun", "chauby"] = Path(
        ..., description="Методология расчета (zhirun или chauby)"
    ),
    datetime_str: str = Query(
        ..., description="Дата и время для расчета (YYYY-MM-DD HH:MM)"
    ),
    db: Session = Depends(get_db),
):
    """
    Рассчитать расклад Ци Мэнь на указанную дату и время по выбранной методологии.
    """
    try:
        datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        chart = qimen_service.calculate_chart(db, method, datetime_obj)
        return chart
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Неверный формат даты и времени. Используйте формат YYYY-MM-DD HH:MM.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка расчета: {str(e)}")


@router.get("/palace/{chart_id}/{palace_no}", response_model=PalaceData)
def get_palace_data(
    chart_id: str = Path(..., description="ID расклада Ци Мэнь"),
    palace_no: int = Path(..., description="Номер дворца (1-9)"),
    db: Session = Depends(get_db),
):
    """
    Получить данные конкретного дворца в раскладе Ци Мэнь.
    """
    try:
        if not 1 <= palace_no <= 9:
            raise HTTPException(
                status_code=400, detail="Неверный номер дворца. Должен быть от 1 до 9."
            )

        palace = qimen_service.get_palace_data(db, chart_id, palace_no)
        if not palace:
            raise HTTPException(status_code=404, detail="Дворец не найден")
        return palace
    except HTTPException:
        raise
    except Exception as e:
        # Fallback: fetch full chart and extract palace
        try:
            chart = qimen_service.get_chart_by_id(db, chart_id)
            if chart and hasattr(chart, "palaces"):
                palace = chart.palaces.get(str(palace_no))
                if palace:
                    return palace
        except Exception:
            pass
        raise HTTPException(
            status_code=500, detail=f"Ошибка получения данных: {str(e)}"
        )


@router.get("/current/{method}", response_model=QimenChart)
def get_current_qimen_chart(
    method: Literal["zhirun", "chauby"] = Path(
        ..., description="Методология расчета (zhirun или chauby)"
    ),
    db: Session = Depends(get_db),
):
    """
    Получить текущий расклад Ци Мэнь по выбранной методологии.
    """
    try:
        current_time = datetime.now()
        chart = qimen_service.calculate_chart(db, method, current_time)
        return chart
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка расчета: {str(e)}")


# ---------------------------------------------------------------------------
# Level endpoints (year/month/day/hour)
# ---------------------------------------------------------------------------

@router.get("/levels/{method}")
def get_qimen_levels(
    method: Literal["zhirun", "chauby"] = Path(...),
    target_date: date = Query(None, description="Дата (YYYY-MM-DD)"),
):
    """Получить все уровни расклада (год, месяц, день, часы) для даты."""
    if target_date is None:
        target_date = date.today()
    try:
        data = get_all_levels(target_date, method)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.get("/hourly/{method}")
def get_qimen_hourly(
    method: Literal["zhirun", "chauby"] = Path(...),
    target_date: date = Query(None, description="Дата (YYYY-MM-DD)"),
):
    """Получить все часовые расклады дня."""
    if target_date is None:
        target_date = date.today()
    try:
        return get_hourly_charts(target_date, method)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.get("/daily/{method}")
def get_qimen_daily(
    method: Literal["zhirun", "chauby"] = Path(...),
    target_date: date = Query(None, description="Дата (YYYY-MM-DD)"),
):
    """Получить дневной расклад."""
    if target_date is None:
        target_date = date.today()
    try:
        chart = get_daily_chart(target_date, method)
        if not chart:
            raise HTTPException(status_code=404, detail="Расклад не найден")
        return chart
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.get("/monthly/{method}")
def get_qimen_monthly(
    method: Literal["zhirun", "chauby"] = Path(...),
    year: int = Query(...),
    month: int = Query(...),
):
    """Получить месячный расклад."""
    try:
        chart = get_monthly_chart(year, month, method)
        if not chart:
            raise HTTPException(status_code=404, detail="Расклад не найден")
        return chart
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.get("/yearly/{method}")
def get_qimen_yearly(
    method: Literal["zhirun", "chauby"] = Path(...),
    year: int = Query(...),
):
    """Получить годовой расклад."""
    try:
        chart = get_yearly_chart(year, method)
        if not chart:
            raise HTTPException(status_code=404, detail="Расклад не найден")
        return chart
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


# ---------------------------------------------------------------------------
# Reference endpoints
# ---------------------------------------------------------------------------

@router.get("/references/stars")
def list_stars():
    """Получить справочник звезд Ци Мэнь."""
    try:
        return get_stars()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.get("/references/gates")
def list_gates():
    """Получить справочник врат Ци Мэнь."""
    try:
        return get_gates()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.get("/references/spirits")
def list_spirits():
    """Получить справочник духов Ци Мэнь."""
    try:
        return get_spirits()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.get("/references/stem_combos")
def list_stem_combos():
    """Получить справочник 100 комбинаций стволов."""
    try:
        return get_stem_combos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.get("/references/trigrams")
def list_trigrams():
    """Получить справочник триграмм Ба Гуа."""
    try:
        return get_trigrams()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.get("/references/stem_combo/{stem_top}/{stem_bottom}")
def get_single_stem_combo(
    stem_top: str = Path(..., description="Верхний ствол"),
    stem_bottom: str = Path(..., description="Нижний ствол"),
):
    """Получить конкретную комбинацию стволов."""
    try:
        combo = get_stem_combo(stem_top, stem_bottom)
        if not combo:
            raise HTTPException(status_code=404, detail="Комбинация не найдена")
        return combo
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")
