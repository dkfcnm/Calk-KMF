# ChineseMetasoft.com — Полный анализ Tong Shu и связанных модулей

## Дата анализа: 2026-05-22
## Учётная запись: dkfcnm3 (Dmitriy Shuvalov, DOB: 1987-04-23 16:02)

---

## 1. Общая структура навигации

### Главное меню (top bar)
- Home | Products | Da Liu Ren | Ba Zi | QMDJ | **Tong Shu** | Feng Shui | Ze Ri | 易 | ZWDS

### Tong Shu Monthly View
- Выбор месяца: January–December + 2027
- Вкладки данных: Na Yin | QMDJ | XKDG | XKDG 局 | Professional | 3 Victories | Ba Zi | Personal
- URL pattern: `/TongShu/Monthly?Type={Type}&Month={M}&Year={Y}&Day={D}`
- Параметр Day добавляется, но страница остаётся месячной (нет детальной страницы дня)

---

## 2. Personal View (персонализированный календарь)

### Данные в ячейке дня (пример: 1 May 2026 — 乙亥)
```
乙 Wood    ☶ 3    1
亥 Pig     ☶ 3
-63 (-10)
*
8 - Danger
Ba Zi: Output (HO)
Na Yin: Companion
XKDG Day: Control Out
6C (D), 3H (Y), Nob (Y)
```

### Поля данных:
| Поле | Описание | Пример |
|------|----------|--------|
| Day number | Число месяца | 1 |
| Stem | Небесный ствол + элемент | 乙 Wood |
| Branch | Земная ветвь + животное | 亥 Pig |
| Main score | Основной балл (возможно, композитный) | -63 |
| Sub-score | Дополнительный балл | (-10) |
| Tung Shu | Номер + название | 8 - Danger |
| Ba Zi 10 God | Бог дня для Day Master | Output (HO) |
| Na Yin | Взаимодействие Na Yin | Companion |
| XKDG Day | Взаимодействие XKDG | Control Out |
| Symbolic stars | Символические звёзды | 6C (D), 3H (Y), Nob (Y) |

### Легенда символических звёзд:
- 6C — Six Combo (六合)
- 3H — Three Harmony (三合)
- Int — Intelligence (文昌)
- PB — Peach Blossom (桃花)
- SH — Sky Horse (驿马)
- Nob — Nobleman (天乙贵人)

### Цветовая кодировка ячеек:
- Зелёный: благоприятные дни
- Жёлтый: нейтральные
- Белый: обычные
- Красный/оранжевый: неблагоприятные

---

## 3. QMDJ View (ежемесячный)

### Данные в ячейке дня:
```
乙 Wood    亥 Pig
Chai Bu: 8 Yang
Zhi Run: 8 Yang
[符 生 天]
SW  S  S
```

### Поля:
- Chai Bu: число + Yin/Yang
- Zhi Run: число + Yin/Yang
- Мини-карта 3×3 (符, 生, 天) + направления (SW, S, N, SE, E, W, NW, NE)

### Особые дни:
- Li Xia (立夏): 5 May 2026, 14:19
- Xiao Man (小满): 21 May 2026, 03:07

---

## 4. Ba Zi View (ежемесячный)

### Данные в ячейке дня:
```
乙 Wood    ☶ 3    1
亥 Pig     ☶ 3
🔴          🌊
-63 (-10)   8 - Danger
Ba Zi: Output (HO)
Na Yin: Companion
XKDG Day: Control Out
```

### Дополнительно:
- Числовые показатели стихий (красные/жёлтые/серые/синие/зелёные блоки)
- Возможно, представление силы 5 элементов в виде мини-графика

---

## 5. XKDG View (Xuan Kong Da Gua)

### Данные в ячейке дня:
```
乙 Wood    亥 Pig
Wood 木    ☶ 3
           ☶ 3
35 - Advancement
Pi-Tai
JiJi-WeiJi
```

### Поля:
- Верхняя и нижняя триграммы с числами
- Номер и название гексаграммы (1-64)
- Пары гуа (Pi-Tai, JiJi-WeiJi, Kan-Li, Zhen-Xun, Qian-Kun, Gen-Dui, Heng-Yi, Sun-Xian)

### Легенда тегов:
- FG — Family Gua
- HT — He Tu
- C5 — Combo of 5
- C10 — Combo of 10
- C15 — Combo of 15
- PG — Pure Gua
- 1St — One Star
- K — Kindred
- SG — Same Group

