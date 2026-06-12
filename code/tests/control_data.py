import sys
import os
import argparse
from typing import List, Dict

# Fix unicode printing on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Ensure imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from code.common.db_manager import db

TABLES_PK = {
    't_bazi_hourly': ['hour_id'],
    't_flying_stars': ['hour_id', 'palace'],
    
    't_qumen_dgiren_hourly': ['chart_id'],
    't_qumen_chauby_hourly': ['chart_id'],
    
    't_qumen_dgiren_year': ['chart_id'],
    't_qumen_dgiren_month': ['chart_id'],
    't_qumen_dgiren_day': ['chart_id'],
    
    # Chai Bu year/month/day удалены — для этих периодов используется Джи Рэн
}

def get_control_name(table_name):
    return f"t_control_{table_name}"

def create_control(table_name, limit=100):
    ctl_name = get_control_name(table_name)
    print(f"Creating control copy for {table_name} -> {ctl_name} ...")
    
    try:
        # PostgreSQL syntax for random order is RANDOM() same as SQLite usually, but let's be safe
        db.execute_query(f"DROP TABLE IF EXISTS {ctl_name}")
        db.execute_query(f"CREATE TABLE {ctl_name} AS SELECT * FROM {table_name} ORDER BY RANDOM() LIMIT {limit}")
        print(f"Success. Created {ctl_name} with {limit} rows.")
    except Exception as e:
        print(f"Error creating control table: {e}")

def verify_table(table_name):
    ctl_name = get_control_name(table_name)
    pk_cols = TABLES_PK.get(table_name)
    
    success = False
    
    if not pk_cols:
        print(f"Unknown PK for {table_name}, skipping.")
        return False
    
    print(f"Verifying {table_name} against {ctl_name}...")
    
    try:
        # Check if control table exists using information_schema
        # Note: table names in PG are usually lowercase
        exists_query = f"SELECT count(*) FROM information_schema.tables WHERE table_name = '{ctl_name}'"
        res = db.fetch_all(exists_query)
        if not res or res[0][0] == 0:
            print(f"Control table {ctl_name} does not exist. Please create it first.")
            return False

        # Load control data
        # fetch_all returns list of tuples. We need column names to map to dict.
        # DBManager doesn't natively return dicts yet in fetch_all (it returns tuples).
        # We need to get columns first.
        
        # Get columns for control table
        cols_query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{ctl_name}' ORDER BY ordinal_position"
        cols_res = db.fetch_all(cols_query)
        columns = [r[0] for r in cols_res]
        
        # Explicitly select columns to ensure order matches 'columns' list
        cols_str = ", ".join(columns)
        control_data = db.fetch_all(f"SELECT {cols_str} FROM {ctl_name}")
        
        errors = 0
        checked = 0
        
        for row_tuple in control_data:
            checked += 1
            row = dict(zip(columns, row_tuple))
            
            # Build WHERE clause
            where_parts = []
            params = []
            pk_vals = []
            
            for pk in pk_cols:
                where_parts.append(f"{pk} = %s")
                params.append(row[pk])
                pk_vals.append(row[pk])
            
            where_sql = " AND ".join(where_parts)
            
            # Query current data
            # Use placeholder from db manager? It uses %s for pg8000
            current_data = db.fetch_all(f"SELECT {cols_str} FROM {table_name} WHERE {where_sql}", params)
            
            if not current_data:
                print(f"  [MISSING] Row with PK {dict(zip(pk_cols, pk_vals))} missing in current table.")
                errors += 1
                continue
            
            current_row_tuple = current_data[0]
            current_row = dict(zip(columns, current_row_tuple))
            
            # Compare columns
            for col in columns:
                val_ctl = row[col]
                val_cur = current_row[col]
                
                # Handle None values
                if val_ctl is None and val_cur is None:
                    continue
                if val_ctl is None or val_cur is None:
                    # One is None, the other isn't
                    pk_dict_repr = repr(dict(zip(pk_cols, pk_vals)))
                    print(f"  [DIFF] PK {pk_dict_repr}: Col '{col}' Expected {repr(val_ctl)} Got {repr(val_cur)}")
                    errors += 1
                    continue

                # Handle type mismatches (str vs int)
                if val_ctl != val_cur:
                    # Try converting both to string
                    if str(val_ctl) == str(val_cur):
                        continue
                        
                    # Allow small float diff
                    if isinstance(val_ctl, (int, float)) and isinstance(val_cur, (int, float)):
                        try:
                            if abs(float(val_ctl) - float(val_cur)) < 1e-9:
                                continue
                        except (ValueError, TypeError):
                            pass
                    
                    pk_dict_repr = repr(dict(zip(pk_cols, pk_vals)))
                    print(f"  [DIFF] PK {pk_dict_repr}: Col '{col}' Expected {repr(val_ctl)} Got {repr(val_cur)}")
                    errors += 1
                    
        if errors == 0:
            print(f"  [OK] Verified {checked} rows. No discrepancies.")
            success = True
        else:
            print(f"  [FAIL] Found {errors} discrepancies in {checked} rows.")
            success = False
            
    except Exception as e:
        print(f"Error verifying {table_name}: {e}")
        success = False
    
    return success

def verify_all_tables(logger=None):
    print("\n--- Running Mandatory Verification ---")
    log_id = None
    if logger:
        log_id = logger.start_stage("Verification (Control Data)")
        
    all_success = True
    for tbl in TABLES_PK.keys():
        if not verify_table(tbl):
            all_success = False
            
    if all_success:
        print("Verification PASSED.")
        if logger and log_id:
            logger.end_stage(log_id, record_count=len(TABLES_PK))
    else:
        print("Verification FAILED.")
        if logger and log_id:
            logger.fail_stage(log_id, "Verification failed")
    
    return all_success

def main():
    parser = argparse.ArgumentParser(description="Manage Control Data for Regression Testing")
    subparsers = parser.add_subparsers(dest="command")
    
    # Create Command
    p_create = subparsers.add_parser("create", help="Create control copy for a table")
    p_create.add_argument("table", help="Table name")
    
    # Create All Command
    subparsers.add_parser("create_all", help="Create control copies for all known tables")
    
    # Verify Command
    p_verify = subparsers.add_parser("verify", help="Verify a table against control copy")
    p_verify.add_argument("table", help="Table name")
    
    # Verify All Command
    subparsers.add_parser("verify_all", help="Verify all tables")
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_control(args.table)
    elif args.command == "create_all":
        for tbl in TABLES_PK.keys():
            create_control(tbl)
    elif args.command == "verify":
        verify_table(args.table)
    elif args.command == "verify_all":
        verify_all_tables()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
