
# 8 Врат (порядок для вращения по часовой стрелке от Xiu Men)
# Xiu (Отдых), Kai (Открытие), Jing (Шок), Si (Смерть), Jing (Великолепие), Du (Тайник), Shang (Ранение), Sheng (Жизнь)
GATES_ORDER = [
    "Xiu", "Kai", "Jing2", "Si", "Jing1", "Du", "Shang", "Sheng"
]
# Jing2 = 驚 (Shock), Jing1 = 景 (Scenery/Splendor)
# Mappings to Chinese
GATES_INFO = {
    "Xiu": {"name_cn": "休", "name_ru": "Отдых", "lucky": 1},
    "Kai": {"name_cn": "開", "name_ru": "Открытие", "lucky": 1},
    "Jing2": {"name_cn": "驚", "name_ru": "Шок", "lucky": -1},
    "Si": {"name_cn": "死", "name_ru": "Смерть", "lucky": -1},
    "Jing1": {"name_cn": "景", "name_ru": "Великолепие", "lucky": 0}, # Нейтрально/ситуативно
    "Du": {"name_cn": "杜", "name_ru": "Тайник", "lucky": -1},
    "Shang": {"name_cn": "傷", "name_ru": "Ранение", "lucky": -1},
    "Sheng": {"name_cn": "生", "name_ru": "Жизнь", "lucky": 1},
}

# 9 Звезд Тай И (порядок номеров 1..9)
STARS_ORDER = [
    "TaiYi",      # 1
    "SheTi",      # 2
    "XuanYuan",   # 3
    "ShaoYao",    # 4
    "TianFu",     # 5
    "QingLong",   # 6
    "XianChi",    # 7
    "TaiYin",     # 8
    "TianYi"      # 9
]

STARS_INFO = {
    "TaiYi": {"id": 1, "name_cn": "太乙", "name_ru": "Тай И", "lucky": 1},
    "SheTi": {"id": 2, "name_cn": "摄提", "name_ru": "Ше Ти", "lucky": -1},
    "XuanYuan": {"id": 3, "name_cn": "轩辕", "name_ru": "Сюань Юань", "lucky": -1},
    "ShaoYao": {"id": 4, "name_cn": "招摇", "name_ru": "Шао Яо", "lucky": -1},
    "TianFu": {"id": 5, "name_cn": "天符", "name_ru": "Тянь Фу", "lucky": -1}, # 50/50, считаем -1 по умолчанию
    "QingLong": {"id": 6, "name_cn": "青龙", "name_ru": "Цин Лун", "lucky": 1},
    "XianChi": {"id": 7, "name_cn": "咸池", "name_ru": "Сянь Чи", "lucky": -1},
    "TaiYin": {"id": 8, "name_cn": "太阴", "name_ru": "Тай Инь", "lucky": 1},
    "TianYi": {"id": 9, "name_cn": "天乙", "name_ru": "Тянь И", "lucky": 1},
}

# Последовательность дворцов для Врат Отдыха (Xiu Men)
# Янская пробежка (Winter Solstice -> Summer Solstice)
GATES_PALACE_SEQ_YANG = [1, 2, 3, 4, 6, 7, 8, 9]
# Иньская пробежка (Summer Solstice -> Winter Solstice)
GATES_PALACE_SEQ_YIN = [9, 8, 7, 6, 4, 3, 2, 1]

