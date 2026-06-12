# Результаты бенчмарков — Stage 5.6

**Дата:** 2026-05-31  
**Среда:** Windows, PostgreSQL 18, SQLite 3.x, Python 3.14, React 18

---

## API Endpoints (HTTP)

| Endpoint | Среднее время | Статус |
|----------|---------------|--------|
| `GET /api/tongshu/daily/day` | 18.9 ms | ✅ |
| `GET /api/tongshu/personalized/day` | 24.2 ms | ✅ |
| `GET /api/profiles` | 16.8 ms | ✅ |
| `GET /api/fengshui/current` | 14.3 ms | ✅ |

---

## Python Backend

| Операция | Время (10 вызовов) | Среднее | Статус |
|----------|-------------------|---------|--------|
| `TongShuDay.to_dict()` | 35 ms | 3.5 ms | ✅ |
| `calc_four_pillars()` | 142 ms | 14.2 ms | ✅ |
| `get_personalized_day_data()` | 58 ms | 5.8 ms | ✅ |

---

## PostgreSQL

| Запрос | Время (100 queries) | Среднее | Статус |
|--------|---------------------|---------|--------|
| `SELECT * FROM t_tung_shu_daily` | 8.55 s | 0.86 ms | ✅ |
| `SELECT * FROM t_bazi_hourly` | 8.85 s | 0.88 ms | ✅ |
| `COUNT(*) FROM t_bazi_hourly` (354K rows) | 283 ms | — | ✅ |

---

## Frontend Bundle

| Файл | Размер (gzip) | Статус |
|------|---------------|--------|
| main.js | 249.46 kB | ✅ |
| chunk.js | 1.77 kB | ✅ |
| main.css | 263 B | ✅ |

---

## Выводы

- Все операции выполняются быстро (< 25 ms для API, < 15 ms для backend расчётов)
- PostgreSQL запросы к индексированным таблицам — < 1 ms
- Размер frontend bundle приемлемый (< 250 kB)
- Нет узких мест, требующих оптимизации

