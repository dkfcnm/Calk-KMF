"""Скрипт заполнения справочников spr_* в SQLite для бацзы‑календаря.

Заполняет:
- spr_heavenly_stem
- spr_earthly_branch
- spr_solar_term
- spr_pillar_cycle
- spr_pillar_month_rule
- spr_pillar_hour_rule

А также рассчитывает t_solar_term_time для заданных лет.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Tuple

import sqlite3
import numpy as np
from astropy.time import Time
from astropy.coordinates import get_sun, GeocentricTrueEcliptic
from astropy import units as u

from .db import ensure_utc, parse_sqlite_timestamp, get_connection, get_placeholder

# from .tongshu import populate_tongshu_reference_data # Missing file


def _normalize_indicator_code(raw_code: str) -> str:
    """Удаляет экранирование и пробелы из обозначения значения индикатора."""

    cleaned = raw_code.replace("\\", "").replace(" ", "").strip()
    if cleaned in {"2", "1"}:
        return f"+{cleaned}"
    if cleaned in {"+2", "+1", "0", "-1", "-2"}:
        return cleaned
    return cleaned


def _parse_numeric_score(raw_score: str) -> float:
    """Конвертирует числовую оценку из Markdown-таблицы в float."""

    normalized = raw_score.replace("\\", "").replace(",", ".").strip()
    if normalized == "":
        raise ValueError("Пустое значение числовой оценки в методологии Мастера Дано")
    return float(normalized)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


MASTER_DANO_INDICATOR_CODE = "master_dano_day_quality"
MASTER_DANO_INDICATOR_ID = 2001
MASTER_DANO_NAME_RU = "Качество дня (Мастер Дано)"
MASTER_DANO_DESCRIPTION_RU = (
    "Качество дня по методике Мастера Дано, учитывает ветвь месяца, ствол и ветвь дня."
)
MASTER_DANO_FILE = PROJECT_ROOT / "Metodology" / "bazci_spr_master_dano.md"
MASTER_DANO_BASE_VALUE_ID = 2001

ANALYSIS_SCOPE_PRESETS: List[Tuple[str, str, str]] = [
    (
        "date",
        "Анализ даты",
        "Показатели, относящиеся к оценке календарной даты и её качеству.",
    ),
    (
        "activation",
        "Активации",
        "Правила и индикаторы для расчёта активаций.",
    ),
    (
        "walk",
        "Прогулки",
        "Показатели для расчёта прогулок и перемещений.",
    ),
    (
        "qimen_chart",
        "Карты Ци Мэнь",
        "Индикаторы, применимые к построению карт Ци Мэнь.",
    ),
]

DAY_OFFICER_SCOPES = ("date",)
MASTER_DANO_SCOPES = ("date",)
SQLITE_PATH = PROJECT_ROOT / "calk_kmf.sqlite"


DAY_OFFICER_INDICATOR_CODE = "day_officer"
DAY_OFFICER_INDICATOR_ID = 1001
DAY_OFFICER_NAME_RU = "12 офицеров дня"
DAY_OFFICER_DESCRIPTION_RU = (
    "Определяет офицера дня по земным ветвям месяца и дня с рекомендациями."
)
DAY_OFFICER_VALUE_DEFINITIONS: List[Dict[str, str | int]] = [
    {
        "value_id": 1,
        "code": "officer_establishment",
        "name_ru": "Установление",
        "favorable": (
            "планирование, помолвка, переговоры, занятие должности, посещение друзей, "
            "начало лечения, путешествие, переезд, начало обучения, начало строительства"
        ),
        "unfavorable": (
            "свадьба, закладка фундамента, снос старых построек, земляные работы"
        ),
    },
    {
        "value_id": 2,
        "code": "officer_removal",
        "name_ru": "Устранение",
        "favorable": (
            "уборка, ремонт, избавление от ненужного, молитва, пост, диета, "
            "увольнение сотрудника, развод, разрыв отношений"
        ),
        "unfavorable": (
            "свадьба, переезд, усыновление, покупка животных, путешествие, "
            "открытие бизнеса, устройство на работу"
        ),
    },
    {
        "value_id": 3,
        "code": "officer_fullness",
        "name_ru": "Наполнение",
        "favorable": (
            "позитивные дела, открытие бизнеса, новоселье, сбор долгов, "
            "подписание соглашений (в вашу пользу)"
        ),
        "unfavorable": (
            "свадьба, обременительные соглашения, занятие новой должности, "
            "юридические дела, переезд, похороны, кредиты, разрушение построек"
        ),
    },
    {
        "value_id": 4,
        "code": "officer_balance",
        "name_ru": "Баланс",
        "favorable": (
            "свадьба, строительство, путешествие, переговоры, решение вопросов, "
            "где вы слабее"
        ),
        "unfavorable": "судебные процессы, раздел имущества, переезд, похороны",
    },
    {
        "value_id": 5,
        "code": "officer_stability",
        "name_ru": "Стабильность",
        "favorable": (
            "переговоры, подписание контрактов, открытие бизнеса, встречи с друзьями, "
            "поиск медицинской помощи"
        ),
        "unfavorable": "переезд, похороны, путешествие",
    },
    {
        "value_id": 6,
        "code": "officer_holding",
        "name_ru": "Удержание",
        "favorable": "начало нового проекта, ремонт, подписание контракта, переговоры",
        "unfavorable": "путешествие, переезд, свадьба",
    },
    {
        "value_id": 7,
        "code": "officer_destruction",
        "name_ru": "Разрушение",
        "favorable": "ремонт, поиск медицинской помощи",
        "unfavorable": (
            "свадьба, переговоры, покупка имущества, путешествие, открытие бизнеса, "
            "подписание контрактов, вступление в должность"
        ),
    },
    {
        "value_id": 8,
        "code": "officer_danger",
        "name_ru": "Опасность",
        "favorable": "инвестиции, встречи с друзьями, перестановка кровати",
        "unfavorable": (
            "путешествие, переезд, земляные работы, ремонт, спорт, свадьба, "
            "начало нового проекта"
        ),
    },
    {
        "value_id": 9,
        "code": "officer_success",
        "name_ru": "Успех",
        "favorable": (
            "начало нового проекта, открытие бизнеса, подписание контрактов, "
            "переговоры, свадьба, путешествие, поиск работы, ремонт, похороны"
        ),
        "unfavorable": "судебные процесс, снос зданий",
    },
    {
        "value_id": 10,
        "code": "officer_harvest",
        "name_ru": "Сбор урожая",
        "favorable": (
            "начало учебы, получение наград, вступление в должность, предложение руки "
            "и сердца, сбор долгов"
        ),
        "unfavorable": (
            "похороны, поиск медицинской помощи, посещение больных, судебные процессы"
        ),
    },
    {
        "value_id": 11,
        "code": "officer_opening",
        "name_ru": "Открытие",
        "favorable": (
            "открытие бизнеса, покупка имущества, земляные работы, инвестиции, "
            "путешествие"
        ),
        "unfavorable": "свадьба, земляные работы, похороны",
    },
    {
        "value_id": 12,
        "code": "officer_closure",
        "name_ru": "Закрытие",
        "favorable": "мелкий ремонт, похороны",
        "unfavorable": "праздники, поиск медицинской помощи",
    },
]

DAY_OFFICER_DAY_BRANCHES = [
    "子",
    "丑",
    "寅",
    "卯",
    "辰",
    "巳",
    "午",
    "未",
    "申",
    "酉",
    "戌",
    "亥",
]

DAY_OFFICER_MATRIX_ROWS = [
    ("子", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
    ("丑", [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
    ("寅", [11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
    ("卯", [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
    ("辰", [9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8]),
    ("巳", [8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7]),
    ("午", [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]),
    ("未", [6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5]),
    ("申", [5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4]),
    ("酉", [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]),
    ("戌", [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2]),
    ("亥", [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1]),
]


def populate_heavenly_stems(con: sqlite3.Connection) -> None:
    """Заполняет справочник небесных стволов spr_heavenly_stem."""
    data = [
        (1, "甲", "Jia", "Цзя", "Дерево", "Ян"),
        (2, "乙", "Yi", "И", "Дерево", "Инь"),
        (3, "丙", "Bing", "Бин", "Огонь", "Ян"),
        (4, "丁", "Ding", "Дин", "Огонь", "Инь"),
        (5, "戊", "Wu", "У", "Земля", "Ян"),
        (6, "己", "Ji", "Цзи", "Земля", "Инь"),
        (7, "庚", "Geng", "Гэн", "Металл", "Ян"),
        (8, "辛", "Xin", "Синь", "Металл", "Инь"),
        (9, "壬", "Ren", "Жэнь", "Вода", "Ян"),
        (10, "癸", "Gui", "Гуй", "Вода", "Инь"),
    ]
    con.execute("DELETE FROM spr_heavenly_stem")
    con.executemany(
        """
        INSERT INTO spr_heavenly_stem
        (stem_id, stem_char, stem_pinyin, stem_rus, element, yin_yang)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        data,
    )


