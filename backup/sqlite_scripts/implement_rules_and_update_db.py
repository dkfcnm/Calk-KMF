import sqlite3
import hashlib
import json

DB_PATH = "e:/Project/Calk_KMF/calk_kmf.sqlite"

def update_scores():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Update Scores
    # ID 1 (Establish) -> 1
    # ID 2 (Remove) -> -1
    # ID 3 (Full) -> 1
    # ID 4 (Balance) -> 1
    # ID 5 (Stable) -> 1
    # ID 6 (Hold) -> -1
    # ID 7 (Destruction) -> -1
    # ID 8 (Danger) -> -1
    # ID 9 (Success) -> 1
    # ID 10 (Harvest) -> 1
    # ID 11 (Open) -> 1
    # ID 12 (Close) -> -1
    updates = [
        (1, 1), (-1, 2), (1, 3), (1, 4), (1, 5), (-1, 6),
        (-1, 7), (-1, 8), (1, 9), (1, 10), (1, 11), (-1, 12)
    ]
    print("Updating scores in spr_indicator_value...")
    for score, val_id in updates:
        cursor.execute("UPDATE spr_indicator_value SET numeric_score = ? WHERE value_id = ?", (score, val_id))
    
    conn.commit()
    conn.close()

def register_rule():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    rule_code = "CHECK_DAY_OFFICER"
    params_json = "{}"
    # Unique ID for this specific rule configuration
    rule_hash = hashlib.md5((rule_code + params_json + "dynamic").encode()).hexdigest()
    
    # Check if exists
    cursor.execute("SELECT rule_id FROM spr_rule_registry WHERE predicate_code=?", (rule_code,))
    row = cursor.fetchone()
    if row:
        print(f"Rule already exists with ID {row[0]}")
        conn.close()
        return

    print(f"Registering rule {rule_code} with ID {rule_hash}...")
    cursor.execute("""
        INSERT INTO spr_rule_registry (rule_id, name_ru, predicate_code, params_json, score_base, score_formula, is_active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
    """, (rule_hash, "Индикатор дня (12 офицеров)", rule_code, params_json, 0, "dynamic"))
    
    # Scope
    cursor.execute("""
        INSERT INTO spr_rule_scope (rule_id, scope_type, is_stop)
        VALUES (?, 'date', 0)
    """, (rule_hash,))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_scores()
    register_rule()
