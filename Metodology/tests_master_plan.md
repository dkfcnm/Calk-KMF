# Мастер-план тестирования Calk_KMF

**Версия:** 1.1  
**Дата:** 2026-05-31  
**Статус:** Активен

---

## 1. Принципы

1. **Каждая задача, затрагивающая UI, должна включать тесты.**
2. **После каждой правки визуала:**
   - Обновить существующие React-тесты, если изменён компонент.
   - Добавить новый тест, если появился новый компонент или поведение.
   - Провести визуальную проверку по чеклисту (раздел 4).
3. **Регрессия:** перед закрытием этапа запускается полный набор тестов (Python + React + API).
4. **Документирование:** результаты тестирования фиксируются в журнале проекта (`03 - Project Journal.md`).

---

## 2. Структура тестов

```
code/tests/                    — Python тесты (backend, логика, API)
frontend/src/tests/            — React тесты (components, hooks, pages)
Metodology/tests_master_plan.md — этот документ (план и чеклисты)
```

---

## 3. Python тесты (backend)

| Файл | Что тестирует | Статус |
|------|---------------|--------|
| `code/tests/control_data.py` | Регрессионные проверки расчётных таблиц (Бацзы, Ци Мэнь, Летящие звёзды) | ✅ Актуален |
| `code/tests/test_analysis_qimen.py` | Анализ Ци Мэнь | ✅ Актуален |
| `code/tests/test_tongshu_day_extended.py` | TongShuDay: lunar_day, nayin per pillar, dagua metadata, hexagram family, production chain | ✅ Актуален |
| `code/tests/test_api_endpoints_http.py` | HTTP тесты всех API endpoints (21 тест) | ✅ Актуален |
| `code/tests/test_reference_data.py` | Наполнение справочников: shensha, ten_god, phase, combos | ✅ 7/7 passed |
| `code/tests/test_combinations.py` | Расчёт комбинаций в TongShuDay (столкновения, слияния, гармонии) | ✅ 3/3 passed |
| `code/tests/test_symbolic_stars.py` | Расчёт символических звёзд в TongShuDay | ✅ 3/3 passed |
| `code/tests/test_stage6_black_rabbit.py` | Stage 6: Black Rabbit columns и данные в PostgreSQL | ✅ 3/3 passed |
| `code/tests/test_stage6_hourly_api.py` | Stage 6: Hourly API — 12 слотов, ten_god, qi_phase, hidden_stems | ✅ 5/5 passed |
| `code/tests/test_ten_gods.py` | Расчёт 10 богов в TongShuDay | ✅ 3/3 passed |
| `code/tests/test_qi_phases.py` | Расчёт фаз Ци в TongShuDay | ✅ 3/3 passed |
| `api/app/services/personalized_service.py` | Персонализированные данные: hidden_stems, ten_gods, qi_phases | ✅ Актуален |
| `api/app/services/profile_service.py` | Расчёт birth chart через BaziEngine | ✅ Актуален |

### Запуск Python тестов

> ⚠️ **Важно:** `pytest` не работает из корня проекта из-за конфликта `code/__init__.py` со стандартной библиотекой Python `code`. Используйте прямой запуск через `python` из временной директории.

```bash
# Запуск из /tmp (или любой другой директории вне проекта) с PYTHONPATH
cd /tmp
PYTHONPATH=/e/Project/Calk_KMF /c/Python314/python /e/Project/Calk_KMF/code/tests/test_api_endpoints_http.py
PYTHONPATH=/e/Project/Calk_KMF /c/Python314/python /e/Project/Calk_KMF/code/tests/test_tongshu_day_extended.py
PYTHONPATH=/e/Project/Calk_KMF /c/Python314/python /e/Project/Calk_KMF/code/tests/test_analysis_qimen.py
PYTHONPATH=/e/Project/Calk_KMF /c/Python314/python /e/Project/Calk_KMF/code/tests/test_reference_data.py
PYTHONPATH=/e/Project/Calk_KMF /c/Python314/python /e/Project/Calk_KMF/code/tests/test_combinations.py
PYTHONPATH=/e/Project/Calk_KMF /c/Python314/python /e/Project/Calk_KMF/code/tests/test_symbolic_stars.py
PYTHONPATH=/e/Project/Calk_KMF /c/Python314/python /e/Project/Calk_KMF/code/tests/test_ten_gods.py
PYTHONPATH=/e/Project/Calk_KMF /c/Python314/python /e/Project/Calk_KMF/code/tests/test_qi_phases.py
```

