# Unified Tong Shu Portal Specification
## Объединённая спецификация на основе анализа mingli.ru и chinesemetasoft.com

**Дата:** 2026-05-23  
**Версия:** 0.1 (draft — до анализа 3-го сайта)  
**Проект:** Calk_KMF v2.3.1

---

## 1. Общая архитектура сравниваемых порталов

### 1.1 mingli.ru
- **Авторизация:** Email + пароль (shda0508@bk.ru)
- **Персонализация:** Профиль с ДРТ (дата-рождения-таймзона)
- **Структура:** Месячный календарь (7×N сетка) → Детальная страница дня → Почасовые блоки (12 шт.)
- **Язык:** Русский
- **Настройки расчёта:** SystemType (Zhi Run / Chai Bu), Chart Type (4 варианта), Ghost mode (3), UTC, Display mode
- **Стек:** jQuery/Vue hybrid, ASP.NET backend

### 1.2 chinesemetasoft.com (CMS)
- **Авторизация:** Email + пароль (dkfcnm3)
- **Персонализация:** Профиль с ДРТ (Dmitriy Shuvalov, 1987-04-23 16:02)
- **Структура:** Месячный календарь (7×N) + 8 вкладок данных + Детальная страница дня (/TongShu/Date) + Интерактивные инструменты (QMDJ Chart, Ba Zi Chart, Ze Ri)
- **Язык:** 18+ языков (English, Русский, Polski, Español, 中文, etc.)
- **Настройки расчёта:** Method (Chai Bu / Zhi Run / Lunar), Convention 2, Chart Type (Hour/Day/Month/Year/Destiny)
- **Стек:** ASP.NET MVC, HTML tables

---

## 2. Функциональный сравнительный анализ

### 2.1 Месячный календарь (основной вид)

| Функция | mingli.ru | CMS | Примечание |
|---------|-----------|-----|------------|
| Сетка 7×N | ✅ | ✅ | Оба — стандартный календарь |
| Навигация по месяцам | ✅ | ✅ | CMS: + быстрый переход на 2027 |
| Персонализация ячеек | ✅ (Professional) | ✅ (Personal) | Разные подходы |
| Цветовая кодировка | ✅ | ✅ | Зелёный=хорошо, красный=плохо |
| Клик по дню → детали | ✅ (/Calendar/Day/...) | ✅ (/TongShu/Date?Date=...) | |
| Вкладки внутри месяца | ❌ | ✅ (8 вкладок) | CMS: Personal/QMDJ/XKDG/XKDG局/Professional/3Victories/BaZi/NaYin |
| Настройки UTC/таймзоны | ✅ (ручной + Auto) | ✅ (Europe/Moscow, +3h) | |

### 2.2 Детальная страница дня

| Функция | mingli.ru | CMS | Примечание |
|---------|-----------|-----|------------|
| Four Pillars | ✅ | ✅ | Оба показывают Year/Month/Day/Hour |
| Hour blocks (12 шт.) | ✅ | ⚠️ (только в /TongShu/Date) | mingli: 23:00–01:00 etc. CMS: 0-1, 1-3, ..., 23-24 |
| QMDJ карты по часам | ✅ (Zhi Run) | ✅ (ChaiBu/ZhiRun/Lunar) | mingli: только Zhi Run; CMS: 3 метода |
| Flying Stars | ❌ | ✅ (Day/Month/Year) | CMS уникально |
| Feng Shui maps | ❌ | ✅ (Day/Month/Year) | CMS уникально |
| Hexagrams (I Ching) | ❌ | ✅ (все столпы + часы) | CMS уникально |
| Activity recommendations | ❌ | ✅ (17 видов деятельности) | CMS уникально |
| XKDG structures | ❌ | ✅ (почасовые + дневные блоки) | CMS уникально |
| Belt system | ❌ | ✅ (12 типов) | CMS уникально |

### 2.3 QMDJ (奇门遁甲)

