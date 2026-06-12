import sqlite3
import hashlib
import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "calk_kmf.sqlite")

def ensure_column_exists(conn, table, column, col_type):
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = {row[1] for row in cursor.fetchall()}
    if column not in columns:
        print(f"Adding column {column} to {table}...")
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")

def setup_guigu():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Ensure Schema
    ensure_column_exists(conn, "spr_heavenly_stem", "guigu_score", "INTEGER")
    ensure_column_exists(conn, "spr_earthly_branch", "guigu_score", "INTEGER")
    ensure_column_exists(conn, "spr_tongshu_guigu_outcome", "numeric_score", "REAL DEFAULT 0")
    
    # 2. Populate Scores (Table 1)
    # Stems: 甲(1) 己(6) -> 9; 乙(2) 庚(7) -> 8; 丙(3) 辛(8) -> 7; 丁(4) 壬(9) -> 6; 戊(5) 癸(10) -> 5
    stem_scores = {
        (1, 6): 9,
        (2, 7): 8,
        (3, 8): 7,
        (4, 9): 6,
        (5, 10): 5
    }
    for ids, score in stem_scores.items():
        placeholders = ','.join('?' * len(ids))
        cursor.execute(f"UPDATE spr_heavenly_stem SET guigu_score = ? WHERE stem_id IN ({placeholders})", (score, *ids))
        
    # Branches: 子(1) 午(7) -> 9; 丑(2) 未(8) -> 8; 寅(3) 申(9) -> 7; 卯(4) 酉(10) -> 6; 辰(5) 戌(11) -> 5; 巳(6) 亥(12) -> 4
    branch_scores = {
        (1, 7): 9,
        (2, 8): 8,
        (3, 9): 7,
        (4, 10): 6,
        (5, 11): 5,
        (6, 12): 4
    }
    for ids, score in branch_scores.items():
        placeholders = ','.join('?' * len(ids))
        cursor.execute(f"UPDATE spr_earthly_branch SET guigu_score = ? WHERE branch_id IN ({placeholders})", (score, *ids))

    # 3. Populate Outcomes (Table 2)
    # Clear old data
    cursor.execute("DELETE FROM spr_tongshu_guigu_outcome")
    
    outcomes = [
        (13, "Солнечный свет (Ри гуан сянь)", "1", "Благоприятный свет солнца.", 1.0),
        (14, "День счастья (Ри тянь сянь)", "-1", "Считается счастливым, но канонический текст «Се Цзи» называет его Духом Бедствий и Катастроф (неблагоприятно).", -1.0),
        (15, "Лунное Сияние (Юэ гуан сянь)", "1", "Благоприятное влияние луны.", 1.0),
        (16, "Золото и Яшма (Цзинь юй сянь)", "1", "Богатство, знатность, благородство.", 1.0),
        (17, "Истребление ворот (Ме мэнь сянь)", "-1", "Крайне опасно; риск уничтожения семьи или рода.", -1.0),
        (18, "Небесная добродетель (Тянь дэ сянь)", "1", "Высокая защита и удача.", 1.0),
        (19, "Небесное несчастье (Тянь сюн шэнь)", "-1", "Дух небесного зла.", -1.0),
        (20, "Земное несчастье (Ди сюн шэнь)", "-1", "Дух земного зла.", -1.0),
        (21, "Жертва Государству (Чжай го сянь)", "-1", "Неблагоприятно для личных дел.", -1.0),
        (22, "Земные сокровища (Ди бао сянь)", "1", "Обретение ресурсов и достатка.", 1.0),
        (23, "Врата Смерти (Сы мэнь сянь)", "-1", "Крайне неблагоприятный период.", -1.0),
        (24, "Благословение / Нишэнь", "1", "Дух благословения и удачи.", 1.0),
        (25, "Великое Добро (Да шань сянь)", "1", "Позитивный исход дел.", 1.0),
        (26, "Великое Благоденствие (Да цзи сянь)", "1", "Святой отшельник, приносящий большое счастье.", 1.0)
    ]
    
    cursor.executemany("""
        INSERT INTO spr_tongshu_guigu_outcome (outcome_number, name_ru, verdict_code, description_ru, numeric_score)
        VALUES (?, ?, ?, ?, ?)
    """, outcomes)
    
    # 4. Register Rule
    predicate_code = "CHECK_GUIGU_NUMBER"
    name_ru = "Числовой метод Гуйгуцзы"
    description = "Характеристика дня по числовому Гуйгуцзы"
    rule_id = hashlib.md5(f"{predicate_code}_v1".encode('utf-8')).hexdigest()
    
    print(f"Registering Rule: {rule_id} ({name_ru})")
    cursor.execute("""
        INSERT OR REPLACE INTO t_rule_registry (rule_id, name_ru, predicate_code, params_json, score_base, score_formula, description, is_active)
        VALUES (?, ?, ?, '{}', 0, 'dynamic', ?, 1)
    """, (rule_id, name_ru, predicate_code, description))
    
    cursor.execute("""
        INSERT OR REPLACE INTO t_rule_scope (rule_id, scope_type, is_stop)
        VALUES (?, 'date', 0)
    """, (rule_id,))
    
    conn.commit()
    conn.close()
    print("Guigu setup completed successfully.")

if __name__ == "__main__":
    setup_guigu()
