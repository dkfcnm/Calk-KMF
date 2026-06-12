# Unified Tong Shu Portal Specification v0.2
## Объединённая спецификация на основе анализа mingli.ru + chinesemetasoft.com + bazi-calculator.com

**Дата:** 2026-05-23  
**Версия:** 0.2 (post-3rd-site analysis)  
**Проект:** Calk_KMF v2.3.1

---

## 1. Общая архитектура трёх порталов

### 1.1 mingli.ru
- **Тип:** Тунг Шу календарь + QMDJ
- **Авторизация:** Email + пароль
- **Структура:** Месячный календарь → Детальная страница дня → 12 почасовых блоков
- **Язык:** Русский
- **Настройки:** SystemType (Zhi Run/Chai Bu), Chart Type (4), Ghost mode (3), UTC

### 1.2 chinesemetasoft.com (CMS)
- **Тип:** Полный комплекс (Tong Shu + QMDJ + Ba Zi + XKDG + Feng Shui + ZWDS)
- **Авторизация:** Email + пароль
- **Структура:** Месячный календарь (8 вкладок) + Детальная страница дня + Ze Ri + QMDJ/Ba Zi Charts
- **Язык:** 18+ языков
- **Настройки:** Method (ChaiBu/ZhiRun/Lunar), Convention 2, Chart Type (Hour/Day/Month/Year/Destiny)

### 1.3 bazi-calculator.com (BaziCalc)
- **Тип:** Ba Zi калькулятор + XKDG выбор даты + Tong Shu + Flying Stars
- **Авторизация:** Email + пароль (Премиум аккаунт)
- **Структура:** Карта рождения + Обзор дня/месяца/года/10 лет/100 лет + XKDG Date Selection + Compact view
- **Язык:** Русский, English
- **Настройки:** Режим Новикок/Передовой, GMT+3, долгота

---

## 2. Расширенный сравнительный анализ (3 сайта)

### 2.1 Месячный календарь

| Функция | mingli.ru | CMS | BaziCalc | Примечание |
|---------|-----------|-----|----------|------------|
| Сетка 7×N | ✅ | ✅ | ✅ | Все три |
| Навигация по месяцам | ✅ | ✅ | ✅ | Все три |
| Day Stem + Branch | ✅ | ✅ | ✅ | Все три |
| 10 God (персонализированный) | ✅ | ✅ | ✅ | Все три |
| Na Yin | ⚠️ | ✅ | ✅ | mingli косвенно |
| Tung Shu (12 Officers) | ✅ | ✅ | ✅ | Все три |
| 28 Constellations | ❌ | ✅ | ✅ | CMS + BaziCalc |
| Symbolic stars | ✅ (6C,3H,Int,PB,SH,Nob) | ✅ (расширенный) | ✅ (расширенный) | BaziCalc: Jue/Extinction, etc. |
| Hour blocks в месяце | ❌ | ❌ | ❌ | Только в деталях |
| Цветовая кодировка | ✅ | ✅ | ✅ | Все три |

### 2.2 Детальная страница дня

| Функция | mingli.ru | CMS | BaziCalc | Примечание |
|---------|-----------|-----|----------|------------|
| Four Pillars | ✅ | ✅ | ✅ | Все три |
| 12 Hour blocks | ✅ | ✅ | ✅ | Все три |
| Hour Stem/Branch/10 God | ✅ | ✅ | ✅ | Все три |
| Hour Na Yin | ❌ | ❌ | ✅ | Только BaziCalc |
| Hour Hexagram (I Ching) | ❌ | ✅ (XKDG) | ✅ (XKDG Date Sel.) | CMS + BaziCalc |
| QMDJ карты по часам | ✅ | ✅ | ❌ | mingli + CMS |
| Flying Stars | ❌ | ✅ | ✅ | CMS + BaziCalc |
| Feng Shui maps | ❌ | ✅ | ✅ (Flying Stars круги) | CMS + BaziCalc |
| Hexagrams for pillars | ❌ | ✅ | ✅ | CMS + BaziCalc |
| Activity recommendations | ❌ | ✅ | ❌ | Только CMS |
| XKDG structures | ❌ | ✅ | ✅ | CMS + BaziCalc |
| Belt system | ❌ | ✅ | ❌ | Только CMS |

### 2.3 QMDJ (奇门遁甲)

