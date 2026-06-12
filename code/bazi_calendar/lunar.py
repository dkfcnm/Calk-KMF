"""Расчёт лунно-солнечных дат китайского календаря.

Модуль содержит минимально необходимый функционал для конвертации
григорианской даты в лунную дату (год, месяц, день, признак високосного
месяца). Логика основана на широко распространённом конвертере Lunar-Solar
Calendar Converter (источник: https://github.com/isee15/Lunar-Solar-Calendar-Converter).

Данные и алгоритм адаптированы под стиль проекта, документация и код —
на русском языке. Основная цель — автономный расчёт лунного месяца и дня
без зависимости от внешних пакетов во время выполнения.

Последнее обновление: 2025-12-25 16:25 MSK.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

from .db import ensure_utc


DEFAULT_LUNAR_TZ_OFFSET = 8  # Китайское стандартное время (UTC+8)

# Кэш объектов timezone для частых смещений (обычно 27 штук)
_TZ_CACHE: dict[int, timezone] = {}


class LunarDateNotExist(ValueError):
    """Исключение для недопустимых лунных дат."""


@dataclass(frozen=True, slots=True)
class LunarDate:
    """Структура с результатом конвертации в лунный календарь."""

    year: int
    month: int
    day: int
    is_leap_month: bool


@dataclass(frozen=True, slots=True)
class SolarDate:
    """Вспомогательная структура для работы с григорианской датой."""

    year: int
    month: int
    day: int

    def to_date(self) -> date:
        return date(self.year, self.month, self.day)

    @classmethod
    def from_date(cls, value: date) -> SolarDate:
        return cls(value.year, value.month, value.day)


@dataclass(frozen=True, slots=True)
class _LunarInternal:
    """Внутренняя структура, используемая при расчётах."""

    year: int
    month: int
    day: int
    is_leap_month: bool


# Табличные данные конвертера. Содержат информацию о длине месяцев
# и високосных месяцах для диапазона 1887–2110 годов.
# Источник: https://github.com/isee15/Lunar-Solar-Calendar-Converter
_LUNAR_MONTH_DAYS = [
    1887,
    0x1694,
    0x16AA,
    0x4AD5,
    0x0AB6,
    0xC4B7,
    0x04AE,
    0x0A56,
    0xB52A,
    0x1D2A,
    0x0D54,
    0x75AA,
    0x156A,
    0x1096D,
    0x095C,
    0x14AE,
    0xAA4D,
    0x1A4C,
    0x1B2A,
    0x08D55,
    0x0AD4,
    0x135A,
    0x495D,
    0x095C,
    0xD49B,
    0x149A,
    0x1A4A,
    0x0BAA5,
    0x16A8,
    0x1AD4,
    0x52DA,
    0x12B6,
    0xE937,
    0x092E,
    0x1496,
    0xB64B,
    0x0D4A,
    0x0DA8,
    0x95B5,
    0x056C,
    0x12AE,
    0x492F,
    0x092E,
    0xCC96,
    0x1A94,
    0x1D4A,
    0x0ADA9,
    0x0B5A,
    0x056C,
    0x726E,
    0x125C,
    0xF92D,
    0x192A,
    0x1A94,
    0x0DB4A,
    0x16AA,
    0x0AD4,
    0x955B,
    0x04BA,
    0x125A,
    0x592B,
    0x152A,
    0xF695,
    0x0D94,
    0x16AA,
    0x0AAB5,
    0x09B4,
    0x14B6,
    0x6A57,
    0x0A56,
    0x1152A,
    0x1D2A,
    0x0D54,
    0x0D5AA,
    0x156A,
    0x096C,
    0x94AE,
    0x14AE,
    0x0A4C,
    0x7D26,
    0x1B2A,
    0xEB55,
    0x0AD4,
    0x12DA,
    0xA95D,
    0x095A,
    0x149A,
    0x9A4D,
    0x1A4A,
    0x11AA5,
    0x16A8,
    0x16D4,
    0xD2DA,
    0x12B6,
    0x0936,
    0x9497,
    0x1496,
    0x1564B,
    0x0D4A,
    0x0DA8,
    0xD5B4,
    0x156C,
    0x12AE,
    0xA92F,
    0x092E,
    0x0C96,
    0x6D4A,
    0x1D4A,
    0x10D65,
    0x0B58,
    0x156C,
    0xB26D,
    0x125C,
    0x192C,
    0x9A95,
    0x1A94,
    0x1B4A,
    0x4B55,
    0x0AD4,
    0xF55B,
    0x04BA,
    0x125A,
    0xB92B,
    0x152A,
    0x1694,
    0x96AA,
    0x15AA,
    0x12AB5,
    0x0974,
    0x14B6,
    0xCA57,
    0x0A56,
    0x1526,
    0x8E95,
    0x0D54,
    0x15AA,
    0x49B5,
    0x096C,
    0xD4AE,
    0x149C,
    0x1A4C,
    0xBD26,
    0x1AA6,
    0x0B54,
    0x6D6A,
    0x12DA,
    0x1695D,
    0x095A,
    0x149A,
    0xDA4B,
    0x1A4A,
    0x1AA4,
    0xBB54,
    0x16B4,
    0x0ADA,
    0x495B,
    0x0936,
    0xF497,
    0x1496,
    0x154A,
    0xB6A5,
    0x0DA4,
    0x15B4,
    0x6AB6,
    0x126E,
    0x1092F,
    0x092E,
    0x0C96,
    0xCD4A,
    0x1D4A,
    0x0D64,
    0x956C,
    0x155C,
    0x125C,
    0x792E,
    0x192C,
    0xFA95,
    0x1A94,
    0x1B4A,
    0xAB55,
    0x0AD4,
    0x14DA,
    0x8A5D,
    0x0A5A,
    0x1152B,
    0x152A,
    0x1694,
    0xD6AA,
    0x15AA,
    0x0AB4,
    0x94BA,
    0x14B6,
    0x0A56,
    0x7527,
    0x0D26,
    0xEE53,
    0x0D54,
    0x15AA,
    0xA9B5,
    0x096C,
    0x14AE,
    0x8A4E,
    0x1A4C,
    0x11D26,
    0x1AA4,
    0x1B54,
    0xCD6A,
    0x0ADA,
    0x095C,
    0x949D,
    0x149A,
    0x1A2A,
    0x5B25,
    0x1AA4,
    0xFB52,
    0x16B4,
    0x0ABA,
    0xA95B,
    0x0936,
    0x1496,
    0x9A4B,
    0x154A,
    0x136A5,
    0x0DA4,
    0x15AC,
]

_SOLAR_1_1 = [
    1887,
    0xEC04C,
    0xEC23F,
    0xEC435,
    0xEC649,
    0xEC83E,
    0xECA51,
    0xECC46,
    0xECE3A,
    0xED04D,
    0xED242,
    0xED436,
    0xED64A,
    0xED83F,
    0xEDA53,
    0xEDC48,
    0xEDE3D,
    0xEE050,
    0xEE244,
    0xEE439,
    0xEE64D,
    0xEE842,
    0xEEA36,
    0xEEC4A,
    0xEEE3E,
    0xEF052,
    0xEF246,
    0xEF43A,
    0xEF64E,
    0xEF843,
    0xEFA37,
    0xEFC4B,
    0xEFE41,
    0xF0054,
    0xF0248,
    0xF043C,
    0xF0650,
    0xF0845,
    0xF0A38,
    0xF0C4D,
    0xF0E42,
    0xF1037,
    0xF124A,
    0xF143E,
    0xF1651,
    0xF1846,
    0xF1A3A,
    0xF1C4E,
    0xF1E44,
    0xF2038,
    0xF224B,
    0xF243F,
    0xF2653,
    0xF2848,
    0xF2A3B,
    0xF2C4F,
    0xF2E45,
    0xF3039,
    0xF324D,
    0xF3442,
    0xF3636,
    0xF384A,
    0xF3A3D,
    0xF3C51,
    0xF3E46,
    0xF403B,
    0xF424E,
    0xF4443,
    0xF4638,
    0xF484C,
    0xF4A3F,
    0xF4C52,
    0xF4E48,
    0xF503C,
    0xF524F,
    0xF5445,
    0xF5639,
    0xF584D,
    0xF5A42,
    0xF5C35,
    0xF5E49,
    0xF603E,
    0xF6251,
    0xF6446,
    0xF663B,
    0xF684F,
    0xF6A43,
    0xF6C37,
    0xF6E4B,
    0xF703F,
    0xF7252,
    0xF7447,
    0xF763C,
    0xF7850,
    0xF7A45,
    0xF7C39,
    0xF7E4D,
    0xF8042,
    0xF8254,
    0xF8449,
    0xF863D,
    0xF8851,
    0xF8A46,
    0xF8C3B,
    0xF8E4F,
    0xF9044,
    0xF9237,
    0xF944A,
    0xF963F,
    0xF9853,
    0xF9A47,
    0xF9C3C,
    0xF9E50,
    0xFA045,
    0xFA238,
    0xFA44C,
    0xFA641,
    0xFA836,
    0xFAA49,
    0xFAC3D,
    0xFAE52,
    0xFB047,
    0xFB23A,
    0xFB44E,
    0xFB643,
    0xFB837,
    0xFBA4A,
    0xFBC3F,
    0xFBE53,
    0xFC048,
    0xFC23C,
    0xFC450,
    0xFC645,
    0xFC839,
    0xFCA4C,
    0xFCC41,
    0xFCE36,
    0xFD04A,
    0xFD23D,
    0xFD451,
    0xFD646,
    0xFD83A,
    0xFDA4D,
    0xFDC43,
    0xFDE37,
    0xFE04B,
    0xFE23F,
    0xFE453,
    0xFE648,
    0xFE83C,
    0xFEA4F,
    0xFEC44,
    0xFEE38,
    0xFF04C,
    0xFF241,
    0xFF436,
    0xFF64A,
    0xFF83E,
    0xFFA51,
    0xFFC46,
    0xFFE3A,
    0x10004E,
    0x100242,
    0x100437,
    0x10064B,
    0x100841,
    0x100A53,
    0x100C48,
    0x100E3C,
    0x10104F,
    0x101244,
    0x101438,
    0x10164C,
    0x101842,
    0x101A35,
    0x101C49,
    0x101E3D,
    0x102051,
    0x102245,
    0x10243A,
    0x10264E,
    0x102843,
    0x102A37,
    0x102C4B,
    0x102E3F,
    0x103053,
    0x103247,
    0x10343B,
    0x10364F,
    0x103845,
    0x103A38,
    0x103C4C,
    0x103E42,
    0x104036,
    0x104249,
    0x10443D,
    0x104651,
    0x104846,
    0x104A3A,
    0x104C4E,
    0x104E43,
    0x105038,
    0x10524A,
    0x10543E,
    0x105652,
    0x105847,
    0x105A3B,
    0x105C4F,
    0x105E45,
    0x106039,
    0x10624C,
    0x106441,
    0x106635,
    0x106849,
    0x106A3D,
    0x106C51,
    0x106E47,
    0x10703C,
    0x10724F,
    0x107444,
    0x107638,
    0x10784C,
    0x107A3F,
    0x107C53,
    0x107E48,
]


def _get_bit_int(data: int, length: int, shift: int) -> int:
    """Возвращает выделенный блок бит."""

    return (data >> shift) & ((1 << length) - 1)


def _solar_to_int(year: int, month: int, day: int) -> int:
    """Преобразует григорианскую дату в число дней относительно эпохи."""

    month = (month + 9) % 12
    year -= month // 10
    return (
        365 * year
        + year // 4
        - year // 100
        + year // 400
        + (month * 306 + 5) // 10
        + (day - 1)
    )


def _solar_from_int(g: int) -> SolarDate:
    """Обратное преобразование из счётчика дней в григорианскую дату."""

    year = (10000 * g + 14780) // 3652425
    ddd = g - (365 * year + year // 4 - year // 100 + year // 400)
    if ddd < 0:
        year -= 1
        ddd = g - (365 * year + year // 4 - year // 100 + year // 400)
    mi = (100 * ddd + 52) // 3060
    month = (mi + 2) % 12 + 1
    year += (mi + 2) // 12
    day = ddd - (mi * 306 + 5) // 10 + 1
    return SolarDate(year, month, day)


def _lunar_to_solar(lunar: _LunarInternal) -> SolarDate:
    """Конвертирует лунную дату во внешний SolarDate."""

    days = _LUNAR_MONTH_DAYS[lunar.year - _LUNAR_MONTH_DAYS[0]]
    leap = _get_bit_int(days, 4, 13)
    offset = 0
    loop_end = leap
    if not lunar.is_leap_month:
        if lunar.month <= leap or leap == 0:
            loop_end = lunar.month - 1
        else:
            loop_end = lunar.month

    for i in range(0, loop_end):
        offset += 30 if _get_bit_int(days, 1, 12 - i) else 29
    offset += lunar.day

    solar11 = _SOLAR_1_1[lunar.year - _SOLAR_1_1[0]]
    year = _get_bit_int(solar11, 12, 9)
    month = _get_bit_int(solar11, 4, 5)
    day = _get_bit_int(solar11, 5, 0)

    return _solar_from_int(_solar_to_int(year, month, day) + offset - 1)


def _solar_to_lunar(solar: SolarDate) -> _LunarInternal:
    """Обратная конвертация: григорианская дата → лунная."""

    index = solar.year - _SOLAR_1_1[0]
    data = (solar.year << 9) | (solar.month << 5) | solar.day
    if _SOLAR_1_1[index] > data:
        index -= 1

    solar11 = _SOLAR_1_1[index]
    year = _get_bit_int(solar11, 12, 9)
    month = _get_bit_int(solar11, 4, 5)
    day = _get_bit_int(solar11, 5, 0)
    offset = _solar_to_int(solar.year, solar.month, solar.day) - _solar_to_int(year, month, day)

    days = _LUNAR_MONTH_DAYS[index]
    leap = _get_bit_int(days, 4, 13)

    lunar_year = index + _SOLAR_1_1[0]
    lunar_month = 1
    offset += 1

    for i in range(0, 13):
        month_days = 30 if _get_bit_int(days, 1, 12 - i) else 29
        if offset > month_days:
            lunar_month += 1
            offset -= month_days
        else:
            break

    lunar_day = offset
    is_leap = False
    if leap != 0 and lunar_month > leap:
        lunar_month -= 1
        if lunar_month == leap:
            is_leap = True

    return _LunarInternal(lunar_year, lunar_month, lunar_day, is_leap)


def convert_solar_to_lunar(solar: SolarDate) -> LunarDate:
    """Конвертирует григорианскую дату в лунную.

    Параметры:
    - solar: григорианская дата.

    Возвращает:
    - структуру :class:`LunarDate`.

    Исключения:
    - LunarDateNotExist, если дата вне диапазона таблиц (1887–2110).
    """

    if not (1887 <= solar.year <= 2110):
        raise LunarDateNotExist(
            "Поддерживаются годы в диапазоне 1887–2110 (исходные таблицы Lunar-Solar Converter)."
        )

    lunar_internal = _solar_to_lunar(solar)
    return LunarDate(
        year=lunar_internal.year,
        month=lunar_internal.month,
        day=lunar_internal.day,
        is_leap_month=lunar_internal.is_leap_month,
    )


def convert_lunar_to_solar(lunar: LunarDate) -> SolarDate:
    """Конвертирует лунную дату в григорианскую."""

    if not (1887 <= lunar.year <= 2110):
        raise LunarDateNotExist(
            "Поддерживаются годы в диапазоне 1887–2110 (исходные таблицы Lunar-Solar Converter)."
        )

    return _lunar_to_solar(
        _LunarInternal(
            year=lunar.year,
            month=lunar.month,
            day=lunar.day,
            is_leap_month=lunar.is_leap_month,
        )
    )


def calc_lunar_date(
    dt_utc: datetime,
    tz_offset_hours: int | None = None,
    base_tz_offset_hours: int = DEFAULT_LUNAR_TZ_OFFSET,
) -> LunarDate:
    """Возвращает лунную дату для указанного момента.

    Параметры:
    - dt_utc: момент времени в UTC;
    - tz_offset_hours: дополнительное смещение, если нужно учитывать локальное
      время пользователя (опционально, по умолчанию None);
    - base_tz_offset_hours: смещение часового пояса, в котором рассчитывается
      лунный календарь (по умолчанию UTC+8 — Пекин).

    Возвращает:
    - :class:`LunarDate` с номером лунного месяца, дня и признаками високосного
      месяца.

    Особенности:
    - Использует локальную дату пользователя (на основе `tz_offset_hours`) для определения
      лунного дня.
    - Это обеспечивает смену лунного дня одновременно со сменой столпа дня (в полночь
      по местному времени).
    """

    dt_utc = ensure_utc(dt_utc)
    
    # 1. Determine the target "Day" based on timezone
    if tz_offset_hours is not None:
        # Use user's local time to determine the calendar date
        target_tz = _TZ_CACHE.get(tz_offset_hours)
        if target_tz is None:
            target_tz = timezone(timedelta(hours=tz_offset_hours))
            _TZ_CACHE[tz_offset_hours] = target_tz
        dt_target = dt_utc.astimezone(target_tz)
    else:
        # Fallback to Base TZ (Beijing) if no user offset provided
        target_tz = _TZ_CACHE.get(base_tz_offset_hours)
        if target_tz is None:
            target_tz = timezone(timedelta(hours=base_tz_offset_hours))
            _TZ_CACHE[base_tz_offset_hours] = target_tz
        dt_target = dt_utc.astimezone(target_tz)

    # 2. Use the calendar date (Year, Month, Day) as the key for Lunar Table lookup
    # This assumes that the mapping "Gregorian Date -> Lunar Date" is applied 
    # to the local civil calendar date.
    
    # ADJUSTMENT: User requires Lunar Day to change with the Day Pillar.
    # Day Pillar changes at 23:00 (Start of Rat Hour).
    # Therefore, 23:00..23:59 of Day X should be treated as Day X+1 for Lunar lookup.
    # We add 1 hour to the time. If it's >= 23:00, it becomes 00:00+ of next day.
    dt_target_adjusted = dt_target + timedelta(hours=1)
    
    solar = SolarDate(dt_target_adjusted.year, dt_target_adjusted.month, dt_target_adjusted.day)
    return convert_solar_to_lunar(solar)


def calc_lunar_components(
    dt_utc: datetime,
    tz_offset_hours: int | None = None,
    base_tz_offset_hours: int = DEFAULT_LUNAR_TZ_OFFSET,
) -> tuple[int, int, bool]:
    """Упрощённый интерфейс: возвращает (месяц, день, признак високосного месяца)."""

    lunar_date = calc_lunar_date(
        dt_utc=dt_utc,
        tz_offset_hours=tz_offset_hours,
        base_tz_offset_hours=base_tz_offset_hours,
    )
    return lunar_date.month, lunar_date.day, lunar_date.is_leap_month
