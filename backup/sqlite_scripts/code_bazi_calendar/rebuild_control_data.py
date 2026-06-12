"""Пересчёт контрольных столпов на основе расчётного алгоритма.

Скрипт читает существующий control_pillars_utc.csv, пересчитывает столпы
через calc_four_pillars с приоритетом данных HKO и перезаписывает CSV.
Дополнительно обновляет таблицу t_control_pillars в SQLite.

Последнее обновление: 2025-12-25 16:00 MSK.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import sqlite3

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from code.bazi_calendar import calc_four_pillars, get_sqlite_connection  # noqa: E402

CSV_PATH = PROJECT_ROOT / "data" / "control_pillars_utc.csv"


def iterate_rows(path: Path) -> Iterable[dict[str, str]]:
    with path.open("r", encoding="utf-8") as file_obj:
        reader = csv.DictReader(file_obj)
        for row in reader:
            yield row


def rewrite_csv(rows: Iterable[dict[str, str]], conn: sqlite3.Connection) -> None:
    temp_path = CSV_PATH.with_suffix(".tmp")
    fieldnames = [
        "source",
        "tz_offset_hours",
        "date_local",
        "time_range_local",
        "dt_utc",
        "year_stem",
        "year_branch",
        "month_stem",
        "month_branch",
        "day_stem",
        "day_branch",
        "hour_stem",
        "hour_branch",
    ]

    with temp_path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            dt = datetime.fromisoformat(row["dt_utc"])
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            tz_offset = int(row["tz_offset_hours"])
            pillars = calc_four_pillars(dt, conn, tz_offset_hours=tz_offset)

            writer.writerow(
                {
                    "source": row["source"],
                    "tz_offset_hours": row["tz_offset_hours"],
                    "date_local": row["date_local"],
                    "time_range_local": row["time_range_local"],
                    "dt_utc": row["dt_utc"],
                    "year_stem": pillars.year.stem_char,
                    "year_branch": pillars.year.branch_char,
                    "month_stem": pillars.month.stem_char,
                    "month_branch": pillars.month.branch_char,
                    "day_stem": pillars.day.stem_char,
                    "day_branch": pillars.day.branch_char,
                    "hour_stem": pillars.hour.stem_char,
                    "hour_branch": pillars.hour.branch_char,
                }
            )

    temp_path.replace(CSV_PATH)


def rewrite_sqlite(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM t_control_pillars")

    with CSV_PATH.open("r", encoding="utf-8") as file_obj:
        reader = csv.DictReader(file_obj)
        rows = [
            (
                row["source"],
                int(row["tz_offset_hours"]),
                row["date_local"],
                row["time_range_local"],
                row["dt_utc"],
                row["year_stem"],
                row["year_branch"],
                row["month_stem"],
                row["month_branch"],
                row["day_stem"],
                row["day_branch"],
                row["hour_stem"],
                row["hour_branch"],
            )
            for row in reader
        ]

    cursor.executemany(
        """
        INSERT INTO t_control_pillars (
            source_file,
            tz_offset_hours,
            date_local,
            time_range_local,
            dt_utc,
            year_stem,
            year_branch,
            month_stem,
            month_branch,
            day_stem,
            day_branch,
            hour_stem,
            hour_branch
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()


def main() -> None:
    conn = get_sqlite_connection()
    try:
        rows = list(iterate_rows(CSV_PATH))
        rewrite_csv(rows, conn)
        rewrite_sqlite(conn)
    finally:
        conn.close()
    print("control_pillars_utc.csv обновлён, t_control_pillars синхронизирована.")


if __name__ == "__main__":
    main()