| Функция | mingli.ru | CMS | BaziCalc | Примечание |
|---------|-----------|-----|----------|------------|
| Методы | Zhi Run / Chai Bu | Chai Bu / Zhi Run / Lunar | ❌ | mingli + CMS |
| Типы карт | Hour/Day | Hour/Day/Month/Year/Destiny | ❌ | CMS лидер |
| Размещение (layout) | 4 типа | Convention 2 | ❌ | mingli лидер |
| Ghost mode | 3 варианта | — | ❌ | Только mingli |
| Мини-карты в месяце | ✅ | ✅ | ❌ | mingli + CMS |
| Полные карты 9 дворцов | ✅ | ✅ | ❌ | mingli + CMS |
| Интерпретации структур | ❌ | ✅ | ❌ | Только CMS |
| 3 Victories (三勝) | ❌ | ✅ | ❌ | Только CMS |

### 2.4 Ba Zi (八字)

| Функция | mingli.ru | CMS | BaziCalc | Примечание |
|---------|-----------|-----|----------|------------|
| Four Pillars | ✅ | ✅ | ✅ | Все три |
| 10 Gods | ✅ | ✅ | ✅ | Все три |
| Hidden Stems | ✅ | ✅ | ✅ | Все три |
| Na Yin | ⚠️ | ✅ | ✅ | Все три |
| Luck Pillars (大运) | ❌ | ✅ | ✅ | CMS + BaziCalc |
| Day Master Strength | ❌ | ✅ | ✅ (в 10 Gods) | CMS + BaziCalc |
| Ba Zhai (八宅) | ❌ | ✅ | ❌ | Только CMS |
| QMDJ Palace of Destiny | ❌ | ✅ | ❌ | Только CMS |
| 10 Aspects scoring | ❌ | ✅ | ❌ | Только CMS |

### 2.5 Xuan Kong Da Gua (玄空大卦)

| Функция | mingli.ru | CMS | BaziCalc | Примечание |
|---------|-----------|-----|----------|------------|
| Гексаграммы дня | ❌ | ✅ | ✅ | CMS + BaziCalc |
| Пары гуа | ❌ | ✅ | ✅ | CMS + BaziCalc |
| Теги (C5, C10, FG, HT) | ❌ | ✅ | ❌ | Только CMS |
| Почасовые структуры | ❌ | ✅ | ✅ (Date Sel.) | CMS + BaziCalc |
| Дневные XKDG блоки | ❌ | ✅ | ❌ | Только CMS |
| **XKDG Date Selection (Рейтинг)** | ❌ | ❌ | ✅ | **Только BaziCalc** |
| **Hourly hexagram compatibility** | ❌ | ❌ | ✅ | **Только BaziCalc** |

### 2.6 Flying Stars (玄空飞星)

| Функция | mingli.ru | CMS | BaziCalc | Примечание |
|---------|-----------|-----|----------|------------|
| Day/Month/Year Charts | ❌ | ✅ (9-grid) | ✅ (9-grid + круги) | CMS + BaziCalc |
| Hour Flying Stars | ❌ | ❌ | ✅ (круговые диаграммы) | **Только BaziCalc** |
| Tai Sui / Sui Po / San Sha | ❌ | ⚠️ (в Feng Shui) | ✅ (с градусами) | **BaziCalc лидер** |
| Yellow 5 / Center Star | ❌ | ⚠️ | ✅ | BaziCalc |
| Great Sun Formula | ❌ | ❌ | ✅ | **Только BaziCalc** |

### 2.7 Ze Ri / Date Selection (择日)

| Функция | mingli.ru | CMS | BaziCalc | Примечание |
|---------|-----------|-----|----------|------------|
| Поиск благоприятных дат | ❌ | ✅ (14 фильтров) | ✅ (XKDG рейтинг) | CMS + BaziCalc |
| Персонализация поиска | ❌ | ✅ | ✅ | CMS + BaziCalc |
| Фильтры | ❌ | 14 шт. | XKDG-based | Разные подходы |
| Результаты с деталями | ❌ | ✅ | ✅ | CMS + BaziCalc |
| Hour compatibility within day | ❌ | ❌ | ✅ | **Только BaziCalc** |

### 2.8 Tong Shu (通书)

