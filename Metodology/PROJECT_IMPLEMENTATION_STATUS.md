# Calk_KMF — Полный статус реализации

**Версия:** 2.8.0  
**Дата обновления:** 2026-06-12  
**Статус:** Активная разработка (Phase 1+2+5.5–5.7+5.13–5.18+7.11+Stage 6+Stage 7+Phase 8 выполнены)

---

## 1. Общая информация

**Название:** Calk_KMF — Unified Tong Shu Portal  
**Цель:** Персонализированный календарь китайской метафизики, объединяющий лучшие функции аналогичных сайтов (mingli.ru, chinesemetasoft.com, bazi-calculator.com)  
**Режим:** Professional (полный набор функций)  
**Язык интерфейса:** Русский (EN, ZH — бэклог)  
**Диапазон дат:** 1900–2100 (из БД)

---

## 2. Обзор проекта и текущее состояние

### 2.1. Основные достижения
✅ **Полностью функциональный календарь Бацзы** с расширенными методологиями  
✅ **Две системы Ци Мэнь** (Чжи Рэн и Чай Бу) с оптимизированными шаблонами  
✅ **Летящие звёзды** с корректным учетом солнечных сезонов  
✅ **Тай И Шен Шу** — дневные и часовые расклады  
✅ **Rule Engine** для анализа с 174 правилами  
✅ **Исправлен алгоритм Черного Кролика** (версия Joey Yap) — полная верификация  
✅ **Высокая производительность** обработки данных  
✅ **MCP интеграция** — настроен MCP сервер PostgreSQL для IDE  
✅ **Phase 1 — Tong Shu Foundation** (2026-05-23): Полная реализация базового календаря Тунг Шу с Four Pillars, 12 Officers, 28 Constellations, Na Yin, Yellow/Black Belt, Moon Phase  
✅ **Phase 5.13** (2026-05-30): Полный цикл пересчёта и тестирования всех модулей  
✅ **Phase 5.14** (2026-05-31): Реализация рекомендаций по оптимизации, наведение порядка в методологии
✅ **Stage 5.17** (2026-05-31): Полный цикл пересчёта и тестирования (регрессия) — все тесты passed
✅ **Stage 5.18** (2026-05-31): Синхронизация Шэнь Ша с PostgreSQL — `spr_shensha_config` (49 звёзд), `symbolic_stars` в UI (TongShuPage day/week/month views), управление в Справочниках
✅ **Phase 2 — Personalization** (2026-05-31): Расчёт birth chart, город+timezone autocomplete, персонализированные 10 Богов/фазы Ци, скрытые стволы, отображение в UI
✅ **Stage 5.5** (2026-05-31): Тестирование React компонентов — 6 suites, 21/21 passed
✅ **Stage 5.6** (2026-05-31): Бенчмарки — API 14–24ms, TongShuDay 3.5ms, PostgreSQL <1ms/query
✅ **Stage 5.7** (2026-05-31): OpenAPI документация — 50 endpoints
✅ **Task 7.11** (2026-05-31): UI Debug IDs — покрытие HomePage, QiMenPage, CrmPage
✅ **Stage 6** (2026-05-31): Расширение дневного представления — hourly slots (12 двухчасовых периодов, сворачиваемые), Black Rabbit (Joey Yap), lunar month, compact Flying Stars (summary line Г/М/Д + сетка без часовых звёзд)
✅ **Stage 7** (2026-06-02): Qi Men полный редизайн — QimenGridV2 с цветовым кодированием дворцов по стихиям/направлениям, рамка с 12 ветвями (животные + время), русские названия и пиньинь для всех элементов, QimenSummaryPanel (сезон, час, декада, главная звезда/врата, 8 триграмм), PalaceExtendedInfo с 100 stem combos и сезонной силой, PostgreSQL-only backend, 5 новых вкладок в Справочниках
✅ **Phase 8** (2026-06-05): Полный переход на PostgreSQL-only — API сервисы (refs.py, tongshu_daily_service.py, personalized_service.py) переведены на SQLAlchemy, удалён SQLite fallback из logger.py и db_config.py, тесты переписаны на PostgreSQL, архивированы 50+ SQLite-зависимых скриптов. Созданы/синхронизированы недостающие таблицы в PostgreSQL: spr_day_officer_value, spr_tongshu_constellation, spr_tongshu_constellation_cycle, spr_great_sun_mountain, spr_qimen_gates, spr_qimen_spirits, spr_qimen_stars, spr_ri_jia. Добавлена колонка dagua_family в spr_jiazi_extended и icon_svg в spr_tongshu_black_rabbit_star. Исправлены placeholders TongShuDay (? → %s) для pg8000. Все тесты проходят: Python 38/38, React 32/32, build успешен.
✅ **GitHub Publication** (2026-06-12): Проект опубликован на GitHub в публичном репозитории `dkfcnm/Calk-KMF`. Создан первый коммит с 349 файлами и детальным описанием. Настроен `.gitignore`, `.gitmessage` (шаблон коммита), `docs/commit-guidelines.md`. Обновлены `CHANGELOG.md`, `PROJECT.md`, `Metodology/bz.md`, `Metodology/tests_master_plan.md`, `Metodology/journal.log`.
✅ **GitHub Release v2.8.0** (2026-06-12): Создан первый релиз на GitHub https://github.com/dkfcnm/Calk-KMF/releases/tag/v2.8.0.
✅ **GitHub Actions** (2026-06-12): Создан workflow `.github/workflows/commit-message-check.yml` и его шаблон сохранён в `docs/github-actions-commit-message-check.yml`. Push в `.github/workflows/` требует Personal Access Token с scope `workflow` (см. `Metodology/bz.md`, Ошибка 28).

