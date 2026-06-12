# Calk_KMF — Unified Tong Shu Portal

**Версия:** 2.8.0  
**Дата обновления:** 2026-06-12  
**Статус:** Активная разработка (Phase 1+2+5.5–5.7+5.13–5.20+6+7.11+Stage 7+Phase 8+9+10 ✅)

> **⚡ Быстрый старт сессии:** Прочитай `SESSION_CONTEXT.md` — там текущий фокус, риски и правила.

---

## 1. Цель проекта

Создать локальный раздел Тунг Шу (通书) — персонализированный календарь китайской метафизики, объединяющий лучшие функции аналогичных сайтов (mingli.ru, chinesemetasoft.com, bazi-calculator.com).

**Ключевые принципы:**
- Профессиональный уровень (Передовой режим)
- Персонализация на основе профилей пользователей
- Полный набор показателей с возможностью настройки отображения
- Экспорт в PDF и Excel

**Язык интерфейса:** Русский (EN, ZH — бэклог)  
**Режим:** Professional  
**Диапазон дат:** 1900–2100 (из БД)

---

## 2. Технологический стек

| Компонент | Технология | Версия | Статус |
|-----------|------------|--------|--------|
| Backend | Python | 3.14 | ✅ |
| API | FastAPI | latest | ✅ |
| БД (production) | PostgreSQL | 18 | ⚠️ Опорная |
| БД (fallback) | SQLite | 3.x | ✅ Основная для разработки |
| Драйвер PostgreSQL | pg8000 | latest | ✅ |
| Frontend | React | 18 | ✅ |
| UI Kit | MUI (Material-UI) | v5 | ✅ |
| MCP интеграция | @modelcontextprotocol/server-postgres | — | ✅ |

---

## 3. Структура проекта

```
Calk_KMF/
├── api/app/                    # FastAPI приложение
├── code/
│   ├── tongshu/               # Тунг Шу календарь (Phase 1 ✅, Phase 2 ✅)
│   ├── bazi_calendar/         # Бацзы календарь (✅ Полностью)
│   ├── qimen/                 # Ци Мэнь Дунь Цзя (✅ Полностью)
│   ├── feng_shui/             # Летящие звёзды (✅ Полностью)
│   ├── taiyi/                 # Тай И Шен Шу (✅ Полностью)
│   ├── analysis/              # Rule Engine (✅)
│   ├── profiles/              # Профили пользователей (Phase 2 ✅)
│   ├── calendar/              # Яндекс Календарь (CalDAV) (✅)
│   ├── common/                # Общие компоненты
│   ├── tests/                 # Регрессионные тесты
│   └── utils/                 # Утилиты миграции и отладки
├── frontend/                   # React приложение
├── data/                       # DDL, Views, SQL
├── scripts/                    # Скрипты генерации и проверки
├── bat/                        # Windows batch файлы
├── Metodology/                 # Методология и архитектура
├── plans/                      # Архитектурные планы
├── docs/                       # Документация (setup, troubleshooting, history)
└── docs/memory_bank/           # Memory Bank
```

### 3.1. Документация схемы БД

При изменении схемы PostgreSQL обновить **два** файла:

| Файл | Назначение | Как обновлять |
|------|-----------|---------------|
| `data/ddl_full_schema_raw.sql` | Полный DDL | `pg_dump --schema-only --no-owner --no-privileges -h 127.0.0.1 -U postgres --file=data/ddl_full_schema_raw.sql calk_kmf` |
| `Metodology/postgresql_schema.md` | Человекочитаемая документация | `python scripts/generate_schema_doc_v2.py` (требуется `POSTGRES_PASSWORD`) |

---

## 4. Принципы производительности (Performance-First)

**Последнее обновление:** 15.02.2026

### 4.1. Ключевые принципы

1. **SQL-First:** Все массовые операции — в БД. Python — только оркестрация.
2. **Иерархичность:** Не вычислять на уровне часа то, что не меняется в течение дня/месяца/года.
3. **Batch-Processing:** Вставка и чтение только пакетами (10k–50k записей).
4. **No-Loop:** Избегать `for row in cursor` в Python для обработки данных.

### 4.2. Стратегия Иерархического Анализа