# Стартовые позиции звезды Тай И для декад (Цзя Цзы, Цзя Сюй и т.д.)
# Декада (Stem Index 0..5, где 0=JiaZi, 1=JiaXu...) -> Palace Number
# В тексте:
# JiaZi (0): Yang=1, Yin=9
# JiaXu (1): Yang=?, Yin=? -> Текст: Декада 甲戌 (JiaXu): Yang=?, Yin=?
# Таблица из текста:
# Декада 甲子 (JiaZi): 1 (Yang), 9 (Yin)
# Декада 甲戌 (JiaXu): 11 (Yang) -> 11-9 = 2?, 9 (Yin)? 
# Текст странный: "Декада 甲戌 ... 11 ... 9 ... 11 ... 1".
# Возможно, это смещение?
# Попробуем восстановить логику:
# Ян: 1 -> 2 -> 3 ...
# Инь: 9 -> 8 -> 7 ...
# Проверим текст: "Обратите внимание на то, что звезда Тай И в первый и последний день декады будет находиться обязательно в том же доме."
# Декада 10 дней. 9 дворцов.
# День 1: Дворец X. День 10: Дворец X + 9 = X (mod 9). Да, совпадает.
# Значит, для каждой декады нужно просто знать стартовый дворец.
# Из текста:
# 甲子 (JiaZi): Yang Start = 1, Yin Start = 9
# 甲戌 (JiaXu): Yang Start = 2 (11-9=2?), Yin Start = 8? (Текст: 11...9...11...1 - очень неясно)
# Логично предположить:
# Ян: +1 каждый день. За 10 дней смещение +10. +10 mod 9 = +1.
# Значит следующая декада начинается на +1 от предыдущей?
# JiaZi (1) -> JiaXu (2) -> JiaShen (3) -> JiaWu (4) -> JiaChen (5) -> JiaYin (6)
# Инь: -1 каждый день. За 10 дней смещение -10. -10 mod 9 = -1.
# JiaZi (9) -> JiaXu (8) -> JiaShen (7) -> JiaWu (6) -> JiaChen (5) -> JiaYin (4)
# Проверим по тексту числа (возможно это номера дней в цикле 60?):
# Декада 甲申 (JiaShen - 3-я): 21 (день цикла? 21-й день). Текст: "21 ... 1 ... 21 ... 9".
# Если JiaShen (21-й день), Yang Start = 3? (1+1+1). Yin Start = 7? (9-1-1).
# Текст: "21 ... 1". Если Yang, то 21 mod 9 = 3. А текст говорит 1? Или 1 это результат?
# Давайте предположим логичную схему (Cycle 9), так как Тай И это нумерология.
TAI_YI_STAR_START_YANG = {
    0: 1, # JiaZi
    1: 2, # JiaXu
    2: 3, # JiaShen
    3: 4, # JiaWu
    4: 5, # JiaChen
    5: 6  # JiaYin
}
TAI_YI_STAR_START_YIN = {
    0: 9, # JiaZi
    1: 8, # JiaXu
    2: 7, # JiaShen
    3: 6, # JiaWu
    4: 5, # JiaChen
    5: 4  # JiaYin
}

# 12 Желтых/Черных путей (Хуан Хей Дао)
# Порядок: QingLong (1), MingTang (2), TianXin (3), ZhuQue (4), JinKui (5), TianDe (6), BaiHu (7), YuTang (8), TianLao (9), XuanWu (10), SiMing (11), GouChen (12)
HUANG_HEI_DAO = [
    "QingLong", "MingTang", "TianXin", "ZhuQue", "JinKui", "TianDe", 
    "BaiHu", "YuTang", "TianLao", "XuanWu", "SiMing", "GouChen"
]
# Lucky maps (1=Lucky, -1=Unlucky)
HUANG_HEI_DAO_INFO = {
    "QingLong": {"name_ru": "Цин Лун (Лазурный Дракон)", "lucky": 1},
    "MingTang": {"name_ru": "Мин Тан (Светлый Зал)", "lucky": 1},
    "TianXin": {"name_ru": "Тянь Синь (Небесная Кара)", "lucky": -1},
    "ZhuQue": {"name_ru": "Чжу Цюэ (Красная Птица)", "lucky": -1},
    "JinKui": {"name_ru": "Цзин Куй (Золотой Сундук)", "lucky": 1},
    "TianDe": {"name_ru": "Тянь Ди (Небесная Добродетель)", "lucky": 1},
    "BaiHu": {"name_ru": "Бай Ху (Белый Тигр)", "lucky": -1},
    "YuTang": {"name_ru": "Ю Тан (Нефритовый Зал)", "lucky": 1},
    "TianLao": {"name_ru": "Тянь Лао (Небесная Тюрьма)", "lucky": -1},
    "XuanWu": {"name_ru": "Сюань У (Темный Воин)", "lucky": -1},
    "SiMing": {"name_ru": "Сы Мин (Управитель Судеб)", "lucky": 1},
    "GouChen": {"name_ru": "Гоу Чэнь (Крюк)", "lucky": -1},
}

# Стартовая ветвь для Цин Лун в зависимости от Ветви Дня
# Day Branch (Zi=1...Hai=12) -> Start Hour Branch (Zi=1...Hai=12)
# Zi(1) -> Shen(9)
# Chou(2) -> Xu(11) ... wait, table in text:
# Day -> Hour(Start QingLong)
# Zi(1), Wu(7) -> Shen(9)
# Mao(4), You(10) -> Yin(3)
# Yin(3), Shen(9) -> Zi(1)
# Si(6), Hai(12) -> Wu(7)
# Chen(5), Xu(11) -> Chen(5)
# Chou(2), Wei(8) -> Xu(11)
QING_LONG_START = {
    1: 9, 7: 9,
    4: 3, 10: 3,
    3: 1, 9: 1,
    6: 7, 12: 7,
    5: 5, 11: 5,
    2: 11, 8: 11
}