### 2.2. Техническая архитектура

#### База данных
- **СУБД:** PostgreSQL 18
- **Размер:** ~5.5 ГБ
- **Таблиц:** 81 (35 расчётных, 43 справочника, 3 служебные)
- **SQL Views:** 35+
- **Драйвер:** pg8000 (Pure Python)
- **MCP сервер:** `@modelcontextprotocol/server-postgres` для интеграции с IDE

#### Основные модули
```
code/
├── common/          # Общие утилиты, DBManager, Config
├── bazi_calendar/   # Расчет Бацзы календаря (Refactored for PG)
├── qimen/          # Ци Мэнь Дунь Цзя (Чжи Рэн, Чай Бу)
├── feng_shui/      # Летящие звезды
├── analysis/       # Rule Engine для анализа
├── calendar/       # Модуль синхронизации с Яндекс Календарем (CalDAV)
├── taiyi/          # Тай И Шен Шу
├── tongshu/        # Тунг Шу календарь (Phase 1 completed)
├── profiles/       # Управление профилями пользователей (заготовка)
├── tests/          # Регрессионные тесты
└── utils/          # Утилиты миграции и отладки
```

#### Данные
- **Период:** 2025-2027 гг.
- **Часовые пояса:** UTC-12 ... UTC+14
- **Записей:** ~355K в t_bazi_hourly, ~3.2M в t_qumen_dgiren_hourly
- **Шаблоны Ци Мэнь:** 1080 уникальных карт

---

## 3. База данных — Детальный статус

### 3.1. Общая статистика

| Параметр | Значение |
|----------|----------|
| Таблиц всего | 100 |
| Справочников (spr_*) | 60 |
| Расчётных таблиц (t_*) | 38 |
| SQL Views | 35+ |
| Размер SQLite | ~5.3 ГБ |
| Период данных | 2025–2027 |
| Часовые пояса | UTC-12 … UTC+14 |
| Записей t_bazi_hourly | ~355K |
| Записей t_qumen_dgiren_hourly | ~3.2M |

### 3.2. Ключевые справочники (наполненные)