| Уровень | Частота (на 1 год) | Куда пишем |
| :--- | :--- | :--- |
| **Год** | 1 | `t_analysis_year` |
| **Месяц** | 12 | `t_analysis_month` |
| **День** | ~365 | `t_analysis_day` |
| **Час** | ~8760 | `t_analysis_hour` |

### 4.3. SQL-First Standard

**Статус:** Утверждённый стандарт (с 15.02.2026)

Сравнительный анализ на модуле Тай И (февраль 2026):
- **Python-цикл:** 5.60 сек.
- **SQL-запрос:** 0.19 сек.
- **Ускорение:** ~29×

**Протокол новых модулей:**
1. Этап анализа: "Можно ли это сделать одним SQL-запросом?"
2. Реализация: Избегать `fetchall` для последующей обработки.
3. Code Review: Любой Python-цикл обработки данных требует обоснования.
4. Hierarchical Check: Если параметр меняется 1 раз в день → тип `day`.

---

## 5. Управление правилами анализа

### 5.1. Структура правил (`t_rule_registry`)

| Поле | Тип | Описание |
|------|-----|----------|
| `rule_id` | TEXT PK | MD5-хэш или UUID |
| `period_type` | TEXT | Уровень: `year` / `month` / `day` / `hour` |
| `name_ru` | TEXT | Название |
| `predicate_code` | TEXT | SQL-шаблон или Python-функция |
| `params_json` | JSONB | Параметры |
| `score_base` | REAL | Базовый балл |
| `is_active` | INTEGER | 1 = включено |

**Принцип иерархии:** Если правило не меняется в течение дня — `day`, не `hour`.

### 5.2. Процесс добавления правила

1. Определить иерархию (Period Type)
2. Реализовать (SQL-First)
3. Зарегистрировать: `INSERT INTO t_rule_registry`
4. Привязать к области: `t_rule_scope`

### 5.3. Запуск расчёта

Скрипт: `code/analysis/run_analysis.py`
- Каскад: Year → Month → Day → Hour
- Автоочистка таблиц для выбранного года

---

## 6. Мониторинг PostgreSQL

### 6.1. Ключевые метрики

- Connections, Transactions/sec, Slow Queries, Query Cache Hit Ratio
- Table/Index Size, Bloat, WAL Activity, CPU/Memory/Disk

### 6.2. Инструменты

- **Встроенные:** `pg_stat_statements`, `pg_stat_database`, `pg_stat_user_tables`
- **Внешние:** pgAdmin, Prometheus + Grafana, pgBadger

---

## 7. Статус задач по фазам

| Фаза | Статус | Примечание |
|------|--------|------------|
| Phase 1 — Foundation | ✅ | Полностью выполнен. Детали в `docs/history.md`. |
| Phase 2 — Personalization (Profiles + Ba Zi) | ✅ | Полностью выполнен. Детали в `docs/history.md`. |
| Phase 3 — Extended (XKDG + Flying Stars + Feng Shui) | 🔄 | 3.4 Flying Stars ✅, 3.5 Feng Shui направления ✅. Остальное в бэклоге. |
| Phase 5 — Polish (Export + Settings + Testing + Infrastructure) | 🔄 | 5.5–5.18 ✅. **Активно: 5.19 — Очистка bat-файлов и создание корректного `start_portal.bat`**. |
| Phase 6 — Расширение дневного представления | ✅ | Полностью выполнен. Детали в `docs/history.md`. |
| Stage 7 — Qi Men: полный редизайн и интеграция | ✅ | Полностью выполнен. Детали в `docs/history.md`. |
| Phase 8 — PostgreSQL-only Migration & Optimization | ✅ | Полностью выполнен. Детали в `docs/history.md`. |
| Phase 9 — QimenEngine SQL CTE Optimization | ✅ | Полностью выполнен. Детали в `docs/history.md`. |
| Phase 10 — Performance Optimization | ✅ | Полностью выполнен. Детали в `docs/history.md`. |

### Phase 5 — Polish