| Функция | mingli.ru | CMS | BaziCalc | Примечание |
|---------|-----------|-----|----------|------------|
| 12 Officers (值日星) | ✅ | ✅ | ✅ | Все три |
| 28 Constellations | ❌ | ✅ | ✅ | CMS + BaziCalc |
| Yellow & Black Belt | ❌ | ✅ | ❌ | Только CMS |
| Dong Gong | ❌ | ✅ | ❌ | Только CMS |
| Black Rabbit | ❌ | ✅ | ❌ | Только CMS |
| Index KP1/3v1 | ❌ | ✅ | ❌ | Только CMS |
| **Tung Shu detailed descriptions** | ⚠️ | ⚠️ | ✅ (расширенные) | **BaziCalc лидер** |
| **Solar term exact times** | ❌ | ✅ | ✅ (с GMT) | CMS + BaziCalc |
| **Moon phases** | ❌ | ✅ | ✅ (полнолуние/новолуние) | CMS + BaziCalc |
| **Lunar date** | ❌ | ✅ | ❌ | Только CMS |

---

## 3. Уникальные находки bazi-calculator.com

### 3.1 XKDG Date Selection (Сюанькун Дагуа - Выбор даты)
Это **самый продвинутый** инструмент выбора даты среди трёх сайтов:

**Рейтинг дня (Day Rating):**
- Сравнение Birth Chart vs Selected Date по 7+ критериям:
  - Год поддерживает День ✅/❌
  - Месяц поддерживает День ✅/❌
  - Час поддерживает День ✅/❌
  - Столкновение ветвей ✅/❌
  - Сань-ша (Цзэ-ша) ⚠️
- **Итоговый вердикт**: "День благоприятный" / "День не благоприятный"

**Выбор часа в течении Дня:**
- 12 двухчасовых блоков
- Для каждого: Stem + Branch + 10 God + Hexagram (верх/низ) + Number + Name
- Галочка/крестик (благоприятен/неблагоприятен)
- Конфликты указаны (например: Ri Po)

**Сань-Ци (Три мистика):**
- Даты: 9.04, 19.04, 29.04
- Только для часов Синь

### 3.2 Flying Stars — круговые диаграммы
- **Уникально**: Hour/Day/Month/Year/Combined круговые диаграммы с направлениями (N, S, E, W, NE, SE, SW, NW)
- 9-палатные сетки для каждого уровня
- Комбинированная диаграмма: День+Месяц+Год+Сань-ша

### 3.3 Tai Sui / Sui Po / San Sha / Yellow 5
- **Уникально**: Точные градусы направлений!
  - Тайсуй (Tai Sui): 15°, W
  - Суйпо (Sui Po): 15°, E
  - Желтая пятерка (Yellow 5): 45°, E
  - Сань-ша (San Sha): 75°, NE
  - У Цзи (Wu Ji): 45°, W
- Это данные для Feng Shui/Date Selection

### 3.4 Great Sun Formula
- **Уникально**: Применение Great Sun Formula к текущему solar term
- Указывает благоприятные направления для ремонта дома
- House facing + active mountain

### 3.5 Tong Shu Descriptions
- **Уникально**: Расширенные описания для каждого 12 Officer и 28 Constellation:
  - Благоприятно для: ...
  - Неблагоприятно для: ...
- Пример (8. Вэй - Опасность):
  - Благоприятно: быть счастливым, распития вина, медитации, религиозных обрядов
  - Неблагоприятно: беды, опасность несчастных случаев
- Пример (28. Кан - Ше):
  - Благоприятно: освобождения заключенных, сельскохозяйственных работ, покупки крупнорогатого скота
  - Неблагоприятно: семейных советов, заключения брака, похорон, инвестиций

### 3.6 Moon Phases
- **Уникально**: Точные даты и время полнолуния и новолуния с GMT
- Полнолуние: 2026-05-01 20:24 GMT+3
- Новолуние: 2026-04-17 14:54, 2026-05-16 23:03 GMT+3

### 3.7 Compact View (Обзор 10 лет)
- 10-летние столбы (Luck Pillars) в компактной таблице
- Годовые столпы с 2017 по 2026
- 10-летний цикл удачи с детальными столпами

---

## 4. Полный перечень показателей (обновлённый v0.2)

### 4.1 Новые категории (от BaziCalc)

**XKDG Date Selection Rating:**
- Year supports Day ✅/❌
- Month supports Day ✅/❌
- Hour supports Day ✅/❌
- Branch Clash (Столкновение ветвей) ✅/❌
- San Sha (Сань-ша / Цзэ-ша) ⚠️
- Overall verdict: Favorable / Unfavorable