| Таблица | Назначение | Записей | Статус |
|---------|------------|---------|--------|
| `spr_heavenly_stem` | 10 Небесных Стволов | 10 | ✅ |
| `spr_earthly_branch` | 12 Земных Ветвей | 12 | ✅ |
| `spr_solar_term` | 24 солнечных сезона | 24 | ✅ |
| `spr_pillar_cycle` | 60 Цзя-Цзы | 60 | ✅ |
| `spr_pillar_month_rule` | Правила месячного столпа | 120 | ✅ |
| `spr_pillar_hour_rule` | Правила часового столпа | 120 | ✅ |
| `spr_jiazi_extended` | Расширенный Цзя-Цзы (Наинь, Да Гуа, Цзюй) | 60 | ✅ |
| `spr_day_officer_mapping` | 12 Офицеров дня | 144 | ✅ |
| `spr_day_officer_value` | Значения офицеров | 12 | ✅ |
| `spr_tongshu_constellation` | 28 созвездий | 28 | ✅ |
| `spr_tongshu_constellation_cycle` | Цикл созвездий по месяцам | 336 | ✅ |
| `spr_yellow_black_matrix` | Матрица Жёлтого/Чёрного пути | 144 | ✅ |
| `spr_yellow_black_stars` | 12 звёзд Ж/Ч пути | 12 | ✅ |
| `spr_tongshu_phase` | 12 фаз Ци | 12 | ✅ |
| `spr_tongshu_phase_mapping` | Маппинг фаз Ци (10×12) | 120 | ✅ |
| `spr_tongshu_ten_god` | 10 Богов (10×10) | 100 | ✅ |
| `spr_tongshu_branch_combo_rule` | Комбинации Земных Ветвей | 39 | ✅ |
| `spr_tongshu_stem_combo_rule` | Комбинации Небесных Стволов | 9 | ✅ |
| `spr_tongshu_shensha_rule` | Символические звёзды (神煞) — правила расчёта | 281 | ✅ |
| `spr_shensha_config` | Настройки символических звёзд (интерпретация, цвет, флаг) | 49 | ✅ |
| `spr_black_rabbit_matrix` | Чёрный Кролик (матрица) | 1800 | ✅ |
| `spr_black_rabbit_scores` | Оценки Чёрного Кролика | 9 | ✅ |
| `spr_flying_star_map` | Карта Летящих Звёзд | — | ✅ |
| `spr_qimen_templates` | Шаблоны Ци Мэнь | 1080 | ✅ |
| `spr_qimen_stem_combos` | 100 комбинаций стволов Ци Мэнь | 100 | ✅ |
| `spr_qimen_trigrams` | Триграммы Ба Гуа | 8 | ✅ |
| `spr_taiyi_stars` | Звёзды Тай И | 9 | ✅ |
| `spr_taiyi_gates` | Врата Тай И | 8 | ✅ |
| `spr_taiyi_spirits` | Духи ХХД | 12 | ✅ |
| `spr_taiyi_jianchu` | 建除 Тай И | 12 | ✅ |
| `spr_taiyi_noble` | Благородные часы Тай И | — | ✅ |
| `spr_taiyi_kong_wang` | Кун Ван Тай И | — | ✅ |
| `spr_master_dano_mapping` | Мастер Дано | — | ✅ |
| `spr_indicator` | Индикаторы анализа | — | ✅ |
| `spr_indicator_value` | Значения индикаторов | — | ✅ |
| `spr_analysis_scope` | Области применения | — | ✅ |
| `spr_skdg_wuxing_relation` | Отношения У-Син СКДГ | 16 | ✅ |
| `spr_skdg_hexagram_pairs` | Пары гексаграмм СКДГ | 904 | ✅ |

### 3.3. Ключевые расчётные таблицы (наполненные)

| Таблица | Назначение | Записей | Статус |
|---------|------------|---------|--------|
| `t_bazi_hourly` | Часовые столпы Бацзы | ~355K | ✅ |
| `t_solar_term_time` | Время солнечных сезонов | ~4800 | ✅ |
| `t_solar_term_time_hko` | Эталонные данные HKO | ~4800 | ✅ |
| `t_time_grid_hourly` | Сетка двухчасовых слотов | — | ✅ |
| `t_qumen_chauby_day` | Ци Мень Чай Бу (дневные) | — | ✅ |
| `t_qumen_chauby_hourly` | Ци Мень Чай Бу (часовые) | — | ✅ |
| `t_qumen_dgiren_day` | Ци Мень Чжи Рэнь (дневные) | — | ✅ |
| `t_qumen_dgiren_hourly` | Ци Мень Чжи Рэнь (часовые) | ~3.2M | ✅ |
| `t_qumen_dgiren_month` | Ци Мень Чжи Рэнь (месячные) | — | ✅ |
| `t_qumen_dgiren_year` | Ци Мень Чжи Рэнь (годовые) | — | ✅ |
| `t_flying_stars` | Летящие звёзды | — | ✅ |
| `t_taiyi_day` | Тай И (дневные, 9 дворцов) | ~3285 | ✅ |
| `t_taiyi_hours` | Тай И (часовые) | — | ✅ |
| `t_analysis_year/month/day/hour` | Результаты Rule Engine | — | ✅ |
| `t_rule_registry` | Реестр правил | 174+ | ✅ |
| `t_rule_scope` | Области правил | — | ✅ |

---

## 4. Backend — Реализованные модули

### 4.1 Бацзы Календарь (`code/bazi_calendar/`)

| Компонент | Описание | Статус |
|-----------|----------|--------|
| `BaziEngine` | Основной движок расчёта | ✅ |
| Four Pillars | Год, Месяц, День, Час | ✅ |
| Solar Terms | 24 сезона с астрономической точностью | ✅ |
| HKO Overrides | Эталонные данные Гонконгской обсерватории | ✅ |
| Lunar Calendar | Лунный месяц/день (включая leap) | ✅ |
| Na Yin | 60 комбинаций Наинь | ✅ |
| Hour Slots | Двухчасовые слоты по всем часовым поясам | ✅ |
| Day Officer Value ID | Расчёт ID офицера дня | ✅ |

