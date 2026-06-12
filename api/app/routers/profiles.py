from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..database.db import get_db
from ..schemas.profile import (
    ProfileCreate, ProfileUpdate, ProfileResponse, ProfileListResponse,
    BirthChartResponse, ProfileHistoryItem
)
from ..services.profile_service import ProfileService
from sqlalchemy import text

router = APIRouter(tags=["profiles"])


@router.get("/cities/search")
def search_cities(
    q: str = Query(..., min_length=1, description="Название города для поиска"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Поиск города в справочнике с автодополнением.
    Возвращает название, координаты, часовой пояс и смещение UTC.
    """
    sql = text("""
        SELECT city_name_ru, city_name_en, country_ru, lat, lon, timezone, utc_offset, region
        FROM spr_city_timezone
        WHERE city_name_ru ILIKE :query OR city_name_en ILIKE :query
        ORDER BY 
            CASE WHEN city_name_ru ILIKE :exact THEN 0 ELSE 1 END,
            population DESC NULLS LAST
        LIMIT :limit
    """)
    result = db.execute(sql, {
        "query": f"%{q}%",
        "exact": f"{q}%",
        "limit": limit,
    })
    cities = [dict(row._mapping) for row in result]
    return {"cities": cities}

@router.post("", response_model=ProfileResponse)
def create_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    """Создать новый профиль"""
    service = ProfileService(db)
    return service.create(profile)

@router.get("", response_model=ProfileListResponse)
def list_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Получить список профилей"""
    service = ProfileService(db)
    items, total = service.list_all(skip=skip, limit=limit, search=search)
    return ProfileListResponse(items=items, total=total)

@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    """Получить профиль по ID"""
    service = ProfileService(db)
    profile = service.get_by_id(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Профиль не найден")
    return profile

@router.put("/{profile_id}", response_model=ProfileResponse)
def update_profile(profile_id: int, update: ProfileUpdate, db: Session = Depends(get_db)):
    """Обновить профиль"""
    service = ProfileService(db)
    profile = service.update(profile_id, update)
    if not profile:
        raise HTTPException(status_code=404, detail="Профиль не найден")
    return profile

@router.delete("/{profile_id}")
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    """Удалить профиль"""
    service = ProfileService(db)
    success = service.delete(profile_id)
    if not success:
        raise HTTPException(status_code=404, detail="Профиль не найден")
    return {"status": "ok", "message": "Профиль удалён"}

@router.post("/{profile_id}/calculate-chart", response_model=BirthChartResponse)
def calculate_birth_chart(profile_id: int, db: Session = Depends(get_db)):
    """Рассчитать/обновить 8 столпов для профиля"""
    service = ProfileService(db)
    chart = service.calculate_birth_chart(profile_id)
    if not chart:
        raise HTTPException(status_code=404, detail="Профиль не найден")
    return chart

@router.get("/{profile_id}/history", response_model=List[ProfileHistoryItem])
def get_profile_history(
    profile_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Получить историю обращений к профилю"""
    service = ProfileService(db)
    return service.get_history(profile_id, skip=skip, limit=limit)

@router.post("/{profile_id}/history")
def add_history_entry(
    profile_id: int,
    action_type: str,
    module: Optional[str] = None,
    reference_date: Optional[date] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Добавить запись в историю профиля"""
    service = ProfileService(db)
    entry = service.add_history(profile_id, action_type, module, reference_date, notes)
    if not entry:
        raise HTTPException(status_code=404, detail="Профиль не найден")
    return {"status": "ok", "entry_id": entry['id']}
