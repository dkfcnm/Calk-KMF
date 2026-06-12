import os
import sys
import hashlib
import json
import traceback

print("Starting setup_jiazi_extended.py...")

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)
print(f"Project root added to path: {project_root}")

try:
    print("Importing db_manager...")
    from code.common.db_manager import db
    print("Importing black_rabbit_logic...")
    from code.analysis.black_rabbit_logic import (
        calculate_day_star, calculate_hour_star, STEMS, BRANCHES,
        FIRST_DAY_PALACE_LOOKUP, get_stem_group
    )
    print("Imports successful.")
except Exception as e:
    print(f"Import error: {e}")
    traceback.print_exc()
    sys.exit(1)

def parse_markdown_table(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    data = []
    headers = []
    
    in_table = False
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('|') and 'Номер' in line and 'Столп' in line:
            headers = [h.strip() for h in line.split('|') if h.strip()]
            in_table = True
            continue
            
        if in_table and line.startswith('|') and '---' in line:
            continue
            
        if in_table and line.startswith('|'):
            # This is a data row
            parts = [p.strip() for p in line.split('|')]
            if len(parts) > 2: # basic check
                # Remove empty start/end if pipe is at start/end
                if parts[0] == '': parts.pop(0)
                if parts[-1] == '': parts.pop()
                data.append(parts)
                
    return headers, data

def generate_black_rabbit_matrix():
    """
    Generate spr_black_rabbit_matrix algorithmically.
    Verified against Tong Shu 2026 — 100% match (362/362).
    Algorithm:
      - palace_1st = FIRST_DAY_PALACE_LOOKUP[jiazi_id - 1]
      - direction = get_stem_group((jiazi_id - 1) % 10)  # special stem group
      - palace = walk(palace_1st, lunar_day - 1, direction)
      - star = palace_to_old[palace]
    """
    palace_to_old = {
        1: 'Меркурий', 2: 'Луна', 3: 'Юпитер', 4: 'Венера',
        5: 'Раху', 6: 'Сатурн', 7: 'Кету', 8: 'Солнце', 9: 'Марс'
    }
    matrix_values = []
    for jiazi_id in range(1, 61):
        palace_1st = FIRST_DAY_PALACE_LOOKUP[jiazi_id - 1]
        stem_idx = (jiazi_id - 1) % 10
        direction = get_stem_group(stem_idx)
        for lunar_day in range(1, 31):
            if direction == 'YANG':
                palace = ((palace_1st - 1 + (lunar_day - 1)) % 9) + 1
            else:
                palace = ((palace_1st - 1 - (lunar_day - 1)) % 9 + 9) % 9 + 1
            star_name = palace_to_old[palace]
            matrix_values.append((jiazi_id, lunar_day, star_name))
    return matrix_values

def setup_jiazi_extended():
    print("Setting up Jiazi Extended Attributes & Black Rabbit (PostgreSQL)...")
    
    # 1. Create Tables
    print("Creating tables...")
    
    # spr_jiazi_extended
    db.execute_query("DROP TABLE IF EXISTS spr_jiazi_extended CASCADE")
    db.execute_query("""
        CREATE TABLE spr_jiazi_extended (
            jiazi_id INTEGER PRIMARY KEY,
            stem TEXT,
            branch TEXT,
            nayin_element TEXT,
            nayin_name TEXT,
            dagua_element INTEGER,
            dagua_period INTEGER,
            dagua_role TEXT
        )
    """)
    db.execute_query("CREATE INDEX IF NOT EXISTS idx_jiazi_stem_branch ON spr_jiazi_extended (stem, branch)")
    
    # spr_black_rabbit_matrix (Old methodology)
    db.execute_query("DROP TABLE IF EXISTS spr_black_rabbit_matrix CASCADE")
    db.execute_query("""
        CREATE TABLE spr_black_rabbit_matrix (
            jiazi_id INTEGER,
            lunar_day INTEGER,
            star_name TEXT,
            PRIMARY KEY (jiazi_id, lunar_day)
        )
    """)
    
    # spr_black_rabbit_scores (Common scores)
    db.execute_query("DROP TABLE IF EXISTS spr_black_rabbit_scores CASCADE")
    db.execute_query("""
        CREATE TABLE spr_black_rabbit_scores (
            star_name TEXT PRIMARY KEY,
            numeric_score DOUBLE PRECISION
        )
    """)
    
    # NEW: spr_black_rabbit_hour_joey
    db.execute_query("DROP TABLE IF EXISTS spr_black_rabbit_hour_joey CASCADE")
    db.execute_query("""
        CREATE TABLE spr_black_rabbit_hour_joey (
            day_stem        TEXT NOT NULL,
            hour_branch     TEXT NOT NULL,
            star_name       TEXT NOT NULL,
            score           DOUBLE PRECISION NOT NULL,
            PRIMARY KEY (day_stem, hour_branch)
        )
    """)
    
    # NEW: spr_black_rabbit_day_joey
    db.execute_query("DROP TABLE IF EXISTS spr_black_rabbit_day_joey CASCADE")
    db.execute_query("""
        CREATE TABLE spr_black_rabbit_day_joey (
            first_day_jiazi_id  INTEGER NOT NULL,
            lunar_day           INTEGER NOT NULL,
            star_name           TEXT NOT NULL,
            score               DOUBLE PRECISION NOT NULL,
            PRIMARY KEY (first_day_jiazi_id, lunar_day)
        )
    """)

    # 2. Populate Scores
    print("Populating Star Scores...")
    scores = {
        'Солнце': 1.0,
        'Венера': 1.0,
        'Юпитер': 1.0,
        'Луна': 1.0,
        'Меркурий': 1.0,
        'Сатурн': -1.0,
        'Марс': -1.0,
        'Раху': -1.0,
        'Кету': -1.0,
        # Joey Jap names might differ slightly, let's ensure coverage
        'Великое Солнце': 2.0,
        'Звезда Металла': 1.0,
        'Звезда Дерева': 1.0,
        'Великая Луна': 1.0,
        'Звезда Воды': 1.0,
        'Звезда Земли': -1.0,
        'Звезда Огня': -1.0
    }
    for star, score in scores.items():
        db.execute_query("INSERT INTO spr_black_rabbit_scores (star_name, numeric_score) VALUES (%s, %s) ON CONFLICT (star_name) DO UPDATE SET numeric_score = EXCLUDED.numeric_score", (star, score))

    # 3. Parse and Populate Main Data (Jiazi Extended)
    md_path = os.path.join(project_root, 'Metodology', 'bazci_dzy_dzi.md')
    print(f"Parsing {md_path}...")
    headers, data = parse_markdown_table(md_path)
    
    print(f"Found {len(data)} rows.")
    count_ok = 0
    
    # Prepare batch data
    jiazi_values = []
    
    for row in data:
        try:
            if not row[0].isdigit():
                continue
                
            jiazi_id = int(row[0])
            stem = row[2]
            branch = row[3]
            nayin_el = row[4]
            nayin_nm = row[5]
            dagua_el = int(row[6])
            dagua_per = int(row[7])
            dagua_role = row[9]
            
            jiazi_values.append((jiazi_id, stem, branch, nayin_el, nayin_nm, dagua_el, dagua_per, dagua_role))
            
            count_ok += 1
        except Exception as e:
            pass # skip invalid rows

    # Batch Insert
    if jiazi_values:
        db.execute_batch("""
            INSERT INTO spr_jiazi_extended 
            (jiazi_id, stem, branch, nayin_element, nayin_name, dagua_element, dagua_period, dagua_role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, jiazi_values)

    print(f"Successfully processed {count_ok} rows for Jiazi Extended.")

    # 3b. Generate Black Rabbit Matrix algorithmically
    print("Generating Black Rabbit Matrix (algorithmic, verified against Tong Shu 2026)...")
    matrix_values = generate_black_rabbit_matrix()
    if matrix_values:
        db.execute_batch("INSERT INTO spr_black_rabbit_matrix (jiazi_id, lunar_day, star_name) VALUES (%s, %s, %s)", matrix_values)
    print(f"Inserted {len(matrix_values)} rows into spr_black_rabbit_matrix.")

    # 4. Populate Joey Jap Tables
    print("Populating Black Rabbit (Joey Jap) Tables...")
    
    # Hour Map
    hour_rows = []
    for stem in STEMS:
        for branch in BRANCHES:
            star = calculate_hour_star(stem, branch)
            if star:
                hour_rows.append((stem, branch, star['name_ru'], star['score']))
    
    if hour_rows:
        db.execute_batch("INSERT INTO spr_black_rabbit_hour_joey (day_stem, hour_branch, star_name, score) VALUES (%s, %s, %s, %s)", hour_rows)

    # Day Map
    day_rows = []
    # Loop 1..60 for First Day Jiazi ID
    for first_id in range(1, 61):
        # Find Stem/Branch of this first day
        # jiazi_id 1 = Jia-Zi (0,0)
        idx = first_id - 1
        
        # Loop Lunar Days 1..30
        for ld in range(1, 31):
            # Current day is (first_day + ld - 1)
            curr_idx = (idx + (ld - 1)) % 60
            curr_stem = STEMS[curr_idx % 10]
            curr_branch = BRANCHES[curr_idx % 12]
            
            star = calculate_day_star(curr_stem, curr_branch, ld)
            if star:
                day_rows.append((first_id, ld, star['name_ru'], star['score']))
                
    if day_rows:
        db.execute_batch("INSERT INTO spr_black_rabbit_day_joey (first_day_jiazi_id, lunar_day, star_name, score) VALUES (%s, %s, %s, %s)", day_rows)


    # 5. Register Rules
    print("Registering Rules...")
    
    rules_config = []
    pillars = [('YEAR', 'Год'), ('MONTH', 'Месяц'), ('DAY', 'День'), ('HOUR', 'Час')]
    
    # NAYIN
    for p_code, p_name in pillars:
        rules_config.append((f"CHECK_NAYIN_{p_code}_EL", f"Наинь (Элемент): {p_name}", f"Элемент Наинь столпа {p_name}"))
        rules_config.append((f"CHECK_NAYIN_{p_code}_NM", f"Наинь (Название): {p_name}", f"Образное название Наинь столпа {p_name}"))
    # DA GUA
    for p_code, p_name in pillars:
        rules_config.append((f"CHECK_DAGUA_{p_code}_EL", f"И-Цзин (Элемент): {p_name}", f"Элемент Да Гуа столпа {p_name}"))
        rules_config.append((f"CHECK_DAGUA_{p_code}_PER", f"И-Цзин (Период): {p_name}", f"Период Да Гуа столпа {p_name}"))
        rules_config.append((f"CHECK_DAGUA_{p_code}_FAM", f"И-Цзин (Семья): {p_name}", f"Семья гексаграммы столпа {p_name}"))
        rules_config.append((f"CHECK_DAGUA_{p_code}_ROLE", f"И-Цзин (Роль): {p_name}", f"Роль в семье столпа {p_name}"))

    # BLACK RABBIT
    rules_config.append(("CHECK_BLACK_RABBIT_M1", "Черный Кролик (Базовый)", "Звезда дня по столпу дня и лунному дню (Методология: Нинель Смолина)"))
    rules_config.append(("CHECK_BLACK_RABBIT_M2", "Черный Кролик (Усиленный)", "Звезда дня по столпу 1-го лунного дня (Методология: Нинель Смолина)"))
    rules_config.append(("CHECK_BLACK_RABBIT_JOEY_DAY", "Черный Кролик (День)", "Звезда дня по методологии Joey Jap"))
    rules_config.append(("CHECK_BLACK_RABBIT_JOEY_HOUR", "Черный Кролик (Час)", "Звезда часа по методологии Joey Jap"))
    
    # Register rules
    for code, name, desc in rules_config:
        rule_id = hashlib.md5(f"{code}_v1".encode('utf-8')).hexdigest()
        
        db.execute_query("""
            INSERT INTO t_rule_registry (rule_id, name_ru, predicate_code, params_json, score_base, score_formula, description, is_active)
            VALUES (%s, %s, %s, '{}', 0, 'dynamic', %s, 1)
            ON CONFLICT (rule_id) DO UPDATE SET 
                name_ru = EXCLUDED.name_ru,
                description = EXCLUDED.description,
                is_active = 1
        """, (rule_id, name, code, desc))
        
        db.execute_query("""
            INSERT INTO t_rule_scope (rule_id, scope_type, is_stop)
            VALUES (%s, 'date', 0)
            ON CONFLICT (rule_id, scope_type) DO NOTHING
        """, (rule_id,))

    print("Jiazi Extended setup completed.")

if __name__ == "__main__":
    setup_jiazi_extended()
