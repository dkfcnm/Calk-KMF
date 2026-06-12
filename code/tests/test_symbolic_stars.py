#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test symbolic stars (shensha) in TongShuDay"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from code.common.db_manager import db

def test_shensha_rules_populated():
    result = db.fetch_one("SELECT COUNT(*) FROM spr_tongshu_shensha_rule")
    count = result[0] if result else 0
    assert count >= 281, f"Expected >= 281 shensha rules, got {count}"
    print(f"[OK] Shensha rules: {count}")

def test_noble_man_exists():
    result = db.fetch_all(
        "SELECT * FROM spr_tongshu_shensha_rule WHERE star_name LIKE '%Благородный%'")
    assert len(result) > 0, "Noble man rules not found"
    print(f"[OK] Noble man rules: {len(result)}")

def test_wenchang_exists():
    result = db.fetch_all(
        "SELECT * FROM spr_tongshu_shensha_rule WHERE star_name LIKE '%академик%'")
    assert len(result) > 0, "Wen Chang rules not found"
    print(f"[OK] Wen Chang rules: {len(result)}")

if __name__ == "__main__":
    test_shensha_rules_populated()
    test_noble_man_exists()
    test_wenchang_exists()
    print("\nAll symbolic stars tests passed!")