### 4.2 Тунг Шу (`code/tongshu/`)

| Компонент | Описание | Статус |
|-----------|----------|--------|
| `TongShuDay` | Центральный класс агрегации данных дня | ✅ |
| Four Pillars | Загрузка из t_bazi_hourly | ✅ |
| Solar Term | Название сезона | ✅ |
| Na Yin (per pillar) | Наинь для года, месяца, дня | ✅ |
| Da Gua Metadata | Период и элемент для каждого столпа | ✅ |
| Hexagram Family Check | Проверка одной семьи гексаграмм | ✅ |
| Production Chain | Цепочка порождения Наинь | ✅ |
| Lunar Day | Лунный день | ✅ |
| 12 Officers | Дневные офицеры (建除十二直) | ✅ |
| 28 Constellations | 二十八宿 | ✅ |
| Belt System | Жёлтый/Чёрный путь (黃黑道) | ✅ |
| Moon Phase | Фаза луны (упрощённо) | ✅ |
| Tong Shu Phase | Фазы Ци по дневному стволу | ✅ |
| **10 Gods** | Персонализированные 10 богов | ✅ *(2026-05-30)* |
| **Qi Phases** | 12 фаз Ци для каждого столпа | ✅ *(2026-05-30)* |
| **Symbolic Stars** | Символические звёзды (神煞) | ✅ *(2026-05-30)* |
| **Combinations** | Столкновения, слияния, гармонии, наказания, разрушения, вреда | ✅ *(2026-05-30)* |

### 4.3 Ци Мэнь Дунь Цзя (`code/qimen/`)

| Компонент | Описание | Статус |
|-----------|----------|--------|
| Чжи Рэнь (Zhi Run) | Годовые, месячные, дневные, часовые расклады | ✅ |
| Чай Бу (Chai Bu) | Часовые расклады | ✅ |
| Шаблоны | 1080 уникальных карт | ✅ |
| Ri Jia | Методология для дневных раскладов | ✅ |
| 符头 | Классический метод расчёта | ✅ |
| Ju Columns | upper/middle/lower × yang/yin в spr_jiazi_extended | ✅ |

### 4.4 Летящие Звёзды (`code/feng_shui/`)

| Компонент | Описание | Статус |
|-----------|----------|--------|
| Периоды | Год, Месяц, День, Час | ✅ |
| 9 дворцов | Соответствующие звёзды | ✅ |
| Сезоны | Корректный расчёт относительно Ли Чунь | ✅ |

### 4.5 Тай И Шен Шу (`code/taiyi/`)

| Компонент | Описание | Статус |
|-----------|----------|--------|
| Дневные расклады | 9 дворцов × 365 дней | ✅ |
| Итоговый балл | `(gate*2 + star*2 + jianchu + xi_shen + noble) * (1 - kong_wang)` | ✅ |
| Часовые данные | 12 духов ХХД, благородные, Кун Ван | ✅ |

### 4.6 Rule Engine (`code/analysis/`)

| Компонент | Описание | Статус |
|-----------|----------|--------|
| `AnalysisEngine` | Базовый движок правил | ✅ |
| `RuleEngine` | Оптимизированный движок с индексацией | ✅ |
| Predicates | Реестр предикатов | ✅ |
| 174 правил | Активные правила в t_rule_registry | ✅ |
| Скоринг | Динамический расчёт score | ✅ |

### 4.7 Чёрный Кролик (`code/analysis/black_rabbit_logic.py`)

| Компонент | Описание | Статус |
|-----------|----------|--------|
| Алгоритм Joey Yap | Линейная формула с полярностью ствола | ✅ |
| Матрица | jiazi_id × lunar_day → звезда | ✅ |
| Верификация | Сверка с эталоном (фев, июл, окт 2026) | ✅ |

---

## 5. Frontend — Реализованные компоненты

### 5.1 TongShu / MonthlyCalendar

| Компонент | Описание | Статус |
|-----------|----------|--------|
| `TongShuPage.tsx` | Основная страница Тунг Шу | ✅ |
| `CalendarGrid.tsx` | Сетка месячного календаря | ✅ |
| `DayCell.tsx` | Ячейка дня (столпы, лунный день, индикаторы) | ✅ |
| `TabBar.tsx` | Переключение режимов (день/неделя/месяц/год) | ✅ |
| `Navigation.tsx` | Навигация по месяцам | ✅ |

### 5.2 TongShu / DayDetail