def populate_earthly_branches(con: sqlite3.Connection) -> None:
    """Заполняет справочник земных ветвей spr_earthly_branch."""
    data = [
        (1, "子", "Zi", "Крыса", "Вода", "Инь", 23, 1),
        (2, "丑", "Chou", "Бык", "Земля", "Ян", 1, 3),
        (3, "寅", "Yin", "Тигр", "Дерево", "Инь", 3, 5),
        (4, "卯", "Mao", "Кролик", "Дерево", "Ян", 5, 7),
        (5, "辰", "Chen", "Дракон", "Земля", "Инь", 7, 9),
        (6, "巳", "Si", "Змея", "Огонь", "Ян", 9, 11),
        (7, "午", "Wu", "Лошадь", "Огонь", "Инь", 11, 13),
        (8, "未", "Wei", "Коза", "Земля", "Ян", 13, 15),
        (9, "申", "Shen", "Обезьяна", "Металл", "Инь", 15, 17),
        (10, "酉", "You", "Петух", "Металл", "Ян", 17, 19),
        (11, "戌", "Xu", "Собака", "Земля", "Инь", 19, 21),
        (12, "亥", "Hai", "Свинья", "Вода", "Ян", 21, 23),
    ]
    con.execute("DELETE FROM spr_earthly_branch")
    con.executemany(
        """
        INSERT INTO spr_earthly_branch
        (branch_id, branch_char, branch_pinyin, branch_rus, element, yin_yang, start_hour, end_hour)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        data,
    )


def populate_solar_terms(con: sqlite3.Connection) -> None:
    """Заполняет справочник 24 солнечных сезонов spr_solar_term."""
    data = [
        (1, "立春", "Начало весны", "Li Chun", 315, 3),  # 寅
        (2, "雨水", "Дождевые воды", "Yu Shui", 330, 3),
        (3, "驚蟄", "Пробуждение насекомых", "Jing Zhe", 345, 4),  # 卯
        (4, "春分", "Весеннее равноденствие", "Chun Fen", 0, 4),
        (5, "清明", "Чистота и ясность", "Qing Ming", 15, 5),  # 辰
        (6, "穀雨", "Хлебные дожди", "Gu Yu", 30, 5),
        (7, "立夏", "Начало лета", "Li Xia", 45, 6),  # 巳
        (8, "小滿", "Малое изобилие", "Xiao Man", 60, 6),
        (9, "芒種", "Колошение хлебов", "Mang Zhong", 75, 7),  # 午
        (10, "夏至", "Летнее солнцестояние", "Xia Zhi", 90, 7),
        (11, "小暑", "Малая жара", "Xiao Shu", 105, 8),  # 未
        (12, "大暑", "Большая жара", "Da Shu", 120, 8),
        (13, "立秋", "Начало осени", "Li Qiu", 135, 9),  # 申
        (14, "處暑", "Прекращение жары", "Chu Shu", 150, 9),
        (15, "白露", "Белые росы", "Bai Lu", 165, 10),  # 酉
        (16, "秋分", "Осеннее равноденствие", "Qiu Fen", 180, 10),
        (17, "寒露", "Холодные росы", "Han Lu", 195, 11),  # 戌
        (18, "霜降", "Выпадение инея", "Shuang Jiang", 210, 11),
        (19, "立冬", "Начало зимы", "Li Dong", 225, 12),  # 亥
        (20, "小雪", "Малые снега", "Xiao Xue", 240, 12),
        (21, "大雪", "Большие снега", "Da Xue", 255, 1),  # 子
        (22, "冬至", "Зимнее солнцестояние", "Dong Zhi", 270, 1),
        (23, "小寒", "Малые холода", "Xiao Han", 285, 2),  # 丑
        (24, "大寒", "Большие холода", "Da Han", 300, 2),
    ]
    con.execute("DELETE FROM spr_solar_term")
    con.executemany(
        """
        INSERT INTO spr_solar_term
        (solar_term_id, solar_term_char, solar_term_name_ru, solar_term_pinyin,
         longitude_deg, month_branch_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        data,
    )


def populate_pillar_month_rule(con: sqlite3.Connection) -> None:
    """Заполняет справочник правил столпа месяца spr_pillar_month_rule."""
    # year_stem_id -> стартовый ствол месяца (month_stem_id) для 1-го месяца (寅)
    start_stem_by_year = {
        1: 3, 6: 3,   # 甲, 己 → 丙
        2: 5, 7: 5,   # 乙, 庚 → 戊
        3: 7, 8: 7,   # 丙, 辛 → 庚
        4: 9, 9: 9,   # 丁, 壬 → 壬
        5: 1, 10: 1,  # 戊, 癸 → 甲
    }
    records = []
    for year_stem_id, first_month_stem_id in start_stem_by_year.items():
        stem_id = first_month_stem_id
        for month_index in range(1, 13):
            records.append((year_stem_id, month_index, stem_id))
            stem_id += 1
            if stem_id > 10:
                stem_id = 1

    con.execute("DELETE FROM spr_pillar_month_rule")
    con.executemany(
        """
        INSERT INTO spr_pillar_month_rule (year_stem_id, month_index, month_stem_id)
        VALUES (?, ?, ?)
        """,
        records,
    )


def populate_pillar_hour_rule(con: sqlite3.Connection) -> None:
    """Заполняет справочник правил столпа часа spr_pillar_hour_rule."""
    # day_stem_group -> стартовый ствол часа для ветви 子 (branch_id = 1)
    start_hour_stem_by_group = {
        (1, 6): 1,   # 甲, 己 → 甲
        (2, 7): 3,   # 乙, 庚 → 丙
        (3, 8): 5,   # 丙, 辛 → 戊
        (4, 9): 7,   # 丁, 壬 → 庚
        (5, 10): 9,  # 戊, 癸 → 壬
    }
    records = []
    for day_stem_group, first_hour_stem_id in start_hour_stem_by_group.items():
        for day_stem_id in day_stem_group:
            stem_id = first_hour_stem_id
            for hour_branch_id in range(1, 13):
                records.append((day_stem_id, hour_branch_id, stem_id))
                stem_id += 1
                if stem_id > 10:
                    stem_id = 1

    con.execute("DELETE FROM spr_pillar_hour_rule")
    con.executemany(
        """
        INSERT INTO spr_pillar_hour_rule (day_stem_id, hour_branch_id, hour_stem_id)
        VALUES (?, ?, ?)
        """,
        records,
    )


def populate_pillar_cycle(con: sqlite3.Connection) -> None:
    """Заполняет таблицу spr_pillar_cycle полным 60-летним циклом Дзя-Цзы."""
    stem_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    branch_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    data = []
    stem_index = 0
    branch_index = 0
    for cycle_index in range(60):
        stem_id = stem_ids[stem_index]
        branch_id = branch_ids[branch_index]
        data.append((cycle_index, stem_id, branch_id))
        stem_index = (stem_index + 1) % len(stem_ids)
        branch_index = (branch_index + 1) % len(branch_ids)

    con.execute("DELETE FROM spr_pillar_cycle")
    con.executemany(
        """
        INSERT INTO spr_pillar_cycle (cycle_index, stem_id, branch_id)
        VALUES (?, ?, ?)
        """,
        data,
    )


def _ensure_day_officer_indicator(con: sqlite3.Connection) -> int:
    """Создаёт или обновляет показатель 12 офицеров дня и возвращает его ID."""

    cursor = con.cursor()
    cursor.execute(
        "SELECT indicator_id FROM spr_indicator WHERE code = ?",
        (DAY_OFFICER_INDICATOR_CODE,),
    )
    row = cursor.fetchone()
    indicator_id = row[0] if row else DAY_OFFICER_INDICATOR_ID

    if row is None:
        cursor.execute(
            """
            INSERT INTO spr_indicator (
                indicator_id,
                code,
                name_ru,
                description_ru,
                level,
                value_type,
                is_active
            ) VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
            (
                indicator_id,
                DAY_OFFICER_INDICATOR_CODE,
                DAY_OFFICER_NAME_RU,
                DAY_OFFICER_DESCRIPTION_RU,
                "day",
                "enum",
            ),
        )
    else:
        cursor.execute(
            """
            UPDATE spr_indicator
            SET name_ru = ?,
                description_ru = ?,
                level = ?,
                value_type = ?,
                is_active = 1
            WHERE indicator_id = ?
            """,
            (
                DAY_OFFICER_NAME_RU,
                DAY_OFFICER_DESCRIPTION_RU,
                "day",
                "enum",
                indicator_id,
            ),
        )

    return indicator_id


def _populate_day_officer_values(con: sqlite3.Connection, indicator_id: int) -> None:
    """Перезаписывает значения показателя 12 офицеров дня."""

    cursor = con.cursor()
    cursor.execute(
        "DELETE FROM spr_indicator_value WHERE indicator_id = ?",
        (indicator_id,),
    )

    cursor.executemany(
        """
        INSERT INTO spr_indicator_value (
            value_id,
            indicator_id,
            code,
            name_ru,
            description_ru,
            interpretation_ru,
            favorable_actions,
            unfavorable_actions,
            numeric_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                item["value_id"],
                indicator_id,
                item["code"],
                item["name_ru"],
                None,
                item["name_ru"],
                item["favorable"],
                item["unfavorable"],
                0.0,
            )
            for item in DAY_OFFICER_VALUE_DEFINITIONS
        ],
    )
