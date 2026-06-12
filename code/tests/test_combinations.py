#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test combinations in TongShuDay"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from code.common.db_manager import db

def test_branch_combo_rules_exist():
    result = db.fetch_one("SELECT COUNT(*) FROM spr_tongshu_branch_combo_rule")
    assert result[0] > 0
    print(f"[OK] Branch combo rules: {result[0]}")

def test_stem_combo_rules_exist():
    result = db.fetch_one("SELECT COUNT(*) FROM spr_tongshu_stem_combo_rule")
    assert result[0] > 0
    print(f"[OK] Stem combo rules: {result[0]}")

def test_combination_types():
    result = db.fetch_all("SELECT DISTINCT combo_name FROM spr_tongshu_branch_combo_rule")
    types = [r[0] for r in result]
    assert len(types) > 0
    print(f"[OK] Branch combo types: {types}")

if __name__ == "__main__":
    test_branch_combo_rules_exist()
    test_stem_combo_rules_exist()
    test_combination_types()
    print("\nAll combination tests passed!")
