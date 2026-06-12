#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tong Shu service — works with t_tung_shu_daily (PostgreSQL-only).
"""

import json
from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


def _parse_json_field(value):
    """Parse JSON string to Python object."""
    if not value:
        return None
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


def _row_to_dict(row) -> dict:
    """Convert SQLAlchemy row to dict with JSON parsing."""
    data = dict(row._mapping)
    # Parse JSON fields
    for field in ['belt_stars', 'symbolic_stars', 'combinations', 'qi_phases', 'ten_gods', 'hidden_stems']:
        if field in data and data[field] is not None:
            data[field] = _parse_json_field(data[field])
    return data


def get_day_data(db: Session, target_date: date) -> Optional[dict]:
    """Get Tong Shu data for a single day from t_tung_shu_daily (PostgreSQL)."""
    query = text("""
        SELECT * FROM t_tung_shu_daily
        WHERE calendar_date = :target_date
        LIMIT 1
    """)
    result = db.execute(query, {"target_date": target_date}).fetchone()
    if not result:
        return None
    return _row_to_dict(result)


def _get_range_data(db: Session, start_date: date, end_date: date) -> List[dict]:
    """Get Tong Shu data for a date range [start, end]."""
    query = text("""
        SELECT * FROM t_tung_shu_daily
        WHERE calendar_date >= :start_date AND calendar_date <= :end_date
        ORDER BY calendar_date
    """)
    results = db.execute(query, {"start_date": start_date, "end_date": end_date}).fetchall()
    return [_row_to_dict(row) for row in results]


def get_month_data(db: Session, year: int, month: int) -> List[dict]:
    """Get Tong Shu data for an entire month."""
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    return _get_range_data(db, start_date, end_date)


def get_week_data(db: Session, start_date: date) -> List[dict]:
    """Get Tong Shu data for a week starting from start_date."""
    end_date = start_date + timedelta(days=6)
    return _get_range_data(db, start_date, end_date)


def get_year_data(db: Session, year: int) -> List[dict]:
    """Get Tong Shu data for an entire year."""
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    return _get_range_data(db, start_date, end_date)


def get_year_data_paginated(db: Session, year: int, page: int = 1, page_size: int = 31) -> dict:
    """Get Tong Shu data for an entire year with pagination."""
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    # Get total count
    count_query = text("""
        SELECT COUNT(*) FROM t_tung_shu_daily
        WHERE calendar_date >= :start_date AND calendar_date <= :end_date
    """)
    total = db.execute(count_query, {"start_date": start_date, "end_date": end_date}).scalar()

    # Calculate offset
    offset = (page - 1) * page_size

    # Get paginated results
    query = text("""
        SELECT * FROM t_tung_shu_daily
        WHERE calendar_date >= :start_date AND calendar_date <= :end_date
        ORDER BY calendar_date
        LIMIT :limit OFFSET :offset
    """)
    results = db.execute(query, {
        "start_date": start_date,
        "end_date": end_date,
        "limit": page_size,
        "offset": offset,
    }).fetchall()

    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

    return {
        "data": [_row_to_dict(row) for row in results],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def get_hours_data(db: Session, target_date: date) -> List[dict]:
    """
    Get hourly data for a specific day from t_bazi_hourly (PostgreSQL).
    Returns 12 double-hour slots with extended data (10 gods, qi phases, hidden stems, symbolic stars).
    """
    # 1. Main query: hour pillars + 10 gods + qi phases
    query = text("""
        SELECT 
            h.slot_start_time_local as time_str,
            h.hour_stem,
            h.hour_branch,
            h.day_stem,
            h.day_branch,
            h.year_stem,
            h.year_branch,
            h.month_stem,
            h.month_branch,
            tg.god_code as ten_god,
            ph.name_ru as qi_phase,
            ph.numeric_score as qi_phase_score
        FROM 
            t_bazi_hourly h
        LEFT JOIN 
            spr_tongshu_ten_god tg ON h.day_stem = tg.day_stem AND h.hour_stem = tg.related_stem
        LEFT JOIN 
            spr_tongshu_phase_mapping pm ON h.day_stem = pm.day_stem AND h.hour_branch = pm.reference_branch
        LEFT JOIN 
            spr_tongshu_phase ph ON pm.phase_id = ph.phase_id
        WHERE 
            h.slot_start_date_local = :target_date
            AND h.tz_offset_hours = 0
        ORDER BY
            h.slot_start_time_local
    """)

    results = db.execute(query, {"target_date": target_date.isoformat()}).fetchall()

    # 2. Collect all hour branches for hidden stems query
    hour_branches = set()
    hours_data = []
    for row in results:
        hour_branches.add(row.hour_branch)
        hours_data.append({
            "time_str": row.time_str,
            "hour_stem": row.hour_stem,
            "hour_branch": row.hour_branch,
            "hour_pillar": row.hour_stem + row.hour_branch,
            "day_stem": row.day_stem,
            "day_branch": row.day_branch,
            "year_stem": row.year_stem,
            "year_branch": row.year_branch,
            "month_stem": row.month_stem,
            "month_branch": row.month_branch,
            "ten_god": row.ten_god,
            "qi_phase": row.qi_phase,
            "qi_phase_score": row.qi_phase_score,
            "hidden_stems": [],
            "symbolic_stars": [],
        })

    if not hours_data:
        return []

    # 3. Hidden stems for all hour branches
    if hour_branches:
        hidden_query = text("""
            SELECT branch_char, stem_char, percentage, is_main
            FROM spr_hidden_stems
            WHERE branch_char = ANY(:branches)
            ORDER BY branch_char, percentage DESC
        """)
        hidden_results = db.execute(hidden_query, {"branches": list(hour_branches)}).fetchall()
        hidden_map = {}
        for row in hidden_results:
            if row.branch_char not in hidden_map:
                hidden_map[row.branch_char] = []
            hidden_map[row.branch_char].append({
                "stem": row.stem_char,
                "percentage": row.percentage,
                "is_main": row.is_main,
            })
        for hd in hours_data:
            hd["hidden_stems"] = hidden_map.get(hd["hour_branch"], [])

    # 4. Symbolic stars — query once for the day (context is identical for all hours)
    first = hours_data[0]
    ss_context = {
        'day_stem': first['day_stem'],
        'day_branch': first['day_branch'],
        'year_branch': first['year_branch'],
        'month_branch': first['month_branch'],
    }
    ss_query = text("""
        SELECT star_name, target_scope, target_value, notes
        FROM spr_tongshu_shensha_rule
        WHERE (master_scope = 'day_stem' AND master_value = :day_stem)
           OR (master_scope = 'day_branch' AND master_value = :day_branch)
           OR (master_scope = 'year_branch' AND master_value = :year_branch)
           OR (master_scope = 'month_branch' AND master_value = :month_branch)
    """)
    ss_results = db.execute(ss_query, ss_context).fetchall()

    for hd in hours_data:
        for ss_row in ss_results:
            target_scope = ss_row.target_scope
            target_value = ss_row.target_value
            present = False
            if target_scope == 'hour_stem' and target_value == hd['hour_stem']:
                present = True
            elif target_scope == 'hour_branch' and target_value == hd['hour_branch']:
                present = True
            elif target_scope == 'day_stem' and target_value == hd['day_stem']:
                present = True
            elif target_scope == 'day_branch' and target_value == hd['day_branch']:
                present = True
            elif target_scope == 'year_branch' and target_value == hd['year_branch']:
                present = True
            elif target_scope == 'month_branch' and target_value == hd['month_branch']:
                present = True
            if present:
                hd["symbolic_stars"].append({
                    "name": ss_row.star_name,
                    "present_in": target_scope,
                    "notes": ss_row.notes,
                })

    return hours_data