---

## 4. React тесты (frontend)

| Файл | Что тестирует | Компонент | Статус |
|------|---------------|-----------|--------|
| `frontend/src/tests/ElementIdMarker.test.js` | ElementIdMarkerContext, ElementIdMarkerLayer | Все страницы | ✅ Актуален |
| `frontend/src/tests/CalendarGrid.test.js` | CalendarGrid: рендеринг, столпы, лунный день, наинь, офицер, созвездие, клик | TongShu / MonthlyCalendar | ✅ Актуален |
| `frontend/src/tests/FlyingStarsGrid.test.js` | FlyingStarsGrid: 9 дворцов, звезды, tooltip, fallback, compact mode | TongShu / DayDetail / FengShui | ✅ 4/4 passed |
| `frontend/src/tests/ProfilesPage.test.js` | ProfilesPage: рендеринг списка, birth chart chips, empty state | Profiles | ✅ 3/3 passed |
| `frontend/src/tests/profileService.test.js` | profileService: listProfiles, calculateChart, searchCities | Services | ✅ 3/3 passed |
| `frontend/src/tests/tongShuService.test.js` | tongShuService: fetchPersonalizedDayData, fetchDailyDayData | Services | ✅ 2/2 passed |

### Правило добавления React-тестов после правки визуала
При изменении любого компонента в `frontend/src/components/`:
1. Если тест уже существует — дополнить его новыми assert'ами.
2. Если теста нет — создать `<ComponentName>.test.js` в `frontend/src/tests/`.
3. Минимальный набор проверок:
   - Компонент рендерится без ошибок.
   - Ключевые текстовые элементы присутствуют.
   - Интерактивные элементы (кнопки, клики) работают.
   - Props передаются корректно.

### Запуск React тестов
```bash
cd frontend
npm test -- --watchAll=false
npm test -- --watchAll=false --testPathPattern="CalendarGrid"
```

---

## 5. UI Debug System Tests

| Страница | Элементы с ID | ¡ виден | Статус |
|----------|---------------|---------|--------|
| **Главная (/)** | — | — | ⬜ (нет элементов с ID) |
| **Тун Шу (/tongshu)** | Tabs, DatePicker, Nav arrows, CalendarGrid cells, Chips | ✅ | Пройден |
| **Справочники (/references)** | Tabs, Search, Filter, Table rows/cells, Action buttons | ✅ | Пройден |
| **Администратор (/admin)** | Switches, Paper containers | ✅ | Пройден |
| **Профили (/profiles)** | Profile cards, birth chart chips, action buttons, dialog | ✅ | Пройден |
| **Главная (/)** | Cards, buttons (Тун Шу, Ци Мэнь, CRM) | ✅ | Пройден |
| **Ци Мэнь (/qimen)** | Title, loading state, page container | ✅ | Пройден |
| **CRM (/crm)** | Title, loading state, page container | ✅ | Пройден |
| **Sidebar (все страницы)** | nav:tab:home/tongshu/qimen/crm/references/admin | ✅ | Пройден |

### Функциональность popup
| Сценарий | Ожидаемый результат | Статус |
|----------|---------------------|--------|
| Клик по ¡ | Открывается popup с ID | ✅ |
| Клик по ID в popup | ID копируется в буфер | ✅ |

### Управление через Администратор
| Сценарий | Ожидаемый результат | Статус |
|----------|---------------------|--------|
| Включить «Показывать ID» | ¡ появляется на всех элементах | ✅ |
| Состояние сохраняется | localStorage (`kmf_element_id_markers`) | ✅ |

---

## 6. API endpoint тесты

### Успешно работают (200 OK)
- `GET /` — root
- `GET /api/tongshu/daily/day` — PostgreSQL
- `GET /api/tongshu/daily/month` — PostgreSQL
- `GET /api/tongshu/daily/week` — PostgreSQL
- `GET /api/tongshu/daily/year` — PostgreSQL
- `GET /api/refs/heavenly-stems` — 10 items
- `GET /api/refs/earthly-branches` — 12 items
- `GET /api/refs/officers` — 12 items
- `GET /api/refs/constellations` — 28 items
- `GET /api/refs/belt-stars` — 12 items
- `GET /api/refs/black-rabbit-stars` — 9 items
- `GET /api/refs/elements` — 5 items
- `GET /api/profiles` — список профилей
- `POST /api/profiles/{id}/calculate-chart` — расчёт карты рождения
- `GET /api/profiles/cities/search` — поиск городов (autocomplete)
- `GET /api/tongshu/personalized/day` — персонализированные данные дня
- `GET /api/fengshui/current` — текущая карта Летящих Звёзд
- `GET /api/fengshui/chart` — карта Летящих Звёзд на дату
- `GET /api/fengshui/directions` — направления Фэн Шуй

