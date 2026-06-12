#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты Stage 6 — Hourly API endpoint.

Проверяет:
1. get_hours_data возвращает ровно 12 слотов
2. Каждый слот содержит time_str, hour_pillar, ten_god, qi_phase, hidden_stems, symbolic_stars
3. hidden_stems — список со stem, percentage, is_main
4. ten_god и qi_phase — не None для большинства слотов
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.app.database.db import engine
from api.app.services import tongshu_service
from sqlalchemy.orm import Session


def test_hourly_api_returns_12_slots():
    """Проверить, что API возвращает 12 двухчасовых слотов."""
    with Session(engine) as db:
        hours = tongshu_service.get_hours_data(db, date(2026, 1, 1))
    assert len(hours) == 12, f"Expected 12 hourly slots, got {len(hours)}"


def test_hourly_api_has_required_fields():
    """Проверить наличие обязательных полей в каждом слоте."""
    with Session(engine) as db:
        hours = tongshu_service.get_hours_data(db, date(2026, 1, 1))
    required = ['time_str', 'hour_stem', 'hour_branch', 'hour_pillar', 'ten_god', 'qi_phase', 'qi_phase_score', 'hidden_stems', 'symbolic_stars']
    for i, slot in enumerate(hours):
        for field in required:
            assert field in slot, f"Slot {i} missing field: {field}"


def test_hourly_hidden_stems_structure():
    """Проверить структуру hidden_stems."""
    with Session(engine) as db:
        hours = tongshu_service.get_hours_data(db, date(2026, 1, 1))
    for slot in hours:
        hs = slot['hidden_stems']
        assert isinstance(hs, list), f"hidden_stems must be list, got {type(hs)}"
        if hs:
            for item in hs:
                assert 'stem' in item, "hidden_stems item missing 'stem'"
                assert 'percentage' in item, "hidden_stems item missing 'percentage'"
                assert 'is_main' in item, "hidden_stems item missing 'is_main'"


def test_hourly_ten_god_not_all_none():
    """Проверить, что ten_god заполнен хотя бы для некоторых слотов."""
    with Session(engine) as db:
        hours = tongshu_service.get_hours_data(db, date(2026, 1, 1))
    filled = sum(1 for h in hours if h.get('ten_god'))
    assert filled >= 6, f"Expected at least 6 slots with ten_god, got {filled}"


def test_hourly_qi_phase_not_all_none():
    """Проверить, что qi_phase заполнен хотя бы для некоторых слотов."""
    with Session(engine) as db:
        hours = tongshu_service.get_hours_data(db, date(2026, 1, 1))
    filled = sum(1 for h in hours if h.get('qi_phase'))
    assert filled >= 6, f"Expected at least 6 slots with qi_phase, got {filled}"


if __name__ == '__main__':
    test_hourly_api_returns_12_slots()
    print("✅ 12 slots OK")
    test_hourly_api_has_required_fields()
    print("✅ Required fields OK")
    test_hourly_hidden_stems_structure()
    print("✅ Hidden stems structure OK")
    test_hourly_ten_god_not_all_none()
    print("✅ Ten god coverage OK")
    test_hourly_qi_phase_not_all_none()
    print("✅ Qi phase coverage OK")
    print("\n🎉 All Stage 6 Hourly API tests passed!")
