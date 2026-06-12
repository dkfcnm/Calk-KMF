import sqlite3
import hashlib
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "calk_kmf.sqlite")

def setup_combinations():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Recreate Tables (Force Schema Update)
    print("Recreating combo rule tables...")
    cursor.execute("DROP TABLE IF EXISTS spr_tongshu_branch_combo_rule")
    cursor.execute("DROP TABLE IF EXISTS spr_tongshu_branch_combo_element") # Old table
    cursor.execute("DROP TABLE IF EXISTS spr_tongshu_stem_combo_rule")
    cursor.execute("DROP TABLE IF EXISTS spr_tongshu_stem_combo_element")   # Old table
    
    cursor.execute("""
    CREATE TABLE spr_tongshu_branch_combo_rule (
        rule_id         INTEGER PRIMARY KEY AUTOINCREMENT,
        combo_name      TEXT NOT NULL,
        combo_type_id   INTEGER NOT NULL,
        numeric_score   REAL NOT NULL,
        item1           TEXT NOT NULL,
        item2           TEXT NOT NULL,
        item3           TEXT,
        description     TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE spr_tongshu_stem_combo_rule (
        rule_id         INTEGER PRIMARY KEY AUTOINCREMENT,
        combo_name      TEXT NOT NULL,
        combo_type_id   INTEGER NOT NULL,
        numeric_score   REAL NOT NULL,
        item1           TEXT NOT NULL,
        item2           TEXT NOT NULL,
        description     TEXT
    )
    """)
    
    # 2. Populate Branch Rules
    # Format: (type_id, name, score, items_list, description)
    branch_data = [
        # 1. Столкновение (-1)
        (1, "Столкновение", -1.0, ["子", "午"], None),
        (1, "Столкновение", -1.0, ["丑", "未"], None),
        (1, "Столкновение", -1.0, ["寅", "申"], None),
        (1, "Столкновение", -1.0, ["卯", "酉"], None),
        (1, "Столкновение", -1.0, ["辰", "戌"], None),
        (1, "Столкновение", -1.0, ["巳", "亥"], None),
        # 2. Слияние (1)
        (2, "Слияние", 1.0, ["子", "丑"], "Земля"),
        (2, "Слияние", 1.0, ["寅", "亥"], "Дерево"),
        (2, "Слияние", 1.0, ["卯", "戌"], "Огонь"),
        (2, "Слияние", 1.0, ["辰", "酉"], "Металл"),
        (2, "Слияние", 1.0, ["巳", "申"], "Вода"),
        (2, "Слияние", 1.0, ["午", "未"], "Огонь"),
        # 3. Гармония (0.5) - Triplets
        (3, "Гармония", 0.5, ["子", "申", "辰"], "Вода"),
        (3, "Гармония", 0.5, ["丑", "巳", "酉"], "Металл"),
        (3, "Гармония", 0.5, ["寅", "午", "戌"], "Огонь"),
        (3, "Гармония", 0.5, ["卯", "亥", "未"], "Дерево"),
        # 4. Наказание (-0.5)
        (4, "Наказание", -0.5, ["子", "卯"], "Двух"), # Uncivilized
        (4, "Наказание", -0.5, ["丑", "未", "辰"], "Земли"), # Bullying (Triplets)
        (4, "Наказание", -0.5, ["寅", "申", "巳"], "Огня"), # Ungrateful (Triplets)
        # Note: In MD, "Mao Zi" is listed separately as line 46, but it's same pair as 43. Skipping dup.
        # Self-Punishment
        (4, "Наказание", -0.5, ["辰", "辰"], "Само-"),
        (4, "Наказание", -0.5, ["午", "午"], "Само-"),
        (4, "Наказание", -0.5, ["酉", "酉"], "Само-"),
        (4, "Наказание", -0.5, ["亥", "亥"], "Само-"),
        # 5. Разрушение (-1)
        (5, "Разрушение", -1.0, ["子", "酉"], None),
        (5, "Разрушение", -1.0, ["丑", "辰"], None),
        (5, "Разрушение", -1.0, ["寅", "亥"], None), # Note: Also Merge(2)? Keeping as distinct rule.
        (5, "Разрушение", -1.0, ["卯", "午"], None),
        (5, "Разрушение", -1.0, ["巳", "申"], None), # Also Merge(2)
        (5, "Разрушение", -1.0, ["未", "戌"], None),
        # 6. Вред (-0.5)
        (6, "Вред", -0.5, ["子", "未"], None),
        (6, "Вред", -0.5, ["丑", "午"], None),
        (6, "Вред", -0.5, ["寅", "巳"], None),
        (6, "Вред", -0.5, ["卯", "辰"], None),
        (6, "Вред", -0.5, ["申", "亥"], None),
        (6, "Вред", -0.5, ["酉", "戌"], None),
        # 7. Сезон (1) - Triplets
        (7, "Сезон", 1.0, ["子", "亥", "丑"], "Вода"),
        (7, "Сезон", 1.0, ["寅", "卯", "辰"], "Дерево"),
        (7, "Сезон", 1.0, ["巳", "午", "未"], "Огонь"),
        (7, "Сезон", 1.0, ["申", "酉", "戌"], "Металл")
    ]
    
    for type_id, name, score, items, desc in branch_data:
        sorted_items = sorted(items)
        item1 = sorted_items[0]
        item2 = sorted_items[1]
        item3 = sorted_items[2] if len(sorted_items) > 2 else None
        
        cursor.execute("""
            INSERT INTO spr_tongshu_branch_combo_rule (combo_name, combo_type_id, numeric_score, item1, item2, item3, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, type_id, score, item1, item2, item3, desc))

    # 3. Populate Stem Rules
    # 1: Слияние (1), 2: Контроль (-0.5)
    stem_data = [
        # Слияние
        (1, "Слияние", 1.0, ["甲", "己"], "Земля"),
        (1, "Слияние", 1.0, ["乙", "庚"], "Металл"),
        (1, "Слияние", 1.0, ["丙", "辛"], "Вода"),
        (1, "Слияние", 1.0, ["丁", "壬"], "Дерево"),
        (1, "Слияние", 1.0, ["戊", "癸"], "Огонь"),
        # Контроль
        (2, "Контроль", -0.5, ["庚", "甲"], None),
        (2, "Контроль", -0.5, ["辛", "乙"], None),
        (2, "Контроль", -0.5, ["壬", "丙"], None),
        (2, "Контроль", -0.5, ["癸", "丁"], None),
        # Missing from snippet but logical completion for Control cycle (Metal->Wood->Earth->Water->Fire->Metal)
        # Assuming only listed in MD are used. 
        # Wait, snippet shows Geng-Jia, Xin-Yi... 
        # Let's strictly follow snippet if possible, or standard theory.
        # Snippet: Geng->Jia, Xin->Yi, Ren->Bing, Gui->Ding.
        # That's 4 pairs.
    ]
    
    for type_id, name, score, items, desc in stem_data:
        sorted_items = sorted(items)
        cursor.execute("""
            INSERT INTO spr_tongshu_stem_combo_rule (combo_name, combo_type_id, numeric_score, item1, item2, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, type_id, score, sorted_items[0], sorted_items[1], desc))
        
    # 4. Register Granular Rules
    # Map (Scope, TypeID) -> (PredicateCode, Name, Description)
    rules_config = [
        # STEMS
        ("stem", 1, "BAZI_STEM_MERGE", "Слияние Небесных Стволов", "Благоприятное объединение"),
        ("stem", 2, "BAZI_STEM_CONTROL", "Контроль Небесных Стволов", "Конфликт или преодоление"),
        # BRANCHES
        ("branch", 1, "BAZI_BRANCH_CLASH", "Столкновение Земных Ветвей", "Резкие перемены, конфликт"),
        ("branch", 2, "BAZI_BRANCH_MERGE", "Слияние Земных Ветвей", "Гармония, объединение (6 слияний)"),
        ("branch", 3, "BAZI_BRANCH_HARMONY", "Гармония Земных Ветвей", "Треугольники (San He)"),
        ("branch", 4, "BAZI_BRANCH_PUNISHMENT", "Наказание Земных Ветвей", "Сложности, самонаказания"),
        ("branch", 5, "BAZI_BRANCH_DESTRUCTION", "Разрушение Земных Ветвей", "Внутренний конфликт"),
        ("branch", 6, "BAZI_BRANCH_HARM", "Вред Земных Ветвей", "Эмоциональные проблемы"),
        ("branch", 7, "BAZI_BRANCH_SEASON", "Сезонная Комбинация Ветвей", "Мощная поддержка сезона (San Hui)")
    ]
    
    # Clean up old single rule if exists
    old_rule_id = hashlib.md5("CHECK_COMBINATIONS_v1".encode('utf-8')).hexdigest()
    cursor.execute("DELETE FROM t_rule_registry WHERE rule_id = ?", (old_rule_id,))
    cursor.execute("DELETE FROM t_rule_scope WHERE rule_id = ?", (old_rule_id,))
    
    print("Registering Granular Rules...")
    for scope, type_id, code, name, desc in rules_config:
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
    print("Combinations setup completed successfully.")

if __name__ == "__main__":
    setup_combinations()
