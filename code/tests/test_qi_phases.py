#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Qi Phases in TongShuDay"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from code.common.db_manager import db

def test_phase_count():
    result = db.fetch_one("SELECT COUNT(*) FROM spr_tongshu_phase")
    count = result[0] if result else 0
    assert count == 12, f"Expected 12 phases, got {count}"
    print(f"[OK] Qi phases: {count}")

def test_phase_mapping_count():
    result = db.fetch_one("SELECT COUNT(*) FROM spr_tongshu_phase_mapping")
    count = result[0] if result else 0
    assert count == 120, f"Expected 120 mappings, got {count}"
    print(f"[OK] Phase mappings: {count}")

def test_all_stems_covered():
    result = db.fetch_all("SELECT DISTINCT day_stem FROM spr_tongshu_phase_mapping")
    stems = [r[0] for r in result]
    assert len(stems) == 10, f"Expected 10 stems, got {len(stems)}"
    print(f"[OK] Stems in phase mapping: {len(stems)}")

if __name__ == "__main__":
    test_phase_count()
    test_phase_mapping_count()
    test_all_stems_covered()
    print("\nAll Qi phase tests passed!")