| Этап | Название | Статус |
|------|----------|--------|
| 5.5 | Тестирование React компонентов | ✅ |
| 5.6 | Проверка производительности | ✅ |
| 5.7 | Финальная документация API | ✅ |
| 5.13 | Полный цикл пересчёта и тестирования | ✅ |
| 5.14 | Оптимизация и наведение порядка в методологии | ✅ |
| 5.15 | Консолидация документации | ✅ |
| 5.16 | Документация схемы PostgreSQL | ✅ |
| 5.17 | Полный цикл пересчёта и тестирования (регрессия) | ✅ |
| 5.18 | Синхронизация Шэнь Ша с PostgreSQL и UI интеграция | ✅ |
| **5.19** | **Очистка bat-файлов запуска портала и создание корректного `start_portal.bat`** | **🔄** |
| **5.20** | **Публикация проекта на GitHub и настройка журнала изменений** | **✅** |

### Бэклог

| Этап | Название | Статус |
|------|----------|--------|
| B.1 | Система скоринга дней | ⬜ |
| B.3 | Сравнение двух профилей | ⬜ |
| B.8 | Мультиязычность (EN, ZH) | ❌ Не требуется |

---

## 8. Журнал ключевых этапов (последние 3)

### GitHub Publication — Публикация проекта и настройка журнала (2026-06-12)
- Создан публичный репозиторий `dkfcnm/Calk-KMF` (GitHub не позволил использовать `Calk_KMF`, использовано `Calk-KMF`)
- Первый коммит `774ecd4`: 349 файлов с детальным описанием всех модулей
- Настроен `.gitignore`: исключены `node_modules`, `__pycache__`, `.env`, логи, БД, бэкапы, кэши IDE
- Создан `.gitmessage` и настроен `commit.template` для детальных коммит-сообщений
- Добавлен `docs/commit-guidelines.md` — правила ведения журнала изменений
- Обновлён `CHANGELOG.md` — зафиксирована публикация и настройка журнала
- Коммит `d8063bd` [DOCS] с изменениями по журналу

### Stage 6 — Расширение дневного представления (2026-05-31)
- **Hourly slots:**
  - API `/api/tongshu/hours/{date_str}` — 12 двухчасовых слотов с ten_god, qi_phase, hidden_stems, symbolic_stars
  - Frontend: сворачиваемая таблица в DailyDayView (время + столп по умолчанию, раскрытие для полных данных)
- **Black Rabbit:**
  - Добавлены колонки `lunar_month`, `black_rabbit_star`, `black_rabbit_score` в `t_tung_shu_daily` (SQLite + PostgreSQL)
  - Заполнены для 365 дней 2026 через `black_rabbit_logic.py`
  - Отображение в day view как Chip с цветовой индикацией (success/error/default по score)
- **Lunar date:** `lunar_day` + `lunar_month` отображаются в блоке «Луна и фазы»
- **Flying Stars compact:**
  - Summary line «Г: X; М: Y; Д: Z» перед сеткой
  - `compact` prop в FlyingStarsGrid — скрывает hour_star chips, меняет легенду
- **Тесты:** Python 48/48 passed, React 21/21 passed, build successful

### Stage 5.18 — Синхронизация Шэнь Ша с PostgreSQL и UI интеграция (2026-05-31)
- **PostgreSQL синхронизация:**
  - Создана `spr_shensha_config` (49 звёзд: 27 classical + 22 V.Zakharov)
  - Добавлена колонка `source` в `spr_tongshu_shensha_rule` (classical / vladimir_zakharov)
  - Синхронизированы данные SQLite → PostgreSQL
  - Добавлена колонка `symbolic_stars` в `t_tung_shu_daily` (SQLite + PostgreSQL)
  - Перегенерированы данные 2026 года (365 записей) с symbolic_stars
- **API:**
  - Переписан `tongshu_service.py` для работы с `t_tung_shu_daily` (PostgreSQL primary)
  - Обновлён `api/app/schemas/tongshu.py` — `TongshuDailyData` теперь включает `symbolic_stars`
  - Обновлены response_model в роутере на `TongshuDailyData`
  - Добавлен парсинг JSON в `tongshu_daily_service.py`
- **Frontend:**
  - Отображение symbolic_stars в детальном виде дня (TongShuPage.js)
  - Колонка "Шэнь Ша" в Week View и Month View (с показом до 3 звёзд + счётчик)
  - Поиск по symbolic_stars в Month View
  - Сборка: успешно (250.95 kB gzipped)
