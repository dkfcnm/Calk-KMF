#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test reference data population in PostgreSQL"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from code.common.db_manager import db

def test_shensha_rule_count():
    result = db.fetch_one("SELECT COUNT(*) FROM spr_tongshu_shensha_rule")
    count = result[0] if result else 0
    assert count > 0, f"spr_tongshu_shensha_rule is empty"
    print(f"[OK] spr_tongshu_shensha_rule: {count} records")

def test_ten_god_count():
    result = db.fetch_one("SELECT COUNT(*) FROM spr_tongshu_ten_god")
    count = result[0] if result else 0
    assert count == 100, f"spr_tongshu_ten_god has {count}, expected 100"
    print(f"[OK] spr_tongshu_ten_god: {count} records")

def test_phase_count():
    result = db.fetch_one("SELECT COUNT(*) FROM spr_tongshu_phase")
    count = result[0] if result else 0
    assert count == 12, f"spr_tongshu_phase has {count}, expected 12"
    print(f"[OK] spr_tongshu_phase: {count} records")

def test_phase_mapping_count():
    result = db.fetch_one("SELECT COUNT(*) FROM spr_tongshu_phase_mapping")
    count = result[0] if result else 0
    assert count == 120, f"spr_tongshu_phase_mapping has {count}, expected 120"
    print(f"[OK] spr_tongshu_phase_mapping: {count} records")

def test_branch_combo_count():
    result = db.fetch_one("SELECT COUNT(*) FROM spr_tongshu_branch_combo_rule")
    count = result[0] if result else 0
    assert count > 0, f"spr_tongshu_branch_combo_rule is empty"
    print(f"[OK] spr_tongshu_branch_combo_rule: {count} records")

def test_stem_combo_count():
    result = db.fetch_one("SELECT COUNT(*) FROM spr_tongshu_stem_combo_rule")
    count = result[0] if result else 0
    assert count > 0, f"spr_tongshu_stem_combo_rule is empty"
    print(f"[OK] spr_tongshu_stem_combo_rule: {count} records")

def test_tung_shu_daily_count():
    result = db.fetch_one("SELECT COUNT(*) FROM t_tung_shu_daily")
    count = result[0] if result else 0
    assert count > 0, f"t_tung_shu_daily is empty"
    print(f"[OK] t_tung_shu_daily: {count} records")

if __name__ == "__main__":
    test_shensha_rule_count()
    test_ten_god_count()
    test_phase_count()
    test_phase_mapping_count()
    test_branch_combo_count()
    test_stem_combo_count()
    test_tung_shu_daily_count()
    print("\nAll reference data tests passed!")