def _populate_day_officer_mapping(con: sqlite3.Connection) -> None:
    """Формирует матрицу соответствия ветвей месяца и дня номеру офицера."""

    cursor = con.cursor()
    cursor.execute("SELECT branch_id, branch_char FROM spr_earthly_branch")
    branch_map = {char: branch_id for branch_id, char in cursor.fetchall()}

    missing = [char for char in DAY_OFFICER_DAY_BRANCHES if char not in branch_map]
    if missing:
        raise ValueError(
            f"Отсутствуют земные ветви в spr_earthly_branch: {', '.join(missing)}"
        )

    cursor.execute("DELETE FROM spr_day_officer_mapping")

    records = []
    for month_char, officer_ids in DAY_OFFICER_MATRIX_ROWS:
        if month_char not in branch_map:
            raise ValueError(f"Нет ветви месяца '{month_char}' в справочнике")
        if len(officer_ids) != len(DAY_OFFICER_DAY_BRANCHES):
            raise ValueError(
                "Матрица офицеров содержит некорректное число колонок для строки "
                f"{month_char}"
            )

        month_branch_id = branch_map[month_char]
        for day_char, officer_value_id in zip(
            DAY_OFFICER_DAY_BRANCHES, officer_ids
        ):
            day_branch_id = branch_map[day_char]
            records.append((month_branch_id, day_branch_id, officer_value_id))

    cursor.executemany(
        """
        INSERT INTO spr_day_officer_mapping (
            month_branch_id,
            day_branch_id,
            officer_value_id
        ) VALUES (?, ?, ?)
        """,
        records,
    )