- **Документация:**
  - Обновлён `data/ddl_full_schema_raw.sql` (spr_shensha_config + source колонка)
  - Обновлён `Metodology/postgresql_schema.md` (описание таблиц)
  - Обновлён `Metodology/reference_tongshu_methodologies.md` (алгоритм + управление)

### Stage 5.17 — Полный цикл пересчёта и тестирования (2026-05-31)
- Python тесты: 8 файлов, все passed (API 21/21, TongShuDay 7/7, reference, combos, symbolic stars, ten gods, qi phases, analysis qimen)
- React тесты: 2 suites, 10/10 passed
- PostgreSQL: 98 таблиц, подключение OK
- Зафиксированы проблемы: pytest конфликт с `code/__init__.py`, Qimen 500 (известно)

### Stage 5.16 — Документация схемы PostgreSQL (2026-05-31)
- Создан `Metodology/postgresql_schema.md` (98 таблиц, 1707 строк)
- Создан `data/ddl_full_schema_raw.sql` (pg_dump)
- Скрипт авто-генерации: `scripts/generate_schema_doc_v2.py`

### Stage 5.15 — Консолидация документации (2026-05-31)
- Созданы единые справочники: `reference_bazi_calendar.md`, `reference_qimen.md`, `reference_tongshu_methodologies.md`
- Архивировано 22 файла в `Metodology/archive/`

### Stage 5.14 — Оптимизация и стабилизация (2026-05-31)
- SQLAlchemy 2.0 fix (`text()`)
- CRM API: 500 → 200 OK
- Новый скрипт синхронизации: `sync_bazi_hourly_to_postgres.py`
- Тесты: Python 47/47, React 10/10, API 21/21 passed

*Архив старых этапов:* [`docs/history.md`](docs/history.md)

---

## 9. Решения по рискам (принятые)

| Риск | Решение | Статус |
|------|---------|--------|
| QMDJ 68.2% match с Excel | Chai Bu как альтернатива | Принято |
| Отсутствие справочников | Наполнить вручную | Принято |
| XKDG Rating алгоритм закрыт | Разработать собственный | Принято |
| Производительность БД | SQL-First + агрегатные таблицы | Принято |
| Scope creep | Строгая приоритизация по фазам | Принято |

---

## 10. Протокол взаимодействия

См. [`Metodology/ai_collaboration_protocol.md`](Metodology/ai_collaboration_protocol.md)

### Актуальные поручения

| ID | Поручение | Дата | Статус |
|----|-----------|------|--------|
| П.11 | Исследовать и задокументировать методологии (10 богов, комбинации, фазы Ци) | 2026-05-30 | ✅ |
| П.12 | Полный цикл пересчёта, тестирования и оптимизации | 2026-05-30 | ✅ |

---

## 11. MCP интеграция

- **Глобальная:** `~/.kimi/mcp.json`
- **Проектная:** `.roo/mcp.json`

| Сервер | Назначение |
|--------|-----------|
| postgres | Read-only SQL к `calk_kmf` |
| context7 | Документация библиотек |
| playwright | Автоматизация браузера |

---

## 12. Управление PostgreSQL

- `bat\DB_Start.bat` — запуск службы PostgreSQL
- `bat\DB_Stop.bat` — остановка службы
- `bat\DB_backup.bat` — резервное копирование

---

## 13. Ссылки

| Что | Где |
|-----|-----|
| Установка и запуск | [`docs/setup.md`](docs/setup.md) |
| Устранение неполадок | [`docs/troubleshooting.md`](docs/troubleshooting.md) |
| Функциональные возможности | [`docs/features.md`](docs/features.md) |
| Архив этапов | [`docs/history.md`](docs/history.md) |
| Методология | [`Metodology/README.md`](Metodology/README.md) |
| Текущий контекст | [`SESSION_CONTEXT.md`](SESSION_CONTEXT.md) |
| База знаний (ошибки) | [`Metodology/bz.md`](Metodology/bz.md) |

---

*Последнее обновление: 2026-06-05 (Phase 9 — оптимизация производительности завершена)*