| Компонент | Описание | Статус |
|-----------|----------|--------|
| `FourPillarsCard.tsx` | Карточка 4 столпов | ✅ |
| `HourlyBlocks.tsx` | 12 двухчасовых блоков | ✅ |
| `XkdgCard.tsx` | СКДГ карточка | ⬜ Заготовка |
| `FlyingStarsGrid.tsx` | Сетка Летящих Звёзд (3×3, compact mode) | ✅ |
| `FengShuiMap.tsx` | Карта Фэн Шуй | ⬜ Заготовка |
| `SymbolicStarsList.tsx` | Список символических звёзд | ⬜ Заготовка |
| `HourlySlots.tsx` | 12 двухчасовых слотов (collapsed/expandable) | ✅ (Stage 6) |

### 5.3 Qi Men Page

| Компонент | Описание | Статус |
|-----------|----------|--------|
| `QimenGridV2.js` | 3×3 сетка с цветовым кодированием, рамка 12 ветвей | ✅ (Stage 7) |
| `QimenSummaryPanel.js` | Левая панель: сезон, час, декада, звезда/врата, триграммы | ✅ (Stage 7) |
| `PalaceExtendedInfo.js` | Детали дворца: 100 combos, сезонная сила | ✅ (Stage 7) |
| `QiMenPage.js` | Табы Час/День/Месяц/Год, DatePicker, методология | ✅ (Stage 7) |

### 5.3 TongShu / ZeRi (Зе Ри)

| Компонент | Описание | Статус |
|-----------|----------|--------|
| `SearchForm.tsx` | Форма поиска благоприятных дат | ⬜ Заготовка |
| `ResultsTable.tsx` | Таблица результатов поиска | ⬜ Заготовка |

### 5.4 TongShu / Export

| Компонент | Описание | Статус |
|-----------|----------|--------|
| `PdfExport.tsx` | Экспорт в PDF | ⬜ Заготовка |
| `ExcelExport.tsx` | Экспорт в Excel | ⬜ Заготовка |

### 5.5 UI Debug System (Phase 7)

| Компонент | Описание | Статус |
|-----------|----------|--------|
| ElementIdMarker | Знак ¡ (U+00A1) в верхнем правом углу | ✅ |
| Копирование | Клик по ¡ копирует ID в буфер | ✅ |
| Администратор | Раздел включения/отключения отображения | ✅ |

---

## 6. API Endpoints

### 6.1 Работающие (200 OK)

| Endpoint | Описание |
|----------|----------|
| `GET /` | Root |
| `GET /api/tongshu/daily/day` | Данные дня (SQLite fallback) |
| `GET /api/tongshu/daily/month` | Данные месяца |
| `GET /api/tongshu/daily/week` | Данные недели |
| `GET /api/tongshu/daily/year` | Данные года |
| `GET /api/refs/heavenly-stems` | 10 Небесных Стволов |
| `GET /api/refs/earthly-branches` | 12 Земных Ветвей |
| `GET /api/refs/officers` | 12 Офицеров |
| `GET /api/refs/constellations` | 28 созвездий |
| `GET /api/refs/belt-stars` | 12 звёзд Ж/Ч пути |
| `GET /api/refs/black-rabbit-stars` | 9 звёзд Чёрного Кролика |
| `GET /api/refs/elements` | 5 элементов |
| `GET /api/profiles` | Список профилей |
| `GET /api/crm/clients/` | CRM клиенты |

### 6.2 Известные проблемы

| Endpoint | Статус | Причина |
|----------|--------|---------|
| `GET /api/qimen/charts/zhirun` | ✅ 200 | Исправлено: PostgreSQL fallback |
| `GET /api/qimen/current/zhirun` | ✅ 200 | Расчёт через QimenEngine |
| `GET /api/qimen/levels/{method}` | ✅ 200 | Все уровни за дату |
| `GET /api/qimen/hourly/{method}` | ✅ 200 | 12 часовых раскладов |
| `GET /api/qimen/daily/{method}` | ✅ 200 | Дневной расклад |
| `GET /api/qimen/monthly/{method}` | ✅ 200 | Месячный расклад |
| `GET /api/qimen/yearly/{method}` | ✅ 200 | Годовой расклад |
| `GET /api/qimen/references/stars` | ✅ 200 | 9 звёзд |
| `GET /api/qimen/references/gates` | ✅ 200 | 8 врат |
| `GET /api/qimen/references/spirits` | ✅ 200 | 8 духов |
| `GET /api/qimen/references/stem_combos` | ✅ 200 | 100 комбинаций |
| `GET /api/qimen/references/trigrams` | ✅ 200 | 8 триграмм |
| `GET /api/fengshui/current` | ✅ 200 | Реализовано |
| `GET /api/taiyi/current` | 501 | Not Implemented |
| `GET /api/bazi/chart` | 501 | Not Implemented |

