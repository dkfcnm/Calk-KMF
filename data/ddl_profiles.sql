-- DDL для модуля профилей (Phase 2.1)
-- Создан: 2025-05-24

-- Основная таблица профилей
CREATE TABLE IF NOT EXISTS t_profile (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    birth_date DATE NOT NULL,
    birth_time TIME,
    birth_city VARCHAR(255),
    birth_city_lat DECIMAL(10, 7),
    birth_city_lon DECIMAL(10, 7),
    birth_timezone VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Комментарии к таблице и колонкам
COMMENT ON TABLE t_profile IS 'Профили пользователей для персонализированных расчетов';
COMMENT ON COLUMN t_profile.name IS 'Имя человека';
COMMENT ON COLUMN t_profile.birth_date IS 'Дата рождения';
COMMENT ON COLUMN t_profile.birth_time IS 'Время рождения';
COMMENT ON COLUMN t_profile.birth_city IS 'Город рождения';
COMMENT ON COLUMN t_profile.birth_city_lat IS 'Широта города рождения';
COMMENT ON COLUMN t_profile.birth_city_lon IS 'Долгота города рождения';
COMMENT ON COLUMN t_profile.birth_timezone IS 'Часовой пояс (IANA)';
COMMENT ON COLUMN t_profile.notes IS 'Заметки';

-- Индексы
CREATE INDEX IF NOT EXISTS idx_profile_name ON t_profile(name);
CREATE INDEX IF NOT EXISTS idx_profile_birth_date ON t_profile(birth_date);

-- Триггер для обновления updated_at
CREATE OR REPLACE FUNCTION update_profile_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_profile_updated_at ON t_profile;
CREATE TRIGGER trg_profile_updated_at
    BEFORE UPDATE ON t_profile
    FOR EACH ROW
    EXECUTE FUNCTION update_profile_updated_at();

-- Таблица рожденных карт (8 столпов)
CREATE TABLE IF NOT EXISTS t_profile_birth_chart (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES t_profile(id) ON DELETE CASCADE,
    year_pillar VARCHAR(10),
    month_pillar VARCHAR(10),
    day_pillar VARCHAR(10),
    hour_pillar VARCHAR(10),
    day_master VARCHAR(10),
    day_master_element VARCHAR(20),
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_profile_birth_chart UNIQUE (profile_id)
);

COMMENT ON TABLE t_profile_birth_chart IS 'Рассчитанные карты рождения (8 столпов)';

-- Таблица истории обращений к профилю
CREATE TABLE IF NOT EXISTS t_profile_history (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES t_profile(id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL,
    module VARCHAR(50),
    reference_date DATE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE t_profile_history IS 'История обращений к профилю';

CREATE INDEX IF NOT EXISTS idx_profile_history_profile_id ON t_profile_history(profile_id);
CREATE INDEX IF NOT EXISTS idx_profile_history_created_at ON t_profile_history(created_at);
