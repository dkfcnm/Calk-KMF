import sqlite3
import hashlib
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "calk_kmf.sqlite")

def add_master_dong_rule():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Define Rule Data
    predicate_code = "CHECK_MASTER_DONG"
    name_ru = "День по Мастеру Дуну"
    description = "Характеристика дня по методу Мастера Дуна"
    # Generate ID based on unique props
    rule_id = hashlib.md5(f"{predicate_code}_dynamic".encode('utf-8')).hexdigest()
    
    print(f"Registering Rule: {rule_id} ({name_ru})")
    
    # 2. Insert/Update Registry
    cursor.execute("""
        INSERT OR REPLACE INTO t_rule_registry (rule_id, name_ru, predicate_code, params_json, score_base, score_formula, description, is_active)
        VALUES (?, ?, ?, '{}', 0, 'dynamic', ?, 1)
    """, (rule_id, name_ru, predicate_code, description))
    
    # 3. Insert/Update Scope
    cursor.execute("""
        INSERT OR REPLACE INTO t_rule_scope (rule_id, scope_type, is_stop)
        VALUES (?, 'date', 0)
    """, (rule_id,))
    
    conn.commit()
    conn.close()
    print("Rule Registered Successfully.")
    return rule_id

if __name__ == "__main__":
    add_master_dong_rule()