---

## 6. XKDG 局 View (Xuan Kong Da Gua Structures)

### Почасовые структуры (двухчасовые блоки):
```
1-3: Combo of 5
3-5: Family Gua
5-7: Combo of 10
7-9: Family Gua
9-11: Combo of 10
11-13: Combo of 10
13-15: He Tu
15-17: Combo of 10
17-19: Family Gua
19-21: Combo of 10
21-23: Combo of 5
23-24: Combo of 5
```

**Ключевое открытие**: XKDG 局 показывает почасовые структуры! Это означает, что календарь содержит почасовые данные, но только для XKDG.

---

## 7. Professional View

### Самая насыщенная вкладка:
```
丁 Fire    ☶ 4    3
丑 Ox      ☶ 7    xx
-180 (-10)
10 - Receive
Ba Zi: Wealth (DW)
Na Yin: Officer
XKDG Day: Same
BR: Moon    8
Ju
```

### Поля:
- Stem/Branch + числа (верхнее/нижнее)
- Коды: xx, ***, x, **
- Основной балл / суб-балл
- Tung Shu число + название
- Ba Zi 10 God
- Na Yin взаимодействие
- XKDG Day взаимодействие
- BR (Branch Related): Moon, Sun, Water, Fire, Metal, Black, Earth, Scarlet
- Ju (局) — QMDJ ju?

### Легенда (левый блок):
- HV — Heavenly Virtue
- MBen — Monthly Benevolence
- Est — Earthly Storage
- WSt — Wealth Storage
- EWth — Earth Wealth
- AS — Advancement Star
- MWC — Monthly Virtue Combo
- MVN — Monthly Virtue Noble
- HOf — Heavenly Officer
- MBr — Month Breaker
- YBr — Year Breaker
- 10S — Ten Spiritual Days
- M3K — Month 3 Killings
- Y3K — Year 3 Killings

### Дополнительные данные:
- DG/KP1: число / число
- 28 C: название созвездия (Willow, Ghost, Carriage, etc.)
- Belt: цвет/тип (Red Phoenix, Golden Lock, Black Tortoise, etc.)

---

## 8. 3 Victories View (三勝)

### Данные в ячейке дня:
```
乙 Wood    亥 Pig
Light (符): S*
[符 生 天]
SW  S  S
```

### Поля:
- Light (符): направление + модификатор (*)
- Power (符): направление
- Blessing (天): направление + модификатор (*)
- Force (生): направление
- Мини-карта 3×3 с иероглифами и направлениями

---

## 9. Na Yin View

### Данные в ячейке дня:
```
乙 Wood    亥 Pig
山頭火
Fire from the mountain
8 - Danger
```

### Поля:
- Na Yin иероглифы
- Na Yin перевод
- Цветной индикатор (треугольник)
- Tung Shu число + название
- Код дня: xx, x, ***, **

---

## 10. Ze Ri (择日) — Date Selection Tool

### Фильтры поиска:
| Категория | Опции |
|-----------|-------|
| 12 Officers | All, Good, Establish, Remove, Full, ... |
| Dong Gong | All, Good, ***, **, * |
| Index KP1 | All, 0, 10, 20, 30, ... |
| 28 Constellations | All, Good, cte (color-based) |
| Yellow & Black Belt | All, Good, Green Dragon, Bright Hall, H. Punishment, ... |
| Na Yin | All, Wood, Earth, Water, Fire, Metal |
| Stars | All, Avoid1, AbundantFortune, Advancement Star, ... |
| Week Day | All, Monday, Tuesday, ... |
| Day Stem | All, Jia, Yi, Bing, Ding, ... |
| Day Branch | All, Zi, Chou, Yin, Mao, ... |
| Person (DOB) | Date not selected / профили |
| Ba Zi | All, bzst1-bzst4 |
| Pi1 | All, 60+, 50+, 40+, 30+, ... |
| Star | All, ThreeHarmony, SixCombo, SixComboFull, Nobleman, ... |

### Диапазон дат: From / To

