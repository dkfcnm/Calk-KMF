"""Скрипт нормализации контрольных таблиц в единый UTC-формат."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, List

import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from code.bazi_calendar import get_sqlite_connection

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CONTROL_PILLARS_MD = PROJECT_ROOT / "Metodology" / "bazci_control.md"
CONTROL_SEASONS_MD = PROJECT_ROOT / "Metodology" / "bazci_control_02.md"

OUTPUT_PILLARS_CSV = DATA_DIR / "control_pillars_utc.csv"
OUTPUT_SEASONS_CSV = DATA_DIR / "control_seasons_utc.csv"


@dataclass
class PillarRow:
    source: str
    tz_offset_hours: int
    date_local: str
    time_range_local: str
    dt_utc: datetime
    year_stem: str
    year_branch: str
    month_stem: str
    month_branch: str
    day_stem: str
    day_branch: str
    hour_stem: str
    hour_branch: str


@dataclass
class SeasonRow:
    source: str
    tz_offset_hours: int
    season_number: int
    local_date: str
    local_time: str
    dt_local: datetime
    dt_utc: datetime


def parse_pillars_markdown(path: Path, tz_offset_hours: int, source_name: str) -> List[PillarRow]:
    rows: List[PillarRow] = []
    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("| Дата | Время |"):
            in_table = True
            continue
        if not in_table:
            continue
        if not stripped.startswith("|") or "---" in stripped:
            continue

        parts = [part.strip() for part in stripped.split("|")]
        if len(parts) < 11:
            continue

        date_local = parts[1]
        time_range = parts[2]
        year_stem, year_branch = parts[3], parts[4]
        month_stem, month_branch = parts[5], parts[6]
        day_stem, day_branch = parts[7], parts[8]
        hour_stem, hour_branch = parts[9], parts[10]

        dt_utc = convert_local_range_to_utc(date_local, time_range, tz_offset_hours)

        rows.append(
            PillarRow(
                source=source_name,
                tz_offset_hours=tz_offset_hours,
                date_local=date_local,
                time_range_local=time_range,
                dt_utc=dt_utc,
                year_stem=year_stem,
                year_branch=year_branch,
                month_stem=month_stem,
                month_branch=month_branch,
                day_stem=day_stem,
                day_branch=day_branch,
                hour_stem=hour_stem,
                hour_branch=hour_branch,
            )
        )

    return rows


def convert_local_range_to_utc(date_str: str, time_range: str, tz_offset_hours: int) -> datetime:
    day, month, year_short = map(int, date_str.split("."))
    year = 2000 + year_short
    base = datetime(year, month, day)

    range_clean = time_range.strip()
    if "(пред.дня)" in range_clean:
        start_part = range_clean.split("-")[0].replace("(пред.дня)", "").strip()
        start_hour, start_minute = map(int, start_part.split(":"))
        local_dt = (base - timedelta(days=1)).replace(hour=start_hour, minute=start_minute)
    else:
        start_part = range_clean.split("-")[0].strip()
        start_hour, start_minute = map(int, start_part.split(":"))
        local_dt = base.replace(hour=start_hour, minute=start_minute)

    return (local_dt - timedelta(hours=tz_offset_hours)).replace(tzinfo=timezone.utc)


def parse_seasons_markdown(path: Path, tz_offset_hours: int, source_name: str) -> List[SeasonRow]:
    rows: List[SeasonRow] = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="|")
        for raw in reader:
            if len(raw) < 4:
                continue
            try:
                season_number = int(raw[1].strip())
            except ValueError:
                continue
            date_str = raw[2].strip()
            time_str = raw[3].strip()
            day, month, year = map(int, date_str.split("."))
            hour, minute = map(int, time_str.split(":"))
            tz_info = timezone(timedelta(hours=tz_offset_hours))
            local_dt = datetime(year, month, day, hour, minute, tzinfo=tz_info)
            dt_utc = local_dt.astimezone(timezone.utc)
            rows.append(
                SeasonRow(
                    source=source_name,
                    tz_offset_hours=tz_offset_hours,
                    season_number=season_number,
                    local_date=date_str,
                    local_time=time_str,
                    dt_local=local_dt,
                    dt_utc=dt_utc,
                )
            )
    return rows


def write_pillars_csv(rows: Iterable[PillarRow], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
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
        )
        for row in rows:
            writer.writerow(
                [
                    row.source,
                    row.tz_offset_hours,
                    row.date_local,
                    row.time_range_local,
                    row.dt_utc.isoformat(),
                    row.year_stem,
                    row.year_branch,
                    row.month_stem,
                    row.month_branch,
                    row.day_stem,
                    row.day_branch,
                    row.hour_stem,
                    row.hour_branch,
                ]
            )


def write_seasons_csv(rows: Iterable[SeasonRow], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "source",
                "tz_offset_hours",
                "season_number",
                "local_date",
                "local_time",
                "dt_utc",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.source,
                    row.tz_offset_hours,
                    row.season_number,
                    row.local_date,
                    row.local_time,
                    row.dt_utc.isoformat(),
                ]
            )


def upsert_sqlite(rows_pillars: Iterable[PillarRow], rows_seasons: Iterable[SeasonRow]) -> None:
    """Записывает данные сезонов в t_solar_term_time_hko."""
    conn = get_sqlite_connection()
    try:
        cursor = conn.cursor()
        
        # t_control_pillars и t_control_seasons удалены как избыточные

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS t_solar_term_time_hko (
                year              INTEGER NOT NULL,
                solar_term_id     INTEGER NOT NULL,
                longitude_deg     INTEGER NOT NULL,
                crossing_hkt      TIMESTAMP NOT NULL,
                crossing_utc      TIMESTAMP NOT NULL,
                tz_offset_hours   INTEGER NOT NULL DEFAULT 8,
                PRIMARY KEY (year, solar_term_id)
            )
            """
        )
        cursor.execute("DELETE FROM t_solar_term_time_hko")
        cursor.execute(
            "SELECT solar_term_id, longitude_deg FROM spr_solar_term ORDER BY solar_term_id"
        )
        solar_term_map = {idx: deg for idx, deg in cursor.fetchall()}

        def map_season_to_term(season_number: int) -> tuple[int, int]:
            # HKO нумерует сезоны с Xiao Han (285°) как 1.
            # Наш solar_term_id=1 это Li Chun (315°).
            # Xiao Han (285°) - это solar_term_id=23.
            # Формула конвертации:
            # season_number 1 (Xiao Han) -> term_id 23
            # season_number 2 (Da Han) -> term_id 24
            # season_number 3 (Li Chun) -> term_id 1
            # ...
            # map: 1->23, 2->24, 3->1 ...
            # term_id = ((season_number + 21) % 24)
            # if result == 0 -> 24? No.
            # Let's check:
            # s=3: (3+21)%24 = 24%24 = 0. We need 1.
            # Wait.
            # Solar Terms:
            # 1: Li Chun (315)
            # ...
            # 23: Xiao Han (285)
            # 24: Da Han (300)
            
            # HKO Season 1 is Xiao Han (285).
            # So s=1 -> t=23.
            # s=2 -> t=24.
            # s=3 -> t=1.
            
            # (s + offset) % 24
            # 1 + 21 = 22. Not 23.
            # 1 + 22 = 23.
            # 2 + 22 = 24.
            # 3 + 22 = 25 % 24 = 1.
            # So term_id = (season_number + 22) % 24
            # If result is 0, it should be 24?
            # 2 + 22 = 24 % 24 = 0. Should be 24.
            # So: term_id = (season_number + 22) % 24
            # if term_id == 0: term_id = 24
            
            # My previous code (which I am replacing) had:
            # solar_term_id = ((season_number + 21) % 24) + 1
            # Let's check:
            # s=1: (1+21)%24 + 1 = 22 + 1 = 23. Correct.
            # s=2: (2+21)%24 + 1 = 23 + 1 = 24. Correct.
            # s=3: (3+21)%24 + 1 = 0 + 1 = 1. Correct.
            # So the formula was correct.
            
            solar_term_id = ((season_number + 21) % 24) + 1
            longitude = solar_term_map.get(solar_term_id)
            if longitude is None:
                raise ValueError(f"Не найден solar_term_id={solar_term_id} в spr_solar_term")
            return solar_term_id, longitude

        hko_records = []
        for row in rows_seasons:
            solar_term_id, longitude = map_season_to_term(row.season_number)
            hko_records.append(
                (
                    row.dt_local.year,
                    solar_term_id,
                    longitude,
                    row.dt_local.isoformat(),
                    row.dt_utc.isoformat(),
                    row.tz_offset_hours,
                )
            )

        cursor.executemany(
            """
            INSERT INTO t_solar_term_time_hko (
                year,
                solar_term_id,
                longitude_deg,
                crossing_hkt,
                crossing_utc,
                tz_offset_hours
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            hko_records,
        )

        conn.commit()
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Нормализация контрольных таблиц (UTC)")
    parser.add_argument(
        "--skip-sqlite",
        action="store_true",
        help="Не записывать данные в SQLite, только CSV",
    )
    args = parser.parse_args()

    pillars_rows = parse_pillars_markdown(
        CONTROL_PILLARS_MD,
        tz_offset_hours=3,
        source_name=CONTROL_PILLARS_MD.name,
    )
    seasons_rows = parse_seasons_markdown(
        CONTROL_SEASONS_MD,
        tz_offset_hours=8,
        source_name=CONTROL_SEASONS_MD.name,
    )

    write_pillars_csv(pillars_rows, OUTPUT_PILLARS_CSV)
    write_seasons_csv(seasons_rows, OUTPUT_SEASONS_CSV)

    if not args.skip_sqlite:
        upsert_sqlite(pillars_rows, seasons_rows)

    print(
        "Преобразовано строк столпов: {count} -> {path}".format(
            count=len(pillars_rows),
            path=OUTPUT_PILLARS_CSV,
        )
    )
    print(
        "Преобразовано строк сезонов: {count} -> {path}".format(
            count=len(seasons_rows),
            path=OUTPUT_SEASONS_CSV,
        )
    )
    if args.skip_sqlite:
        print("Запись в SQLite пропущена (опция --skip-sqlite)")
    else:
        print("Данные обновлены в таблице t_solar_term_time_hko")


if __name__ == "__main__":
    main()
