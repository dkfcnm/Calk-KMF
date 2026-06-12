from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Tuple
from datetime import date, datetime, timezone as dt_timezone, timedelta
import sys
import os

# Add project root to path for BaziEngine
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from code.bazi_calendar import calc_four_pillars
from code.bazi_calendar.db import get_connection

from ..schemas.profile import ProfileCreate, ProfileUpdate

class ProfileService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, profile: ProfileCreate):
        sql = text("""
            INSERT INTO t_profile (name, birth_date, birth_time, birth_city, 
                birth_city_lat, birth_city_lon, birth_timezone, notes)
            VALUES (:name, :birth_date, :birth_time, :birth_city,
                :birth_city_lat, :birth_city_lon, :birth_timezone, :notes)
            RETURNING *
        """)
        result = self.db.execute(sql, {
            'name': profile.name,
            'birth_date': profile.birth_date,
            'birth_time': profile.birth_time,
            'birth_city': profile.birth_city,
            'birth_city_lat': profile.birth_city_lat,
            'birth_city_lon': profile.birth_city_lon,
            'birth_timezone': profile.birth_timezone,
            'notes': profile.notes,
        })
        self.db.commit()
        row = result.mappings().first()
        return dict(row) if row else None

    def get_by_id(self, profile_id: int):
        sql = text("SELECT * FROM t_profile WHERE id = :id")
        result = self.db.execute(sql, {'id': profile_id})
        row = result.mappings().first()
        if not row:
            return None
        profile = dict(row)
        # Load birth chart if exists
        chart_sql = text("SELECT * FROM t_profile_birth_chart WHERE profile_id = :pid")
        chart_result = self.db.execute(chart_sql, {'pid': profile_id})
        chart_row = chart_result.mappings().first()
        if chart_row:
            profile['birth_chart'] = dict(chart_row)
        return profile

    def list_all(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> Tuple[List[dict], int]:
        if search:
            count_sql = text("""
                SELECT COUNT(*) as total FROM t_profile
                WHERE name ILIKE :search OR birth_city ILIKE :search
            """)
            count_result = self.db.execute(count_sql, {'search': f'%{search}%'})
        else:
            count_sql = text("SELECT COUNT(*) as total FROM t_profile")
            count_result = self.db.execute(count_sql)
        total = count_result.mappings().first()['total']

        if search:
            sql = text("""
                SELECT * FROM t_profile 
                WHERE name ILIKE :search OR birth_city ILIKE :search
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """)
            result = self.db.execute(sql, {
                'search': f'%{search}%',
                'limit': limit,
                'offset': skip,
            })
        else:
            sql = text("""
                SELECT * FROM t_profile 
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """)
            result = self.db.execute(sql, {'limit': limit, 'offset': skip})

        items = [dict(row) for row in result.mappings()]
        
        # Load birth charts for all profiles
        if items:
            profile_ids = [p['id'] for p in items]
            chart_sql = text("""
                SELECT * FROM t_profile_birth_chart 
                WHERE profile_id = ANY(:pids)
            """)
            chart_result = self.db.execute(chart_sql, {'pids': profile_ids})
            charts = {row['profile_id']: dict(row) for row in chart_result.mappings()}
            for item in items:
                if item['id'] in charts:
                    item['birth_chart'] = charts[item['id']]
        
        return items, total

    def update(self, profile_id: int, update: ProfileUpdate):
        # Build dynamic update
        fields = []
        params = {'id': profile_id}
        for field, value in update.model_dump(exclude_unset=True).items():
            if value is not None:
                fields.append(f"{field} = :{field}")
                params[field] = value
        
        if not fields:
            return self.get_by_id(profile_id)

        sql = text(f"""
            UPDATE t_profile 
            SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = :id
            RETURNING *
        """)
        result = self.db.execute(sql, params)
        self.db.commit()
        row = result.mappings().first()
        return dict(row) if row else None

    def delete(self, profile_id: int) -> bool:
        sql = text("DELETE FROM t_profile WHERE id = :id RETURNING id")
        result = self.db.execute(sql, {'id': profile_id})
        self.db.commit()
        return result.fetchone() is not None

    def calculate_birth_chart(self, profile_id: int):
        """Calculate birth chart using BaziEngine and save to t_profile_birth_chart."""
        profile = self.get_by_id(profile_id)
        if not profile:
            return None

        birth_date = profile.get('birth_date')
        birth_time = profile.get('birth_time')
        birth_timezone = profile.get('birth_timezone')

        if not birth_date or not birth_time:
            return None

        # Parse birth_time (time object or string "HH:MM:SS")
        if isinstance(birth_time, str):
            from datetime import time as dt_time
            parts = birth_time.split(':')
            birth_time = dt_time(int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)

        # Build datetime
        dt = datetime.combine(birth_date, birth_time)

        # Parse timezone offset
        tz_offset_hours = 0
        if birth_timezone:
            tz_str = str(birth_timezone).strip()
            # Format: "+03:00" or "+3" or "180" (minutes)
            if tz_str.startswith('+') or tz_str.startswith('-'):
                try:
                    if ':' in tz_str:
                        parts = tz_str.split(':')
                        tz_offset_hours = int(parts[0])
                    else:
                        tz_offset_hours = int(tz_str)
                except ValueError:
                    tz_offset_hours = 0
            else:
                try:
                    # Might be minutes (from spr_city_timezone.utc_offset)
                    tz_offset_hours = int(float(tz_str) / 60)
                except ValueError:
                    tz_offset_hours = 0

        # Calculate four pillars
        conn = get_connection()
        try:
            pillars = calc_four_pillars(dt, conn, tz_offset_hours=tz_offset_hours)
        finally:
            conn.close()

        # Get day master element from spr_heavenly_stem
        day_stem = pillars.day.stem_char
        element_sql = text("SELECT element FROM spr_heavenly_stem WHERE stem_char = :stem")
        element_result = self.db.execute(element_sql, {'stem': day_stem})
        element_row = element_result.mappings().first()
        day_master_element = element_row['element'] if element_row else 'Неизвестно'

        # Delete existing chart
        del_sql = text("DELETE FROM t_profile_birth_chart WHERE profile_id = :pid")
        self.db.execute(del_sql, {'pid': profile_id})

        # Insert calculated chart
        insert_sql = text("""
            INSERT INTO t_profile_birth_chart 
            (profile_id, year_pillar, month_pillar, day_pillar, hour_pillar, 
             day_master, day_master_element,
             year_stem, year_branch, month_stem, month_branch,
             day_stem, day_branch, hour_stem, hour_branch)
            VALUES 
            (:pid, :year_pillar, :month_pillar, :day_pillar, :hour_pillar,
             :day_master, :day_master_element,
             :year_stem, :year_branch, :month_stem, :month_branch,
             :day_stem, :day_branch, :hour_stem, :hour_branch)
            RETURNING *
        """)
        result = self.db.execute(insert_sql, {
            'pid': profile_id,
            'year_pillar': f"{pillars.year.stem_char}{pillars.year.branch_char}",
            'month_pillar': f"{pillars.month.stem_char}{pillars.month.branch_char}",
            'day_pillar': f"{pillars.day.stem_char}{pillars.day.branch_char}",
            'hour_pillar': f"{pillars.hour.stem_char}{pillars.hour.branch_char}",
            'day_master': day_stem,
            'day_master_element': day_master_element,
            'year_stem': pillars.year.stem_char,
            'year_branch': pillars.year.branch_char,
            'month_stem': pillars.month.stem_char,
            'month_branch': pillars.month.branch_char,
            'day_stem': pillars.day.stem_char,
            'day_branch': pillars.day.branch_char,
            'hour_stem': pillars.hour.stem_char,
            'hour_branch': pillars.hour.branch_char,
        })
        self.db.commit()
        row = result.mappings().first()
        return dict(row) if row else None

    def get_history(self, profile_id: int, skip: int = 0, limit: int = 50) -> List[dict]:
        sql = text("""
            SELECT * FROM t_profile_history 
            WHERE profile_id = :pid
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        result = self.db.execute(sql, {
            'pid': profile_id,
            'limit': limit,
            'offset': skip,
        })
        return [dict(row) for row in result.mappings()]

    def add_history(self, profile_id: int, action_type: str, 
                    module: Optional[str] = None, 
                    reference_date: Optional[date] = None,
                    notes: Optional[str] = None):
        sql = text("""
            INSERT INTO t_profile_history 
            (profile_id, action_type, module, reference_date, notes)
            VALUES (:pid, :action, :module, :ref_date, :notes)
            RETURNING *
        """)
        result = self.db.execute(sql, {
            'pid': profile_id,
            'action': action_type,
            'module': module,
            'ref_date': reference_date,
            'notes': notes,
        })
        self.db.commit()
        row = result.mappings().first()
        return dict(row) if row else None