def populate_day_officer_reference(con: sqlite3.Connection) -> int:
    """Готовит показатель 12 офицеров день и связанный справочник соответствий."""

    indicator_id = _ensure_day_officer_indicator(con)
    _populate_day_officer_values(con, indicator_id)
    _populate_day_officer_mapping(con)
    return indicator_id


def _ensure_analysis_scopes(con: sqlite3.Connection) -> None:
    """Гарантирует заполнение справочника областей применения правил."""

    cursor = con.cursor()
    cursor.execute("DELETE FROM spr_analysis_scope")
    cursor.executemany(
        """
        INSERT INTO spr_analysis_scope (scope_code, name_ru, description_ru)
        VALUES (?, ?, ?)
        """,
        ANALYSIS_SCOPE_PRESETS,
    )


def _assign_indicator_scopes(
    con: sqlite3.Connection,
    indicator_id: int,
    scopes: Tuple[str, ...],
) -> None:
    """Присваивает показателю набор областей применения."""

    cursor = con.cursor()
    cursor.execute(
        "DELETE FROM spr_indicator_scope WHERE indicator_id = ?",
        (indicator_id,),
    )
    if scopes:
        cursor.executemany(
            """
            INSERT INTO spr_indicator_scope (indicator_id, scope_code)
            VALUES (?, ?)
            """,
            [(indicator_id, scope) for scope in scopes],
        )


