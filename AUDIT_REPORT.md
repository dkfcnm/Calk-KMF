# Полный аудит кодовой базы и табличной структуры Calk_KMF

**Дата аудита:** 2026-05-16  
**Версия проекта:** v2.3 (статус: стабильная эксплуатация)  
**Методология:** Автоматизированный аудит 4 независимыми агентами (БД, Backend, Расчетные модули, Frontend) + кросс-верификация.  

---

## 1. Резюме (Executive Summary)

Обнаружено **80+ проблем** различной критичности. Проект находится в переходном состоянии (SQLite → PostgreSQL), что привело к техническому долгу: параллельно существуют legacy- и новые реализации, часть кода обращается к SQLite в обход центрального `DBManager`, а часть модулей нарушает архитектурный принцип **SQL-First**.

**Топ-5 критических рисков:**
1. **SQL-инъекции** в `qimen_service.py` и `tongshu_service.py` (f-string в SQL-запросах)
2. **Отсутствие индексов** на таблицах с 14.5M+ записей (`t_analysis_date`, `t_analysis_direction`)
3. **N+1 запросы** в `tongshu_service.py` (~1095 запросов за год вместо одного batch-запроса)
4. **Мертвый/дублирующий код** в `qimen/run_update_*_optimized.py` и `bazi_calendar/run_update_optimized.py` (миллионы Python-итераций вместо SQL)
5. **Runtime-ошибки** во фронтенде (отсутствующий импорт, race conditions, убийство всех процессов в `stop_app.bat`)

---

## 2. Критические проблемы (🔴 Немедленное действие)

### 2.1. Безопасность: SQL-инъекции через f-string

| Файл | Строки | Уязвимость |
|------|--------|------------|
| `api/app/services/qimen_service.py` | 42-55 | `table_name`, даты, `limit`, `offset` в f-string |
| `api/app/services/qimen_service.py` | 115, 134 | `chart_table`, `palace_table` в f-string |
| `api/app/services/tongshu_service.py` | 22-40 | `date_str` в `WHERE date::date = '{date_str}'` |
| `api/app/services/tongshu_service.py` | 65-74 | `day_stem` в f-string |
| `api/app/services/tongshu_service.py` | 232-244 | `date_str` в f-string |
| `api/app/services/crm_service.py` | 230-235 | Динамический SQL через f-string в `update_parts` |

**Рекомендация:** Перейти на SQL-параметры (`:param`) для всех значений. Имена таблиц валидировать по whitelist (`TABLE_MAPPING`).

### 2.2. Производительность: Отсутствие индексов на огромных таблицах

| Таблица | Строки | Индексы | Последствия |
|---------|--------|---------|-------------|
| `t_analysis_date` | 14.5M | 0 | Любой запрос по `hour_id` или `rule_id` — Full Table Scan |
| `t_analysis_direction` | 1.8M | 0 | Full Table Scan при фильтрации по дворцу/часу |
| `t_qumen_chauby_day/month/year` | ~10K | 0 | Медленный поиск раскладов |
| `t_qumen_dgiren_day/month/year` | ~10K | 0 | Медленный поиск раскладов |

**SQL-исправление:**
```sql
CREATE INDEX idx_analysis_date_hour_id ON t_analysis_date(hour_id);
CREATE INDEX idx_analysis_date_rule_id ON t_analysis_date(rule_id);
CREATE INDEX idx_analysis_direction_hour_id ON t_analysis_direction(hour_id);
CREATE INDEX idx_analysis_direction_palace ON t_analysis_direction(palace_no);
```

### 2.3. Производительность: N+1 в TongShu

| Функция | Запросов | Должно быть |
|---------|----------|-------------|
| `get_year_data` | ~1095 | 1 batch |
| `get_month_data` | ~90 | 1 batch |
| `get_week_data` | 21 | 1 batch |
| `get_hours_data` | 13 | 1 JOIN |

### 2.4. Битый Foreign Key

`t_chart_analysis` ссылается на `spr_indicator_rule`, которой **не существует** в БД.