**Hourly Hexagram Compatibility:**
- Each of 12 hour blocks: Stem + Branch + Hexagram + Compatibility check
- Conflicts marked (e.g., Ri Po)

**Flying Stars Circular Diagrams:**
- Hour, Day, Month, Year, Combined
- Directions with degrees (N=0°, S=180°, E=90°, W=270°)
- 9-palace grids

**Feng Shui Directions (degrees):**
- Tai Sui: 15°
- Sui Po: 15°
- Yellow 5: 45°
- San Sha: 75°
- Center Flying Star: 45°
- Wu Ji: 45°

**Great Sun Formula:**
- Active solar term
- House facing directions (active for renovation)
- Active mountain
- Combinations (e.g., SW1, NW3)

**Moon Phases:**
- Full Moon exact datetime (GMT)
- New Moon exact datetime (GMT)

**San Qi (三奇):**
- Special dates (human mystic)
- Restricted to specific hour stems

---

## 5. Что уже реализовано в Calk_KMF (текущее состояние v0.2)

### ✅ Реализовано:
1. **t_bazi_hourly** (355K rows): Four Pillars для каждого часа 1900-2100
2. **t_qumen_dgiren_hourly/monthly/daily**: QMDJ Zhi Run (классический)
3. **t_qumen_chauby_hourly/monthly/daily**: QMDJ Chai Bu
4. **spr_jiazi_extended**: 6 ju columns
5. **spr_solar_term**: Solar terms для ju calculation
6. **t_solar_term_time**: Exact crossing times
7. **pillar calculation**: calc_day_pillar с 子时 rollover

### ⚠️ Частично:
8. **Hour QMDJ**: 68.2% match (классический принят)
9. **Day QMDJ**: 2.8% match (ожидаемо)
10. **Flying Stars**: таблица есть, но не проверена
11. **10 Gods**: есть логика, но не интегрирована в календарь

### ❌ Не реализовано (обновлённый список):
12. 28 Constellations
13. Yellow & Black Belt
14. 12 Officers (Tung Shu numbers есть, но не как система с описаниями)
15. XKDG (гексаграммы, структуры, рейтинг)
16. Ba Zhai (八宅)
17. Luck Pillars (大运)
18. Ze Ri / XKDG Date Selection
19. Belt system
20. Day Stars (Good/Bad)
21. Activity recommendations
22. Feng Shui daily maps + directions (degrees)
23. Hexagrams for pillars
24. 3 Victories
25. QMDJ interpretations/structures/strategies
26. Personalization (user profiles)
27. Lunar date conversion
28. Moon phase data
29. Great Sun Formula
30. San Qi (三奇)
31. Flying Stars circular diagrams
32. Tai Sui / Sui Po / San Sha / Yellow 5
33. Scoring system

---

## 6. Открытые вопросы (v0.2 — обновлённые после 3-го сайта)

### Q1. Приоритеты реализации
> **Какой функционал приоритетен для первого релиза?**
> - Вариант A: Core (месячный календарь + Four Pillars + QMDJ + Tung Shu)
> - Вариант B: Extended (Core + Ba Zi 10 Gods + Na Yin + Symbolic Stars + 28 Constellations)
> - Вариант C: Professional (Extended + XKDG + Flying Stars + Feng Shui + Ze Ri)

### Q2. QMDJ методология
> **Какие методы поддерживать?**
> - Zhi Run ✅ (есть)
> - Chai Bu ✅ (есть)
> - Lunar — что это? Нужно исследовать

### Q3. Персонализация
> **Нужна ли регистрация пользователей?**
> - Все 3 сайта требуют авторизации для персонализированных данных
> - Без авторизации — generic календарь?

### Q4. XKDG Date Selection
> **Нужен ли XKDG рейтинг дней (как в BaziCalc)?**
> - Сравнение Birth Chart vs Date по Year/Month/Hour/Clash
> - Это отдельный сложный модуль

### Q5. Flying Stars визуализация
> **Как отображать Flying Stars?**
> - Вариант A: 9-палатные сетки (как CMS + BaziCalc)
> - Вариант B: Круговые диаграммы (как BaziCalc)
> - Вариант C: Оба

### Q6. Feng Shui направления
> **Нужны ли точные градусы направлений (Tai Sui, Sui Po, San Sha, Yellow 5)?**
> - BaziCalc показывает: 15°, 45°, 75° и т.д.
> - Это Feng Shui модуль

