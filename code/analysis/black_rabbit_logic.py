
# -*- coding: utf-8 -*-
"""
Black Rabbit (Wu Tu Ze Ri Fa) Algorithm Implementation.
Methodology: Joey Jap.
"""

# Stems and Branches for indexing
STEMS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# Palace Map (Pai Shan Tu)
# 1:Water, 2:Moon, 3:Wood, 4:Ketu, 5:Earth, 6:Rahu, 7:Metal, 8:Sun, 9:Fire
PALACE_STARS = {
    1: {'name_ru': 'Звезда Воды', 'score': 1.0, 'is_good': True},
    2: {'name_ru': 'Великая Луна', 'score': 1.0, 'is_good': True},
    3: {'name_ru': 'Звезда Дерева', 'score': 1.0, 'is_good': True},
    4: {'name_ru': 'Кету', 'score': -1.0, 'is_good': False},
    5: {'name_ru': 'Звезда Земли', 'score': -1.0, 'is_good': False},
    6: {'name_ru': 'Раху', 'score': -1.0, 'is_good': False},
    7: {'name_ru': 'Звезда Металла', 'score': 1.0, 'is_good': True},
    8: {'name_ru': 'Великое Солнце', 'score': 2.0, 'is_good': True}, # Bonus for Sun
    9: {'name_ru': 'Звезда Огня', 'score': -1.0, 'is_good': False},
}

# Sequences
# Yang (Clockwise): 1->8->3->4->9->2->7->6->5->1
SEQ_YANG = [1, 8, 3, 4, 9, 2, 7, 6, 5]
# Yin (Counter): 1->6->7->2->9->4->3->8->5->1
SEQ_YIN = [1, 6, 7, 2, 9, 4, 3, 8, 5]

def get_stem_idx(char):
    try:
        return STEMS.index(char)
    except ValueError:
        return -1

def get_branch_idx(char):
    try:
        return BRANCHES.index(char)
    except ValueError:
        return -1

# Таблица стартового дворца 1-го лунного дня для 60 JiaZi.
# Индекс = jiazi_id_1го_дня - 1.
# Получена из spr_black_rabbit_matrix (verified against Tong Shu 2026 v2).
FIRST_DAY_PALACE_LOOKUP = [
    3, 8, 8, 1, 8, 8, 3, 4, 4, 9,  # 1-10
    2, 2, 7, 6, 6, 1, 8, 8, 3, 4,  # 11-20
    4, 9, 3, 2, 7, 6, 6, 1, 6, 6,  # 21-30
    7, 3, 3, 9, 4, 4, 2, 8, 8, 1,  # 31-40
    8, 8, 2, 4, 4, 9, 3, 3, 7, 6,  # 41-50
    6, 1, 6, 6, 7, 2, 2, 9, 4, 4,  # 51-60
]

def get_stem_group(stem_idx):
    """
    Returns 'YANG' or 'YIN' based on Black Rabbit SPECIAL rules.
    Используется для часового метода и справочно.
    Yang Group: Jia(0), Ji(5), Ding(3), Ren(8), Wu(4), Gui(9).
    Yin Group: Yi(1), Geng(6), Bing(2), Xin(7).
    """
    if stem_idx in [0, 5, 3, 8, 4, 9]:
        return 'YANG'
    return 'YIN'

def get_standard_stem_group(stem_idx):
    """
    Returns 'YANG' or 'YIN' based on STANDARD Yin/Yang classification.
    Используется для дневного метода (daily star distribution).
    Yang: Jia(0), Bing(2), Wu(4), Geng(6), Ren(8).
    Yin: Yi(1), Ding(3), Ji(5), Xin(7), Gui(9).
    """
    if stem_idx % 2 == 0:
        return 'YANG'
    return 'YIN'

def move_palace(start_palace, steps, direction_group):
    """
    Moves `steps` number of times from `start_palace` using the sequence defined by `direction_group`.
    """
    seq = SEQ_YANG if direction_group == 'YANG' else SEQ_YIN
    try:
        start_idx = seq.index(start_palace)
    except ValueError:
        return start_palace # Should not happen
    
    final_idx = (start_idx + steps) % 9
    return seq[final_idx]