---

## 7. Тесты

### 7.1 Python тесты

| Файл | Тестов | Статус |
|------|--------|--------|
| `test_tongshu_day_extended.py` | 7 | ✅ 7/7 passed |
| `test_api_endpoints_http.py` | 21 | ✅ 21/21 passed |
| `test_analysis_qimen.py` | — | ✅ Актуален |
| `control_data.py` | — | ✅ Актуален |
| `test_reference_data.py` | 7 | ✅ 7/7 passed |
| `test_combinations.py` | 3 | ✅ 3/3 passed |
| `test_symbolic_stars.py` | 3 | ✅ 3/3 passed |
| `test_ten_gods.py` | 3 | ✅ 3/3 passed |
| `test_qi_phases.py` | 3 | ✅ 3/3 passed |
| **ИТОГО Python** | **70** | **✅ 70/70 passed** |

### 7.2 React тесты

| Файл | Компонент | Статус |
|------|-----------|--------|
| `CalendarGrid.test.js` | MonthlyCalendar | ✅ 8/8 passed |
| `ElementIdMarker.test.js` | UI Debug IDs | ✅ 2/2 passed |
| `QiMenPage.test.js` | QiMenPage: tabs, levels, palace click | ✅ 6/6 passed |
| `QimenGridV2.test.js` | QimenGridV2: rendering, palace cells | ✅ 4/4 passed |
| **Все React тесты** | — | ✅ 32/32 passed |

---

## 8. Инфраструктура

| Компонент | Описание | Статус |
|-----------|----------|--------|
| `DB_Start.bat` | Запуск PostgreSQL | ✅ |
| `DB_Stop.bat` | Остановка PostgreSQL | ✅ |
| `DB_backup.bat` | Бэкап БД | ✅ |
| `start_app.bat` | Запуск приложения | ✅ |
| `stop_app.bat` | Остановка приложения | ✅ |
| `start_portal.bat` | Запуск портала (PG + FE) | ✅ |
| `stop_portal.bat` | Остановка портала | ✅ |
| MCP Server | Интеграция PostgreSQL с IDE | ✅ |
| `.env` / `.env.example` | Конфигурация окружения | ✅ |
| GitHub repository | Публичный репозиторий `dkfcnm/Calk-KMF` | ✅ |
| `.gitignore` | Исключение лишних файлов из репозитория | ✅ |
| `.gitmessage` | Шаблон детального коммита | ✅ |
| `docs/commit-guidelines.md` | Правила ведения журнала изменений | ✅ |

---

## 9. Методологии — Реализованные расчёты

### 9.1 Что анализируется для даты (TongShuDay)

| Показатель | Подробности |
|------------|-------------|
| Four Pillars (四柱) | Год, Месяц, День, Час + ствол/ветвь отдельно |
| Solar Term (节气) | 24 сезона с точным временем наступления |
| Na Yin (纳音) | Элемент и название для каждого столпа |
| Da Gua (玄空大卦) | Period, Element Number, Family |
| Hexagram Family | Проверка одной семьи (年-月-日) |
| Production Chain | Цепочка порождения Наинь |
| Lunar Day | Лунный день (1-30) + лунный месяц |
| 12 Officers (十二值日星) | 建除十二直 с категорией благоприятности |
| 28 Constellations (二十八宿) | Название, направление, природа |
| Belt System (黃黑道) | Жёлтый/Чёрный путь + звёзды |
| Moon Phase | Фаза + % видимости |
| Tong Shu Phase | 五离 / 九空 |
| **10 Gods (十神)** | Год, Месяц, День, Час относительно Day Master |
| **Qi Phases (十二长生)** | Рождение, Купание, Пик, Смерть и т.д. |
| **Symbolic Stars (神煞)** | Благородный человек, Академик, Персик, Лошадь, Генерал, Искусства, Ангел смерти, Три ша, Одинокая планета, Красный луань, Куйган и др. |
| **Black Rabbit** | Joey Yap / Wu Tu Ze Ri Fa — ежедневная звезда |
| **Combinations (冲合刑害破)** | Столкновения, Слияния, Гармонии, Наказания, Разрушения, Вред, Сезоны |

### 9.2 Методологии Ци Мэнь

| Система | Уровни | Статус |
|---------|--------|--------|
| Чжи Рэнь (Zhi Run) | Год, Месяц, День, Час | ✅ |
| Чай Бу (Chai Bu) | Час | ✅ |
| Шаблоны | 1080 карт | ✅ |