def _parse_master_dano_tables() -> Tuple[
    List[Dict[str, str | float | int]],
    Dict[Tuple[str, str, str], int],
]:
    """Читает методологию Мастера Дано и возвращает значения и матрицу."""

    with MASTER_DANO_FILE.open("r", encoding="utf-8") as fh:
        lines = [line.strip() for line in fh.readlines() if line.strip()]

    # Первая таблица начинается с заголовка "| id индикатора | ..."
    header_idx = next(
        idx for idx, line in enumerate(lines) if line.startswith("| id индикатора")
    )
    matrix_header_idx = next(
        idx for idx, line in enumerate(lines) if line.startswith("| ЗВ Месяца")
    )

    value_rows = lines[header_idx + 2 : matrix_header_idx]
    values: List[Dict[str, str | float | int]] = []
    for offset, row in enumerate(value_rows):
        parts = [part.strip() for part in row.split("|")[1:-1]]
        if len(parts) != 3:
            continue
        code_raw, name_ru, score_raw = parts
        code = _normalize_indicator_code(code_raw)
        numeric_score = _parse_numeric_score(score_raw)
        values.append(
            {
                "value_id": MASTER_DANO_BASE_VALUE_ID + offset,
                "code": code,
                "name_ru": name_ru,
                "numeric_score": numeric_score,
            }
        )

    mapping: Dict[Tuple[str, str, str], int] = {}
    header_row = lines[matrix_header_idx + 2]
    day_branches = [cell.strip() for cell in header_row.split("|")[3:-1]]

    current_row_idx = matrix_header_idx + 3
    while current_row_idx < len(lines):
        row = lines[current_row_idx]
        if not row.startswith("|"):
            break
        parts = [part.strip() for part in row.split("|")[1:-1]]
        current_row_idx += 1
        if len(parts) < 3:
            continue

        month_branch = parts[0]
        day_stem = parts[1]
        cell_values = parts[2 : 2 + len(day_branches)]
        for day_branch, indicator_code in zip(day_branches, cell_values):
            if not indicator_code:
                continue
            mapping[(month_branch, day_stem, day_branch)] = _normalize_indicator_code(indicator_code)

    return values, mapping


