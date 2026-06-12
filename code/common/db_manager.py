
import pg8000.dbapi
import logging
from typing import List, Tuple, Any, Optional
from contextlib import contextmanager
from queue import Queue, Empty
from code.common.db_config import PG_CONFIG

logger = logging.getLogger(__name__)

class DBManager:
    def __init__(self, pool_size: int = 5):
        self.config = PG_CONFIG
        self._pool: Queue = Queue(maxsize=pool_size)
        self._pool_size = pool_size

    def _create_connection(self):
        return pg8000.dbapi.connect(
            user=self.config['user'],
            password=self.config['password'],
            host=self.config['host'],
            port=self.config['port'],
            database=self.config['database']
        )

    def get_connection(self):
        try:
            conn = self._pool.get_nowait()
            try:
                conn.cursor().execute("SELECT 1")
                return conn
            except Exception:
                try:
                    conn.close()
                except Exception:
                    pass
        except Empty:
            pass
        return self._create_connection()

    def _return_connection(self, conn):
        try:
            self._pool.put_nowait(conn)
        except Exception:
            try:
                conn.close()
            except Exception:
                pass

    @contextmanager
    def get_cursor(self, commit: bool = False):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            self._return_connection(conn)

    def execute_query(self, query: str, params: Optional[List[Any]] = None) -> None:
        with self.get_cursor(commit=True) as cursor:
            cursor.execute(query, params or [])

    def fetch_all(self, query: str, params: Optional[List[Any]] = None) -> List[Tuple]:
        with self.get_cursor() as cursor:
            cursor.execute(query, params or [])
            return cursor.fetchall()

    def fetch_one(self, query: str, params: Optional[List[Any]] = None) -> Optional[Tuple]:
        with self.get_cursor() as cursor:
            cursor.execute(query, params or [])
            return cursor.fetchone()

    def execute_batch(self, query: str, params_list: List[List[Any]]) -> None:
        if not params_list:
            return
        with self.get_cursor(commit=True) as cursor:
            cursor.executemany(query, params_list)

# Singleton instance
db = DBManager()