### 9.3 Методологии Тай И

| Компонент | Статус |
|-----------|--------|
| Дневные расклады (9 дворцов) | ✅ |
| Итоговый балл дня | ✅ |
| Часовые духи ХХД | ✅ |
| Благородные часы | ✅ |
| Кун Ван | ✅ |

---

## 10. Бэклог — Что НЕ реализовано

### 10.1 Phase 2 — Personalization ✅

| Этап | Описание | Статус |
|------|----------|--------|
| 2.2 | Автоматический расчёт временной поправки по городу | ✅ |
| 2.3 | Сохранение 8 столпов в профиле | ✅ |
| 2.4 | Персонализированный 10 God (UI) | ✅ |
| 2.5 | Hidden Stems (藏干) | ✅ |
| 2.6 | Symbolic Stars UI (6C, 3H, Int, PB, SH, Nob) | ✅ |
| 2.7 | Настройки отображения | ✅ |

### 10.2 Phase 3 — Extended

| Этап | Описание | Статус |
|------|----------|--------|
| 3.4 | Flying Stars 9-grid | ✅ |
| 3.5 | Feng Shui направления | ✅ |
| 3.6 | Moon Phases (точные) | ✅ |
| 3.7 | Great Sun Formula | ✅ |
| 3.8 | San Qi (三奇) | ✅ |

### 10.3 Phase 4 — Advanced

| Этап | Описание | Статус |
|------|----------|--------|
| 4.1 | Ze Ri search engine | ⬜ |
| 4.2 | XKDG Date Selection Rating | ⬜ |
| 4.3 | Hourly Hexagrams (I Ching) | ⬜ |
| 4.4 | Activity Recommendations | ⬜ |
| 4.5 | Подробные описания | ⬜ |

### 10.4 Phase 5 — Polish

| Этап | Описание | Статус |
|------|----------|--------|
| 5.1 | PDF экспорт | ⬜ |
| 5.2 | Excel экспорт | ⬜ |
| 5.5 | Тестирование React компонентов | ✅ |
| 5.6 | Проверка производительности | ✅ |
| 5.7 | Финальная документация API | ✅ |
| 5.6 | Проверка производительности | ⬜ |
| 5.7 | Финальная документация API | ⬜ |

### 10.5 Phase 7 — UI Debug

| Этап | Описание | Статус |
|------|----------|--------|
| 7.11 | Тестирование ¡ на всех страницах | ✅ |

---

## 11. Журнал ключевых изменений (Project Journal — сводка)

### 2026-05-31: Stage 3.4+3.5 — Flying Stars 9-grid + Feng Shui направления
- Рассчитаны Летящие Звёзды: 3.2M строк в `t_flying_stars` (62.5 сек)
- API: реализованы `/api/fengshui/chart`, `/api/fengshui/current`, `/api/fengshui/directions`
- Frontend: создан `FlyingStarsGrid.js` — 3×3 сетка 9 дворцов с годовой/месячной/дневной/часовой звёздами
- Интеграция: Flying Stars отображаются на дневном виде TongShuPage
- Тесты: React 13/13 passed (3 suites), API 21/21 passed

### 2026-05-31: Stage 6 — Расширение дневного представления
- **Hourly slots:** API `/api/tongshu/hours/{date_str}` — 12 слотов с ten_god, qi_phase, hidden_stems, symbolic_stars
- **Black Rabbit:** Колонки `black_rabbit_star`, `black_rabbit_score`, `lunar_month` добавлены в `t_tung_shu_daily` (SQLite + PostgreSQL), заполнены для 365 дней 2026
- **UI:** TongShuPage day view — hourly table (collapsed/expandable), Black Rabbit chip, lunar month, compact Flying Stars (summary line + grid без hour_star)
- **FlyingStarsGrid:** `compact` prop — скрывает hour_star chips и меняет легенду
- **Тесты:** Python 48/48 passed, React 21/21 passed, build successful

### 2026-05-31: Stage 5.17 — Полный цикл пересчёта и тестирования
- Python: API 21/21, TongShuDay 7/7, reference, combos, symbolic stars, ten gods, qi phases, analysis qimen — all passed
- React: 10/10 passed (2 suites)
- PostgreSQL: 98 таблиц, соединение стабильно
- Зафиксированы проблемы: pytest конфликт с `code/__init__.py` (решение: запуск через `python` из /tmp с PYTHONPATH)

