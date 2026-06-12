import sqlite3
import os
import sys
import hashlib

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

DB_PATH = os.path.join(project_root, "calk_kmf.sqlite")
SOURCE_DB_PATH = os.path.join(project_root, "Metodology", "BD.db")

def setup_yellow_black():
    print("Setting up Yellow & Black Belts...")
    
    if not os.path.exists(SOURCE_DB_PATH):
        print(f"Error: Source DB not found at {SOURCE_DB_PATH}")
        return

    # Connect to both DBs
    conn_src = sqlite3.connect(SOURCE_DB_PATH)
    cursor_src = conn_src.cursor()
    
    conn_dest = sqlite3.connect(DB_PATH)
    cursor_dest = conn_dest.cursor()

    # 1. Create Tables
    print("Creating tables in main DB...")
    
    cursor_dest.execute("DROP TABLE IF EXISTS spr_yellow_black_stars")
    cursor_dest.execute("""
        CREATE TABLE spr_yellow_black_stars (
            id INTEGER PRIMARY KEY,
            name TEXT,
            score REAL
        )
    """)
    
    cursor_dest.execute("DROP TABLE IF EXISTS spr_yellow_black_matrix")
    cursor_dest.execute("""
        CREATE TABLE spr_yellow_black_matrix (
            month_branch TEXT,
            day_branch TEXT,
            star_id INTEGER,
            PRIMARY KEY (month_branch, day_branch)
        )
    """)

    # 2. Migrate Data
    print("Migrating Stars...")
    
    # Define scores based on methodology (Yellow +1, Black -1)
    # Yellow: Qing Long, Ming Tang, Jin Kui, Tian De, Yu Tang, Si Ming
    # Black: Tian Xing, Zhu Que, Bai Hu, Tian Lao, Xuan Wu, Gou Chen
    star_scores = {
        'Зеленый дракон': 1.0,
        'Светлый зал': 1.0,
        'Золотой Замок': 1.0,
        'Драгоценный свет': 1.0,
        'Нефритовый зал': 1.0,
        'Правитель жизни': 1.0, # Or 'Правильтель жизни' check spelling
        
        'Небесное наказание': -1.0,
        'Красный феникс': -1.0, # Check spelling 'феникс' or 'феникc' (cyrillic/latin c)
        'Белый тигр': -1.0,
        'Небесная тюрьма': -1.0,
        'Черная черепаха': -1.0,
        'Абордажный крюк': -1.0
    }
    
    try:
        cursor_src.execute("SELECT id, nm FROM t_spr_yellow_black_belts")
        rows = cursor_src.fetchall()
        for r in rows:
            sid = r[0]
            nm = r[1].strip()
            # Default to 0 if unknown
            score = 0.0
            
            # Normalize for matching: lowercase, replace latin c with cyrillic с
            nm_norm = nm.lower().replace('c', 'с')
            
            for k, v in star_scores.items():
                k_norm = k.lower().replace('c', 'с')
                if k_norm == nm_norm or k_norm in nm_norm:
                    score = v
                    break
            
            cursor_dest.execute("INSERT INTO spr_yellow_black_stars (id, name, score) VALUES (?, ?, ?)", (sid, nm, score))
        print(f"Migrated {len(rows)} stars with inferred scores.")
        
    except Exception as e:
        print(f"Error migrating stars: {e}")
        return

    print("Migrating Matrix...")
    try:
        cursor_src.execute('SELECT "month", "day", "id" FROM t_spr_calendar_yellow_black_belts')
        rows = cursor_src.fetchall()
        for r in rows:
            # Source DB might use different branch chars or same. Assuming same.
            cursor_dest.execute("INSERT INTO spr_yellow_black_matrix (month_branch, day_branch, star_id) VALUES (?, ?, ?)", (r[0], r[1], r[2]))
        print(f"Migrated {len(rows)} matrix entries.")
    except Exception as e:
        print(f"Error migrating matrix: {e}")
        return

    # 3. Register Rule
    print("Registering Rule...")
    rule_code = "CHECK_YELLOW_BLACK"
    rule_name = "Желтый и черный путь"
    rule_desc = "Характеристика дня по методологии Желтого и черного пути"
    rule_id = hashlib.md5(f"{rule_code}_v1".encode('utf-8')).hexdigest()
    
    # Cleanup old if exists
    cursor_dest.execute("DELETE FROM t_rule_registry WHERE predicate_code = ?", (rule_code,))
    
    cursor_dest.execute("""
        INSERT OR REPLACE INTO t_rule_registry (rule_id, name_ru, predicate_code, params_json, score_base, score_formula, description, is_active)
        VALUES (?, ?, ?, '{}', 0, 'dynamic', ?, 1)
    """, (rule_id, rule_name, rule_code, rule_desc))
    
    cursor_dest.execute("""
        INSERT OR REPLACE INTO t_rule_scope (rule_id, scope_type, is_stop)
        VALUES (?, 'date', 0)
    """, (rule_id,))

    conn_dest.commit()
    conn_src.close()
    conn_dest.close()
    print("Yellow & Black Belts setup completed.")

if __name__ == "__main__":
    setup_yellow_black()
