import datetime
import time
from typing import Optional
from code.common.db_manager import db


class CalculationLogger:
    def __init__(self, db_path: str = None):
        # db_path is ignored, kept for legacy signature compatibility
        self.db_path = db_path
        self._ensure_table()

    def _ensure_table(self):
        sql = """
            CREATE TABLE IF NOT EXISTS t_sys_calculation_log (
                id SERIAL PRIMARY KEY,
                stage_name TEXT NOT NULL,
                start_dt TEXT NOT NULL,
                end_dt TEXT,
                duration_sec REAL,
                record_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'RUNNING',
                error_msg TEXT
            )
        """
        try:
            db.execute_query(sql)
        except Exception as e:
            print(f"Logger Init Error: {e}")

    def start_stage(self, stage_name: str) -> int:
        """Starts a logging stage and returns the log ID."""
        start_dt = datetime.datetime.now().isoformat()

        sql = """
            INSERT INTO t_sys_calculation_log (stage_name, start_dt, status)
            VALUES (%s, %s, 'RUNNING')
            RETURNING id
        """
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(sql, [stage_name, start_dt])
                row = cursor.fetchone()
                log_id = row[0]
        except Exception as e:
            print(f"Logger Start Error: {e}")
            log_id = -1

        print(f"[{stage_name}] Started at {start_dt}")
        return log_id

    def end_stage(self, log_id: int, record_count: int = 0):
        """Ends a logging stage successfully."""
        if log_id == -1:
            return

        end_dt = datetime.datetime.now().isoformat()

        # Calculate duration
        sql_sel = "SELECT start_dt FROM t_sys_calculation_log WHERE id = %s"
        row = db.fetch_one(sql_sel, [log_id])

        duration = 0.0
        if row:
            start_val = row[0]
            if isinstance(start_val, str):
                start_dt = datetime.datetime.fromisoformat(start_val)
            else:
                start_dt = start_val
            duration = (datetime.datetime.now() - start_dt).total_seconds()

        sql_upd = """
            UPDATE t_sys_calculation_log
            SET end_dt = %s, duration_sec = %s, record_count = %s, status = 'SUCCESS'
            WHERE id = %s
        """
        db.execute_query(sql_upd, [end_dt, duration, record_count, log_id])
        print(f"[{log_id}] Completed. Count: {record_count}. Duration: {duration:.2f}s")

    def fail_stage(self, log_id: int, error_msg: str):
        """Marks a stage as failed."""
        if log_id == -1:
            return

        end_dt = datetime.datetime.now().isoformat()

        sql = """
            UPDATE t_sys_calculation_log
            SET end_dt = %s, status = 'ERROR', error_msg = %s
            WHERE id = %s
        """
        db.execute_query(sql, [end_dt, error_msg, log_id])
        print(f"[{log_id}] Failed: {error_msg}")

    def cleanup_old_logs(self, days: int = 90):
        """Deletes logs older than specified days."""
        cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()

        sql = "DELETE FROM t_sys_calculation_log WHERE start_dt < %s"
        db.execute_query(sql, [cutoff_date])
        print(f"[Cleanup] Old logs cleanup requested (< {cutoff_date}).")