### Q7. Tong Shu описания
> **Нужны ли расширенные описания для 12 Officers и 28 Constellations?**
> - BaziCalc: подробно что благоприятно/неблагоприятно
> - mingli/CMS: минимально

### Q8. Hourly Hexagrams
> **Нужны ли гексаграммы Ицзин для каждого часового блока?**
> - BaziCalc: 12 hexagrams per day in XKDG Date Selection
> - CMS: hexagrams for pillars in day detail

### Q9. Scoring
> **Какую систему скоринга использовать?**
> - CMS: Personal Index, KP1/3v1, XKDG %
> - BaziCalc: XKDG Date Selection Rating (✅/❌)
> - Создать свою или комбинировать?

### Q10. Интеграция модулей
> **Как unified portal взаимодействует с существующими модулями Calk_KMF?**
> - Ba Zi, QMDJ, Calendar — уже есть
> - Feng Shui, Tai Yi — есть ли?

### Q11-Q12. Технические (без изменений)

---

## 7. Рекомендуемая архитектура v0.2

### 7.1 Обновлённая модульная структура

```
unified_portal/
├── core/
│   ├── monthly_calendar.py
│   ├── day_detail.py
│   ├── four_pillars.py
│   └── tung_shu.py              # + описания Officers/Constellations
├── qmdj/
│   ├── day_chart.py
│   ├── hour_chart.py
│   ├── interactive_chart.py
│   └── interpretations.py
├── bazi/
│   ├── ten_gods.py
│   ├── luck_pillars.py
│   ├── day_master_strength.py
│   └── ba_zhai.py
├── xkdg/
│   ├── daily_hexagram.py
│   ├── hourly_structures.py
│   ├── daily_blocks.py
│   └── date_selection.py        # НОВОЕ: XKDG Date Selection Rating
├── feng_shui/
│   ├── flying_stars.py          # + круговые диаграммы
│   ├── daily_map.py
│   ├── directions.py            # НОВОЕ: Tai Sui, Sui Po, San Sha, Yellow 5
│   └── great_sun_formula.py     # НОВОЕ
├── tong_shu/
│   ├── officers_12.py           # + описания
│   ├── constellations_28.py     # + описания
│   ├── belt_system.py
│   ├── day_stars.py
│   ├── special_days.py
│   ├── moon_phases.py           # НОВОЕ
│   └── solar_term_details.py    # НОВОЕ
├── zeri/
│   ├── search_engine.py
│   ├── xkdg_rating.py           # НОВОЕ
│   └── results.py
└── api/
    ├── monthly_view.py
    ├── day_view.py
    └── zeri_search.py
```

### 7.2 Новые таблицы БД (дополнение к v0.1)

```sql
-- XKDG Date Selection Rating
CREATE TABLE t_xkdg_date_rating (
    date DATE,
    profile_id INT,
    year_supports_day BOOLEAN,
    month_supports_day BOOLEAN,
    hour_supports_day BOOLEAN,
    branch_clash VARCHAR,
    san_sha VARCHAR,
    is_favorable BOOLEAN,
    PRIMARY KEY (date, profile_id)
);

-- Hourly Hexagram Compatibility
CREATE TABLE t_hourly_hexagram (
    hour_id INT PRIMARY KEY,  -- FK to t_bazi_hourly
    upper_trigram_id INT,
    lower_trigram_id INT,
    hexagram_number INT,
    is_favorable BOOLEAN,
    conflict_type VARCHAR
);

-- Flying Stars Circular
CREATE TABLE t_flying_stars_circular (
    date DATE,
    star_type VARCHAR,  -- "Hour", "Day", "Month", "Year", "Combined"
    direction_degrees JSONB,  -- {"N": 0, "NE": 45, ...}
    PRIMARY KEY (date, star_type)
);

-- Feng Shui Directions
CREATE TABLE t_feng_shui_directions (
    date DATE PRIMARY KEY,
    tai_sui_dir VARCHAR,
    tai_sui_deg INT,
    sui_po_dir VARCHAR,
    sui_po_deg INT,
    san_sha_dir VARCHAR,
    san_sha_deg INT,
    yellow_5_dir VARCHAR,
    yellow_5_deg INT,
    center_star_dir VARCHAR,
    center_star_deg INT
);

-- Great Sun Formula
CREATE TABLE t_great_sun_formula (
    solar_term_id INT PRIMARY KEY,
    active_facing_dirs JSONB,
    active_mountain VARCHAR,
    combinations JSONB
);

-- Moon Phases
CREATE TABLE t_moon_phases (
    date DATE PRIMARY KEY,
    phase_type VARCHAR,  -- "Full", "New", "First Quarter", "Last Quarter"
    phase_datetime TIMESTAMP,
    phase_datetime_gmt TIMESTAMP
);

-- 12 Officers Descriptions
CREATE TABLE spr_officer_descriptions (
    officer_number INT PRIMARY KEY,
    officer_name_ru VARCHAR,
    officer_name_en VARCHAR,
    officer_name_zh VARCHAR,
    favorable_for TEXT,
    unfavorable_for TEXT
);

-- 28 Constellations Descriptions
CREATE TABLE spr_constellation_descriptions (
    constellation_id INT PRIMARY KEY,
    constellation_name_ru VARCHAR,
    constellation_name_en VARCHAR,
    constellation_name_zh VARCHAR,
    element VARCHAR,
    favorable_for TEXT,
    unfavorable_for TEXT
);

-- San Qi (三奇)
CREATE TABLE t_san_qi (
    date DATE PRIMARY KEY,
    qi_type VARCHAR,  -- "Human", "Heaven", "Earth"
    valid_hour_stems JSONB
);
```

