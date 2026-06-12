# Управление правилами анализа (New Architecture)

## Обзор
Система анализа (Date Analysis, Qimen Direction, Activation) построена на едином реестре правил в PostgreSQL. Оценка производится на основе стратегии **SQL-First** и **Hierarchical Analysis**.

## 1. Структура правил (`t_rule_registry`)
Правила хранятся в таблице `t_rule_registry` (PostgreSQL).

### Основные поля:
*   **`rule_id` (TEXT, PK):** Уникальный ID (MD5-хэш или UUID).
*   **`period_type` (TEXT):** **ОБЯЗАТЕЛЬНО.** Уровень расчета (`year`, `month`, `day`, `hour`).
    *   *Принцип:* Если правило не меняется в течение дня, оно должно быть `day` (или `month`/`year`), но не `hour`.
*   **`name_ru` (TEXT):** Название правила.
*   **`predicate_code` (TEXT):** Код проверки (SQL-шаблон или Python-функция).
*   **`params_json` (JSONB):** Параметры (например, `{"heaven": "甲", "earth": "丙"}`).
*   **`score_base` (REAL):** Базовый балл.
*   **`is_active` (INTEGER):** 1 = включено.

## 2. Процесс добавления правила

### Шаг 1: Определение иерархии (Period Type)
Перед созданием правила задайте вопрос: **"Как часто меняется результат этого правила?"**
*   Раз в год -> `year`
*   Раз в месяц -> `month`
*   Раз в день -> `day`
*   Раз в час -> `hour`

**Запрещено** регистрировать медленные правила (например, "День сталкивается с Годом") как `hour`.

### Шаг 2: Реализация (SQL-First)
Приоритет отдается правилам, реализуемым через `INSERT INTO ... SELECT ... JOIN`.
Python-логика используется только для сверхсложных вычислений.

### Шаг 3: Регистрация (SQL)
Пример добавления правила для структур Ци Мэнь (Часовой уровень):

```sql
INSERT INTO t_rule_registry (
    rule_id, period_type, name_ru, predicate_code, 
    params_json, score_base, is_active
) VALUES (
    md5('qimen_structure_wood_fire'), 
    'hour', 
    'Дерево рождает Огонь', 
    'CHECK_QIMEN_STEMS',
    '{"heaven": "甲", "earth": "丙"}',
    10, 
    1
);
```

### Шаг 4: Привязка к области (Scope)
```sql
INSERT INTO t_rule_scope (rule_id, scope_type, is_stop)
VALUES (md5('qimen_structure_wood_fire'), 'direction', 0);
```

## 3. Запуск расчета
Расчет выполняется скриптом `code/analysis/run_analysis.py`.
Скрипт автоматически:
1.  Очищает таблицы результатов (`t_analysis_direction_hour` и т.д.) для выбранного года.
2.  Выполняет расчет каскадом: Year -> Month -> Day -> Hour.
3.  Использует `period_type` для выбора соответствующих правил на каждом этапе.

## 4. Результаты
Результаты сохраняются в иерархические таблицы:
*   `t_analysis_year`
*   `t_analysis_month`
*   `t_analysis_day` / `t_analysis_direction_day`
*   `t_analysis_hour` / `t_analysis_direction_hour`

