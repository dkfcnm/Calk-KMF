import sqlite3
import sys

# Fix console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DB_PATH = os.path.join(PROJECT_ROOT, "calk_kmf.sqlite")

def create_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Создаем таблицу шаблонов
    # Один шаблон = 9 строк (по одной на дворец)
    sql = """
    CREATE TABLE IF NOT EXISTS spr_qimen_templates (
        template_id TEXT PRIMARY KEY,   -- Hash(rasklad_id + palace_no) - Уникальный ID записи
        rasklad_id TEXT,                -- ID Расклада (например, 'Yang_1_甲子') - Группировочный ключ
        
        yin_yang TEXT,          -- 'Yang' или 'Yin'
        ju_num INTEGER,         -- 1-9
        hour_stem_branch TEXT,  -- Столп часа (например, '甲子')
        
        palace_no INTEGER,      -- 1-9
        
        structure TEXT,         -- Небесный ствол + Земной ствол
        heaven_stem TEXT,       -- Небесный ствол
        is_fou_tou_heaven INTEGER, -- Флаг Фу Тоу Неба (true/false -> 1/0)
        
        earth_stem TEXT,        -- Земной ствол
        is_fou_tou_earth INTEGER, -- Флаг Фу Тоу Земли (true/false -> 1/0)
        
        star TEXT,              -- Звезда
        is_main_star INTEGER,   -- Флаг главной звезды
        
        gate TEXT,              -- Ворота
        is_main_gate INTEGER,   -- Флаг главных врат
        
        spirit TEXT             -- Дух
    );
    """
    cursor.execute(sql)
    
    # Индексы
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_qimen_templates_search ON spr_qimen_templates (yin_yang, ju_num, hour_stem_branch)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_qimen_templates_rasklad ON spr_qimen_templates (rasklad_id)")
    
    conn.commit()
    conn.close()
    print("Table spr_qimen_templates created.")

if __name__ == "__main__":
    create_table()