| Функция | mingli.ru | CMS | Примечание |
|---------|-----------|-----|------------|
| Методы | Zhi Run / Chai Bu | Chai Bu / Zhi Run / Lunar | CMS: + Lunar |
| Типы карт | Hour/Day (минимально) | Hour/Day/Month/Year/Destiny/AnnualForecast | CMS: гораздо богаче |
| Размещение (layout) | 4 типа (Joey Yap / Calvin Yap / Zheng Xian Rong / Huang Heng Yu) | Convention 2 | mingli: 4 типа; CMS: 1 тип? |
| Ghost mode | 3 варианта | — | mingli уникально |
| Мини-карты в месяце | ✅ (Zhi Run) | ✅ (ChaiBu + ZhiRun) | |
| Полные карты 9 дворцов | ✅ | ✅ | Оба |
| Интерпретации структур | ❌ | ✅ (подробные описания) | CMS уникально |
| Стратегии (36 стратагем) | ❌ | ✅ | CMS уникально |
| Stems Formations | ❌ | ✅ | CMS уникально |
| 3 Victories (三勝) | ❌ | ✅ | CMS уникально |

### 2.4 Ba Zi (八字)

| Функция | mingli.ru | CMS | Примечание |
|---------|-----------|-----|------------|
| Four Pillars | ✅ | ✅ | Оба |
| 10 Gods (十神) | ✅ | ✅ | Оба |
| Hidden Stems | ✅ | ✅ | Оба |
| Na Yin | ⚠️ (косвенно) | ✅ (отдельная вкладка) | CMS выделил в отдельный модуль |
| Luck Pillars (大运) | ❌ | ✅ (10 периодов по 10 лет) | CMS уникально |
| Day Master Strength | ❌ | ✅ (50/50 бар + круговая диаграмма) | CMS уникально |
| Ba Zhai (八宅) | ❌ | ✅ (8 Mansions) | CMS уникально |
| QMDJ Palace of Destiny | ❌ | ✅ | CMS уникально |
| Scoring (10 Aspects) | ❌ | ✅ (Joseph Yu / Ken Lai) | CMS уникально |

### 2.5 Xuan Kong Da Gua (玄空大卦)

| Функция | mingli.ru | CMS | Примечание |
|---------|-----------|-----|------------|
| Гексаграммы дня | ❌ | ✅ | CMS уникально |
| Пары гуа | ❌ | ✅ (Pi-Tai, JiJi-WeiJi, etc.) | CMS уникально |
| Теги (C5, C10, FG, HT, etc.) | ❌ | ✅ | CMS уникально |
| Почасовые структуры | ❌ | ✅ (Combo of 5/10, He Tu, Pure Gua) | CMS уникально |
| Дневные XKDG блоки | ❌ | ✅ (He Tu, Combo 10, Combo 5-15, 7 Star Robbery, etc.) | CMS уникально |

### 2.6 Tung Shu (通书 / 12 Officers)

| Функция | mingli.ru | CMS | Примечание |
|---------|-----------|-----|------------|
| 12 Officers (值日星) | ✅ | ✅ | Оба: Establish, Remove, Full, etc. |
| 28 Constellations | ❌ | ✅ (Weaving Maiden, Ghost, etc.) | CMS уникально |
| Yellow & Black Belt | ❌ | ✅ (Bright Hall, Jade Hall, etc.) | CMS уникально |
| Black Rabbit | ❌ | ✅ | CMS уникально |
| Dong Gong | ❌ | ✅ | CMS уникально |
| Index KP1/3v1 | ❌ | ✅ (-85/6 и т.д.) | CMS уникально |
| Tung Shu numbers | ✅ (1-12) | ✅ (1-12) | Оба |

### 2.7 Ze Ri (择日 — выбор даты)

| Функция | mingli.ru | CMS | Примечание |
|---------|-----------|-----|------------|
| Поиск благоприятных дат | ❌ | ✅ | CMS уникально |
| Фильтры (14 шт.) | ❌ | ✅ | CMS уникально |
| Персонализация поиска | ❌ | ✅ (DOB-based) | CMS уникально |
| Результаты с деталями | ❌ | ✅ (20 на страницу) | CMS уникально |
| QMDJ 1-4 / XKDG / Feng Shui | ❌ | ✅ (вкладки в Ze Ri) | CMS уникально |

### 2.8 Дополнительные модули

