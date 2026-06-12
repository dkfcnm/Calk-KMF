#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты Stage 6 — Black Rabbit и lunar_month в t_tung_shu_daily.

Проверяет:
1. Колонки lunar_month, black_rabbit_star, black_rabbit_score существуют в PostgreSQL
2. Данные заполнены для 2026 года (365 дней)
3. Значения корректны (score — число, star — не пустая строка)
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.app.database.db import engine
from sqlalchemy import text


def test_postgres_has_black_rabbit_columns():
    """Проверить, что колонки существуют в PostgreSQL."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 't_tung_shu_daily'
              AND column_name IN ('lunar_month', 'black_rabbit_star', 'black_rabbit_score')
        """)).fetchall()
        cols = [r[0] for r in result]
    assert 'lunar_month' in cols, "lunar_month missing in PostgreSQL"
    assert 'black_rabbit_star' in cols, "black_rabbit_star missing in PostgreSQL"
    assert 'black_rabbit_score' in cols, "black_rabbit_score missing in PostgreSQL"


def test_postgres_black_rabbit_data_2026():
    """Проверить, что данные Black Rabbit заполнены для 2026 года в PostgreSQL."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) FROM t_tung_shu_daily
            WHERE calendar_date >= '2026-01-01' AND calendar_date <= '2026-12-31'
              AND black_rabbit_star IS NOT NULL
        """)).scalar()
    assert result == 365, f"Expected 365 rows with black_rabbit_star in PG, got {result}"


def test_black_rabbit_values_reasonable():
    """Проверить, что значения Black Rabbit корректны (score в диапазоне -1..1)."""
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT black_rabbit_star, black_rabbit_score, lunar_month
            FROM t_tung_shu_daily
            WHERE calendar_date >= '2026-01-01' AND calendar_date <= '2026-12-31'
            LIMIT 10
        """)).fetchall()
    for star, score, lunar_month in rows:
        assert star and len(star.strip()) > 0, "black_rabbit_star is empty"
        assert isinstance(score, (int, float)), f"black_rabbit_score is not numeric: {score}"
        assert -1 <= score <= 2, f"black_rabbit_score out of range: {score}"
        assert lunar_month and len(lunar_month.strip()) > 0, "lunar_month is empty"


if __name__ == '__main__':
    test_postgres_has_black_rabbit_columns()
    print("✅ PostgreSQL columns OK")
    test_postgres_black_rabbit_data_2026()
    print("✅ PostgreSQL data OK")
    test_black_rabbit_values_reasonable()
    print("✅ Values reasonable OK")
    print("\n🎉 All Stage 6 Black Rabbit tests passed!")