def _ensure_master_dano_indicator(con: sqlite3.Connection) -> int:
    """Создаёт или обновляет показатель Мастера Дано."""

    cursor = con.cursor()
    cursor.execute(
        "SELECT indicator_id FROM spr_indicator WHERE code = ?",
        (MASTER_DANO_INDICATOR_CODE,),
    )
    row = cursor.fetchone()
    indicator_id = row[0] if row else MASTER_DANO_INDICATOR_ID

    if row is None:
        cursor.execute(
            """
            INSERT INTO spr_indicator (
                indicator_id,
                code,
                name_ru,
                description_ru,
                level,
                value_type,
                is_active
            ) VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
            (
                indicator_id,
                MASTER_DANO_INDICATOR_CODE,
                MASTER_DANO_NAME_RU,
                MASTER_DANO_DESCRIPTION_RU,
                "day",
                "enum",
            ),
        )
    else:
        cursor.execute(
            """
            UPDATE spr_indicator
            SET name_ru = ?,
                description_ru = ?,
                level = ?,
                value_type = ?,
                is_active = 1
            WHERE indicator_id = ?
            """,
            (
                MASTER_DANO_NAME_RU,
                MASTER_DANO_DESCRIPTION_RU,
                "day",
                "enum",
                indicator_id,
            ),
        )

    return indicator_id


def _populate_master_dano_values(
    con: sqlite3.Connection,
    indicator_id: int,
    values: List[Dict[str, str | float | int]],
) -> Dict[str, int]:
    """Заполняет значения индикатора Мастера Дано и возвращает карту код → value_id."""

    cursor = con.cursor()
    cursor.execute(
        "DELETE FROM spr_indicator_value WHERE indicator_id = ?",
        (indicator_id,),
    )

    cursor.executemany(
        """
        INSERT INTO spr_indicator_value (
            value_id,
            indicator_id,
            code,
            name_ru,
            description_ru,
            interpretation_ru,
            numeric_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                int(item["value_id"]),
                indicator_id,
                _normalize_indicator_code(str(item["code"])),
                str(item["name_ru"]),
                None,
                str(item["name_ru"]),
                float(item["numeric_score"]),
            )
            for item in values
        ],
    )

    code_to_value_id: Dict[str, int] = {
        _normalize_indicator_code(str(item["code"])): int(item["value_id"]) for item in values
    }

    return code_to_value_id


