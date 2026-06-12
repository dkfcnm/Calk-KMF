#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for TongShuDay extended fields (lunar_day, nayin per pillar,
dagua metadata, hexagram family, production chain).
PostgreSQL-only.
"""
import sys
import os
from datetime import date

sys.stdout.reconfigure(encoding='utf-8')
# Preload stdlib modules that conflict with project package names
# before adding project root to sys.path (code/calendar shadows stdlib calendar)
import calendar
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from code.tongshu.core.tongshu_day import TongShuDay
from code.common.db_manager import db


def test_tongshu_day_extended_fields():
    conn = db.get_connection()

    # Test a known date: 2026-05-24
    day = TongShuDay(date(2026, 5, 24), conn)

    # Basic pillars must be loaded
    assert day.year_pillar is not None
    assert day.month_pillar is not None
    assert day.day_pillar is not None

    # Lunar day
    assert day.lunar_day is not None
    assert isinstance(day.lunar_day, int)

    # Na Yin per pillar
    assert day.year_nayin_element is not None
    assert day.month_nayin_element is not None
    assert day.day_nayin_element is not None
    assert day.year_nayin_element in ['Дерево', 'Огонь', 'Земля', 'Металл', 'Вода']

    # Da Gua metadata
    assert day.year_period is not None
    assert day.month_period is not None
    assert day.day_period is not None
    assert isinstance(day.year_period, int)
    assert isinstance(day.year_element_num, int)

    # Hexagram family same (boolean)
    assert day.hexagram_family_same in [True, False]

    # Production chain
    assert day.production_chain is not None
    assert isinstance(day.production_chain, bool)

    conn.close()
    print("✅ test_tongshu_day_extended_fields passed")


def test_tongshu_day_another_date():
    conn = db.get_connection()

    day = TongShuDay(date(2026, 1, 1), conn)
    assert day.day_pillar is not None
    assert day.lunar_day is not None

    conn.close()
    print("✅ test_tongshu_day_another_date passed")


def test_tongshu_day_officer():
    conn = db.get_connection()

    day = TongShuDay(date(2026, 6, 15), conn)
    assert day.day_officer_char is not None
    assert day.day_officer_name_ru is not None

    conn.close()
    print("✅ test_tongshu_day_officer passed")


def test_tongshu_day_constellation():
    conn = db.get_connection()

    day = TongShuDay(date(2026, 7, 20), conn)
    assert day.constellation_char is not None
    assert day.constellation_name_ru is not None

    conn.close()
    print("✅ test_tongshu_day_constellation passed")


def test_tongshu_day_belt():
    conn = db.get_connection()

    day = TongShuDay(date(2026, 8, 10), conn)
    assert day.belt_type is not None
    assert day.belt_stars is not None

    conn.close()
    print("✅ test_tongshu_day_belt passed")


def test_tongshu_day_moon_phase():
    conn = db.get_connection()

    day = TongShuDay(date(2026, 9, 5), conn)
    assert day.moon_phase_name is not None
    assert isinstance(day.moon_phase_pct, (int, float))

    conn.close()
    print("✅ test_tongshu_day_moon_phase passed")


def test_tongshu_day_symbolic_stars():
    conn = db.get_connection()

    day = TongShuDay(date(2026, 10, 1), conn)
    assert day.symbolic_stars is not None
    assert isinstance(day.symbolic_stars, list)

    conn.close()
    print("✅ test_tongshu_day_symbolic_stars passed")


if __name__ == '__main__':
    test_tongshu_day_extended_fields()
    test_tongshu_day_another_date()
    test_tongshu_day_officer()
    test_tongshu_day_constellation()
    test_tongshu_day_belt()
    test_tongshu_day_moon_phase()
    test_tongshu_day_symbolic_stars()
    print("\n🎉 All TongShuDay extended tests passed!")
