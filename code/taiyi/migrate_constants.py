import sys
import os
import json

# Ensure we can import from code/
sys.path.insert(0, os.getcwd())

from code.common.db_manager import db
from code.taiyi.constants import (
    GATES_ORDER, GATES_INFO,
    STARS_ORDER, STARS_INFO,
    HUANG_HEI_DAO, HUANG_HEI_DAO_INFO,
    QING_LONG_START, XI_SHEN_DIRECTION, DIR_TO_PALACE,
    TAI_YI_NOBLE_HOURS, JIE_LU_KONG_WANG,
    TAI_YI_STAR_START_YANG, TAI_YI_STAR_START_YIN,
    GATES_PALACE_SEQ_YANG, GATES_PALACE_SEQ_YIN
)

def migrate_taiyi_constants():
    print("Migrating Tai Yi constants to DB...")
    
    with db.get_cursor(commit=True) as cursor:
        # 1. Gates
        cursor.execute("DROP TABLE IF EXISTS spr_taiyi_gates CASCADE")
        cursor.execute("""
            CREATE TABLE spr_taiyi_gates (
                id INTEGER PRIMARY KEY,
                code TEXT,
                name_cn TEXT,
                name_ru TEXT,
                lucky_score INTEGER
            )
        """)
        gates_data = []
        for i, code in enumerate(GATES_ORDER):
            info = GATES_INFO[code]
            gates_data.append((i, code, info['name_cn'], info['name_ru'], info['lucky']))
        
        cursor.executemany("INSERT INTO spr_taiyi_gates VALUES (%s, %s, %s, %s, %s)", gates_data)
        
        # 2. Stars
        cursor.execute("DROP TABLE IF EXISTS spr_taiyi_stars CASCADE")
        cursor.execute("""
            CREATE TABLE spr_taiyi_stars (
                id INTEGER PRIMARY KEY,
                code TEXT,
                name_cn TEXT,
                name_ru TEXT,
                lucky_score INTEGER
            )
        """)
        stars_data = []
        for code in STARS_ORDER:
            info = STARS_INFO[code]
            stars_data.append((info['id'], code, info['name_cn'], info['name_ru'], info['lucky']))
            
        cursor.executemany("INSERT INTO spr_taiyi_stars VALUES (%s, %s, %s, %s, %s)", stars_data)

        # 3. Spirits (Huang Hei Dao)
        cursor.execute("DROP TABLE IF EXISTS spr_taiyi_spirits CASCADE")
        cursor.execute("""
            CREATE TABLE spr_taiyi_spirits (
                id INTEGER PRIMARY KEY,
                code TEXT,
                name_cn TEXT, -- Not in constants, but maybe needed? Keeping placeholder
                name_ru TEXT,
                lucky_score INTEGER
            )
        """)
        spirits_data = []
        for i, code in enumerate(HUANG_HEI_DAO):
            info = HUANG_HEI_DAO_INFO[code]
            # Extract RU name from "Name (Desc)" format if needed, or keep as is
            name_ru = info['name_ru']
            spirits_data.append((i, code, '', name_ru, info['lucky']))
            
        cursor.executemany("INSERT INTO spr_taiyi_spirits VALUES (%s, %s, %s, %s, %s)", spirits_data)

        # 4. Qing Long Start
        cursor.execute("DROP TABLE IF EXISTS spr_taiyi_qing_long_start CASCADE")
        cursor.execute("""
            CREATE TABLE spr_taiyi_qing_long_start (
                day_branch_id INTEGER PRIMARY KEY,
                start_hour_idx INTEGER
            )
        """)
        ql_data = [(k, v) for k, v in QING_LONG_START.items()]
        cursor.executemany("INSERT INTO spr_taiyi_qing_long_start VALUES (%s, %s)", ql_data)

        # 5. Xi Shen (Spirit of Happiness)
        cursor.execute("DROP TABLE IF EXISTS spr_taiyi_xi_shen CASCADE")
        cursor.execute("""
            CREATE TABLE spr_taiyi_xi_shen (
                day_stem_id INTEGER PRIMARY KEY,
                palace_id INTEGER
            )
        """)
        xs_data = []
        for stem_id, direction in XI_SHEN_DIRECTION.items():
            palace_id = DIR_TO_PALACE.get(direction, 0)
            xs_data.append((stem_id, palace_id))
        cursor.executemany("INSERT INTO spr_taiyi_xi_shen VALUES (%s, %s)", xs_data)

        # 6. Noble Hours
        cursor.execute("DROP TABLE IF EXISTS spr_taiyi_noble CASCADE")
        cursor.execute("""
            CREATE TABLE spr_taiyi_noble (
                day_stem_id INTEGER,
                hour_branch_id INTEGER,
                PRIMARY KEY (day_stem_id, hour_branch_id)
            )
        """)
        noble_data = []
        for stem_id, branches in TAI_YI_NOBLE_HOURS.items():
            for b in branches:
                noble_data.append((stem_id, b))
        cursor.executemany("INSERT INTO spr_taiyi_noble VALUES (%s, %s)", noble_data)

        # 7. Kong Wang (Void)
        cursor.execute("DROP TABLE IF EXISTS spr_taiyi_kong_wang CASCADE")
        cursor.execute("""
            CREATE TABLE spr_taiyi_kong_wang (
                day_stem_id INTEGER,
                hour_branch_id INTEGER,
                PRIMARY KEY (day_stem_id, hour_branch_id)
            )
        """)
        kw_data = []
        for stem_id, branches in JIE_LU_KONG_WANG.items():
            for b in branches:
                kw_data.append((stem_id, b))
        cursor.executemany("INSERT INTO spr_taiyi_kong_wang VALUES (%s, %s)", kw_data)
        
        # 8. Star Start Position
        cursor.execute("DROP TABLE IF EXISTS spr_taiyi_star_start CASCADE")
        cursor.execute("""
            CREATE TABLE spr_taiyi_star_start (
                cycle_type TEXT,
                decade_idx INTEGER,
                start_palace INTEGER,
                PRIMARY KEY (cycle_type, decade_idx)
            )
        """)
        ss_data = []
        for dec, pal in TAI_YI_STAR_START_YANG.items():
            ss_data.append(('YANG', dec, pal))
        for dec, pal in TAI_YI_STAR_START_YIN.items():
            ss_data.append(('YIN', dec, pal))
        cursor.executemany("INSERT INTO spr_taiyi_star_start VALUES (%s, %s, %s)", ss_data)

        # 9. Gate Sequence
        cursor.execute("DROP TABLE IF EXISTS spr_taiyi_gate_seq CASCADE")
        cursor.execute("""
            CREATE TABLE spr_taiyi_gate_seq (
                cycle_type TEXT,
                seq_idx INTEGER,
                palace_id INTEGER,
                PRIMARY KEY (cycle_type, seq_idx)
            )
        """)
        gs_data = []
        for i, pal in enumerate(GATES_PALACE_SEQ_YANG):
            gs_data.append(('YANG', i, pal))
        for i, pal in enumerate(GATES_PALACE_SEQ_YIN):
            gs_data.append(('YIN', i, pal))
        cursor.executemany("INSERT INTO spr_taiyi_gate_seq VALUES (%s, %s, %s)", gs_data)

        # 10. Palace Ring (Structural)
        cursor.execute("DROP TABLE IF EXISTS spr_taiyi_palace_ring CASCADE")
        cursor.execute("""
            CREATE TABLE spr_taiyi_palace_ring (
                palace_id INTEGER PRIMARY KEY,
                ring_idx INTEGER
            )
        """)
        # Ring: 1, 8, 3, 4, 9, 2, 7, 6
        ring_order = [1, 8, 3, 4, 9, 2, 7, 6]
        pr_data = [(p, i) for i, p in enumerate(ring_order)]
        cursor.executemany("INSERT INTO spr_taiyi_palace_ring VALUES (%s, %s)", pr_data)

    print("Tai Yi constants migrated successfully.")

if __name__ == "__main__":
    migrate_taiyi_constants()
