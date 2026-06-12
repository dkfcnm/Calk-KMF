import sys
import os

# Ensure imports work
sys.path.insert(0, os.getcwd())

from code.common.db_manager import db

def migrate():
    print("Starting Hierarchical Analysis Migration...")
    
    # 1. Create Hierarchical Tables
    tables = {
        "t_analysis_year": """
            CREATE TABLE IF NOT EXISTS t_analysis_year (
                year INTEGER,
                rule_id TEXT,
                result_value TEXT,
                score DOUBLE PRECISION,
                PRIMARY KEY (year, rule_id)
            )
        """,
        "t_analysis_month": """
            CREATE TABLE IF NOT EXISTS t_analysis_month (
                year INTEGER,
                month INTEGER,
                rule_id TEXT,
                result_value TEXT,
                score DOUBLE PRECISION,
                PRIMARY KEY (year, month, rule_id)
            )
        """,
        "t_analysis_day": """
            CREATE TABLE IF NOT EXISTS t_analysis_day (
                date_val DATE,
                rule_id TEXT,
                result_value TEXT,
                score DOUBLE PRECISION,
                PRIMARY KEY (date_val, rule_id)
            )
        """,
        "t_analysis_hour": """
            CREATE TABLE IF NOT EXISTS t_analysis_hour (
                hour_id TEXT,
                rule_id TEXT,
                result_value TEXT,
                score DOUBLE PRECISION,
                PRIMARY KEY (hour_id, rule_id)
            )
        """
    }
    
    for tbl, ddl in tables.items():
        print(f"Creating {tbl}...")
        db.execute_query(ddl)
        
    # 2. Add period_type to t_rule_registry
    print("Checking period_type column...")
    try:
        # Check if column exists (PostgreSQL specific check for simplicity in this hybrid env)
        # For universal support, we try to add it and ignore error if exists
        db.execute_query("ALTER TABLE t_rule_registry ADD COLUMN period_type TEXT DEFAULT 'hour'")
        print("Column period_type added.")
    except Exception as e:
        print(f"Column period_type might already exist or error: {e}")

    try:
        db.execute_query("ALTER TABLE spr_rule_registry ADD COLUMN period_type TEXT DEFAULT 'hour'")
        print("Column period_type added to spr_rule_registry.")
    except Exception as e:
        print(f"Column period_type might already exist in spr_rule_registry or error: {e}")

    # 3. Update Rule Classifications
    print("Updating Rule Classifications...")
    
    updates = [
        # Year Level
        ("year", "predicate_code LIKE '%_YEAR%' AND predicate_code NOT LIKE '%_DM_YEAR%' AND predicate_code NOT LIKE '%_DAY%' AND predicate_code NOT LIKE '%_HOUR%'"),
        ("year", "predicate_code IN ('CHECK_NAYIN_YEAR_EL', 'CHECK_NAYIN_YEAR_NM', 'CHECK_DAGUA_YEAR_EL', 'CHECK_DAGUA_YEAR_PER', 'CHECK_DAGUA_YEAR_FAM', 'CHECK_DAGUA_YEAR_ROLE', 'CHECK_QI_PHASE_PILLAR_YEAR')"),
        
        # Month Level
        ("month", "predicate_code LIKE '%_MONTH%' AND predicate_code NOT LIKE '%_DM_MONTH%' AND predicate_code NOT LIKE '%_DAY%' AND predicate_code NOT LIKE '%_HOUR%'"),
        ("month", "predicate_code IN ('CHECK_NAYIN_MONTH_EL', 'CHECK_NAYIN_MONTH_NM', 'CHECK_DAGUA_MONTH_EL', 'CHECK_DAGUA_MONTH_PER', 'CHECK_DAGUA_MONTH_FAM', 'CHECK_DAGUA_MONTH_ROLE', 'CHECK_QI_PHASE_PILLAR_MONTH')"),
        # Combinations Year+Month are handled via params in code, but rule registry might generic BAZI_BRANCH_CLASH.
        # Ideally, specific rules should be tagged. But current BAZI_BRANCH_CLASH is generic.
        # We will handle Combinations specially in code or logic. 
        # But let's try to tag what we can. 
        # Actually, if the predicate is generic, we can't tag it 'year' in registry if it's used for 'hour' too.
        # However, run_analysis uses 'BAZI_BRANCH_CLASH' for all levels.
        # We might need to split rules or just rely on the logic in run_analysis to insert into correct table.
        # BUT user asked to "register separate characteristic". 
        # If the rule ID is shared, we have a problem.
        # CURRENTLY: run_analysis generates rule_id on the fly? No, it joins t_rule_registry.
        # If t_rule_registry has one entry for BAZI_BRANCH_CLASH, we cannot assign different periods.
        # We assume specific rules for specific levels will be created or we just tag specific named predicates.
        
        # Day Level
        ("day", "predicate_code IN ('CHECK_DAY_OFFICER', 'CHECK_MASTER_DONG', 'CHECK_YELLOW_BLACK')"),
        ("day", "predicate_code LIKE 'CHECK_BLACK_RABBIT_%' AND predicate_code != 'CHECK_BLACK_RABBIT_JOEY_HOUR'"),
        ("day", "predicate_code IN ('CHECK_NAYIN_DAY_EL', 'CHECK_NAYIN_DAY_NM', 'CHECK_DAGUA_DAY_EL', 'CHECK_DAGUA_DAY_PER', 'CHECK_DAGUA_DAY_FAM', 'CHECK_DAGUA_DAY_ROLE', 'CHECK_QI_PHASE_PILLAR_DAY', 'CHECK_QI_PHASE_DM_YEAR', 'CHECK_QI_PHASE_DM_MONTH', 'CHECK_QI_PHASE_DM_DAY')"),

        # Hour Level
        ("hour", "predicate_code IN ('CHECK_GUIGU_NUMBER', 'CHECK_BLACK_RABBIT_JOEY_HOUR')"),
        ("hour", "predicate_code LIKE '%_HOUR%' OR predicate_code LIKE 'CHECK_QIMEN%'"),
    ]
    
    for p_type, condition in updates:
        sql = f"UPDATE t_rule_registry SET period_type = '{p_type}' WHERE {condition}"
        print(f"Applying {p_type} to rules matching: {condition[:50]}...")
        db.execute_query(sql)

    print("Migration completed.")

if __name__ == "__main__":
    migrate()