| Функция | mingli.ru | CMS | Примечание |
|---------|-----------|-----|------------|
| Da Liu Ren | ❌ | ✅ (отдельный модуль) | CMS |
| ZWDS (紫微斗数) | ❌ | ✅ (отдельный модуль) | CMS |
| Feng Shui (отдельный) | ❌ | ✅ (отдельный модуль) | CMS |
| Yi Jing (易经) | ❌ | ✅ (отдельный модуль) | CMS |
| 1080 QMDJ Charts | ❌ | ✅ | CMS |
| Tables/Spravs | ❌ | ✅ (QMDJ Tables, Resources) | CMS |

---

## 3. Полный перечень показателей (единый словарь)

### 3.1 Four Pillars (四柱)
- Year Pillar (年柱): Stem + Branch + Element + Animal + Hidden Stems + Na Yin
- Month Pillar (月柱): Stem + Branch + Element + Animal + Hidden Stems + Na Yin
- Day Pillar (日柱): Stem + Branch + Element + Animal + Hidden Stems + Na Yin
- Hour Pillar (时柱): Stem + Branch + Element + Animal + Hidden Stems + Na Yin
- Conception Pillar (胎元): опционально
- Life Palace (命宫): опционально

### 3.2 Tung Shu Base (12 Officers)
1. Establish (建) / 1
2. Remove (除) / 2
3. Full (满) / 3
4. Balance (平) / 4
5. Stable (定) / 5
6. Initiate (执) / 6
7. Destruction (破) / 7
8. Danger (危) / 8
9. Success (成) / 9
10. Receive (收) / 10
11. Open (开) / 11
12. Close (闭) / 12

### 3.3 QMDJ (奇门遁甲)
- **Day Chart**: Structure (Yin/Yang + ju), Lead Stem, Envoy, Lead Star, 28 Constellations, Jia hides behind, Sky Horse, Death & Emptiness, Nobleman, 3 Victories, Day clash, Hour clash
- **Hour Chart**: Full 9-palace map with Doors, Stars, Stems, Deities, Directions
- **Methods**: Zhi Run (置闰), Chai Bu (拆补), Lunar (置闰阴遁?)
- **Interpretations**: Structures, Stems Formations, Extra Stems Formations, Strategies

### 3.4 Ba Zi Extended (八字扩展)
- 10 Gods (十神): Friend, HO, RW, 7K, IW, DO, EG, IR, DR, DW
- Day Master Strength: % Strong / % Weak
- Five Factors pie chart
- Luck Pillars (大运): 10 periods × 10 years
- Ba Zhai (八宅): Gua Number, Life Star, 8 Directions (Favorable/Unfavorable)
- Special Stars: Nobleman, Intelligence, Sky Horse, Peach Blossom, Solitary, Heavenly Doctor, Illness Star, Death & Emptiness

### 3.5 Xuan Kong Da Gua (玄空大卦)
- Hexagram 1-64 (I Ching)
- Upper/Lower trigrams with element numbers
- Gua pairs: Pi-Tai, JiJi-WeiJi, Kan-Li, Zhen-Xun, Qian-Kun, Gen-Dui, Heng-Yi, Sun-Xian
- Tags: FG, HT, C5, C10, C15, PG, 1St, K, SG
- Hourly structures: Combo of 5, Combo of 10, He Tu, Pure Gua, Family Gua
- Daily blocks: He Tu, Combo 10, Combo 5-15, 7 Star Robbery, Stem Branch Combo, Stem 7K, Stem IW

### 3.6 Flying Stars (玄空飞星)
- Day Flying Star Chart (9-palace)
- Month Flying Star Chart
- Year Flying Star Chart
- Central stars overlay (Day/Month/Year/Hour)

### 3.7 Feng Shui Daily Maps
- Day/Month/Year 9-palace grids
- Stars: Grand Duke, Robbery Sha, Five Ghost, Peach Blossom, Sky Horse, Duke Virtue, Annual Sha, Year Breaker, etc.
- GSF ( auspicious directions )

### 3.8 Symbolic Stars (神煞)
**mingli.ru:**
- Sha directions (冲的方向)
- Clash animals (冲的生肖)
- 6C, 3H, Int, PB, SH, Nob (в Personal)