# Дух Счастья (Сю Шэнь) - направление (Дворец или Ветвь?)
# Текст: "Например, в день 丁卯 - направление на Юг целый день счастливое."
# Таблица:
# Wu(5), Gui(10) -> SE (Chen/Si)? Text says: 戊癸 ... (missed text)
# Let's use standard Xi Shen (Spirit of Happiness) directions if text is incomplete, or try to parse text mapping.
# Text:
# 戊(5) 癸(10) -> ?
# 丁(4) 壬(9) -> ?
# 丙(3) 辛(8) -> ?
# 喜神 (XiShen)
# 甲(1) 己(6) -> ?
# 乙(2) 庚(7) -> ?
# Standard Xi Shen directions (from classic Tong Shu):
# Jia, Ji -> NE (Gen)
# Yi, Geng -> NW (Qian)
# Bing, Xin -> SW (Kun)
# Ding, Ren -> S (Li)
# Wu, Gui -> SE (Xun)
XI_SHEN_DIRECTION = {
    1: "NE", 6: "NE", # Gen 8
    2: "NW", 7: "NW", # Qian 6
    3: "SW", 8: "SW", # Kun 2
    4: "S",  9: "S",  # Li 9
    5: "SE", 10: "SE" # Xun 4
}
# Map Direction to Palace
DIR_TO_PALACE = {
    "N": 1, "NE": 8, "E": 3, "SE": 4, "S": 9, "SW": 2, "W": 7, "NW": 6
}

# Благородный Тай И (Tai Yi Gui Ren) - Счастливые часы
# Stem -> Branches (list)
# Jia(1), Wu(5) -> Chou(2), Wei(8)
# Yi(2), Ji(6) -> Zi(1), Shen(9)
# Bing(3), Ding(4) -> You(10), Hai(12)
# Geng(7), Xin(8) -> Yin(3), Wu(7)  <-- Отличие от Бацзы для Geng!
# Ren(9), Gui(10) -> Mao(4), Si(6)
TAI_YI_NOBLE_HOURS = {
    1: [2, 8], 5: [2, 8],
    2: [1, 9], 6: [1, 9],
    3: [10, 12], 4: [10, 12],
    7: [3, 7], 8: [3, 7],
    9: [4, 6], 10: [4, 6]
}

# Отрезанный путь (Jie Lu Kong Wang)
# Day Stem -> Hours (Stems Ren(9), Gui(10))
# Jia(1), Ji(6) -> Shen(9), You(10)
# Yi(2), Geng(7) -> Wu(7), Wei(8)
# Bing(3), Xin(8) -> Chen(5), Si(6)
# Ding(4), Ren(9) -> Yin(3), Mao(4)
# Wu(5), Gui(10) -> Zi(1), Chou(2), Xu(11), Hai(12) ? Text: "Xu Hai" at end.
# Text table:
# Jia/Ji -> Shen/You
# Yi/Geng -> Wu/Wei
# Bing/Xin -> Chen/Si
# Ding/Ren -> Yin/Mao
# Wu/Gui -> Zi/Chou ... and Xu/Hai?
# Let's stick to standard logic: We need hours where Stem is Ren or Gui.
# Five Rat Method (Wu Hu Dun):
# Jia/Ji Day -> Hour Stems start with Jia(1) at Zi.
#   Zi(1)=Jia, Chou(2)=Yi, Yin(3)=Bing, Mao(4)=Ding, Chen(5)=Wu, Si(6)=Ji, Wu(7)=Geng, Wei(8)=Xin, Shen(9)=Ren, You(10)=Gui. Correct.
# So we can calculate this dynamically, no need for hardcoded table if we have Wu Hu Dun logic. 
# But table is faster.
JIE_LU_KONG_WANG = {
    1: [9, 10], 6: [9, 10],
    2: [7, 8], 7: [7, 8],
    3: [5, 6], 8: [5, 6],
    4: [3, 4], 9: [3, 4],
    5: [1, 2, 11, 12], 10: [1, 2, 11, 12] # Wu/Gui days: Zi=Ren, Chou=Gui. And Xu=Ren, Hai=Gui.
}

