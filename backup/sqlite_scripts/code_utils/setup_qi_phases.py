import sqlite3
import os
import sys
import hashlib
import re

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

DB_PATH = os.path.join(project_root, "calk_kmf.sqlite")

def setup_qi_phases():
    print("Setting up Bazi Qi Phases...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create Dictionary Table
    print("Creating table spr_bazi_qi_phase...")
    cursor.execute("DROP TABLE IF EXISTS spr_bazi_qi_phase")
    cursor.execute("""
        CREATE TABLE spr_bazi_qi_phase (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stem_char TEXT NOT NULL,
            branch_char TEXT NOT NULL,
            phase_id INTEGER NOT NULL,
            phase_name TEXT NOT NULL,
            numeric_score REAL DEFAULT 0
        )
    """)
    cursor.execute("CREATE INDEX idx_qi_phase_stem_branch ON spr_bazi_qi_phase (stem_char, branch_char)")

    # 2. Parse Markdown Data
    # Hardcoding the table structure from the file to ensure stability if file moves
    # Columns: ID, Name, Score, Empty, 甲, 乙, 丙, 丁, 戊, 己, 庚, 辛, 壬, 癸
    stems = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    
    # Row format: (PhaseID, Name, Score, [Branches for each stem...])
    data_rows = [
        (1, "Рождение", 1.0, ['亥', '午', '寅', '酉', '寅', '酉', '巳', '子', '申', '卯']),
        (2, "Купание", 0.0, ['子', '巳', '卯', '申', '卯', '申', '午', '亥', '酉', '寅']), # Score empty in file -> 0
        (3, "Шапка и пояс", 1.0, ['丑', '辰', '辰', '未', '辰', '未', '未', '戌', '戌', '丑']),
        (4, "Поступление на службу", 1.0, ['寅', '卯', '巳', '午', '巳', '午', '申', '酉', '亥', '子']),
        (5, "Пик рассвета", 1.0, ['卯', '寅', '午', '巳', '午', '巳', '酉', '申', '子', '亥']), # FIXED: 庚 (idx 6) is 酉, not 寅
        (6, "Увядание", 0.5, ['辰', '丑', '未', '辰', '未', '辰', '戌', '未', '丑', '戌']),
        (7, "Болезнь", 0.5, ['巳', '子', '申', '卯', '申', '卯', '亥', '午', '寅', '酉']),
        (8, "Смерть", 0.0, ['午', '亥', '酉', '寅', '酉', '寅', '子', '巳', '卯', '申']),
        (9, "Могила", 0.0, ['未', '戌', '戌', '丑', '戌', '丑', '丑', '辰', '辰', '未']),
        (10, "Обрыв", 0.0, ['申', '酉', '亥', '子', '亥', '子', '寅', '卯', '巳', '午']),
        (11, "Зачатие", 0.5, ['酉', '申', '子', '亥', '子', '亥', '卯', '寅', '午', '巳']),
        (12, "Вынашивание", 0.5, ['戌', '未', '丑', '戌', '丑', '戌', '辰', '丑', '未', '辰'])
    ]

    print("Populating spr_bazi_qi_phase...")
    count = 0
    for phase_id, phase_name, score, branches in data_rows:
        for idx, branch in enumerate(branches):
            stem = stems[idx]
            cursor.execute("""
                INSERT INTO spr_bazi_qi_phase (stem_char, branch_char, phase_id, phase_name, numeric_score)
                VALUES (?, ?, ?, ?, ?)
            """, (stem, branch, phase_id, phase_name, score))
            count += 1
    
    print(f"Inserted {count} combinations.")

    # 3. Register Rules
    # Group A: Day Master (Day Stem) -> Pillar Branch
    # Group B: Pillar Stem -> Pillar Branch
    
    rules_config = [
        # GROUP A (Day Master)
        ("CHECK_QI_PHASE_DM_YEAR", "Фаза Ци (ЭЛ): Год", "Фаза Ци Элемента Личности в Земной Ветви Года"),
        ("CHECK_QI_PHASE_DM_MONTH", "Фаза Ци (ЭЛ): Месяц", "Фаза Ци Элемента Личности в Земной Ветви Месяца"),
        ("CHECK_QI_PHASE_DM_DAY", "Фаза Ци (ЭЛ): День", "Фаза Ци Элемента Личности в Земной Ветви Дня"),
        ("CHECK_QI_PHASE_DM_HOUR", "Фаза Ци (ЭЛ): Час", "Фаза Ци Элемента Личности в Земной Ветви Часа"),
        
        # GROUP B (Pillar Strength)
        ("CHECK_QI_PHASE_PILLAR_YEAR", "Фаза Ци (Столп): Год", "Фаза Ци НС Года в ЗВ Года"),
        ("CHECK_QI_PHASE_PILLAR_MONTH", "Фаза Ци (Столп): Месяц", "Фаза Ци НС Месяца в ЗВ Месяца"),
        ("CHECK_QI_PHASE_PILLAR_DAY", "Фаза Ци (Столп): День", "Фаза Ци НС Дня в ЗВ Дня"),
        ("CHECK_QI_PHASE_PILLAR_HOUR", "Фаза Ци (Столп): Час", "Фаза Ци НС Часа в ЗВ Часа")
    ]

    print("Registering Rules...")
    # Clean old rules if any
    cursor.execute("DELETE FROM t_rule_registry WHERE predicate_code LIKE 'CHECK_QI_PHASE_%'")
    cursor.execute("DELETE FROM t_rule_scope WHERE rule_id IN (SELECT rule_id FROM t_rule_registry WHERE predicate_code LIKE 'CHECK_QI_PHASE_%')") # Logic for cascade

    for code, name, desc in rules_config:
        rule_id = hashlib.md5(f"{code}_v1".encode('utf-8')).hexdigest()
        print(f"  - {code}: {rule_id}")
        
        cursor.execute("""
            INSERT OR REPLACE INTO t_rule_registry (rule_id, name_ru, predicate_code, params_json, score_base, score_formula, description, is_active)
            VALUES (?, ?, ?, '{}', 0, 'dynamic', ?, 1)
        """, (rule_id, name, code, desc))
        
        cursor.execute("""
            INSERT OR REPLACE INTO t_rule_scope (rule_id, scope_type, is_stop)
            VALUES (?, 'date', 0)
        """, (rule_id,))

    conn.commit()
    conn.close()
    print("Qi Phases setup completed.")

if __name__ == "__main__":
    setup_qi_phases()