def _populate_master_dano_mapping(
    con: sqlite3.Connection,
    mapping_raw: Dict[Tuple[str, str, str], int | str],
    code_to_value_id: Dict[str, int],
) -> None:
    """Формирует матрицу Мастера Дано в справочнике."""

    cursor = con.cursor()
    cursor.execute("SELECT branch_id, branch_char FROM spr_earthly_branch")
    branch_map = {char: branch_id for branch_id, char in cursor.fetchall()}

    cursor.execute("SELECT stem_id, stem_char FROM spr_heavenly_stem")
    stem_map = {char: stem_id for stem_id, char in cursor.fetchall()}

    cursor.execute("DELETE FROM spr_master_dano_mapping")

    records = []
    for (month_branch, day_stem, day_branch), code in mapping_raw.items():
        if month_branch not in branch_map or day_branch not in branch_map:
            raise ValueError(
                f"Неизвестная земная ветвь в матрице Мастера Дано: {month_branch}/{day_branch}"
            )
        if day_stem not in stem_map:
            raise ValueError(f"Неизвестный небесный ствол '{day_stem}' в матрице Мастера Дано")
        str_code = str(code)
        if str_code not in code_to_value_id:
            raise ValueError(f"Неизвестный код значения Мастера Дано: {str_code}")

        records.append(
            (
                branch_map[month_branch],
                stem_map[day_stem],
                branch_map[day_branch],
                code_to_value_id[str_code],
            )
        )

    if records:
        cursor.executemany(
            """
            INSERT INTO spr_master_dano_mapping (
                month_branch_id,
                day_stem_id,
                day_branch_id,
                indicator_value_id
            ) VALUES (?, ?, ?, ?)
            """,
            records,
        )


