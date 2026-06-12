# Архив этапов (Calk_KMF)

> **Примечание:** Старые записи журнала этапов. Актуальные записи — в `PROJECT.md` раздел 8.

---

## Stage 6 — Расширение дневного представления (2026-05-31)

- **Hourly slots:** 12 двухчасовых слотов в day view (сворачиваемые, с 10 богами, фазами Ци, скрытыми стволами, шэнь ша)
- **Black Rabbit:** Колонки `black_rabbit_star`, `black_rabbit_score`, `lunar_month` в `t_tung_shu_daily` (SQLite + PostgreSQL)
- **Flying Stars compact:** Summary line `Г: X; М: Y; Д: Z` + compact grid без hour_star
- **Тесты:** Python 48/48 passed, React 22/22 passed, build successful

---

## Stage 5.12 — Переработка карточек дней (2026-05-24)

- Расширена `t_tung_shu_daily` (15 новых колонок: lunar_day, nayin, dagua, hexagram_family, production_chain)
- Переработан `CalendarGrid.js` с отображением столпов Бацзы
- Обновлены bat-файлы запуска портала

---

## Stage 5.11 — MCP сервер PostgreSQL (2026-05-16)

- Настроен `@modelcontextprotocol/server-postgres`
- Добавлены ju колонки в `spr_jiazi_extended`
- Исправлен расчет `curr_date` для hourly chart (UTC → LOCAL)
- Верификация против `Smart Tablica 2026`: 68.2% совпадение (классическая методология признана корректной)

---

## Stage 5.10 — Реализация СКДГ правил (2026-02-09)

- 20 правил оценки дат по методу Сюань Кун Да Гуа
- Справочники: `spr_skdg_wuxing_relation` (16 строк), `spr_skdg_hexagram_pairs` (904 строки)
- Результаты: 672K строк (hour-level), 5.7K строк (day-level)

---

## Stage 5.9 — Модуль синхронизации с Яндекс Календарём (2026-02-28)

- CalDAV протокол, библиотека `caldav`
- Генерация событий из Бацзы-данных (753 события)
- Идемпотентность подтверждена