---

## 8. Обновлённый план реализации

### Phase 1: Core Foundation (2-3 недели)
- [ ] Unified monthly calendar (7×N grid)
- [ ] Day cell: Four Pillars + 10 God + Tung Shu number + Na Yin
- [ ] Color coding
- [ ] Navigation (month/year/today)
- [ ] Basic QMDJ day ju (Zhi Run + Chai Bu)

### Phase 2: Personalization (2-3 недели)
- [ ] User profiles (DOB, gender, timezone)
- [ ] Ba Zi 10 Gods personalized
- [ ] Basic symbolic stars (6C, 3H, Int, PB, SH, Nob)
- [ ] 28 Constellations

### Phase 3: Extended Data (3-4 недели)
- [ ] 12 Officers system + descriptions
- [ ] Hourly QMDJ maps (12 blocks)
- [ ] XKDG daily hexagrams
- [ ] Flying Stars (9-grid)
- [ ] Moon phases

### Phase 4: Advanced (4-6 недель)
- [ ] XKDG Date Selection Rating
- [ ] Hourly hexagrams compatibility
- [ ] Feng Shui directions (Tai Sui, Sui Po, San Sha, Yellow 5)
- [ ] Flying Stars circular diagrams
- [ ] Great Sun Formula
- [ ] Activity recommendations

### Phase 5: Ze Ri & Polish (3-4 недели)
- [ ] Ze Ri search engine (14 filters + XKDG rating)
- [ ] Results with details
- [ ] Export (PDF/Excel)
- [ ] Multi-language support

---

## 9. Сравнительная таблица: Топ-фичи каждого сайта

| Ранг | Сайт | Топ-фича | Уникальность |
|------|------|----------|-------------|
| 1 | mingli.ru | QMDJ с 4 layout + Ghost mode | Только здесь |
| 2 | CMS | Ze Ri с 14 фильтрами | Только здесь |
| 3 | CMS | QMDJ интерпретации + стратегии | Только здесь |
| 4 | CMS | Ba Zhai (八宅) | Только здесь |
| 5 | CMS | 3 Victories (三勝) | Только здесь |
| 6 | BaziCalc | XKDG Date Selection Rating | Только здесь |
| 7 | BaziCalc | Hourly hexagram compatibility | Только здесь |
| 8 | BaziCalc | Flying Stars circular diagrams | Только здесь |
| 9 | BaziCalc | Tai Sui/Sui Po/San Sha/Yellow 5 degrees | Только здесь |
| 10 | BaziCalc | Great Sun Formula | Только здесь |
| 11 | BaziCalc | Tong Shu detailed descriptions | Лучшие описания |
| 12 | BaziCalc | 10-year luck cycle compact view | Только здесь |
| 13 | mingli | Hourly QMDJ mini-maps in month view | Удобно |
| 14 | CMS | 8 data tabs in month view | Богатство |
| 15 | CMS | 18 languages | Масштаб |

---

## 10. Следующие шаги

1. **Пользователь отвечает на вопросы Q1-Q10**
2. **Финализируем спецификацию v1.0**
3. **Приступаем к реализации Phase 1 (Core Foundation)**
4. **Параллельно: наполнение БД** (12 Officers descriptions, 28 Constellations, etc.)