### Успешно работают (200 OK) — дополнительно
- `GET /api/crm/clients/` — CRM клиенты
- `GET /api/profiles` — профили
- `GET /api/refs/shensha-config` — 49 записей конфигурации Шэнь Ша
- `PUT /api/refs/shensha-config/{id}` — обновление конфигурации звезды
- `GET /api/tongshu/calendar/day` — возвращает `symbolic_stars` (TongshuDailyData)
- `GET /api/tongshu/calendar/month` — возвращает `symbolic_stars` для каждого дня
- `GET /api/tongshu/calendar/week` — возвращает `symbolic_stars` для каждого дня
- `GET /api/tongshu/hours/{date_str}` — возвращает 12 часовых слотов с ten_god, qi_phase, hidden_stems, symbolic_stars

### Известные проблемы
- `GET /api/qimen/charts/zhirun` — 500 (таблицы `t_qimen_*` не существуют в PostgreSQL; реальные таблицы `t_qumen_*` + `spr_qimen_templates`)
- `GET /api/qimen/current/zhirun` — 500 (таблицы `t_qimen_*` не существуют в PostgreSQL)
- `GET /api/fengshui/current` — 501 Not Implemented
- `GET /api/taiyi/current` — 501 Not Implemented
- `GET /api/bazi/chart` — 501 Not Implemented
| Endpoint | Статус | Причина | Действие |
|----------|--------|---------|----------|
| `GET /api/qimen/charts/zhirun` | ✅ 200 | Исправлено | — |
| `GET /api/qimen/current/zhirun` | ✅ 200 | Исправлено | — |
| `GET /api/crm/clients/` | ✅ 200 | Исправлено | — |
| `GET /api/fengshui/current` | ✅ 200 | Реализовано | — |
| `GET /api/taiyi/current` | 501 | Not Implemented | Требуется реализация |
| `GET /api/bazi/chart` | 501 | Not Implemented | Требуется реализация |

---

## 6. Визуальный чеклист (после каждой правки UI)

### 6.1 Общие проверки
- [ ] Нет ошибок в консоли браузера (F12 → Console).
- [ ] Нет регрессий в layout (сдвиги, обрезания, наложения).
- [ ] Цветовая схема соответствует дизайну (MUI тема).
- [ ] Адаптивность: проверить на ширине 1920px, 1366px, 768px.

### 6.2 Qi Men Page
- [x] **Level tabs:** Час / День / Месяц / Год — переключение работает. ✅
- [x] **DatePicker:** выбор даты, загрузка раскладов. ✅
- [x] **Method toggle:** Джи Жэнь / Чай Бу. ✅
- [x] **QimenGridV2:** 3×3 сетка с цветовым кодированием дворцов по стихиям/направлениям. ✅
- [x] **Directional border:** 12 ветвей с животными и временем вокруг сетки. ✅
- [x] **Palace cells:** Небесный ствол (крупно), земной ствол, звезда, дух, врата — с русскими названиями и пиньинем. ✅
- [x] **Center cell:** Ян/Инь, номер структуры (Ju), тип расклада, система. ✅
- [x] **Indicators:** 值使 (главная звезда), 值符 (главные врата), 伏吟. ✅
- [x] **Summary panel:** Сезон, час, инструмент декады, главная звезда, главные врата, триграммы. ✅
- [x] **PalaceExtendedInfo:** Комбинация стволов (100 combos), сезонная сила, описания. ✅
- [x] **ReferencesPage:** QM ЗВЁЗДЫ, QM ВРАТА, QM ДУХИ, QM КОМБО, QM ТРИГРАММЫ. ✅

