#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test 10 Gods in TongShuDay"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from code.common.db_manager import db

def test_ten_god_count():
    result = db.fetch_one("SELECT COUNT(*) FROM spr_tongshu_ten_god")
    count = result[0] if result else 0
    assert count == 100, f"Expected 100 ten god mappings, got {count}"
    print(f"[OK] Ten god mappings: {count}")

def test_all_day_masters():
    result = db.fetch_all("SELECT DISTINCT day_stem FROM spr_tongshu_ten_god")
    stems = [r[0] for r in result]
    assert len(stems) == 10, f"Expected 10 day masters, got {len(stems)}"
    print(f"[OK] Day masters covered: {len(stems)}")

def test_all_ten_gods():
    result = db.fetch_all("SELECT DISTINCT god_code FROM spr_tongshu_ten_god")
    gods = [r[0] for r in result]
    assert len(gods) == 10, f"Expected 10 god types, got {len(gods)}"
    print(f"[OK] Ten god types: {len(gods)}")

if __name__ == "__main__":
    test_ten_god_count()
    test_all_day_masters()
    test_all_ten_gods()
    print("\nAll ten gods tests passed!")