### 2.5. Frontend: Runtime-ошибки

| Проблема | Файл | Строка |
|----------|------|--------|
| Отсутствует импорт `TextField` | `TongShuPage.js` | 127 |
| Race condition (вложенный async без await) | `QiMenPage.js` | 84-95 |
| Двойная загрузка при монтировании | `QiMenPage.js` | 52-63 |
| `stop_app.bat` убивает **все** `node.exe`/`python.exe` в системе | `stop_app.bat` | — |

---

## 3. Высокий приоритет (🟡 Ближайший спринт)

### 3.1. Дублирование кода

| Что дублируется | Где | Рекомендация |
|-----------------|-----|--------------|
| Pydantic-модели в роутерах | `crm.py`, `qimen.py`, `tongshu.py` (routers) | Удалить, импортировать из `schemas/` |
| axios-бойлерплейт | `crmService.js`, `qimenService.js`, `tongShuService.js` | Создать единый `api.js` с interceptors |
| UI-логика загрузки/ошибок | `TongShuPage`, `QiMenPage`, `CrmPage` | Кастомный хук `useApi` |
| Формы CRM | `ClientForm.js`, `SessionForm.js` | Базовый `Form` компонент или Formik |
| `check_*.py` скрипты | 8+ файлов в корне | Объединить в `scripts/db_check.py` |
| Qimen batch-версии | `run_update_zhirun_optimized.py`, `run_update_chauby_optimized.py` | **Удалить** (SQL-версии быстрее) |

### 3.2. Архитектурные нарушения Backend

- **Бизнес-логика в роутерах:** `crm.py` проверяет существование клиента перед каждой операцией — это задача сервиса.
- **ORM-модели не используются:** `models/crm.py` определяет relationships, но сервисы используют raw SQL. Либо перейти на ORM, либо удалить модели.
- **Отсутствует centralized exception handling:** Все роутеры оборачивают `except Exception` в 500 — маскируют `IntegrityError`, `NoResultFound` и баги.
- **Нет логирования:** Ни в одном файле бэкенда нет `logging.getLogger(__name__)`.

### 3.3. Мертвый / Legacy код

| Файл | Проблема |
|------|----------|
| `code/qimen/run_update_zhirun_optimized.py` | Дублирует SQL-версию через медленный Python-цикл |
| `code/qimen/run_update_chauby_optimized.py` | Дублирует SQL-версию через медленный Python-цикл |
| `code/analysis/setup_schema.py` | Создает старую схему `t_analysis_date` в обход DBManager |
| `code/bazi_calendar/engine.py` | `get_solar_term_start` — пустая функция (`pass`) |
| `code/common/logger.py` | Открывает собственное SQLite-соединение, игнорируя DBManager |
| `create_crm_tables.py` | Дублирует миграции, нет версионирования |

### 3.4. Нарушение SQL-First

| Модуль | Проблема | Влияние |
|--------|----------|---------|
| `bazi_calendar/run_update_optimized.py` | Python-цикл по 27 таймзонам × 3 года × слоты. Миллионы итераций. | **Главное узкое место производительности** |
| `analysis/run_analysis.py` | 20 отдельных `INSERT` с общим CTE. Конкатенация в `JOIN` (`||`) блокирует индексы. | ~2-3 сек, но может быть <1 сек |

### 3.5. Дублирование таблиц в БД

| Старые (много данных) | Новые (пустые/мало) | Рекомендация |
|-----------------------|---------------------|--------------|
| `t_analysis_date` (14.5M) | `t_analyz_date` | Завершить миграцию |
| `t_analysis_direction` (1.8M) | `t_analyz_direction` | Завершить миграцию |

---

## 4. Средний приоритет (🟢 Техдолг)

### 4.1. Backend

- Нет пагинации в `list_client_sessions`, `get_client_calculations`, `get_client_notes`
- Нет API для `bazi_calendar/`, `taiyi/`, `feng_shui/`, `analysis/`
- `pool_size`/`max_overflow` не настроены в `database/db.py`
- CORS `allow_origins=["*"]` — вынести в `.env`
- `reload=True` захардкожено в `main.py`