### 6.3 TongShu / Day View
- [ ] **Профиль selector:** dropdown с профилями в дневном виде, загрузка списка.
- [ ] **Персонализация:** при выборе профиля отображается баннер с day_master и элементом.
- [ ] **Hidden Stems:** скрытые стволы для всех 4 столбов с процентами и цветовой индикацией (main vs secondary).
- [ ] **Персонализированные 10 Богов:** отображаются для год/месяц/день/час при выбранном профиле.
- [ ] **Персонализированные фазы Ци:** отображаются для год/месяц/день/час при выбранном профиле.
- [x] **Hourly Slots:** 12 двухчасовых слотов, свёрнутые по умолчанию (время + столп), раскрытие для 10 богов, фаз Ци, скрытых стволов, шэнь ша. ✅ (Stage 6)
- [x] **Black Rabbit:** отображение звезды Чёрного Кролика с оценкой. ✅ (Stage 6)
- [x] **Lunar Date:** лунный день + лунный месяц. ✅ (Stage 6)
- [x] **Flying Stars Compact:** summary line «Г: X; М: Y; Д: Z» + компактная 3×3 сетка без часовых звёзд. ✅ (Stage 6)
- [ ] 3 столпа БаЦзы отображаются (день, месяц, год).
- [ ] Номера периодов и элементов видны.
- [ ] Григорианский номер дня + лунный день с фазой.
- [ ] Элементы Наинь в китайских иероглифах.
- [ ] Индикаторы семьи гексаграмм / цепочки порождения.
- [ ] Officer chip, constellation chip, belt chip.
- [ ] Hover-эффект на ячейке.
- [ ] Клик по ячейке переключает на дневной вид.
- [ ] **Комбинации:** индикаторы столкновений/слияний между столпами.
- [x] **Symbolic Stars:** отображение найденных звёзд (tooltip или chip). ✅ (З.4 — добавлен раздел в Справочниках)
- [x] **Symbolic Stars (детальный вид):** блок «Символические звёзды (神煞)» с Chip'ами и tooltip. ✅ (Stage 5.18)
- [x] **Symbolic Stars (week/month view):** колонка «Шэнь Ша» с до 3 звёзд + счётчик. ✅ (Stage 5.18)
- [x] **Symbolic Stars (поиск):** поиск по названиям звёзд в Month View. ✅ (Stage 5.18)
- [ ] **10 Gods:** персонализированные 10 богов для каждого столпа (при выбранном профиле).
- [ ] **Qi Phases:** фазы Ци для каждого столпа (tooltip или мини-иконка).

### 6.3 Profiles Page
- [ ] Список профилей отображается с именем, датой, городом.
- [ ] **Birth Chart Chip:** 4 столба + day_master отображаются на карточке профиля.
- [ ] Кнопка «Рассчитать карту» вызывает API и обновляет карточку.
- [ ] City autocomplete работает (поиск по русскому/английскому названию).
- [ ] При выборе города заполняются lat/lon/timezone.

### 6.4 Навигация
- [ ] Переключение месяцев (стрелки, выпадающий список).
- [ ] Переключение режимов просмотра (день/неделя/месяц/год).
- [ ] Текущий день подсвечивается.

### 6.5 UI Debug IDs (если включены)
- [ ] Значок ¡ отображается на всех элементах с `data-element-id`.
- [ ] Клик по ¡ копирует ID в буфер.

---

## 7. Регрессионный прогон перед закрытием этапа

```bash
# 1. Python тесты
cd /e/Project/Calk_KMF
PYTHONPATH=/e/Project/Calk_KMF /c/Python314/python code/tests/test_tongshu_day_extended.py
PYTHONPATH=/e/Project/Calk_KMF /c/Python314/python code/tests/test_api_endpoints_http.py

# 2. React тесты
cd frontend
npm test -- --watchAll=false

# 3. Линтинг
cd frontend
npx eslint src/components/tongshu/MonthlyCalendar/CalendarGrid.js
```

---

## 8. GitHub Infrastructure Tests

При изменениях, связанных с системой контроля версий (Git) и публикацией на GitHub, выполнять следующие проверки:

| # | Проверка | Команда / Способ | Ожидаемый результат |
|---|----------|------------------|---------------------|
| 8.1 | `.gitignore` существует и исключает лишние файлы | `cat .gitignore` | Файл содержит правила для `node_modules/`, `__pycache__/`, `*.pyc`, `.env`, `*.log`, `*.db`, `*.backup`, `.headroom/`, `.playwright-mcp/`, `.kimi/`, `_gsdata_/` |
| 8.2 | В индекс не попадают исключённые файлы | `git add . && git diff --cached --name-only \| grep -E "node_modules\|__pycache__\|\.env$\|\.log$\|\.db$\|\.backup$"` | Пустой вывод |
| 8.3 | Шаблон коммита настроен | `git config commit.template` | Вывод: `.gitmessage` |
| 8.4 | Файл шаблона коммита существует | `ls .gitmessage` | Файл найден |
| 8.5 | Remote указывает на корректный репозиторий без токена | `git remote -v` | URL `https://github.com/dkfcnm/Calk-KMF.git` без credentials |
| 8.6 | `.git/config` не содержит токен | `grep -i "ghp_" .git/config` | Пустой вывод |
| 8.7 | Коммит проходит с детальным сообщением | `git commit` (без `-m`) | Открывается редактор с шаблоном `.gitmessage` |
| 8.8 | Push в main доступен | `git push origin main` | Успешная отправка (требуется аутентификация) |