**CMS:**
- 28 Constellations (二十八宿)
- Yellow & Black Belt (黃黑道十二神)
- 12 Officers
- Dong Gong
- Black Rabbit
- Belt types: Heavenly Punishment, Red Phoenix, Golden Lock, Precious Light, White Tiger, Jade Hall, Heavenly Jail, Black Tortoise, Life Governor, Grappling Hook, Green Dragon, Bright Hall
- Day Stars Good: Auspicious Army, Civilian Day, Heavenly Wealth, Important Noble, Heavenly Harmony, Yang Noble, Benefit Descendants, Minister Day, Monthly Wealth, Wealth Storage
- Day Stars Bad: Axe Sha, Big Mishap, Charred Trees, Earth Depression, Earthly Fire, Flying Chaste, Four Abandonment, Golden God, Month Detest, Month Frail, Month Sha, Near Abandonment, Five Ghost, Heavenly Depression, Heavenly Fire, Heavenly Jail, Lonely Fire Ding, Roasting Star, Death Charm, Earthly Officer Charm, Four Major Graves, Heaven and Earth Shifting, Lesser Consumer, Wu Capital Heaven Sha
- Special Days: Ten Spiritual Days, Yang Gong Disaster Day, Fire Star Day, Heavenly Thief Day, Month Suppressed Big Mishap Day, Heavenly Grace Day

### 3.9 3 Victories (三勝 / 三阴)
- Heavenly Yi (太乙): direction
- Heaven (天): direction
- Life (生): direction
- Light (符): direction + modifier
- Power (符): direction
- Blessing (天): direction + modifier
- Force (生): direction

### 3.10 Scoring / Index
- **mingli.ru**: Нет явного скоринга
- **CMS**: Personal Index (0-100?), Index KP1/3v1 (-85/6), XKDG Family/Total (%), Main score (-63), Sub-score (-10)

### 3.11 Activities (择日应用)
- Praying Worshipping, Collecting Debt, Constructing Drains/Roof, Dissolving Arrangement, Financial Activities, Groundbreaking, Marriage, Moving House, Networking, Renovation, Seeking Medical Treatment, Signing Contracts, Starting New Business/Job, Trading, Travelling

---

## 4. Что уже реализовано в Calk_KMF (текущее состояние)

### ✅ Реализовано:
1. **t_bazi_hourly** (355K rows): Four Pillars для каждого часа 1900-2100
2. **t_qumen_dgiren_hourly/monthly/daily**: QMDJ Zhi Run (классический)
3. **t_qumen_chauby_hourly/monthly/daily**: QMDJ Chai Bu
4. **spr_jiazi_extended**: 6 ju columns (upper/middle/lower × yang/yin)
5. **spr_solar_term**: Solar terms для ju calculation
6. **t_solar_term_time**: Exact crossing times
7. **t_flying_stars**: Flying Stars data (есть?)
8. **pillar calculation**: calc_day_pillar с 子时 rollover
9. **Classical logic**: fu_tou, yuan, solar_term lookup

### ⚠️ Частично / нуждается в проверке:
1. Hour QMDJ: 68.2% match с Excel (классический принят как авторитетный)
2. Day QMDJ: 2.8% match (ожидаемо, разные методологии)
3. Flying Stars: таблица есть, но не проверена
4. 10 Gods: есть логика, но не интегрирована в календарь

### ❌ Не реализовано:
1. 28 Constellations
2. Yellow & Black Belt
3. 12 Officers (Tung Shu numbers есть, но не как система)
4. XKDG (гексаграммы, структуры)
5. Ba Zhai (八宅)
6. Luck Pillars (大运)
7. Ze Ri (поиск с фильтрами)
8. Belt system
9. Day Stars (Good/Bad)
10. Activity recommendations
11. Scoring system
12. Feng Shui daily maps
13. Hexagrams for pillars
14. 3 Victories
15. QMDJ interpretations/structures/strategies
16. Personalization (user profiles)
17. Lunar date conversion
18. Moon phase data

---

## 5. Открытые вопросы (для обсуждения после анализа 3-го сайта)

### 5.1 Приоритеты реализации
> **Q1. Какой функционал приоритетен для первого релиза unified portal?**
> - Вариант A: Core (месячный календарь + Four Pillars + QMDJ + Tung Shu)
> - Вариант B: Extended (Core + Ba Zi 10 Gods + Na Yin + Symbolic Stars + Scoring)
> - Вариант C: Professional (Extended + XKDG + Flying Stars + Feng Shui + Ze Ri)

