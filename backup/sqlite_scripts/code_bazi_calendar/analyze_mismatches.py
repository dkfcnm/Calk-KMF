"""Утилита для анализа расхождений контрольных столпов с расчётами.

Скрипт читает файл control_pillars_utc.csv, пересчитывает столпы с учётом
приоритета данных HKO и выводит список расхождений с идентификацией
солнечного термина.

Последнее обновление: 2025-12-25 15:55 MSK.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from code.bazi_calendar import (
    calc_four_pillars,
    get_prev_solar_term,
    get_sqlite_connection,
)


@dataclass(slots=True)
class MismatchEntry:
    """Строка с расхождением между ожиданием и расчётом."""

    date_local: str
    time_range_local: str
    expected: tuple[str, str, str, str, str, str, str, str]
    actual: tuple[str, str, str, str, str, str, str, str]
    solar_term_id: int
    crossing_utc: str

    def as_dict(self) -> dict[str, str]:
        return {
            "date_local": self.date_local,
            "time_range_local": self.time_range_local,
            "expected": ",".join(self.expected),
            "actual": ",".join(self.actual),
            "solar_term_id": str(self.solar_term_id),
            "crossing_utc": self.crossing_utc,
        }


def analyze_control_csv(csv_path: Path) -> List[MismatchEntry]:
    conn = get_sqlite_connection()
    try:
        mismatches: List[MismatchEntry] = []
        with csv_path.open("r", encoding="utf-8") as file_obj:
            reader = csv.DictReader(file_obj)
            for row in reader:
                dt = datetime.fromisoformat(row["dt_utc"])
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                else:
                    dt = dt.astimezone(timezone.utc)
                tz = int(row["tz_offset_hours"])
                pillars = calc_four_pillars(dt, conn, tz_offset_hours=tz)
                expected = (
                    row["year_stem"],
                    row["year_branch"],
                    row["month_stem"],
                    row["month_branch"],
                    row["day_stem"],
                    row["day_branch"],
                    row["hour_stem"],
                    row["hour_branch"],
                )
                actual = (
                    pillars.year.stem_char,
                    pillars.year.branch_char,
                    pillars.month.stem_char,
                    pillars.month.branch_char,
                    pillars.day.stem_char,
                    pillars.day.branch_char,
                    pillars.hour.stem_char,
                    pillars.hour.branch_char,
                )
                if expected != actual:
                    solar_term_id, crossing = get_prev_solar_term(
                        dt,
                        conn,
                        tz_offset_hours=tz,
                    )
                    mismatches.append(
                        MismatchEntry(
                            date_local=row["date_local"],
                            time_range_local=row["time_range_local"],
                            expected=expected,
                            actual=actual,
                            solar_term_id=solar_term_id,
                            crossing_utc=crossing.isoformat(),
                        )
                    )
        return mismatches
    finally:
        conn.close()


def write_mismatches_csv(entries: Iterable[MismatchEntry], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(
            file_obj,
            fieldnames=[
                "date_local",
                "time_range_local",
                "expected",
                "actual",
                "solar_term_id",
                "crossing_utc",
            ],
        )
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry.as_dict())


def main() -> None:
    csv_path = PROJECT_ROOT / "data" / "control_pillars_utc.csv"
    output_path = PROJECT_ROOT / "data" / "control_mismatch_details.csv"

    # Обеспечиваем вывод в консоль в UTF-8, если доступно
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8")

    mismatches = analyze_control_csv(csv_path)
    write_mismatches_csv(mismatches, output_path)

    print(f"Всего несоответствий: {len(mismatches)}")
    print(f"Детали сохранены в {output_path}")
    for entry in mismatches[:20]:
        print(entry.as_dict())


if __name__ == "__main__":
    main()