### 8.2 Push workflow файлов

При изменении `.github/workflows/*.yml` требуется Personal Access Token с scope `workflow`.
Если push отклонён с ошибкой:
```
refusing to allow a Personal Access Token to create or update workflow ... without `workflow` scope
```
— создай новый токен с scope `workflow` (или `repo`) и используй его для push.

### 8.1 Ручной чеклист перед push

- [ ] Сообщение коммита содержит тип `[ADD]`, `[FIX]`, `[REFACT]`, `[PERF]`, `[TEST]`, `[DOCS]`, `[DB]` или `[CONFIG]`.
- [ ] Сообщение коммита содержит краткое описание (до 72 символов) и подробное описание.
- [ ] В подробном описании указаны: что изменено, почему, какие модули затронуты, результаты тестов.
- [ ] Временные файлы (`*.tmp`, `*.log`, debug-артефакты) не добавлены в коммит.
- [ ] `.git/config` не содержит токенов или паролей.

---

## 9. История изменений

| Дата | Что добавлено/изменено | Автор |
|------|------------------------|-------|
| 2026-06-12 | Добавлен раздел 8 — GitHub Infrastructure Tests. Обновлены чеклисты для Git workflow. | AI Agent |
| 2026-05-24 | Создан мастер-план. Добавлены Python тесты (TongShuDay, API endpoints). Добавлен React тест (CalendarGrid). | AI Agent |
| 2026-05-30 | Этап 5.11: добавлены планы тестов для справочников (shensha, ten_god, phase, combos), комбинаций, symbolic stars, 10 gods, qi phases. Обновлён визуальный чеклист. | AI Agent |
| 2026-05-31 | Stage 5.18: добавлены тесты symbolic_stars в API и UI, синхронизация PostgreSQL, раздел Шэнь Ша в Справочниках. Обновлён bz.md. | AI Agent |
| 2026-05-31 | Phase 2: добавлены тесты для персонализации (hidden_stems, personalized ten_gods/qi_phases), birth chart calculation, city autocomplete, fengshui endpoints. Обновлён API и визуальный чеклист. | AI Agent |
| 2026-05-31 | Stage 6: Расширение дневного представления — hourly slots (collapsed/expandable), Black Rabbit, lunar month, compact Flying Stars. Python 48/48, React 21/21 passed. | AI Agent |

---

---

## 9. Чеклист Stage 5.18 — Шэнь Ша синхронизация и UI

### 9.1 PostgreSQL
- [x] `spr_shensha_config` создана (49 записей)
- [x] `spr_tongshu_shensha_rule.source` добавлена
- [x] `t_tung_shu_daily.symbolic_stars` синхронизирована SQLite → PostgreSQL
- [x] `tongshu_service.py` работает с `t_tung_shu_daily`

### 9.2 API
- [x] `GET /api/tongshu/calendar/day` возвращает `symbolic_stars`
- [x] `GET /api/tongshu/calendar/month` возвращает `symbolic_stars`
- [x] `GET /api/tongshu/calendar/week` возвращает `symbolic_stars`
- [x] `GET /api/refs/shensha-config` возвращает 49 записей
- [x] `PUT /api/refs/shensha-config/{id}` обновляет запись

### 9.3 Frontend
- [x] TongShuPage: детальный вид — блок «Символические звёзды (神煞)»
- [x] TongShuPage: Week View — колонка «Шэнь Ша»
- [x] TongShuPage: Month View — колонка «Шэнь Ша» + поиск
- [x] ReferencesPage: вкладка «ШЕНЬ ША» с редактированием
- [x] Сборка проходит без ошибок

### 9.4 Документация
- [x] `data/ddl_full_schema_raw.sql` обновлён
- [x] `Metodology/postgresql_schema.md` обновлён
- [x] `Metodology/reference_tongshu_methodologies.md` обновлён
- [x] `Metodology/bz.md` создан