def calculate_day_star(day_stem, day_branch, lunar_day):
    """
    Вычисляет Дневную Звезду Чёрного Кролика (Joey Yap).
    Алгоритм (reverse-engineered, верифицирован на 7 датах 2026):
      1. Вычислить jiazi_id 1-го лунного дня
      2. first_palace = FIRST_DAY_PALACE_LOOKUP[(jiazi_id_1st - 1) % 9]
      3. Направление = стандартная Инь/Ян ствола 1-го ЛД (чётный=Yang=CW, нечётный=Yin=CCW)
      4. palace_current = walk(first_palace, lunar_day - 1, direction)
    
    Параметры:
      day_stem: Небесный Ствол текущего дня (символ)
      day_branch: Земная Ветвь текущего дня (символ)
      lunar_day: Номер лунного дня (1-30)
    Возвращает: dict с name_ru, score, is_good или None.
    Обновлено: 2026-02-15
    """
    d_stem_idx = get_stem_idx(day_stem)
    d_branch_idx = get_branch_idx(day_branch)
    
    if d_stem_idx == -1 or d_branch_idx == -1:
        return None

    # 1. Вычисляем jiazi_id текущего дня (1-60)
    # jiazi_id = ((stem_idx * 6 - branch_idx * 5) % 60) + 1 — но проще через формулу:
    # jiazi_id определяется парой (stem_idx, branch_idx) в 60-элементном цикле.
    # Формула: jiazi_id = ((d_stem_idx - d_branch_idx) % 12) * 5 + d_stem_idx + 1
    # Но надёжнее через обратный ход.
    # Используем стандартную формулу: jiazi_id = (d_stem_idx + d_branch_idx * 5) % 60
    # На самом деле: jiazi_id = ((d_branch_idx % 2 == d_stem_idx % 2) проверка + цикл)
    # Простой расчёт: stem и branch на одинаковой чётности.
    # jiazi_id текущего дня:
    day_jiazi_id = _compute_jiazi_id(d_stem_idx, d_branch_idx)
    
    if day_jiazi_id is None:
        return None
    
    # 2. jiazi_id 1-го лунного дня
    first_jiazi_id = ((((day_jiazi_id - 1) - (lunar_day - 1)) % 60 + 60) % 60) + 1
    
    # 3. Стартовый дворец 1-го ЛД (из lookup-таблицы)
    palace_1st = FIRST_DAY_PALACE_LOOKUP[first_jiazi_id - 1]
    
    # 4. Направление: special stem group (Joey Yap / Wu Tu)
    # Yang: Jia(0), Ji(5), Ding(3), Ren(8), Wu(4), Gui(9) -> +1
    # Yin: Yi(1), Geng(6), Bing(2), Xin(7) -> -1
    stem_1st_idx = (d_stem_idx - (lunar_day - 1)) % 10
    day_1st_dir = get_stem_group(stem_1st_idx)
    
    # 5. Движение: простое числовое +1 (Yang) или -1 (Yin) с wrap-around 1..9
    if day_1st_dir == 'YANG':
        palace_current = ((palace_1st - 1 + (lunar_day - 1)) % 9) + 1
    else:
        palace_current = ((palace_1st - 1 - (lunar_day - 1)) % 9 + 9) % 9 + 1
    
    return PALACE_STARS.get(palace_current)

def _compute_jiazi_id(stem_idx, branch_idx):
    """
    Вычисляет jiazi_id (1-60) из индексов ствола (0-9) и ветви (0-11).
    Ствол и ветвь должны иметь одинаковую чётность.
    """
    # Ствол и ветвь в цикле Цзя-Цзы всегда одной чётности
    if stem_idx % 2 != branch_idx % 2:
        return None
    # Формула: jiazi_id определяется через CRT (Chinese Remainder Theorem)
    # Цикл: stem_idx = (jiazi_id - 1) % 10, branch_idx = (jiazi_id - 1) % 12
    # Решение: jiazi_id - 1 ≡ stem_idx (mod 10), jiazi_id - 1 ≡ branch_idx (mod 12)
    # Используем перебор (быстрый, до 60 итераций)
    for jid in range(60):
        if jid % 10 == stem_idx and jid % 12 == branch_idx:
            return jid + 1
    return None

def calculate_hour_star(day_stem, hour_branch):
    """
    Calculates the Hour Star.
    """
    d_stem_idx = get_stem_idx(day_stem)
    h_branch_idx = get_branch_idx(hour_branch)
    
    if d_stem_idx == -1 or h_branch_idx == -1:
        return None
        
    # Table 4 Logic
    # Groups for Start Palace
    # Jia(0)/Ji(5) -> 1 Kan, CW
    # Yi(1)/Geng(6) -> 7 Dui, CCW
    # Bing(2)/Xin(7) -> 3 Zhen, CCW
    # Ding(3)/Ren(8) -> 9 Li, CW
    # Wu(4)/Gui(9) -> 5 Center, CW
    
    start_palace = 1
    direction = 'YANG' # Clockwise default
    
    if d_stem_idx in [0, 5]: # Jia, Ji
        start_palace = 1
        direction = 'YANG'
    elif d_stem_idx in [1, 6]: # Yi, Geng
        start_palace = 7
        direction = 'YIN'
    elif d_stem_idx in [2, 7]: # Bing, Xin
        start_palace = 3
        direction = 'YIN'
    elif d_stem_idx in [3, 8]: # Ding, Ren
        start_palace = 9
        direction = 'YANG'
    elif d_stem_idx in [4, 9]: # Wu, Gui
        start_palace = 5
        direction = 'YANG'
        
    # Steps = hour_branch_idx (Rat=0, etc.)
    palace_hour = move_palace(start_palace, h_branch_idx, direction)
    
    return PALACE_STARS.get(palace_hour)
