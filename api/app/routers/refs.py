"""
Reference data admin API — CRUD for Tong Shu reference tables.
PostgreSQL-only via SQLAlchemy.
"""

import time
from functools import wraps
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..database.db import get_db

router = APIRouter()


def cache_with_ttl(seconds=3600):
    def decorator(func):
        cache = {}
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use function name as key since ref endpoints only have db session as parameter
            key = func.__name__
            now = time.time()
            if key in cache and now - cache[key]['time'] < seconds:
                return cache[key]['value']
            result = func(*args, **kwargs)
            cache[key] = {'value': result, 'time': now}
            return result
        return wrapper
    return decorator


# ==========================================================================
# 12 Officers
# ==========================================================================

class OfficerValue(BaseModel):
    officer_value_id: int
    officer_char: str
    officer_pinyin: Optional[str] = None
    officer_name_ru: Optional[str] = None
    officer_name_en: Optional[str] = None
    officer_category: Optional[str] = None
    description_ru: Optional[str] = None
    description_short_ru: Optional[str] = None
    icon_svg: Optional[str] = None


@router.get("/officers", response_model=List[OfficerValue])
@cache_with_ttl(seconds=3600)
def get_officers(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM spr_day_officer_value ORDER BY officer_value_id"))
    rows = result.fetchall()
    return [dict(r._mapping) for r in rows]


@router.put("/officers/{officer_id}", response_model=OfficerValue)
def update_officer(officer_id: int, data: OfficerValue, db: Session = Depends(get_db)):
    result = db.execute(text("""
        UPDATE spr_day_officer_value SET
            officer_char = :officer_char, officer_pinyin = :officer_pinyin, officer_name_ru = :officer_name_ru,
            officer_name_en = :officer_name_en, officer_category = :officer_category, description_ru = :description_ru,
            description_short_ru = :description_short_ru, icon_svg = :icon_svg
        WHERE officer_value_id = :officer_id
    """), {
        "officer_char": data.officer_char, "officer_pinyin": data.officer_pinyin,
        "officer_name_ru": data.officer_name_ru, "officer_name_en": data.officer_name_en,
        "officer_category": data.officer_category, "description_ru": data.description_ru,
        "description_short_ru": data.description_short_ru, "icon_svg": data.icon_svg,
        "officer_id": officer_id
    })
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Officer not found")
    db.commit()
    return data


# ==========================================================================
# 28 Constellations
# ==========================================================================

class Constellation(BaseModel):
    constellation_id: int
    constellation_char: str
    constellation_pinyin: Optional[str] = None
    constellation_name_ru: Optional[str] = None
    constellation_name_en: Optional[str] = None
    direction_group: Optional[str] = None
    direction_group_ru: Optional[str] = None
    element: Optional[str] = None
    animal: Optional[str] = None
    animal_ru: Optional[str] = None
    nature: Optional[str] = None
    description_ru: Optional[str] = None
    activities_good_ru: Optional[str] = None
    activities_bad_ru: Optional[str] = None
    icon_svg: Optional[str] = None


@router.get("/constellations", response_model=List[Constellation])
@cache_with_ttl(seconds=3600)
def get_constellations(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM spr_tongshu_constellation ORDER BY constellation_id"))
    rows = result.fetchall()
    return [dict(r._mapping) for r in rows]


@router.put("/constellations/{constellation_id}", response_model=Constellation)
def update_constellation(constellation_id: int, data: Constellation, db: Session = Depends(get_db)):
    result = db.execute(text("""
        UPDATE spr_tongshu_constellation SET
            constellation_char = :constellation_char, constellation_pinyin = :constellation_pinyin,
            constellation_name_ru = :constellation_name_ru, constellation_name_en = :constellation_name_en,
            direction_group = :direction_group, direction_group_ru = :direction_group_ru,
            element = :element, animal = :animal, animal_ru = :animal_ru, nature = :nature,
            description_ru = :description_ru, activities_good_ru = :activities_good_ru,
            activities_bad_ru = :activities_bad_ru, icon_svg = :icon_svg
        WHERE constellation_id = :constellation_id
    """), {
        "constellation_char": data.constellation_char, "constellation_pinyin": data.constellation_pinyin,
        "constellation_name_ru": data.constellation_name_ru, "constellation_name_en": data.constellation_name_en,
        "direction_group": data.direction_group, "direction_group_ru": data.direction_group_ru,
        "element": data.element, "animal": data.animal, "animal_ru": data.animal_ru,
        "nature": data.nature, "description_ru": data.description_ru,
        "activities_good_ru": data.activities_good_ru, "activities_bad_ru": data.activities_bad_ru,
        "icon_svg": data.icon_svg, "constellation_id": constellation_id
    })
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Constellation not found")
    db.commit()
    return data


# ==========================================================================
# Belt Stars (Yellow/Black)
# ==========================================================================

class BeltStar(BaseModel):
    id: int
    name: Optional[str] = None
    score: Optional[float] = None
    icon_svg: Optional[str] = None


@router.get("/belt-stars", response_model=List[BeltStar])
@cache_with_ttl(seconds=3600)
def get_belt_stars(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM spr_yellow_black_stars ORDER BY id"))
    rows = result.fetchall()
    return [dict(r._mapping) for r in rows]


@router.put("/belt-stars/{star_id}", response_model=BeltStar)
def update_belt_star(star_id: int, data: BeltStar, db: Session = Depends(get_db)):
    result = db.execute(text("""
        UPDATE spr_yellow_black_stars SET name = :name, score = :score, icon_svg = :icon_svg WHERE id = :star_id
    """), {"name": data.name, "score": data.score, "icon_svg": data.icon_svg, "star_id": star_id})
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Star not found")
    db.commit()
    return data


# ==========================================================================
# 10 Heavenly Stems (10 НС)
# ==========================================================================

class HeavenlyStem(BaseModel):
    stem_id: int
    stem_char: Optional[str] = None
    stem_pinyin: Optional[str] = None
    stem_rus: Optional[str] = None
    element: Optional[str] = None
    yin_yang: Optional[str] = None
    guigu_score: Optional[int] = None
    color_hex: Optional[str] = None
    icon_svg: Optional[str] = None


@router.get("/heavenly-stems", response_model=List[HeavenlyStem])
@cache_with_ttl(seconds=3600)
def get_heavenly_stems(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM spr_heavenly_stem ORDER BY stem_id"))
    rows = result.fetchall()
    return [dict(r._mapping) for r in rows]


@router.put("/heavenly-stems/{stem_id}", response_model=HeavenlyStem)
def update_heavenly_stem(stem_id: int, data: HeavenlyStem, db: Session = Depends(get_db)):
    result = db.execute(text("""
        UPDATE spr_heavenly_stem SET
            stem_char = :stem_char, stem_pinyin = :stem_pinyin, stem_rus = :stem_rus, element = :element,
            yin_yang = :yin_yang, guigu_score = :guigu_score, color_hex = :color_hex, icon_svg = :icon_svg
        WHERE stem_id = :stem_id
    """), {
        "stem_char": data.stem_char, "stem_pinyin": data.stem_pinyin, "stem_rus": data.stem_rus,
        "element": data.element, "yin_yang": data.yin_yang, "guigu_score": data.guigu_score,
        "color_hex": data.color_hex, "icon_svg": data.icon_svg, "stem_id": stem_id
    })
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Stem not found")
    db.commit()
    return data


# ==========================================================================
# 12 Earthly Branches (12 ЗВ)
# ==========================================================================

class EarthlyBranch(BaseModel):
    branch_id: int
    branch_char: Optional[str] = None
    branch_pinyin: Optional[str] = None
    branch_rus: Optional[str] = None
    element: Optional[str] = None
    yin_yang: Optional[str] = None
    yuan_level: Optional[int] = None
    start_hour: Optional[int] = None
    end_hour: Optional[int] = None
    guigu_score: Optional[int] = None
    color_hex: Optional[str] = None
    icon_svg: Optional[str] = None


@router.get("/earthly-branches", response_model=List[EarthlyBranch])
@cache_with_ttl(seconds=3600)
def get_earthly_branches(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM spr_earthly_branch ORDER BY branch_id"))
    rows = result.fetchall()
    return [dict(r._mapping) for r in rows]


@router.put("/earthly-branches/{branch_id}", response_model=EarthlyBranch)
def update_earthly_branch(branch_id: int, data: EarthlyBranch, db: Session = Depends(get_db)):
    result = db.execute(text("""
        UPDATE spr_earthly_branch SET
            branch_char = :branch_char, branch_pinyin = :branch_pinyin, branch_rus = :branch_rus,
            element = :element, yin_yang = :yin_yang, yuan_level = :yuan_level,
            start_hour = :start_hour, end_hour = :end_hour,
            guigu_score = :guigu_score, color_hex = :color_hex, icon_svg = :icon_svg
        WHERE branch_id = :branch_id
    """), {
        "branch_char": data.branch_char, "branch_pinyin": data.branch_pinyin, "branch_rus": data.branch_rus,
        "element": data.element, "yin_yang": data.yin_yang, "yuan_level": data.yuan_level,
        "start_hour": data.start_hour, "end_hour": data.end_hour,
        "guigu_score": data.guigu_score, "color_hex": data.color_hex, "icon_svg": data.icon_svg,
        "branch_id": branch_id
    })
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Branch not found")
    db.commit()
    return data


# ==========================================================================
# Black Rabbit Stars
# ==========================================================================

class BlackRabbitStar(BaseModel):
    star_name: str
    description_ru: Optional[str] = None
    nature: Optional[str] = None
    color_hex: Optional[str] = None
    icon_svg: Optional[str] = None


@router.get("/black-rabbit-stars", response_model=List[BlackRabbitStar])
@cache_with_ttl(seconds=3600)
def get_black_rabbit_stars(db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT DISTINCT star_name FROM spr_black_rabbit_matrix ORDER BY star_name
    """))
    rows = result.fetchall()
    stars = []
    for r in rows:
        star_name = r[0]
        extra = db.execute(text("""
            SELECT description_ru, nature, color_hex, icon_svg
            FROM spr_tongshu_black_rabbit_star WHERE star_name = :star_name
        """), {"star_name": star_name}).fetchone()
        if extra:
            stars.append({
                "star_name": star_name,
                "description_ru": extra[0],
                "nature": extra[1],
                "color_hex": extra[2],
                "icon_svg": extra[3],
            })
        else:
            stars.append({"star_name": star_name, "description_ru": None, "nature": None, "color_hex": None, "icon_svg": None})
    return stars


@router.put("/black-rabbit-stars/{star_name}", response_model=BlackRabbitStar)
def update_black_rabbit_star(star_name: str, data: BlackRabbitStar, db: Session = Depends(get_db)):
    result = db.execute(text("""
        UPDATE spr_tongshu_black_rabbit_star SET
            description_ru = :description_ru, nature = :nature, color_hex = :color_hex, icon_svg = :icon_svg
        WHERE star_name = :star_name
    """), {
        "description_ru": data.description_ru, "nature": data.nature,
        "color_hex": data.color_hex, "icon_svg": data.icon_svg, "star_name": star_name
    })
    if result.rowcount == 0:
        db.execute(text("""
            INSERT INTO spr_tongshu_black_rabbit_star (star_name, description_ru, nature, color_hex, icon_svg)
            VALUES (:star_name, :description_ru, :nature, :color_hex, :icon_svg)
        """), {
            "star_name": star_name, "description_ru": data.description_ru,
            "nature": data.nature, "color_hex": data.color_hex, "icon_svg": data.icon_svg
        })
    db.commit()
    return data


# ==========================================================================
# 5 Elements Display Settings
# ==========================================================================

class ElementDisplay(BaseModel):
    element_id: int
    element_name_ru: Optional[str] = None
    element_name_en: Optional[str] = None
    element_char: Optional[str] = None
    color_hex: Optional[str] = None
    bg_color_hex: Optional[str] = None
    text_color_hex: Optional[str] = None
    display_order: Optional[int] = None
    icon_svg: Optional[str] = None


@router.get("/elements", response_model=List[ElementDisplay])
@cache_with_ttl(seconds=3600)
def get_elements(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM spr_element_display ORDER BY display_order"))
    rows = result.fetchall()
    return [dict(r._mapping) for r in rows]


@router.put("/elements/{element_id}", response_model=ElementDisplay)
def update_element(element_id: int, data: ElementDisplay, db: Session = Depends(get_db)):
    result = db.execute(text("""
        UPDATE spr_element_display SET
            element_name_ru = :element_name_ru, element_name_en = :element_name_en, element_char = :element_char,
            color_hex = :color_hex, bg_color_hex = :bg_color_hex, text_color_hex = :text_color_hex,
            display_order = :display_order, icon_svg = :icon_svg
        WHERE element_id = :element_id
    """), {
        "element_name_ru": data.element_name_ru, "element_name_en": data.element_name_en,
        "element_char": data.element_char, "color_hex": data.color_hex,
        "bg_color_hex": data.bg_color_hex, "text_color_hex": data.text_color_hex,
        "display_order": data.display_order, "icon_svg": data.icon_svg, "element_id": element_id
    })
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Element not found")
    db.commit()
    return data


# ==========================================================================
# Shen Sha (Symbolic Stars) Config
# ==========================================================================

class ShenShaConfig(BaseModel):
    config_id: int
    star_key: str
    display_name_ru: Optional[str] = None
    display_name_zh: Optional[str] = None
    category: Optional[str] = None
    nature: Optional[str] = None
    color_hex: Optional[str] = None
    is_active: Optional[int] = 1
    tooltip_text: Optional[str] = None
    interpretation_text: Optional[str] = None
    short_interpretation: Optional[str] = None
    source: Optional[str] = None
    display_order: Optional[int] = 0


@router.get("/shensha-config", response_model=List[ShenShaConfig])
@cache_with_ttl(seconds=3600)
def get_shensha_config(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM spr_shensha_config ORDER BY display_order, config_id"))
    rows = result.fetchall()
    return [dict(r._mapping) for r in rows]


@router.put("/shensha-config/{config_id}", response_model=ShenShaConfig)
def update_shensha_config(config_id: int, data: ShenShaConfig, db: Session = Depends(get_db)):
    result = db.execute(text("""
        UPDATE spr_shensha_config SET
            display_name_ru = :display_name_ru, display_name_zh = :display_name_zh, category = :category,
            nature = :nature, color_hex = :color_hex, is_active = :is_active, tooltip_text = :tooltip_text,
            interpretation_text = :interpretation_text, short_interpretation = :short_interpretation,
            source = :source, display_order = :display_order
        WHERE config_id = :config_id
    """), {
        "display_name_ru": data.display_name_ru, "display_name_zh": data.display_name_zh,
        "category": data.category, "nature": data.nature, "color_hex": data.color_hex,
        "is_active": data.is_active, "tooltip_text": data.tooltip_text,
        "interpretation_text": data.interpretation_text, "short_interpretation": data.short_interpretation,
        "source": data.source, "display_order": data.display_order, "config_id": config_id
    })
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="ShenSha config not found")
    db.commit()
    return data