def populate_master_dano_reference(con: sqlite3.Connection) -> int:
    """Готовит справочники и матрицу качества дня по Мастеру Дано."""

    values, mapping = _parse_master_dano_tables()
    indicator_id = _ensure_master_dano_indicator(con)
    code_to_value_id = _populate_master_dano_values(con, indicator_id, values)
    _populate_master_dano_mapping(con, mapping, code_to_value_id)
    return indicator_id


def populate_solar_term_time(
    con: sqlite3.Connection,
    years: list[int],
) -> None:
    """Вычисляет астрономические моменты 24 солнечных сезонов и заполняет t_solar_term_time.

    Параметры:
    - years: список григорианских лет для расчёта.
    """
    cursor = con.cursor()
    cursor.execute("SELECT solar_term_id, longitude_deg FROM spr_solar_term ORDER BY solar_term_id")
    terms = cursor.fetchall()
    if not terms:
        raise ValueError("Таблица spr_solar_term пуста, невозможно рассчитать сезоны")

    if not years:
        return

    ph = get_placeholder()
    placeholders = ",".join(ph for _ in years)
    cursor.execute(f"DELETE FROM t_solar_term_time WHERE year IN ({placeholders})", years)

    for year in years:
        start_time = Time(f"{year}-01-01 00:00:00")
        end_time = Time(f"{year}-12-31 23:59:59")
        dt_span = end_time - start_time
        # Сетка 100000 точек на год для высокой точности
        times = start_time + dt_span * np.linspace(0.0, 1.0, 100000)
        sun_positions = get_sun(times).transform_to(GeocentricTrueEcliptic())
        sun_longitudes = sun_positions.lon.wrap_at(360 * u.deg).degree

        for solar_term_id, degree in terms:
            idx = int(np.abs(sun_longitudes - degree).argmin())
            closest_time = times[idx]
            dt_py: datetime = closest_time.to_datetime() # Возвращает UTC
            
            cursor.execute(
                f"""
                INSERT INTO t_solar_term_time
                    (year, solar_term_id, longitude_deg, crossing_utc, crossing_gmt0)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph})
                """,
                (year, solar_term_id, int(degree), dt_py.isoformat(), dt_py.isoformat()),
            )


def main() -> None:
    print("DEBUG: Using PostgreSQL connection")    con = get_connection()
    print(f"DEBUG: Connection type: {type(con)}")
    try:
        # Static tables already migrated to PostgreSQL
        # _ensure_analysis_scopes(con)
        # populate_heavenly_stems(con)
        # populate_earthly_branches(con)
        # populate_solar_terms(con)
        # populate_pillar_month_rule(con)
        # populate_pillar_hour_rule(con)
        # populate_pillar_cycle(con)
        # day_officer_indicator_id = populate_day_officer_reference(con)
        # _assign_indicator_scopes(con, day_officer_indicator_id, DAY_OFFICER_SCOPES)
        # master_dano_indicator_id = populate_master_dano_reference(con)
        # _assign_indicator_scopes(con, master_dano_indicator_id, MASTER_DANO_SCOPES)
        # populate_tongshu_reference_data(con)
        
        # Расчёт только для нужных лет
        current_year = date.today().year
        # 1864 (эталон), 2024..2027 (текущие и контроль)
        years = [1864] + list(range(current_year - 1, current_year + 3))
        
        print("Recalculating solar terms for years:", years)
        populate_solar_term_time(con, years)
        con.commit()
    finally:
        con.close()


if __name__ == "__main__":
    main()
