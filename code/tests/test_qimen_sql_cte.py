#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for compute_qimen_chart SQL CTE function against Python QimenEngine.
"""
import sys
import os
import random

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "api"))

from code.common.config import load_config_from_db
from code.qimen.engine import QimenEngine
from code.common.db_manager import db


def _chart_to_dict(chart):
    """Convert QimenChart dataclass to plain dict for JSON comparison."""
    return {
        'hour_id': chart.hour_id,
        'chart_num': chart.chart_num,
        'yin_yang': chart.yin_yang,
        'palaces': {
            str(k): {
                'palace_no': v.palace_no,
                'earth_stem': v.earth_stem,
                'is_fou_tou_earth': v.is_fou_tou_earth,
                'heaven_stem': v.heaven_stem,
                'is_fou_tou_heaven': v.is_fou_tou_heaven,
                'star': v.star,
                'is_main_star': v.is_main_star,
                'gate': v.gate,
                'is_main_gate': v.is_main_gate,
                'spirit': v.spirit,
            }
            for k, v in chart.palaces.items()
        }
    }


def test_random_charts(count=10):
    """Generate random charts and compare Python vs SQL output."""
    config = load_config_from_db()
    engine = QimenEngine(config)

    stems = config.stems
    branches = config.branches
    solar_term_ids = list(config.solar_term_ju.keys())

    mismatches = []
    for i in range(count):
        solar_term_id = random.choice(solar_term_ids)
        day_stem = random.choice(stems)
        day_branch = random.choice(branches)
        hour_stem = random.choice(stems)
        hour_branch = random.choice(branches)
        hour_id = f"test_{i}"

        # Python engine
        py_chart = engine.compute_chart(
            hour_id=hour_id,
            solar_term_id=solar_term_id,
            day_stem=day_stem,
            day_branch=day_branch,
            hour_stem=hour_stem,
            hour_branch=hour_branch,
        )
        py_dict = _chart_to_dict(py_chart)

        # SQL function
        sql = 'SELECT compute_qimen_chart(%s, %s, %s, %s, %s, %s, %s, %s)'
        params = [hour_id, solar_term_id, day_stem, day_branch, hour_stem, hour_branch, None, None]
        result = db.fetch_one(sql, params)
        sql_json = result[0]

        if py_dict != sql_json:
            mismatches.append({
                'hour_id': hour_id,
                'solar_term_id': solar_term_id,
                'day_pillar': day_stem + day_branch,
                'hour_pillar': hour_stem + hour_branch,
                'python': py_dict,
                'sql': sql_json,
            })

    if mismatches:
        print(f"[FAIL] {len(mismatches)} mismatch(es) out of {count} random charts")
        for m in mismatches[:3]:
            print(f"  -> {m['hour_id']}: st={m['solar_term_id']}, day={m['day_pillar']}, hour={m['hour_pillar']}")
            for p in range(1, 10):
                pk = str(p)
                if m['python']['palaces'][pk] != m['sql']['palaces'][pk]:
                    print(f"     Palace {p}:")
                    print(f"       PY:  {m['python']['palaces'][pk]}")
                    print(f"       SQL: {m['sql']['palaces'][pk]}")
        raise AssertionError(f"{len(mismatches)} chart(s) mismatched between Python and SQL")
    else:
        print(f"[OK] All {count} random charts match between Python and SQL")


def test_forced_charts(count=5):
    """Test forced ju / yin_yang combinations."""
    config = load_config_from_db()
    engine = QimenEngine(config)

    stems = config.stems
    branches = config.branches
    solar_term_ids = list(config.solar_term_ju.keys())

    mismatches = []
    for i in range(count):
        solar_term_id = random.choice(solar_term_ids)
        day_stem = random.choice(stems)
        day_branch = random.choice(branches)
        hour_stem = random.choice(stems)
        hour_branch = random.choice(branches)
        forced_ju = random.randint(1, 9)
        forced_yy = random.choice(['Yin', 'Yang'])
        hour_id = f"forced_{i}"

        py_chart = engine.compute_chart(
            hour_id=hour_id,
            solar_term_id=solar_term_id,
            day_stem=day_stem,
            day_branch=day_branch,
            hour_stem=hour_stem,
            hour_branch=hour_branch,
            forced_ju=forced_ju,
            forced_yin_yang=forced_yy,
        )
        py_dict = _chart_to_dict(py_chart)

        sql = 'SELECT compute_qimen_chart(%s, %s, %s, %s, %s, %s, %s, %s)'
        params = [hour_id, solar_term_id, day_stem, day_branch, hour_stem, hour_branch, forced_ju, forced_yy]
        result = db.fetch_one(sql, params)
        sql_json = result[0]

        if py_dict != sql_json:
            mismatches.append({
                'hour_id': hour_id,
                'forced_ju': forced_ju,
                'forced_yy': forced_yy,
                'python': py_dict,
                'sql': sql_json,
            })

    if mismatches:
        print(f"[FAIL] {len(mismatches)} mismatch(es) out of {count} forced charts")
        for m in mismatches[:3]:
            print(f"  -> {m['hour_id']}: ju={m['forced_ju']}, yy={m['forced_yy']}")
            for p in range(1, 10):
                pk = str(p)
                if m['python']['palaces'][pk] != m['sql']['palaces'][pk]:
                    print(f"     Palace {p}:")
                    print(f"       PY:  {m['python']['palaces'][pk]}")
                    print(f"       SQL: {m['sql']['palaces'][pk]}")
        raise AssertionError(f"{len(mismatches)} forced chart(s) mismatched")
    else:
        print(f"[OK] All {count} forced charts match between Python and SQL")


def test_specific_known_values():
    """Test a few specific known-good chart inputs."""
    config = load_config_from_db()
    engine = QimenEngine(config)

    cases = [
        ('known_1', 1, '甲', '子', '甲', '子'),
        ('known_2', 15, '甲', '子', '甲', '子'),
        ('known_3', 1, '丙', '寅', '庚', '午'),
        ('known_4', 5, '戊', '辰', '壬', '申'),
        ('known_5', 22, '癸', '酉', '乙', '丑'),
    ]

    for hour_id, solar_term_id, day_stem, day_branch, hour_stem, hour_branch in cases:
        py_chart = engine.compute_chart(
            hour_id=hour_id,
            solar_term_id=solar_term_id,
            day_stem=day_stem,
            day_branch=day_branch,
            hour_stem=hour_stem,
            hour_branch=hour_branch,
        )
        py_dict = _chart_to_dict(py_chart)

        sql = 'SELECT compute_qimen_chart(%s, %s, %s, %s, %s, %s, %s, %s)'
        params = [hour_id, solar_term_id, day_stem, day_branch, hour_stem, hour_branch, None, None]
        result = db.fetch_one(sql, params)
        sql_json = result[0]

        assert py_dict == sql_json, f"Mismatch for {hour_id}"

    print(f"[OK] All {len(cases)} specific known charts match")


TESTS = [
    test_specific_known_values,
    test_random_charts,
    test_forced_charts,
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