### Результаты (по 20 на страницу):
| Колонка | Содержимое |
|---------|------------|
| Date | День недели, число, месяц, год |
| Day Basic Info | 4 столпа (иероглифы), Officer, DG/KP1, 28 C, Belt, Na Yin |
| Day Stars (Good) | Auspicious Army, Civilian Day, Heavenly Wealth, Important Noble, ... |
| Day Stars (Bad) | Five Ghost, Heavenly Depression, Heavenly Fire, Heavenly Jail, ... |
| Day Special Info | Ten Spiritual Days, Fire Star Day, Sha Days, ... |
| Xuan Kong Da Gua | Гексаграмма + почасовые структуры |

### Кнопка Chart для каждого дня — возможно, открывает детальную страницу

---

## 11. QMDJ Chart (детальная почасовая страница)

### URL: `/QiMenDunJia/Chart`

### Настройки:
| Параметр | Опции |
|----------|-------|
| Date | YYYY-MM-DD |
| Local Time | Hour (0-23), Minutes (0-59) |
| Chart Type | Hour, Day, Month, Year, Annual Forecast, Destiny, Five Charms - Day |
| Method | Chai Bu, Zhi Run, Lunar |

### Four Pillars (текущий расчёт):
- Hour, Day, Month, Year столпы с цветовой кодировкой
- Hidden Stems, Jie Qi, Na Yin, Stars

### QMDJ Карта (9 дворцов):
- Structure: Yang 5
- Lead Stem, Envoy, Lead Star
- 28 Constellations
- Jia hides behind (Hour/Day)
- Sky Horse, Death & Emptiness, Nobleman
- 3 Victories: Heavenly Yi, Heaven, Life
- Palaces: Internal/External
- Day clash, Hour clash

### Таблицы интерпретаций:
1. **Structure** — структуры для каждого дворца с описаниями
2. **Stems Formation** — комбинации стволов
3. **Extra Stems Formation** — дополнительные комбинации
4. **Strategy** — стратегии (36 стратагем?)

### Convention: "This chart is plotted by using: Convention 2"

---

## 12. Ba Zi Chart (детальная страница)

### URL: `/BaZi/Chart`

### Типы анализа:
- Standard, Fortune, Year, Minute, 8P, 2 Charts

### Four Pillars + Conception + Life Palace:
- Stem, Branch, Hidden Stems, Jie Qi, Na Yin, Stars, Relations
- Hexagram (гексаграмма Ицзин)
- Group, Out of Gua, Family, Stratagem

### 10 Aspects (10 Gods):
- Friend, Hurting Officer, Rob Wealth, Seven Killing, Indirect Wealth, Direct Officer, Eating God, Indirect Resources, Direct Resources, Direct Wealth
- Chinese Name, Stem, Joseph Yu / Ken Lai scores, Strength bar

### Ba Zi Analysis:
- Chart Id, Day Master, Nobleman, Intelligence, Sky Horse, Peach Blossom, Solitary, Heavenly Doctor, Illness Star, Death & Emptiness
- Regulating Useful God, He Luo Li Shu
- Season, Day Master Strength (50/50 bar)
- Five Factors pie chart

### Ba Zhai - 8 Mansions:
- Gua Number, Life Star, Group
- Favorable/Unfavorable Directions

### QMDJ Palace of Destiny:
- Palace, Life Stem, Star, Door, Guardian, Stems Combo

### Luck Pillars (大运):
- 10 столбцов (возраст 5-95)
- Каждый: Stem, Branch, Hidden Stems, Na Yin, Stars, Relations, Hexagram

---

## 13. Сравнение с mingli.ru

| Функция | mingli.ru | chinesemetasoft.com |
|---------|-----------|---------------------|
| **Авторизация** | Email + пароль | Email + пароль |
| **Персонализация** | Да (профиль с ДРТ) | Да (профиль с ДРТ) |
| **Месячный вид** | 7×N сетка | 7×N сетка |
| **Почасовые данные** | 12 блоков (23:00–01:00 etc.) | Только в QMDJ Chart |
| **Tung Shu** | Да (числа + названия) | Да (числа + названия) |
| **Ba Zi** | 4 столпа + 10 Gods | 4 столпа + 10 Gods + Hidden Stems + Na Yin + Stars |
| **QMDJ** | Мини-карты (Zhi Run) | Chai Bu / Zhi Run / Lunar |
| **XKDG** | Нет | Да (гексаграммы + структуры) |
| **Na Yin** | Нет | Да (отдельная вкладка) |
| **Professional** | Flying Stars, Sha, 24 mountains | HV, MBen, 28 Constellations, Belts |
| **3 Victories** | Нет | Да (Light, Power, Blessing, Force) |
| **Ze Ri** | Нет | Да (расширенный поиск с фильтрами) |
| **Ba Zhai** | Нет | Да (8 Mansions) |
| **Luck Pillars** | Нет | Да (10 периодов) |
| **Настройки** | SystemType, ChartType, Ghost mode, UTC | Method (ChaiBu/ZhiRun/Lunar), Convention |
| **Языки** | Русский | 18+ языков |
| **Интерпретации** | Минимальные | Очень подробные (QMDJ структуры, стратегии) |
| **Scoring** | Нет явного | Да (-63 (-10), 145 (10) и т.д.) |
| **Цветовая кодировка** | Да | Да (зелёный/жёлтый/красный) |