### 5.2 QMDJ методология
> **Q2. Какие методы QMDJ поддерживать?**
> - Zhi Run (置闰) — классический, уже реализован ✅
> - Chai Bu (拆补) — есть t_qumen_chauby ✅
> - Lunar (置闰阴遁?) — что это? Нужно исследовать
> - Сколько "Convention" / "Chart Type" поддерживать?

### 5.3 Персонализация
> **Q3. Нужна ли регистрация пользователей с сохранением профилей ДРТ?**
> - mingli и CMS оба требуют авторизации для Personal view
> - Без авторизации показывается generic (неперсонализированный) календарь?

### 5.4 Скоринг
> **Q4. Нужна ли система скоринга дней?**
> - CMS использует: Personal Index, Index KP1/3v1, XKDG Family/Total%, Main/Sub scores
> - Алгоритм CMS неизвестен
> - Создать свой алгоритм или реверс-инжинирить?

### 5.5 Языки
> **Q5. Какие языки поддерживать?**
> - Русский (основной, как mingli)
> - English (как CMS)
> - 中文 (иероглифы)
> - Или мультиязычность с переключателем?

### 5.6 Детализация
> **Q6. Какой уровень детализации почасовых данных?**
> - mingli: 12 блоков с мини-QMDJ картами
> - CMS: Только в детальной странице дня (/TongShu/Date) + интерактивный QMDJ Chart
> - Показывать почасовые данные прямо в месячном виде или только по клику?

### 5.7 Визуализация
> **Q7. Какие графические элементы нужны?**
> - Цветовая кодировка ячеек (у обоих)
> - Бар-чарты стихий (CMS Ba Zi)
> - Круговые диаграммы (CMS)
> - 9-палатные сетки (QMDJ, Flying Stars, Feng Shui)
> - Гексаграммы (XKDG)

### 5.8 Интерпретации
> **Q8. Нужны ли текстовые интерпретации (как в CMS)?**
> - CMS: Очень подробные (QMDJ structures, strategies, descriptions)
> - mingli: Минимальные
> - Это требует большой базы знаний

### 5.9 Ze Ri (Date Selection)
> **Q9. Нужен ли инструмент выбора благоприятных дат?**
> - CMS: 14 фильтров + персонализация + результаты с деталями
> - Это отдельный большой модуль

### 5.10 Интеграция с существующими модулями
> **Q10. Как unified portal взаимодействует с существующими модулями Calk_KMF?**
> - Ba Zi calculator (уже есть)
> - QMDJ calculator (уже есть)
> - Calendar module (уже есть)
> - Feng Shui module (есть?)
> - Tai Yi module (есть?)

### 5.11 Технические вопросы
> **Q11. Как хранить и обновлять данные?**
> - PostgreSQL (online) / SQLite (offline fallback)
> - Какой диапазон дат предварительно рассчитывать?
> - Как часто обновлять?

> **Q12. Производительность:**
> - t_bazi_hourly: 355K rows
> - t_qumen_dgiren_hourly: ~355K rows
> - Добавление Flying Stars, XKDG, Feng Shui — сколько строк?
> - Кэширование месячных/дневных агрегатов?

---

## 6. Предложения для архитектуры Calk_KMF

