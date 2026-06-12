-- =============================================================================
-- Исправление битого Foreign Key в t_chart_analysis
-- Проблема: FK ссылается на несуществующую таблицу spr_indicator_rule
-- Решение: Переключить FK на существующую таблицу spr_indicator
-- =============================================================================

-- 1. Удаляем старый FK, если он существует
-- (PostgreSQL требует знания имени constraint)
DO $$
DECLARE
    fk_name TEXT;
BEGIN
    SELECT tc.constraint_name INTO fk_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
    WHERE tc.table_name = 't_chart_analysis'
      AND tc.constraint_type = 'FOREIGN KEY'
      AND kcu.column_name = 'indicator_id';

    IF fk_name IS NOT NULL THEN
        EXECUTE format('ALTER TABLE t_chart_analysis DROP CONSTRAINT %I', fk_name);
        RAISE NOTICE 'Dropped old FK: %', fk_name;
    END IF;
END $$;

-- 2. Создаем новый FK на spr_indicator (если еще не существует)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE table_name = 't_chart_analysis'
          AND constraint_name = 'fk_t_chart_analysis_indicator_id'
    ) THEN
        ALTER TABLE t_chart_analysis
        ADD CONSTRAINT fk_t_chart_analysis_indicator_id
        FOREIGN KEY (indicator_id) REFERENCES spr_indicator(indicator_id);
        RAISE NOTICE 'Created new FK on spr_indicator';
    END IF;
END $$;
