#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Personalized Tong Shu service — returns day data personalized to a profile's day master.
PostgreSQL-only via SQLAlchemy.
"""

from datetime import date
from typing import Optional, Dict, Any

from sqlalchemy import text
from sqlalchemy.orm import Session


def get_personalized_day_data(
    db: Session, target_date: date, profile_day_master: Optional[str] = None
) -> Dict[str, Any]:
    """Get full Tong Shu day data with optional personalization."""
    # 1. Load base day data from t_tung_shu_daily
    result = db.execute(text("""
        SELECT
            year_stem, year_branch, month_stem, month_branch,
            day_stem, day_branch, hour_stem, hour_branch
        FROM t_tung_shu_daily
        WHERE calendar_date = :target_date
        LIMIT 1
    """), {"target_date": target_date})
    row = result.fetchone()
    if not row:
        raise ValueError(f"No data found for date {target_date}")

    data = {
        "year_stem": row.year_stem,
        "year_branch": row.year_branch,
        "month_stem": row.month_stem,
        "month_branch": row.month_branch,
        "day_stem": row.day_stem,
        "day_branch": row.day_branch,
        "hour_stem": row.hour_stem,
        "hour_branch": row.hour_branch,
    }

    # 2. Batch hidden stems for all 4 pillars in one query
    branches = [data["year_branch"], data["month_branch"], data["day_branch"], data["hour_branch"]]
    branch_keys = ["year", "month", "day", "hour"]
    hidden_result = db.execute(text("""
        SELECT branch_char, stem_char, percentage, is_main
        FROM spr_hidden_stems
        WHERE branch_char = ANY(:branches)
        ORDER BY branch_char, order_num
    """), {"branches": branches})
    hidden_map: Dict[str, list] = {}
    for r in hidden_result.fetchall():
        hidden_map.setdefault(r.branch_char, []).append({
            "stem": r.stem_char, "percentage": r.percentage, "is_main": bool(r.is_main)
        })
    data["hidden_stems"] = {k: hidden_map.get(b, []) for k, b in zip(branch_keys, branches)}

    if not profile_day_master:
        return data

    # 3. Batch ten gods for all 4 stems in one query
    stems = [data["year_stem"], data["month_stem"], data["day_stem"], data["hour_stem"]]
    stem_keys = ["year", "month", "day", "hour"]
    tg_result = db.execute(text("""
        SELECT related_stem, god_code
        FROM spr_tongshu_ten_god
        WHERE day_stem = :day_stem AND related_stem = ANY(:stems)
    """), {"day_stem": profile_day_master, "stems": stems})
    tg_map = {r.related_stem: r.god_code for r in tg_result.fetchall()}
    data["personalized_ten_gods"] = {k: tg_map.get(s) for k, s in zip(stem_keys, stems)}

    # 4. Batch qi phases for all 4 branches in one query
    qp_result = db.execute(text("""
        SELECT m.reference_branch, p.name_ru
        FROM spr_tongshu_phase_mapping m
        JOIN spr_tongshu_phase p ON p.phase_id = m.phase_id
        WHERE m.day_stem = :day_stem AND m.reference_branch = ANY(:branches)
    """), {"day_stem": profile_day_master, "branches": branches})
    qp_map = {r.reference_branch: r.name_ru for r in qp_result.fetchall()}
    data["personalized_qi_phases"] = {k: qp_map.get(b) for k, b in zip(branch_keys, branches)}

    return data