---

## 14. Ключевые находки для Calk_KMF

### A. Персонализация и скоринг
- chinesemetasoft.com использует **композитный скоринг** для дней
- Скоринг учитывает: Ba Zi 10 Gods, Na Yin, XKDG, символические звёзды
- Нужно исследовать алгоритм скоринга

### B. Почасовые данные
- **mingli.ru**: 12 двухчасовых блоков с QMDJ картами для каждого дня
- **chinesemetasoft.com**: Почасовые данные только в QMDJ Chart (интерактивный инструмент) и XKDG 局 (структуры по часам)
- **Calk_KMF**: Уже имеет t_bazi_hourly (355K строк) — можно показывать почасовые данные

### C. Методы расчёта QMDJ
- **mingli.ru**: Zhi Run / Chai Bu
- **chinesemetasoft.com**: Chai Bu / Zhi Run / Lunar
- **Calk_KMF**: Пока только Zhi Run (классический)

### D. Дополнительные модули
- **28 Constellations** (二十八宿) — Professional view
- **Yellow & Black Belt** (黃黑道) — Professional view
- **12 Officers** (十二值日星) — Ze Ri
- **Ba Zhai** (八宅) — Ba Zi Chart
- **Luck Pillars** (大運) — Ba Zi Chart
- **36 Stratagems** (三十六計) — QMDJ Chart

### E. URL Patterns
```
/TongShu/Monthly?Type=Personal&Month=5&Year=2026
/TongShu/Monthly?Type=QiMenDunJia&Month=5&Year=2026
/TongShu/Monthly?Type=BaZi&Month=5&Year=2026
/TongShu/Monthly?Type=XuanKongDaGua&Month=5&Year=2026
/TongShu/Monthly?Type=XuanKongDaGuaStructures&Month=5&Year=2026
/TongShu/Monthly?Type=Professional&Month=5&Year=2026
/TongShu/Monthly?Type=Qmdj3V&Month=5&Year=2026
/TongShu/Monthly?Type=NaYin&Month=5&Year=2026

/QiMenDunJia/Chart
/BaZi/Chart
/ZeRi/TongShu
/ZeRi/TongShuSearch
```

---

## 15. Рекомендации для Unified Portal

### Приоритет 1 (Core):
1. Месячный календарь 7×N с day cells
2. Four Pillars для каждого дня
3. Tung Shu numbers (1-12)
4. QMDJ daily ju (Yin/Yang + number)
5. Ba Zi 10 Gods (персонализированно)
6. Na Yin interactions
7. Цветовая кодировка (благоприятность)

### Приоритет 2 (Extended):
8. Почасовые QMDJ карты (12 блоков)
9. XKDG daily hexagrams
10. Symbolic stars (6C, 3H, Int, PB, SH, Nob)
11. Professional view (28 Constellations, Belts, 12 Officers)
12. 3 Victories (Light, Power, Blessing, Force)

### Приоритет 3 (Advanced):
13. Ze Ri — поиск благоприятных дат с фильтрами
14. QMDJ Chart (интерактивный, почасовой)
15. Ba Zi Chart (с Luck Pillars, 10 Gods scores)
16. XKDG 局 (почасовые структуры)
17. Ba Zhai (8 Mansions)
18. Detailed interpretations (структуры, стратегии)

### Приоритет 4 (Integration):
19. Пользовательские профили (DOB, пол, часовой пояс)
20. Скоринговая система (композитный балл)
21. Экспорт данных (PDF, Excel)
22. API для интеграции
