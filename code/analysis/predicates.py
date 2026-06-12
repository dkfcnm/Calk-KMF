import json

class PredicateRegistry:
    def __init__(self):
        self._registry = {}

    def register(self, code):
        def wrapper(func):
            self._registry[code] = func
            return func
        return wrapper

    def get(self, code):
        return self._registry.get(code)

registry = PredicateRegistry()

# Базовые предикаты (примеры)
@registry.register("ALWAYS_TRUE")
def check_always_true(context, params):
    return True, "Always True"

@registry.register("ALWAYS_FALSE")
def check_always_false(context, params):
    return False, "Always False"

from code.common.db_manager import db

# Кэш для маппинга офицеров: (month_branch_char, day_branch_char) -> (name_ru, score)
_officer_map_cache = {}

def _load_officer_map():
    if _officer_map_cache:
        return

    sql = """
    SELECT mb.branch_char, db.branch_char, iv.name_ru, iv.numeric_score
    FROM spr_day_officer_mapping dom
    JOIN spr_earthly_branch mb ON mb.branch_id = dom.month_branch_id
    JOIN spr_earthly_branch db ON db.branch_id = dom.day_branch_id
    JOIN spr_indicator_value iv ON iv.value_id = dom.officer_value_id
    """
    try:
        rows = db.fetch_all(sql)
        for row in rows:
            # (m_char, d_char) -> (name, score)
            _officer_map_cache[(row[0], row[1])] = (row[2], row[3])
    except Exception as e:
        print(f"Error loading officer map: {e}")

@registry.register("CHECK_DAY_OFFICER")
def check_day_officer(context, params):
    """
    Определяет 12 офицеров дня.
    Context: {
        "month_pillar": "丙寅",
        "day_pillar": "戊子"
    }
    Returns: (True, OfficerName, Score)
    """
    # Загружаем карту при первом вызове
    if not _officer_map_cache:
        _load_officer_map()
        
    m_pillar = context.get('month_pillar')
    d_pillar = context.get('day_pillar')
    
    if not m_pillar or not d_pillar:
        return False, "Missing pillar info"
        
    # Извлекаем Ветвь (второй символ)
    # Предполагается формат "СтволВетвь" (2 символа)
    try:
        m_branch = m_pillar[1]
        d_branch = d_pillar[1]
    except IndexError:
        return False, "Invalid pillar format"
        
    if (m_branch, d_branch) in _officer_map_cache:
        name, score = _officer_map_cache[(m_branch, d_branch)]
        return True, name, score
        
    return False, "Mapping not found"

@registry.register("CHECK_QIMEN_STEMS")
def check_qimen_stems(context, params):
    """
    Проверяет структуру: Небесный ствол (Heaven) на Земном стволе (Earth).
    Params: {"heaven": "甲", "earth": "丙"}
    Context: {"heaven_stem": "甲", "earth_stem": "丙", ...}
    """
    ctx_heaven = context.get('heaven_stem')
    ctx_earth = context.get('earth_stem')
    
    # Если в контексте нет данных (например, пустой дворец или ошибка), пропускаем
    if not ctx_heaven or not ctx_earth:
        return False, None
        
    target_heaven = params.get('heaven')
    target_earth = params.get('earth')
    
    if ctx_heaven == target_heaven and ctx_earth == target_earth:
        return True, f"Структура {target_heaven} на {target_earth}"
        
    return False, None
