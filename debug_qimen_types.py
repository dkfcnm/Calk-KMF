
import sys
import os
import json

sys.path.insert(0, os.getcwd())
from code.common.db_manager import db

def check_qimen_data():
    print("Checking Qimen Data Types...")
    
    # 1. spr_qimen_templates columns
    print("spr_qimen_templates schema:")
    cols = db.fetch_all("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'spr_qimen_templates'")
    for c in cols:
        print(f"  {c[0]}: {c[1]}")
        
    # 2. Sample data from spr_qimen_templates
    print("Sample spr_qimen_templates:")
    res = db.fetch_all("SELECT heaven_stem, earth_stem FROM spr_qimen_templates LIMIT 5")
    for r in res:
        print(f"  H: {r[0]} ({type(r[0])}), E: {r[1]} ({type(r[1])})")
        
    # 3. Sample rules from t_rule_registry
    print("Sample Qimen Rules:")
    res = db.fetch_all("SELECT params_json FROM t_rule_registry WHERE predicate_code = 'CHECK_QIMEN_STEMS' LIMIT 5")
    for r in res:
        print(f"  Params: {r[0]}")

if __name__ == "__main__":
    check_qimen_data()
