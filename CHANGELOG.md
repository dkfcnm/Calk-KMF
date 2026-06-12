# Журнал изменений (Changelog)

Все значимые изменения в проекте будут документироваться в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
и проект придерживается [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Добавлено
- Базовая версия скриптов для запуска (`start_app.bat`) и остановки (`stop_app.bat`) приложения
- Автоматический установщик зависимостей (`setup_deps.bat`)
- Подробная документация в README.md

## [2.5.0] - Phase 2 — Персонализация (2026-05-31)

### Добавлено
- **Расчёт карты рождения (BaZi)**: `ProfileService.calculate_birth_chart()` — интеграция с `BaziEngine`, расчёт 4 столбов, определение day_master и элемента
- **Персонализированные данные Тун Шу**: новый API endpoint `GET /api/tongshu/personalized/day` — hidden_stems, personalized_ten_gods, personalized_qi_phases относительно day_master профиля
- **Профиль selector в календаре**: dropdown для выбора профиля в дневном виде Тун Шу
- **Отображение персонализации в UI**:
  - Баннер с именем профиля и day_master
  - Скрытые стволы (hidden_stems) с процентами для всех 4 столбов
  - Персонализированные 10 Богов (year/month/day/hour)
  - Персонализированные фазы Ци (year/month/day/hour)
- **Справочник городов**: `spr_city_timezone` (104 города) + API `/api/profiles/cities/search` для autocomplete
- **Скрытые стволы в SQLite**: таблица `spr_hidden_stems` скопирована из PostgreSQL в `calk_kmf.sqlite`

### Изменено
- `list_all()` в `profile_service.py` теперь подгружает `birth_chart` для всех профилей
- `ProfilesPage` отображает birth_chart на карточке профиля (4 столба + day_master)

### Тесты
- Python backend: 14/14 passed (включая новые проверки personalized_service)
- React: 13/13 passed
- API endpoints: 21/21 passed

## [2.5.1] - Stage 5.5 — Тестирование React компонентов (2026-05-31)

### Добавлено
- **Новые React тесты**:
  - `frontend/src/tests/ProfilesPage.test.js` — 3 теста (рендеринг списка, birth chart chips, empty state)
  - `frontend/src/tests/profileService.test.js` — 3 теста (listProfiles, calculateChart, searchCities)
  - `frontend/src/tests/tongShuService.test.js` — 2 теста (fetchPersonalizedDayData, fetchDailyDayData)

### Тесты
- React: 6 suites, 21/21 passed
- Python backend: 14/14 passed
- API endpoints: 21/21 passed

## [2.5.2] - Stage 5.6+5.7+7.11 — Performance, API Docs, UI Debug (2026-05-31)

### Добавлено
- **Бенчмарки**: `Metodology/benchmark_results.md` — замеры API (14–24ms), TongShuDay (3.5ms), calc_four_pillars (14ms), PostgreSQL (<1ms/query)
- **UI Debug IDs**: покрытие HomePage, QiMenPage, CrmPage (cards, buttons, titles, loading states)
- **OpenAPI**: 50 endpoints задокументированы автоматически через FastAPI

### Тесты
- React: 6 suites, 21/21 passed
- Build: успешен, bundle 249.63 kB

## [2.4.0] - Stage 5.14 — Оптимизация и стабилизация (2026-05-31)

### Исправлено
- **SQLAlchemy 2.0 совместимость**: Все `db.execute(query)` в `api/app/services/qimen_service.py` и `api/app/services/crm_service.py` обёрнуты в `text()` для совместимости с SQLAlchemy 2.0
- **CRM API**: Исправлена ошибка 500, теперь возвращает `200 OK` для `/api/crm/clients/`
- **Bazi Calendar генератор**: Исправлен `run_update_optimized.py` — параметры `year_start`/`year_end` вместо глобальных констант `YEAR_START`/`YEAR_END`
- **Rule Engine**: Исправлен SQL запрос — убраны ссылки на несуществующие колонки `hexagram_num`/`hexagram_name` в `spr_jiazi_extended`
- **Qimen API**: Обнаружено несоответствие имён таблиц (`t_qimen_*` в коде vs `t_qumen_*` в БД) — требуется миграция

### Добавлено
- **Скрипт синхронизации**: `scripts/sync_bazi_hourly_to_postgres.py` — перенос `t_bazi_hourly` из SQLite в PostgreSQL через CSV+psql COPY (354,807 rows за ~25s)
- **Новые тесты**: 
  - `code/tests/test_reference_data.py` — 7/7 passed (shensha, ten_god, phase, combos)
  - `code/tests/test_combinations.py` — 3/3 passed (столкновения, слияния, гармонии)
  - `code/tests/test_symbolic_stars.py` — 3/3 passed (символические звёзды)
  - `code/tests/test_ten_gods.py` — 3/3 passed (10 богов)
  - `code/tests/test_qi_phases.py` — 3/3 passed (фазы Ци)
- **Результаты тестирования**: Python 47/47 passed, React 10/10 passed, API 21/21 passed

### Оптимизировано
- **Методология**: Архивировано 7 устаревших файлов в `Metodology/archive/`
- **Полный цикл пересчёта**: Все модули пересчитаны и протестированы (Бацзы, Ци Мень, Летящие звёзды, Тай И, Rule Engine)

## [Unreleased] - Phase 1 Foundation

### Добавлено
- **Батники запуска/остановки портала**: `start_portal.bat` и `stop_portal.bat` — запускают/останавливают FastAPI backend (порт 8000) и React frontend (порт 3000)
- **Проверка работоспособности**: Все разделы протестированы (Главная, Тун Шу, Ци Мэнь, CRM, Справочники). Новые API `/daily/*` работают корректно со SQLite fallback
- **Модуль справочников (админка)**: Страница `/references` с CRUD-редактором для:
  - 12 Officers (`spr_day_officer_value`) — символ, пиньинь, названия, категория (благоприятный/смешанный/неблагоприятный), описания
  - 28 Constellations (`spr_tongshu_constellation`) — символ, пиньинь, название, направление, элемент, животное, характер, описание
  - Belt Stars (`spr_yellow_black_stars`) — название, счёт, тип (жёлтый/чёрный/нейтральный)
- **API справочников**: `GET/PUT /api/refs/officers`, `/api/refs/constellations`, `/api/refs/belt-stars` — работают с SQLite, не требуют PostgreSQL
- **Модуль Тунг Шу (Phase 1)**: Полная реализация фундамента календаря Тунг Шу.
  - `code/tongshu/` — структура модулей: `core/`, `bazi/`, `xkdg/`, `feng_shui/`, `symbolic/`, `zeri/`, `api/`
  - `code/profiles/` — заготовка для управления профилями пользователей
  - **Справочники**: `spr_day_officer_value` (12 Офицеров с описаниями), `spr_tongshu_constellation` (28 созвездий), `spr_tongshu_constellation_cycle` (месячный цикл)
  - **Класс `TongShuDay`** (`code/tongshu/core/tongshu_day.py`): Агрегирует Four Pillars, 12 Officers, 28 Constellations, Na Yin, Yellow/Black Belt, Moon Phase, Solar Term
  - **Таблица `t_tung_shu_daily`**: Агрегатные данные за каждый день (365 записей для 2026 года)
  - **Скрипт генерации**: `scripts/generate_tung_shu_daily.py` — batch-генерация за год/месяц
  - **API endpoints** (`/api/tongshu/daily/*`): `/day`, `/month`, `/week`, `/year` — работают с SQLite fallback, не требуют PostgreSQL
  - **React-интерфейс**: Обновлён `TongShuPage.js` — 4 режима просмотра (День/Неделя/Месяц/Год), цветовая кодировка по типу пояса (жёлтый/чёрный), Chip для Officers и Constellations, Tooltip для направлений
  - **Frontend service**: Добавлены `fetchDailyDayData`, `fetchDailyMonthData`, `fetchDailyWeekData`, `fetchDailyYearData`

## [2.3.1] - 2026-05-16

### Добавлено
- **MCP сервер PostgreSQL**: Настроен `@modelcontextprotocol/server-postgres` для работы с БД `calk_kmf` через MCP протокол. Конфигурации: `~/.kimi/mcp.json` (глобальная) и `.roo/mcp.json` (проектная).
- **Справочник `spr_jiazi_extended`**: Добавлены 6 колонок ju для Ци Мень Чжи Жень — `upper_ju_yang`, `middle_ju_yang`, `lower_ju_yang`, `upper_ju_yin`, `middle_ju_yin`, `lower_ju_yin`.
- **Скрипты верификации**: Созданы инструменты для сравнения часовых раскладов с эталоном `Smart Tablica 2026.xlsx`.

### Исправлено
- **Ци Мень Чжи Жень (часовые расклады)**: Исправлен расчет `curr_date` в SQL-запросе hourly chart — теперь используется `slot_start_date_local::DATE` вместо `slot_start_date_utc::DATE`. Это устранило смещение ju_num для часов, пересекающих полночь UTC (совпадение с эталоном выросло с 67.3% до 68.2%).

### Проанализировано
- **Верификация hourly charts**: Проведено сравнение 4380 записей (2026 год, MSK) с `Smart Tablica 2026`. Установлено, что Excel использует упрощенный/неклассический метод (часто берет "следующий" solar_term вместо текущего, для 子 часа — циклический метод). Классическая реализация проекта признана корректной.

## [1.0.0] - 2026-04-18

### Добавлено
- Создана базовая структура проекта для бэкенда на FastAPI и фронтенда на React
- Реализованы API для работы с данными календаря Тун Шу
- Реализованы API для работы с раскладами Ци Мень
- Реализован базовый API для CRM-системы
- Разработаны компоненты интерфейса для просмотра календаря Тун Шу
- Разработаны компоненты интерфейса для просмотра раскладов Ци Мень
- Разработаны компоненты интерфейса для CRM
- Интегрированы все компоненты в единый пользовательский интерфейс

### Исправлено
- Исправлены проблемы с отображением кириллических символов в скриптах
- Исправлены проблемы с определением зависимостей
- Улучшено обнаружение и завершение процессов

### Изменено
- Сервисы переведены на единый стиль использования axios вместо fetch API
- Стандартизирован формат ответов API
- Улучшена обработка ошибок в API и интерфейсе