---

## 10. Чеклист Stage 6 — Расширение дневного представления

### 10.1 PostgreSQL
- [x] `t_tung_shu_daily.lunar_month` добавлена и заполнена
- [x] `t_tung_shu_daily.black_rabbit_star` добавлена и заполнена (365 дней 2026)
- [x] `t_tung_shu_daily.black_rabbit_score` добавлена и заполнена

### 10.2 API
- [x] `GET /api/tongshu/hours/{date_str}` возвращает 12 слотов с ten_god, qi_phase, hidden_stems, symbolic_stars
- [x] `GET /api/tongshu/daily/day` возвращает black_rabbit_star, black_rabbit_score, lunar_month
- [x] Pydantic schema `TongshuDailyData` обновлена
- [x] Pydantic schema `TongshuHourData` обновлена

### 10.3 Frontend
- [x] TongShuPage: Hourly slots table — collapsed by default, expandable row
- [x] TongShuPage: Black Rabbit chip в основных показателях
- [x] TongShuPage: Lunar day + lunar month в блоке «Луна и фазы»
- [x] TongShuPage: Flying Stars summary line «Г: X; М: Y; Д: Z» + compact grid без hour_star
- [x] FlyingStarsGrid: `compact` prop поддержан
- [x] Сборка проходит без ошибок

### 10.4 Тесты
- [x] Python: 48/48 passed
- [x] React: 21/21 passed
- [x] Build: успешен

| 2026-06-05 | Phase 8: PostgreSQL-only migration — перевод API (refs.py, tongshu_daily_service.py, personalized_service.py) на SQLAlchemy, удаление SQLite fallback, архивирование 50+ скриптов, перевод тестов на PostgreSQL. Python тесты: 38/38 passed (test_tongshu_day_extended, test_analysis_qimen, test_stage6_black_rabbit, test_reference_data, test_combinations, test_symbolic_stars, test_ten_gods, test_qi_phases, test_qimen_pg_service, test_stage6_hourly_api). React тесты: 32/32 passed. Build: успешен. | AI Agent |

---

## 11. Чеклист Phase 8 — PostgreSQL-only Migration

### 11.1 API переведены на PostgreSQL
- [x] `GET /api/refs/officers` — SQLAlchemy
- [x] `GET /api/refs/constellations` — SQLAlchemy
- [x] `GET /api/refs/belt-stars` — SQLAlchemy
- [x] `GET /api/refs/heavenly-stems` — SQLAlchemy
- [x] `GET /api/refs/earthly-branches` — SQLAlchemy
- [x] `GET /api/refs/black-rabbit-stars` — SQLAlchemy
- [x] `GET /api/refs/elements` — SQLAlchemy
- [x] `GET /api/refs/shensha-config` — SQLAlchemy
- [x] `GET /api/tongshu/daily/*` — SQLAlchemy (tongshu_service.py)
- [x] `GET /api/tongshu/personalized/day` — SQLAlchemy

### 11.2 Удаление SQLite fallback
- [x] `code/common/db_config.py` — удалён DB_TYPE, только PostgreSQL
- [x] `code/common/logger.py` — удалён SQLite fallback
- [x] `code/bazi_calendar/db.py` — PostgreSQL-only
- [x] `api/app/services/tongshu_daily_service.py` — удалён

### 11.3 Архивирование
- [x] Диагностические скрипты в корне → `backup/sqlite_scripts/`
- [x] Скрипты миграции → `backup/sqlite_scripts/code_utils/`
- [x] SQLite-генераторы → `backup/sqlite_scripts/scripts/`

### 11.4 Тесты
- [x] `test_tongshu_day_extended.py` — PostgreSQL (pg8000)
- [x] `test_analysis_qimen.py` — PostgreSQL (DBManager)
- [x] `test_stage6_black_rabbit.py` — PostgreSQL-only
- [x] `test_reference_data.py` — ✅ 7/7 passed
- [x] `test_combinations.py` — ✅ 3/3 passed
- [x] `test_symbolic_stars.py` — ✅ 3/3 passed
- [x] `test_ten_gods.py` — ✅ 3/3 passed
- [x] `test_qi_phases.py` — ✅ 3/3 passed
- [x] `test_qimen_pg_service.py` — ✅ 12/12 passed
- [x] `test_stage6_hourly_api.py` — ✅ 5/5 passed

*Последнее обновление: 2026-06-05*