### 4.2. Frontend

- Нет `AbortController` / cleanup в `useEffect`
- `window.location.reload()` как единственный retry
- `LocalizationProvider` создается при каждом рендере
- `QimenGrid`, `PalaceDetail` не обернуты в `React.memo`
- Нет `useCallback` на обработчиках

### 4.3. Инфраструктура

- `start_app.bat`: жестко зашитые зависимости, нет проверки порта 3000, `timeout` вместо health-check
- `setup_deps.bat`: нет `requirements.txt`, инсталляторы не удаляются
- Нет `requirements.txt` в корне проекта

### 4.4. База данных

- 25 идентичных timezone-view (`v_bazi_hourly_tz_m12`…`p14`) → заменить на одну функцию
- 6 пустых справочников `spr_tongshu_*`
- `t_control_*` покрывают только 10 из 24 основных таблиц
- `spr_indicator_value` имеет колонки с пустым типом данных (`""`)

---

## 5. Детализация по слоям

### 5.1. База данных (SQLite, ~4.79 GB)

**Общая статистика:**
- 71 таблица | 34 VIEW | 20 индексов
- MAIN: 24 | REFERENCE: 37 | CONTROL: 10

**Что хорошо:**
- `t_bazi_hourly` проиндексирована (12 индексов)
- Ключевые справочники на месте и корректны
- Система комментариев DDL реализована (`spr_table_comment`: 41, `spr_column_comment`: 196)

**Что плохо:**
- Огромные таблицы без индексов (`t_analysis_date`: 14.5M строк, 0 индексов)
- Битый FK (`t_chart_analysis` → несуществующая `spr_indicator_rule`)
- Дублирование analysis-таблиц (миграция не завершена)
- Избыточные VIEW (25 timezone-view вместо функции)

### 5.2. Backend API (FastAPI)

**Обнаружено:** 36 проблем.

**Критические:**
- SQL-инъекции через f-string во всех сервисах
- N+1 в `tongshu_service.py`
- Отсутствие аутентификации и rate limiting

**Архитектурные:**
- Pydantic-модели продублированы в роутерах и `schemas/`
- Бизнес-логика валидации клиента находится в роутерах, а не в сервисах
- ORM-модели определены, но используется raw SQL
- Нет centralized exception handler
- Нет логирования

### 5.3. Модули расчетов

**SQL-First соблюдается в:** `qimen/run_update_zhirun.py`, `qimen/run_update_chauby.py`, `feng_shui/run_update.py`, `taiyi/run_update.py`, `analysis/run_analysis.py`.

**Нарушение SQL-First в:**
- `bazi_calendar/run_update_optimized.py` — главное узкое место. Python-цикл по слотам вместо SQL-CTE `generate_series`.
- `bazi_calendar/hourly.py` — та же медленная логика legacy-заполнения.

**Мертвый код:**
- `run_update_zhirun_optimized.py` и `run_update_chauby_optimized.py` (Python-batch дублирует SQL)
- `analysis/setup_schema.py` (старая схема, обходит DBManager)
- `bazi_calendar/engine.py::get_solar_term_start` (пустая функция)

**Тесты:**
- `test_analysis_qimen.py` тестирует Python-движок `AnalysisEngine`, который в production не используется для массовых расчетов (используется SQL из `run_analysis.py`).
- `control_data.py` не покрывает `t_analysis_*` таблицы.

### 5.4. Frontend (React + MUI)

**Критические runtime-проблемы:**
- Отсутствующий импорт `TextField` в `TongShuPage.js`
- Race conditions в `QiMenPage.js`
- `stop_app.bat` убивает все процессы Node/Python

**Архитектурные:**
- Нет единого axios-instance
- Нет слоя для работы с данными (кастомные хуки)
- Вся логика загрузки/ошибок копируется в каждой странице
- Компоненты вью встроены в `TongShuPage.js`

