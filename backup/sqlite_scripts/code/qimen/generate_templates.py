import sqlite3
import sys
import os
import time
import hashlib

# Fix console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Add project root to path (INSERT at 0 to shadow system 'code' module)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from code.common.config import load_config_from_db
from code.qimen.engine import QimenEngine

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DB_PATH = os.path.join(PROJECT_ROOT, "calk_kmf.sqlite")

def generate_template_id_hash(rasklad_id, palace_no):
    raw = f"{rasklad_id}_{palace_no}"
    return hashlib.md5(raw.encode('utf-8')).hexdigest()

def generate_templates():
    print("Generating 1080 Qimen Templates...")
    
    config = load_config_from_db(DB_PATH)
    engine = QimenEngine(config)
    
    # Генерируем список 60 Цзя Цзы
    jia_zi_list = []
    stems = config.stems # 10
    branches = config.branches # 12
    for i in range(60):
        s = stems[i % 10]
        b = branches[i % 12]
        jia_zi_list.append((s, b, s+b))
        
    results = []
    
    # 1080 = 2 (Yin/Yang) * 9 (Ju) * 60 (Hours)
    count = 0
    
    for yin_yang in ['Yang', 'Yin']:
        is_yang = (yin_yang == 'Yang')
        
        for ju_num in range(1, 10):
            
            for s, b, sb_str in jia_zi_list:
                
                # Генерируем ID расклада
                # Пример: Yang_1_甲子
                rasklad_id = f"{yin_yang}_{ju_num}_{sb_str}"
                
                # Вызываем Engine напрямую (layout_board)
                chart = engine._layout_board(
                    hour_id="TEMPLATE",
                    ju_num=ju_num,
                    yin_yang=yin_yang,
                    is_yang=is_yang,
                    focus_stem=s,
                    focus_branch=b
                )
                
                # Разбираем результат (9 дворцов)
                for p_no, p_data in chart.palaces.items():
                    # structure = Heaven + Earth
                    structure = p_data.heaven_stem + p_data.earth_stem
                    
                    template_id_hash = generate_template_id_hash(rasklad_id, p_no)
                    
                    results.append((
                        template_id_hash,
                        rasklad_id,
                        yin_yang,
                        ju_num,
                        sb_str,
                        
                        p_no,
                        
                        structure,
                        p_data.heaven_stem,
                        p_data.is_fou_tou_heaven,
                        
                        p_data.earth_stem,
                        p_data.is_fou_tou_earth,
                        
                        p_data.star,
                        p_data.is_main_star,
                        
                        p_data.gate,
                        p_data.is_main_gate,
                        
                        p_data.spirit
                    ))
                
                count += 1
                if count % 100 == 0:
                    print(f"Generated {count}/1080 charts...", flush=True)

    print(f"Generation complete. Total charts: {count}. Total rows: {len(results)}")
    
    # Save to DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clear old
    cursor.execute("DELETE FROM spr_qimen_templates")
    
    print("Inserting into DB...")
    cursor.executemany("""
        INSERT INTO spr_qimen_templates (
            template_id, rasklad_id, yin_yang, ju_num, hour_stem_branch,
            palace_no, structure, heaven_stem, is_fou_tou_heaven,
            earth_stem, is_fou_tou_earth, star, is_main_star,
            gate, is_main_gate, spirit
        ) VALUES (?,?,?,?,?, ?,?,?,?, ?,?,?,?, ?,?,?)
    """, results)
    
    conn.commit()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    generate_templates()