### 6.1 Модульная структура
```
unified_portal/
├── core/
│   ├── monthly_calendar.py      # Месячный календарь 7×N
│   ├── day_detail.py            # Детальная страница дня
│   ├── four_pillars.py          # Four Pillars (использует существующее)
│   └── tung_shu.py              # 12 Officers, Tung Shu numbers
├── qmdj/
│   ├── day_chart.py             # QMDJ daily (Zhi Run + Chai Bu)
│   ├── hour_chart.py            # QMDJ hourly (12 blocks)
│   ├── interactive_chart.py     # Интерактивный QMDJ (как CMS Chart)
│   └── interpretations.py       # Структуры, стратегии (опционально)
├── bazi/
│   ├── ten_gods.py              # 10 Gods personalized
│   ├── luck_pillars.py          # 大运 (опционально)
│   ├── day_master_strength.py   # Сила Day Master
│   └── ba_zhai.py               # 八宅 (опционально)
├── xkdg/
│   ├── daily_hexagram.py        # Гексаграмма дня
│   ├── hourly_structures.py     # Почасовые структуры
│   └── daily_blocks.py          # He Tu, Combo 10, etc.
├── feng_shui/
│   ├── flying_stars.py          # Flying Stars (Day/Month/Year)
│   ├── daily_map.py             # Feng Shui daily map
│   └── auspicious_directions.py # Благоприятные направления
├── symbolic_stars/
│   ├── constellation_28.py      # 二十八宿
│   ├── belt_system.py           # 黃黑道
│   ├── day_stars.py             # Good/Bad stars
│   └── special_days.py          # Special day markers
├── scoring/
│   ├── day_score.py             # Композитный балл дня
│   ├── personal_index.py        # Персонализированный индекс
│   └── compatibility.py         # Совместимость с профилем
├── zeri/
│   ├── search_engine.py         # Поиск с фильтрами
│   └── results.py               # Результаты с деталями
└── api/
    ├── monthly_view.py          # API для месячного вида
    ├── day_view.py              # API для детальной страницы
    └── zerisearch.py            # API для Ze Ri
```

### 6.2 База данных — новые таблицы
```sql
-- Tung Shu base
CREATE TABLE t_tung_shu_daily (
    date DATE PRIMARY KEY,
    officer_number INT,       -- 1-12
    officer_name VARCHAR,
    constellation_id INT,     -- 28 Constellations
    belt_id INT,              -- Yellow & Black Belt
    dong_gong VARCHAR,
    black_rabbit VARCHAR,
    index_kp1 INT,
    index_3v1 INT,
    tung_shu_number INT       -- 1-12
);

-- XKDG Daily
CREATE TABLE t_xkdg_daily (
    date DATE PRIMARY KEY,
    upper_trigram_id INT,
    lower_trigram_id INT,
    hexagram_number INT,      -- 1-64
    gua_pair VARCHAR,
    tags JSONB                -- ["C10", "FG", "HT"]
);

-- XKDG Hourly Structures
CREATE TABLE t_xkdg_hourly (
    hour_id INT PRIMARY KEY,  -- FK to t_bazi_hourly
    structure_type VARCHAR,   -- "Combo of 5", "Combo of 10", "He Tu", "Pure Gua"
    focus_on VARCHAR,
    interaction VARCHAR       -- "Produce Out", "Control Out", etc.
);

-- Flying Stars
CREATE TABLE t_flying_stars (
    date DATE,
    star_type VARCHAR,        -- "Day", "Month", "Year"
    center_star INT,
    se_star INT, s_star INT, sw_star INT,
    e_star INT, w_star INT,
    ne_star INT, n_star INT, nw_star INT,
    PRIMARY KEY (date, star_type)
);

-- Symbolic Stars
CREATE TABLE t_symbolic_stars (
    date DATE,
    star_name VARCHAR,
    star_type VARCHAR,        -- "Good", "Bad", "Special"
    is_personalized BOOLEAN,
    PRIMARY KEY (date, star_name)
);

-- Day Scoring
CREATE TABLE t_day_score (
    date DATE,
    profile_id INT,           -- NULL for generic
    main_score INT,
    sub_score INT,
    personal_index INT,
    xkdg_family_pct INT,
    xkdg_total_pct INT,
    PRIMARY KEY (date, profile_id)
);

-- Activities
CREATE TABLE t_activity_recommendations (
    date DATE,
    activity_name VARCHAR,
    is_recommended BOOLEAN,
    reason VARCHAR,
    PRIMARY KEY (date, activity_name)
);
```

