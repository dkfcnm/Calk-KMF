#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Qi Men PostgreSQL service - reference data and chart lookups.
"""
import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "api"))

from datetime import date
from api.app.services.qimen_pg_service import (
    get_hourly_charts, get_daily_chart, get_monthly_chart, get_yearly_chart,
    get_all_levels, get_stars, get_gates, get_spirits, get_stem_combos, get_stem_combo,
    get_trigrams,
)


def test_get_stars():
    stars = get_stars()
    assert len(stars) == 9, f"Expected 9 stars, got {len(stars)}"
    assert stars[0]['star_char'] == '蓬'
    print(f"[OK] get_stars -> {len(stars)} stars")


def test_get_gates():
    gates = get_gates()
    assert len(gates) == 8, f"Expected 8 gates, got {len(gates)}"
    assert gates[0]['gate_char'] == '休'
    print(f"[OK] get_gates -> {len(gates)} gates")


def test_get_spirits():
    spirits = get_spirits()
    assert len(spirits) == 8, f"Expected 8 spirits, got {len(spirits)}"
    assert spirits[0]['spirit_char'] == '符'
    print(f"[OK] get_spirits -> {len(spirits)} spirits")


def test_get_stem_combos():
    combos = get_stem_combos()
    assert len(combos) == 100, f"Expected 100 combos, got {len(combos)}"
    assert combos[0]['combo_char'] == '甲甲'
    print(f"[OK] get_stem_combos -> {len(combos)} combos")


def test_get_stem_combo_specific():
    combo = get_stem_combo('甲', '丙')
    assert combo is not None
    assert combo['favorability'] == 1
    assert 'Зеленый дракон' in combo['name_ru']
    print(f"[OK] get_stem_combo(甲, 丙) -> {combo['name_ru']}")


def test_get_trigrams():
    trigrams = get_trigrams()
    assert len(trigrams) == 8, f"Expected 8 trigrams, got {len(trigrams)}"
    assert trigrams[0]['trigram_char'] == '乾'
    print(f"[OK] get_trigrams -> {len(trigrams)} trigrams")


def test_get_hourly_charts():
    charts = get_hourly_charts(date(2026, 6, 1), 'zhirun')
    assert len(charts) == 12, f"Expected 12 hourly charts, got {len(charts)}"
    assert 'chart_num' in charts[0]
    assert 'palaces' in charts[0]
    assert len(charts[0]['palaces']) == 9
    print(f"[OK] get_hourly_charts(2026-06-01) -> {len(charts)} charts, 9 palaces each")


def test_get_daily_chart():
    chart = get_daily_chart(date(2026, 6, 1), 'zhirun')
    assert chart is not None
    assert chart['level'] == 'day'
    assert chart['chart_num'] > 0
    assert len(chart['palaces']) == 9
    print(f"[OK] get_daily_chart(2026-06-01) -> Ju {chart['chart_num']} {chart['yin_yang']}")


def test_get_monthly_chart():
    chart = get_monthly_chart(2026, 6, 'zhirun')
    assert chart is not None
    assert chart['level'] == 'month'
    assert len(chart['palaces']) == 9
    print(f"[OK] get_monthly_chart(2026, 6) -> Ju {chart['chart_num']} {chart['yin_yang']}")


def test_get_yearly_chart():
    chart = get_yearly_chart(2026, 'zhirun')
    if chart:
        assert chart['level'] == 'year'
        assert len(chart['palaces']) == 9
        print(f"[OK] get_yearly_chart(2026) -> Ju {chart['chart_num']} {chart['yin_yang']}")
    else:
        print("[SKIP] get_yearly_chart(2026) -> no data in DB")


def test_get_all_levels():
    data = get_all_levels(date(2026, 6, 1), 'zhirun')
    assert 'hours' in data
    assert 'day' in data
    assert 'month' in data
    assert 'year' in data
    assert len(data['hours']) == 12
    assert data['day'] is not None
    assert data['month'] is not None
    print(f"[OK] get_all_levels(2026-06-01) -> year={data['year'] is not None}, month={data['month']['chart_num']}, day={data['day']['chart_num']}, hours={len(data['hours'])}")


def test_date_without_data():
    chart = get_daily_chart(date(2025, 1, 1), 'zhirun')
    assert chart is None
    hours = get_hourly_charts(date(2025, 1, 1), 'zhirun')
    assert len(hours) == 0
    print("[OK] Date without data returns empty/null gracefully")


TESTS = [
    test_get_stars,
    test_get_gates,
    test_get_spirits,
    test_get_stem_combos,
    test_get_stem_combo_specific,
    test_get_trigrams,
    test_get_hourly_charts,
    test_get_daily_chart,
    test_get_monthly_chart,
    test_get_yearly_chart,
    test_get_all_levels,
    test_date_without_data,
]


def run_tests():
    passed = 0
    failed = 0
    for func in TESTS:
        try:
            func()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"[FAIL] {func.__name__}: {e}")

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed out of {len(TESTS)}")
    return failed == 0


if __name__ == '__main__':
    ok = run_tests()
    sys.exit(0 if ok else 1)