### 2026-05-31: Stage 5.15 — Консолидация документации
- **Создан единый справочник Тунг Шу:** `reference_tongshu_methodologies.md` (12 файлов объединены)
- **Создан единый справочник Бацзы:** `reference_bazi_calendar.md` (4 файла объединены)
- **Создан единый справочник Ци Мэнь:** `reference_qimen.md` (3 файла объединены)
- **Архивировано:** 22 файла в `Metodology/archive/` и `archive/research/`
- **Сокращён:** `00_project_architecture_v2.md` (убраны дубли)
- **Обновлён:** `tests_master_plan.md` (добавлен раздел UI Debug Tests + примечание по запуску)
- **Обновлён:** `Metodology/README.md` (единый индекс с правилом обновления)

### 2026-05-31: Stage 5.14 — Оптимизация и стабилизация
- **SQLAlchemy 2.0 fix:** `text()` в `qimen_service.py` и `crm_service.py`
- **CRM API:** Исправлена ошибка 500 → `200 OK`
- **Bazi Calendar:** Исправлены параметры `year_start`/`year_end`
- **Rule Engine:** Исправлен SQL (убраны `hexagram_num`/`hexagram_name`)
- **Новый скрипт:** `sync_bazi_hourly_to_postgres.py` (CSV+psql COPY, ~25s для 354K rows)
- **Тесты:** Python 47/47, React 10/10, API 21/21 passed
- **Metodology cleanup:** 7 файлов архивированы в `Metodology/archive/`

### 2026-05-30: Stage 5.13 — Полный цикл пересчёта
- Бацзы, Ци Мень, Летящие звёзды, Тай И — пересчитаны и протестированы
- Справочники синхронизированы: shensha (281), ten_god (100), phase (120), combos (48)
- Новые тесты: `test_reference_data.py`, `test_combinations.py`, `test_symbolic_stars.py`, `test_ten_gods.py`, `test_qi_phases.py`

### 2026-05-24: Переработка карточек дней + UI Debug System
- Расширена `t_tung_shu_daily` (15 новых колонок)
- Переработан `CalendarGrid.js` с отображением столпов Бацзы
- Обновлены bat-файлы запуска портала
- UI Debug System: знак ¡ для всех элементов

### 2026-05-16: Верификация Ци Мень Чжи Жень + MCP
- Настроен `@modelcontextprotocol/server-postgres`
- Добавлены ju колонки в `spr_jiazi_extended`
- Исправлен расчет `curr_date` для hourly chart (UTC → LOCAL)
- Верификация против `Smart Tablica 2026`: 68.2% совпадение (классическая методология признана корректной)

### 2026-02-28: Модуль синхронизации с Яндекс Календарём
- CalDAV протокол, библиотека `caldav`
- Генерация событий из Бацзы-данных (753 события)
- Идемпотентность подтверждена

### 2026-02-09: Реализация правил СКДГ
- 20 правил оценки дат по методу Сюань Кун Да Гуа
- Справочники: `spr_skdg_wuxing_relation` (16), `spr_skdg_hexagram_pairs` (904)
- Результаты: 672K строк (hour-level), 5.7K строк (day-level)

### 2026-02-17: Исправление Чёрного Кролика
- Алгоритм Joey Yap: линейная формула с полярностью ствола
- Верификация: февраль, июль, октябрь 2026

---

## 12. Производительность

### Оптимизации
- **WAL режим:** Параллельные чтения во время записи
- **Пакетная обработка:** 50K записей за операцию
- **Шаблоны Ци Мэнь:** Замена вычислений поиском (1080 карт)
- **Гибридный анализ:** SQL для структур, Python для логики
- **SQL-First:** Перевод модулей на SQL CTE (ускорение до 29x)

### Метрики
- **Расчет Бацзы:** ~7 мин (Python) / ~25 сек (CSV+COPY)
- **Расчет Ци Мени:** 64 сек (Чжи Рень полный пересчет)
- **Анализ правил (Rule Engine):** ~2-4 минуты для года
- **Обслуживание БД:** ~5 минут (VACUUM + ANALYZE)

---

## 13. Качество данных

### Регрессионное тестирование
- **Контрольные таблицы:** 10 таблиц с эталонными данными
- **Автоматическая проверка:** После каждого изменения
- **Статус:** Все тесты проходят успешно (Python 58/58, React 22/22)

### Валидация
- **Солнечные термины:** Сверка с данными Гонконгской обсерватории
- **Черный Кролик:** Сверка с эталоном (февраль, июль, октябрь 2026)
- **Ци Мень Чжи Рень:** Верификация через классический метод 符头 + solar_term + 三元

---

*Документ является единым источником правды о состоянии проекта. Обновляется при каждом значимом изменении.*