### 6.3 Frontend — React компоненты
```
src/components/tongshu/
├── MonthlyCalendar/
│   ├── CalendarGrid.tsx       # 7×N сетка
│   ├── DayCell.tsx            # Ячейка дня (Personal/Professional)
│   ├── TabBar.tsx             # Вкладки (QMDJ/XKDG/BaZi/etc.)
│   └── Navigation.tsx         # Месяц/год/сегодня
├── DayDetail/
│   ├── FourPillarsCard.tsx
│   ├── QmdjHourlyBlocks.tsx   # 12 блоков
│   ├── XkdgCard.tsx
│   ├── FlyingStarsGrid.tsx
│   ├── FengShuiMap.tsx
│   ├── ActivityList.tsx
│   └── SymbolicStarsList.tsx
├── Qmdj/
│   ├── QmdjChart.tsx          # 9-палатная карта
│   ├── QmdjControls.tsx       # Method/Type/Convention
│   └── QmdjInterpretation.tsx
├── BaZi/
│   ├── TenGodsTable.tsx
│   ├── LuckPillarsTable.tsx
│   └── DayMasterStrength.tsx
├── Scoring/
│   ├── DayScoreBadge.tsx
│   ├── ScoreBar.tsx
│   └── ColorCoding.tsx
└── ZeRi/
    ├── SearchForm.tsx         # 14 фильтров
    └── ResultsTable.tsx
```

---

## 7. План реализации (предварительный)

### Phase 1: Core Foundation (2-3 недели)
- [ ] Unified monthly calendar (7×N grid)
- [ ] Day cell with Four Pillars + Tung Shu number
- [ ] Color coding (favorable/unfavorable)
- [ ] Navigation (month/year/today)
- [ ] Basic QMDJ day ju (Zhi Run + Chai Bu)

### Phase 2: Personalization (2-3 недели)
- [ ] User profiles (DOB, gender, timezone)
- [ ] Ba Zi 10 Gods personalized
- [ ] Basic scoring (Main/Sub scores)
- [ ] Symbolic stars (6C, 3H, Int, PB, SH, Nob)

### Phase 3: Extended Data (3-4 недели)
- [ ] 28 Constellations
- [ ] Yellow & Black Belt
- [ ] 12 Officers system
- [ ] Na Yin interactions
- [ ] XKDG daily hexagrams
- [ ] Hourly QMDJ maps (12 blocks)

### Phase 4: Advanced (4-6 недель)
- [ ] Flying Stars
- [ ] Feng Shui daily maps
- [ ] XKDG hourly structures
- [ ] Belt system
- [ ] Day Stars (Good/Bad)
- [ ] Activity recommendations

### Phase 5: Ze Ri & Polish (3-4 недели)
- [ ] Ze Ri search engine
- [ ] 14 filters
- [ ] Results with details
- [ ] Export (PDF/Excel)
- [ ] Multi-language support

---

## 8. Ожидание 3-го сайта

После анализа 3-го сайта нужно будет:
1. Дополнить эту спецификацию новыми находками
2. Обновить сравнительную таблицу
3. Скорректировать приоритеты
4. Уточнить технические решения на основе ответов на вопросы Q1-Q12
5. Перейти к реализации Phase 1

---

## 9. Приложение: Словарь терминов

| Английский | 中文 | Русский | Описание |
|------------|------|---------|----------|
| Tung Shu | 通书 | Тун Шу | Китайский астрологический календарь |
| Four Pillars | 四柱 | Четыре столпа | Год, Месяц, День, Час |
| QMDJ | 奇门遁甲 | Ци Мэнь Дунь Цзя | Тайное сокрытие Цзя в вратах |
| Ba Zi | 八字 | Ба Цзы | Четыре столпа (8 символов) |
| XKDG | 玄空大卦 | Сюань Кун Да Гуа | Великие гексаграммы Тёмного Неба |
| Ze Ri | 择日 | Цэ Жи | Выбор благоприятной даты |
| 12 Officers | 十二值日星 | 12 служащих дня | 建除满平定执破危成收开闭 |
| 28 Constellations | 二十八宿 | 28 созвездий | Лунные мансионы |
| Na Yin | 纳音 | На Инь | Звук поглощения (60 комбинаций) |
| 10 Gods | 十神 | 10 богов | Персонажи Ба Цзы |
| Luck Pillars | 大运 | Да Юнь | Большие циклы (10×10 лет) |
| Flying Stars | 飞星 | Летящие звёзды | Сюань Кун Фэй Син |
| Ba Zhai | 八宅 | 8 домов/дворцов | 8 мансионов Фэн Шуй |
| 3 Victories | 三勝 | Три победы | Сан Шэн (太乙/天/生) |