### 5.5. Инфраструктура

- 8+ `check_*.py` скриптов с дублирующей функциональностью
- Batch-скрипты не используют `requirements.txt`
- `create_crm_tables.py` дублирует функциональность миграций

---

## 6. Рекомендуемый план действий

### Этап 1: Критический фикс (1-2 дня)

1. **Исправить SQL-инъекции** — перевести все сервисы на параметризованные запросы
2. **Создать индексы** на `t_analysis_date`, `t_analysis_direction`
3. **Исправить frontend runtime:**
   - Добавить импорт `TextField`
   - Исправить race condition в `QiMenPage`
   - Исправить `stop_app.bat` (PID-файлы вместо глобального taskkill)
4. **Исправить битый FK** — создать `spr_indicator_rule` или переключить на `t_rule_registry`

### Этап 2: Высокий приоритет (1-2 недели)

5. **Удалить мертвый код:**
   - `code/qimen/run_update_*_optimized.py`
   - `code/analysis/setup_schema.py`
   - Пустые функции
6. **Устранить N+1** в `tongshu_service.py` — batch-запросы
7. **Рефакторинг роутеров:**
   - Вынести Pydantic-модели из роутеров в `schemas/`
   - Перенести валидацию клиента из роутеров в сервисы
   - Добавить centralized exception handler
8. **Frontend:**
   - Создать `services/api.js` с единым axios-instance
   - Создать кастомный хук `useApi`
   - Добавить `AbortController` в useEffect
9. **Объединить `check_*.py`** в единый диагностический скрипт

### Этап 3: Средний приоритет (2-4 недели)

10. **SQL-First для bazi_calendar:**
    - Переписать генерацию слотов на SQL-CTE (`generate_series`)
    - Увеличить batch size с 10K до 50K
    - Рассмотреть `COPY` для PostgreSQL
11. **Оптимизация analysis:**
    - Заменить `LIKE '2026%'` на `EXTRACT(YEAR FROM ...)`
    - Материализовать CTE во временную таблицу для SKDG
    - Добавить функциональный индекс на конкатенацию stem/branch
12. **Завершить миграцию analysis-таблиц** — удалить/переименовать `t_analysis_*` → `t_analyz_*`
13. **Добавить API** для `bazi`, `taiyi`, `feng_shui`
14. **Настроить пул соединений** (`pool_size=10`, `max_overflow=20`)
15. **Добавить логирование** во все слои

### Этап 4: Долгосрочные улучшения

16. Внедрить Alembic для миграций БД
17. Добавить аутентификацию (OAuth2/JWT)
18. Создать `requirements.txt` и обновить batch-скрипты
19. Добавить rate limiting (`slowapi`)
20. Заменить 25 timezone-view на одну SQL-функцию

---

## 7. Метрики и ожидаемый эффект

| Метрика | Текущее | После фикса | Экономия |
|---------|---------|-------------|----------|
| Расчет Ба Цзы (3 года, 27 TZ) | Минуты (Python-цикл) | Секунды (SQL) | **~10-50x** |
| TongShu: загрузка года | ~1095 запросов | 1 запрос | **99.9%** |
| TongShu: загрузка месяца | ~90 запросов | 1 запрос | **98.9%** |
| Analysis: запрос по `hour_id` | Full Table Scan (14.5M) | Index Seek | **~1000x** |
| Размер мертвого кода | ~2000 строк | 0 | Поддерживаемость |
| N+1 запросов | 10+ мест | 0 | Надежность + скорость |

---

## 8. Артефакты аудита

Сгенерированные файлы:
- `DB_AUDIT_REPORT.md` — детальный отчет по БД
- `db_audit_result.json` — сырые данные аудита БД (145 KB)
- `db_audit_report.py` + `db_audit_analyzer.py` — скрипты для повторного аудита

---

*Аудит проведен автоматизированной системой. Для уточнений по конкретным находкам обращайтесь к соответствующим разделам.*
