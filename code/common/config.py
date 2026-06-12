import sys
import os

# Ensure imports work if run directly
sys.path.insert(0, os.getcwd())

from dataclasses import dataclass
from typing import Dict, List, Tuple
from code.common.db_manager import db

@dataclass
class ProjectConfig:
    # Qimen
    solar_term_ju: Dict[int, Tuple[int, int, int]]
    ri_jia_table: Dict[str, Dict[str, Tuple[int, int, int]]]
    stems: List[str]
    branches: List[str]
    gods: List[str]
    gods_ru: List[str]
    stars: Dict[int, str]
    stars_ru: Dict[int, str]
    gates: Dict[int, str]
    gates_ru: Dict[int, str]
    leader_stems: Dict[int, str]
    yuan_levels: Dict[str, int]
    
    # Feng Shui
    month_star_map: Dict[Tuple[str, str], int]
    hour_star_map: Dict[Tuple[str, int, str], int]

def load_config_from_db(db_path: str = None) -> ProjectConfig:
    # db_path is ignored, using central DBManager
    
    # 1. Solar Term Ju
    rows = db.fetch_all("SELECT solar_term_id, upper_ju, middle_ju, lower_ju FROM spr_solar_term WHERE upper_ju IS NOT NULL")
    solar_term_ju = {row[0]: (row[1], row[2], row[3]) for row in rows}
    
    # 2. Ri Jia (из spr_jiazi_extended — колонки *_ju_yang / *_ju_yin)
    rows = db.fetch_all("""
        SELECT stem || branch AS day_pillar,
               upper_ju_yang, middle_ju_yang, lower_ju_yang,
               upper_ju_yin, middle_ju_yin, lower_ju_yin
        FROM spr_jiazi_extended ORDER BY jiazi_id
    """)
    ri_jia = {}
    for row in rows:
        pillar = row[0]
        ri_jia[pillar] = {
            'yang': (row[1], row[2], row[3]),
            'yin':  (row[4], row[5], row[6])
        }
    
    # 3. Stems & Branches
    rows = db.fetch_all("SELECT stem_char FROM spr_heavenly_stem ORDER BY stem_id")
    stems = [r[0] for r in rows]
    
    rows = db.fetch_all("SELECT branch_char FROM spr_earthly_branch ORDER BY branch_id")
    branches = [r[0] for r in rows]
    
    # 4. Gods
    rows = db.fetch_all("SELECT name_en, spirit_char AS name_ru FROM spr_gods ORDER BY id")
    gods = [r[0] for r in rows]
    gods_ru = [r[1] for r in rows]
    
    # 5. Stars
    rows = db.fetch_all("SELECT id, name_en, star_char AS name_ru FROM spr_stars")
    stars = {r[0]: r[1] for r in rows}
    stars_ru = {r[0]: r[2] for r in rows}
    
    # 6. Gates
    rows = db.fetch_all("SELECT id, name_en, gate_char AS name_ru FROM spr_gates")
    gates = {r[0]: r[1] for r in rows}
    gates_ru = {r[0]: r[2] for r in rows}
    
    # 7. Leader Stems
    rows = db.fetch_all("SELECT idx, stem FROM spr_leader_stems")
    leader_stems = {r[0]: r[1] for r in rows}
    
    # 8. Yuan Levels
    rows = db.fetch_all("SELECT branch_char, yuan_level FROM spr_earthly_branch WHERE yuan_level IS NOT NULL")
    yuan_levels = {r[0]: r[1] for r in rows}
    
    # 9. Month Stars
    rows = db.fetch_all("SELECT year_branch, month_branch, star FROM spr_month_stars")
    month_star_map = {(r[0], r[1]): r[2] for r in rows}
    
    # 10. Hour Stars
    rows = db.fetch_all("SELECT day_branch, yin_yang, hour_branch, star FROM spr_hour_stars")
    hour_star_map = {(r[0], r[1], r[2]): r[3] for r in rows}
    
    return ProjectConfig(
        solar_term_ju=solar_term_ju,
        ri_jia_table=ri_jia,
        stems=stems,
        branches=branches,
        gods=gods,
        gods_ru=gods_ru,
        stars=stars,
        stars_ru=stars_ru,
        gates=gates,
        gates_ru=gates_ru,
        leader_stems=leader_stems,
        yuan_levels=yuan_levels,
        month_star_map=month_star_map,
        hour_star_map=hour_star_map
    )
