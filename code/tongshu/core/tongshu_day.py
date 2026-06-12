#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TongShuDay — central class aggregating all daily data for Tong Shu calendar.

Usage:
    from code.tongshu.core.tongshu_day import TongShuDay
    day = TongShuDay.for_date('2026-05-16', conn)
    print(day.day_pillar)        # e.g. '庚申'
    print(day.day_officer_char)  # e.g. '定'
    print(day.constellation_char) # e.g. '翼'
"""

from datetime import date, datetime, timedelta
from typing import Optional, Dict, Any, List


class TongShuDay:
    """
    Aggregates all Tong Shu indicators for a specific calendar day.
    """

    def __init__(self, target_date: date, conn):
        self.target_date = target_date
        self.conn = conn

        # Four Pillars (loaded at noon for the day)
        self.year_pillar: Optional[str] = None
        self.month_pillar: Optional[str] = None
        self.day_pillar: Optional[str] = None
        self.hour_pillar: Optional[str] = None

        self.year_stem: Optional[str] = None
        self.year_branch: Optional[str] = None
        self.month_stem: Optional[str] = None
        self.month_branch: Optional[str] = None
        self.day_stem: Optional[str] = None
        self.day_branch: Optional[str] = None
        self.hour_stem: Optional[str] = None
        self.hour_branch: Optional[str] = None

        # Solar term
        self.solar_term_id: Optional[int] = None
        self.solar_term_char: Optional[str] = None
        self.solar_term_name_ru: Optional[str] = None

        # Na Yin (day pillar legacy + per-pillar)
        self.nayin_element: Optional[str] = None
        self.nayin_name: Optional[str] = None
        self.year_nayin_element: Optional[str] = None
        self.year_nayin_name: Optional[str] = None
        self.month_nayin_element: Optional[str] = None
        self.month_nayin_name: Optional[str] = None
        self.day_nayin_element: Optional[str] = None
        self.day_nayin_name: Optional[str] = None

        # Da Gua metadata (period / element number)
        self.year_period: Optional[int] = None
        self.month_period: Optional[int] = None
        self.day_period: Optional[int] = None
        self.year_element_num: Optional[int] = None
        self.month_element_num: Optional[int] = None
        self.day_element_num: Optional[int] = None

        # Hexagram family check
        self.hexagram_family_same: bool = False

        # Production chain check
        self.production_chain: bool = False

        # Lunar day
        self.lunar_day: Optional[int] = None

        # 12 Officers
        self.day_officer_char: Optional[str] = None
        self.day_officer_name_ru: Optional[str] = None
        self.day_officer_category: Optional[str] = None

        # 28 Constellation
        self.constellation_char: Optional[str] = None
        self.constellation_name_ru: Optional[str] = None
        self.constellation_direction: Optional[str] = None
        self.constellation_nature: Optional[str] = None

        # Yellow / Black Belt
        self.belt_type: Optional[str] = None  # 'yellow' or 'black'
        self.belt_stars: Optional[List[str]] = None

        # Moon phase
        self.moon_phase_name: Optional[str] = None
        self.moon_phase_pct: Optional[float] = None

        # Tong Shu phase (五离 / 九空 / etc.)
        self.tongshu_phase_char: Optional[str] = None
        self.tongshu_phase_name_ru: Optional[str] = None

        # 10 Gods (十神) — per pillar relative to day master
        self.year_ten_god: Optional[str] = None
        self.month_ten_god: Optional[str] = None
        self.day_ten_god: Optional[str] = None
        self.hour_ten_god: Optional[str] = None

        # Qi Phases (十二长生) — per pillar
        self.year_qi_phase: Optional[str] = None
        self.month_qi_phase: Optional[str] = None
        self.day_qi_phase: Optional[str] = None
        self.hour_qi_phase: Optional[str] = None

        # Symbolic Stars (神煞)
        self.symbolic_stars: List[Dict[str, str]] = []

        # Combinations (冲/合/刑/害/破)
        self.stem_combinations: List[Dict[str, Any]] = []
        self.branch_combinations: List[Dict[str, Any]] = []

        # San Qi (三奇)
        self.san_qi: Optional[str] = None

        # Great Sun Formula (太阳到山)
        self.great_sun_mountain: Optional[str] = None
        self.great_sun_mountain_name: Optional[str] = None

        # Load all data
        self._load_four_pillars()
        self._load_solar_term()
        self._load_lunar_day()
        self._load_nayin()
        self._load_dagua_metadata()
        self._check_hexagram_family()
        self._check_production_chain()
        self._load_day_officer()
        self._load_constellation()
        self._load_belt()
        self._load_moon_phase()
        self._load_tongshu_phase()
        self._load_ten_gods()
        self._load_qi_phases()
        self._load_symbolic_stars()
        self._calculate_combinations()
        self._calculate_san_qi()
        self._calculate_great_sun()

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------
    @classmethod
    def for_date(cls, dt: Any, conn) -> "TongShuDay":
        """Create TongShuDay from date string or date object."""
        if isinstance(dt, str):
            dt = datetime.strptime(dt, "%Y-%m-%d").date()
        return cls(dt, conn)

    # ------------------------------------------------------------------
    # Internal loaders
    # ------------------------------------------------------------------
    def _load_four_pillars(self):
        """Load Four Pillars from t_bazi_hourly (noon hour = most stable)."""
        cursor = self.conn.cursor()
        date_str = self.target_date.strftime("%Y-%m-%d")
        # Use 12:00 local time as representative
        cursor.execute("""
            SELECT year_pillar, month_pillar, day_pillar, hour_pillar,
                   year_stem, year_branch, month_stem, month_branch,
                   day_stem, day_branch, hour_stem, hour_branch,
                   solar_term_id
            FROM t_bazi_hourly
            WHERE slot_start_date_local = %s AND slot_start_time_local BETWEEN '11:00' AND '13:00'
            LIMIT 1
        """, (date_str,))
        row = cursor.fetchone()
        if row:
            (self.year_pillar, self.month_pillar, self.day_pillar, self.hour_pillar,
             self.year_stem, self.year_branch, self.month_stem, self.month_branch,
             self.day_stem, self.day_branch, self.hour_stem, self.hour_branch,
             self.solar_term_id) = row
        else:
            # Fallback: any hour of the day
            cursor.execute("""
                SELECT year_pillar, month_pillar, day_pillar, hour_pillar,
                       year_stem, year_branch, month_stem, month_branch,
                       day_stem, day_branch, hour_stem, hour_branch,
                       solar_term_id
                FROM t_bazi_hourly
                WHERE slot_start_date_local = %s
                LIMIT 1
            """, (date_str,))
            row = cursor.fetchone()
            if row:
                (self.year_pillar, self.month_pillar, self.day_pillar, self.hour_pillar,
                 self.year_stem, self.year_branch, self.month_stem, self.month_branch,
                 self.day_stem, self.day_branch, self.hour_stem, self.hour_branch,
                 self.solar_term_id) = row

    def _load_solar_term(self):
        """Load solar term name from spr_solar_term."""
        if self.solar_term_id is None:
            return
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT solar_term_char, solar_term_name_ru
            FROM spr_solar_term
            WHERE solar_term_id = %s
        """, (self.solar_term_id,))
        row = cursor.fetchone()
        if row:
            self.solar_term_char, self.solar_term_name_ru = row

    def _load_lunar_day(self):
        """Load lunar day from t_bazi_hourly (noon slot)."""
        cursor = self.conn.cursor()
        date_str = self.target_date.strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT lunar_day
            FROM t_bazi_hourly
            WHERE slot_start_date_local = %s AND slot_start_time_local BETWEEN '11:00' AND '13:00'
            LIMIT 1
        """, (date_str,))
        row = cursor.fetchone()
        if row and row[0] is not None:
            self.lunar_day = row[0]
        else:
            # Fallback: any hour of the day
            cursor.execute("""
                SELECT lunar_day
                FROM t_bazi_hourly
                WHERE slot_start_date_local = %s
                LIMIT 1
            """, (date_str,))
            row = cursor.fetchone()
            if row and row[0] is not None:
                self.lunar_day = row[0]

    def _load_nayin(self):
        """Load Na Yin from spr_jiazi_extended for year, month and day pillars."""
        cursor = self.conn.cursor()
        pillars = {
            "year": self.year_pillar,
            "month": self.month_pillar,
            "day": self.day_pillar,
        }
        valid = {k: v for k, v in pillars.items() if v}
        if not valid:
            return
        placeholders = ", ".join(["%s"] * len(valid))
        cursor.execute(f"""
            SELECT stem || branch AS pillar, nayin_element, nayin_name
            FROM spr_jiazi_extended
            WHERE stem || branch IN ({placeholders})
        """, list(valid.values()))
        lookup = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
        for prefix, pillar in valid.items():
            if pillar in lookup:
                setattr(self, f"{prefix}_nayin_element", lookup[pillar][0])
                setattr(self, f"{prefix}_nayin_name", lookup[pillar][1])
        self.nayin_element = self.day_nayin_element
        self.nayin_name = self.day_nayin_name

    def _load_dagua_metadata(self):
        """Load Da Gua period and element number for each pillar."""
        cursor = self.conn.cursor()
        pillars = {
            "year": self.year_pillar,
            "month": self.month_pillar,
            "day": self.day_pillar,
        }
        valid = {k: v for k, v in pillars.items() if v}
        if not valid:
            return
        placeholders = ", ".join(["%s"] * len(valid))
        cursor.execute(f"""
            SELECT stem || branch AS pillar, dagua_period, dagua_element
            FROM spr_jiazi_extended
            WHERE stem || branch IN ({placeholders})
        """, list(valid.values()))
        lookup = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
        for prefix, pillar in valid.items():
            if pillar in lookup:
                setattr(self, f"{prefix}_period", lookup[pillar][0])
                setattr(self, f"{prefix}_element_num", lookup[pillar][1])

    def _check_hexagram_family(self):
        """Check if all three pillars belong to the same hexagram family."""
        cursor = self.conn.cursor()
        pillars = [self.year_pillar, self.month_pillar, self.day_pillar]
        if not all(pillars):
            return
        cursor.execute("""
            SELECT stem || branch AS pillar, dagua_family
            FROM spr_jiazi_extended
            WHERE stem || branch IN (%s, %s, %s)
        """, tuple(pillars))
        lookup = {row[0]: row[1] for row in cursor.fetchall()}
        families = [lookup.get(p) for p in pillars]
        if all(f is not None for f in families) and families[0] == families[1] == families[2]:
            self.hexagram_family_same = True

    def _check_production_chain(self):
        """Check if year/month/day nayin elements form a production chain."""
        PRODUCES = {
            "Дерево": "Огонь",
            "Огонь": "Земля",
            "Земля": "Металл",
            "Металл": "Вода",
            "Вода": "Дерево",
        }
        elems = [self.year_nayin_element, self.month_nayin_element, self.day_nayin_element]
        if None in elems:
            return
        # Chain from year to day
        chain_fwd = (
            PRODUCES.get(elems[0]) == elems[1] and PRODUCES.get(elems[1]) == elems[2]
        )
        # Chain from day to year
        chain_rev = (
            PRODUCES.get(elems[2]) == elems[1] and PRODUCES.get(elems[1]) == elems[0]
        )
        self.production_chain = chain_fwd or chain_rev

    def _load_day_officer(self):
        """Load 12 Officers from spr_day_officer_mapping."""
        if not self.month_branch or not self.day_branch:
            return
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT v.officer_char, v.officer_name_ru, v.officer_category
            FROM spr_day_officer_mapping m
            JOIN spr_day_officer_value v ON v.officer_value_id = m.officer_value_id
            JOIN spr_earthly_branch mb ON mb.branch_id = m.month_branch_id
            JOIN spr_earthly_branch db ON db.branch_id = m.day_branch_id
            WHERE mb.branch_char = %s AND db.branch_char = %s
        """, (self.month_branch, self.day_branch))
        row = cursor.fetchone()
        if row:
            self.day_officer_char, self.day_officer_name_ru, self.day_officer_category = row

    def _load_constellation(self):
        """Load 28 Constellation from spr_tongshu_constellation_cycle."""
        if not self.month_branch:
            return
        cursor = self.conn.cursor()
        day_offset = self.target_date.day - 1
        cursor.execute("""
            SELECT c.constellation_char, c.constellation_name_ru,
                   c.direction_group_ru, c.nature
            FROM spr_tongshu_constellation_cycle cy
            JOIN spr_tongshu_constellation c ON c.constellation_id = cy.constellation_id
            JOIN spr_earthly_branch mb ON mb.branch_id = cy.month_branch_id
            WHERE mb.branch_char = %s AND cy.day_offset = %s
        """, (self.month_branch, day_offset))
        row = cursor.fetchone()
        if row:
            self.constellation_char, self.constellation_name_ru, self.constellation_direction, self.constellation_nature = row

    def _load_belt(self):
        """Load Yellow/Black Belt from spr_yellow_black_matrix and _stars.
        
        Matrix keyed by month_branch + day_branch. Stars have score:
        score > 0 = yellow (auspicious), score < 0 = black (inauspicious).
        """
        if not self.month_branch or not self.day_branch:
            return
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT s.name, s.score
            FROM spr_yellow_black_matrix m
            JOIN spr_yellow_black_stars s ON s.id = m.star_id
            WHERE m.month_branch = %s AND m.day_branch = %s
        """, (self.month_branch, self.day_branch))
        rows = cursor.fetchall()
        if not rows:
            return
        self.belt_stars = []
        total_score = 0.0
        for star_name, score in rows:
            self.belt_stars.append(star_name)
            total_score += score
        # Determine belt type based on aggregate score
        if total_score > 0:
            self.belt_type = "yellow"
        elif total_score < 0:
            self.belt_type = "black"
        else:
            self.belt_type = "neutral"

    def _load_moon_phase(self):
        """Calculate accurate moon phase using ephem library."""
        try:
            import ephem
            moon = ephem.Moon(self.target_date)
            illumination = moon.phase  # 0-100%
            self.moon_phase_pct = round(illumination, 1)

            # Determine waxing/waning by comparing with previous day
            prev_day = self.target_date - __import__('datetime').timedelta(days=1)
            prev_moon = ephem.Moon(prev_day)
            prev_illum = prev_moon.phase
            is_waxing = illumination >= prev_illum

            if illumination < 2:
                self.moon_phase_name = "Новолуние"
            elif illumination < 45:
                self.moon_phase_name = "Растущая" if is_waxing else "Убывающая"
            elif illumination < 55:
                self.moon_phase_name = "Первая четверть" if is_waxing else "Последняя четверть"
            elif illumination < 98:
                self.moon_phase_name = "Растущая (более половины)" if is_waxing else "Убывающая (более половины)"
            else:
                self.moon_phase_name = "Полнолуние"
        except Exception:
            # Fallback to simplified calculation
            anchor = date(2026, 1, 29)
            cycle = 29.53059
            delta = (self.target_date - anchor).days
            phase = (delta % cycle) / cycle
            self.moon_phase_pct = round(phase * 100, 1)
            if phase < 0.03 or phase > 0.97:
                self.moon_phase_name = "Новолуние"
            elif phase < 0.22:
                self.moon_phase_name = "Растущая"
            elif phase < 0.28:
                self.moon_phase_name = "Первая четверть"
            elif phase < 0.47:
                self.moon_phase_name = "Растущая (более половины)"
            elif phase < 0.53:
                self.moon_phase_name = "Полнолуние"
            elif phase < 0.72:
                self.moon_phase_name = "Убывающая (более половины)"
            elif phase < 0.78:
                self.moon_phase_name = "Последняя четверть"
            else:
                self.moon_phase_name = "Убывающая"

    def _load_tongshu_phase(self):
        """Load Tong Shu phase (五离 / 九空) from spr_tongshu_phase_mapping."""
        if not self.day_stem:
            return
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.name_ru, p.numeric_score
            FROM spr_tongshu_phase_mapping m
            JOIN spr_tongshu_phase p ON p.phase_id = m.phase_id
            WHERE m.day_stem = %s
        """, (self.day_stem,))
        row = cursor.fetchone()
        if row:
            self.tongshu_phase_name_ru = row[0]
            # numeric_score can be used for severity if needed
            # Keep phase_char as None since table has no char column
            self.tongshu_phase_char = None

    def _load_ten_gods(self):
        """Load 10 Gods for each pillar relative to day master."""
        if not self.day_stem:
            return
        cursor = self.conn.cursor()
        stems = {
            "year": self.year_stem,
            "month": self.month_stem,
            "day": self.day_stem,
            "hour": self.hour_stem,
        }
        valid_stems = [s for s in stems.values() if s]
        if not valid_stems:
            return
        placeholders = ", ".join(["%s"] * len(valid_stems))
        cursor.execute(f"""
            SELECT related_stem, god_code FROM spr_tongshu_ten_god
            WHERE day_stem = %s AND related_stem IN ({placeholders})
        """, [self.day_stem] + valid_stems)
        lookup = {row[0]: row[1] for row in cursor.fetchall()}
        for prefix, stem in stems.items():
            if stem and stem in lookup:
                setattr(self, f"{prefix}_ten_god", lookup[stem])

    def _load_qi_phases(self):
        """Load Qi Phase for each pillar."""
        if not self.day_stem:
            return
        cursor = self.conn.cursor()
        branches = {
            "year": self.year_branch,
            "month": self.month_branch,
            "day": self.day_branch,
            "hour": self.hour_branch,
        }
        valid_branches = [b for b in branches.values() if b]
        if not valid_branches:
            return
        placeholders = ", ".join(["%s"] * len(valid_branches))
        cursor.execute(f"""
            SELECT m.reference_branch, p.name_ru
            FROM spr_tongshu_phase_mapping m
            JOIN spr_tongshu_phase p ON p.phase_id = m.phase_id
            WHERE m.day_stem = %s AND m.reference_branch IN ({placeholders})
        """, [self.day_stem] + valid_branches)
        lookup = {row[0]: row[1] for row in cursor.fetchall()}
        for prefix, branch in branches.items():
            if branch and branch in lookup:
                setattr(self, f"{prefix}_qi_phase", lookup[branch])

    def _load_symbolic_stars(self):
        """Load symbolic stars (神煞) for the day."""
        if not self.day_stem or not self.day_branch or not self.year_branch or not self.month_branch:
            return
        cursor = self.conn.cursor()
        # Build context for matching
        context = {
            'day_stem': self.day_stem,
            'day_branch': self.day_branch,
            'year_branch': self.year_branch,
            'month_branch': self.month_branch,
        }
        # Query rules that match any of our context values
        # We use a simple OR matching: if master_scope+master_value matches context
        sql = """
            SELECT star_name, master_scope, master_value, target_scope, target_value, notes
            FROM spr_tongshu_shensha_rule
            WHERE (master_scope = 'day_stem' AND master_value = %s)
               OR (master_scope = 'day_branch' AND master_value = %s)
               OR (master_scope = 'year_branch' AND master_value = %s)
               OR (master_scope = 'month_branch' AND master_value = %s)
        """
        cursor.execute(sql, (self.day_stem, self.day_branch, self.year_branch, self.month_branch))
        rows = cursor.fetchall()
        for star_name, master_scope, master_value, target_scope, target_value, notes in rows:
            # Determine if the star is present: check if target value exists in current pillars
            present = False
            present_in = None
            pillar_map = {
                'day_stem': self.day_stem,
                'day_branch': self.day_branch,
                'year_stem': self.year_stem,
                'year_branch': self.year_branch,
                'month_stem': self.month_stem,
                'month_branch': self.month_branch,
                'hour_stem': self.hour_stem,
                'hour_branch': self.hour_branch,
            }
            if target_scope in pillar_map and pillar_map[target_scope] == target_value:
                present = True
                present_in = target_scope
            if present:
                self.symbolic_stars.append({
                    'name': star_name,
                    'present_in': present_in,
                    'notes': notes,
                })

    def _calculate_combinations(self):
        """Calculate stem and branch combinations between pillars."""
        if not self.day_stem:
            return
        cursor = self.conn.cursor()

        stems = [
            ("year", self.year_stem),
            ("month", self.month_stem),
            ("day", self.day_stem),
            ("hour", self.hour_stem),
        ]
        branches = [
            ("year", self.year_branch),
            ("month", self.month_branch),
            ("day", self.day_branch),
            ("hour", self.hour_branch),
        ]

        # Pre-fetch all stem combo rules (small table)
        cursor.execute("""
            SELECT item1, item2, combo_name, combo_type_id, numeric_score, description
            FROM spr_tongshu_stem_combo_rule
        """)
        stem_combo_lookup = {}
        for row in cursor.fetchall():
            stem_combo_lookup[(row[0], row[1])] = (row[2], row[3], row[4], row[5])

        # Pre-fetch all branch combo rules (small table)
        cursor.execute("""
            SELECT item1, item2, item3, combo_name, combo_type_id, numeric_score, description
            FROM spr_tongshu_branch_combo_rule
        """)
        branch_combo_2 = {}
        branch_combo_3 = {}
        for row in cursor.fetchall():
            if row[2] is None:
                branch_combo_2[(row[0], row[1])] = (row[3], row[4], row[5], row[6])
            else:
                branch_combo_3[(row[0], row[1], row[2])] = (row[3], row[4], row[5], row[6])

        # Stem combinations
        stem_pairs = [
            (stems[i], stems[j]) for i in range(4) for j in range(i+1, 4)
            if stems[i][1] and stems[j][1]
        ]
        for (p1, s1), (p2, s2) in stem_pairs:
            key = tuple(sorted([s1, s2]))
            if key in stem_combo_lookup:
                row = stem_combo_lookup[key]
                self.stem_combinations.append({
                    'pillar1': p1, 'pillar2': p2,
                    'combo_name': row[0], 'combo_type_id': row[1],
                    'score': row[2], 'description': row[3],
                })

        # Branch combinations (2-item)
        branch_pairs = [
            (branches[i], branches[j]) for i in range(4) for j in range(i+1, 4)
            if branches[i][1] and branches[j][1]
        ]
        for (p1, b1), (p2, b2) in branch_pairs:
            key = tuple(sorted([b1, b2]))
            if key in branch_combo_2:
                row = branch_combo_2[key]
                self.branch_combinations.append({
                    'pillar1': p1, 'pillar2': p2,
                    'combo_name': row[0], 'combo_type_id': row[1],
                    'score': row[2], 'description': row[3],
                })

        # Branch combinations (3-item: harmony / season)
        branch_triplets = [
            (branches[i], branches[j], branches[k])
            for i in range(4) for j in range(i+1, 4) for k in range(j+1, 4)
            if branches[i][1] and branches[j][1] and branches[k][1]
        ]
        for (p1, b1), (p2, b2), (p3, b3) in branch_triplets:
            key = tuple(sorted([b1, b2, b3]))
            if key in branch_combo_3:
                row = branch_combo_3[key]
                self.branch_combinations.append({
                    'pillar1': p1, 'pillar2': p2, 'pillar3': p3,
                    'combo_name': row[0], 'combo_type_id': row[1],
                    'score': row[2], 'description': row[3],
                })

    def _calculate_san_qi(self):
        """Calculate San Qi (三奇) — Three Wonders from 4 pillars."""
        stems = [
            self.year_stem, self.month_stem, self.day_stem, self.hour_stem,
        ]
        stem_set = set(s for s in stems if s)
        # 天上三奇: 甲, 戊, 庚
        if {'甲', '戊', '庚'}.issubset(stem_set):
            self.san_qi = "天上三奇 (Небесный мистик)"
        # 地上三奇: 乙, 丙, 丁
        elif {'乙', '丙', '丁'}.issubset(stem_set):
            self.san_qi = "地上三奇 (Земной мистик)"
        # 人中三奇: 壬, 癸, 辛
        elif {'壬', '癸', '辛'}.issubset(stem_set):
            self.san_qi = "人中三奇 (Человеческий мистик)"

    def _calculate_great_sun(self):
        """Calculate Great Sun Formula (太阳到山) — sun arrival at mountain."""
        if not self.solar_term_char:
            return
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT mountain_char, mountain_name_ru, opposite_mountain
            FROM spr_great_sun_mountain
            WHERE solar_term_char = %s
        """, (self.solar_term_char,))
        row = cursor.fetchone()
        if row:
            self.great_sun_mountain = row[0]
            self.great_sun_mountain_name = row[1]

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """Serialize all loaded data to a dictionary."""
        return {
            "date": self.target_date.isoformat(),
            "four_pillars": {
                "year": self.year_pillar,
                "month": self.month_pillar,
                "day": self.day_pillar,
                "hour": self.hour_pillar,
            },
            "solar_term": {
                "char": self.solar_term_char,
                "name_ru": self.solar_term_name_ru,
            },
            "nayin": {
                "element": self.nayin_element,
                "name": self.nayin_name,
                "year_element": self.year_nayin_element,
                "year_name": self.year_nayin_name,
                "month_element": self.month_nayin_element,
                "month_name": self.month_nayin_name,
                "day_element": self.day_nayin_element,
                "day_name": self.day_nayin_name,
            },
            "dagua": {
                "year_period": self.year_period,
                "month_period": self.month_period,
                "day_period": self.day_period,
                "year_element_num": self.year_element_num,
                "month_element_num": self.month_element_num,
                "day_element_num": self.day_element_num,
            },
            "hexagram_family_same": self.hexagram_family_same,
            "production_chain": self.production_chain,
            "lunar_day": self.lunar_day,
            "day_officer": {
                "char": self.day_officer_char,
                "name_ru": self.day_officer_name_ru,
                "category": self.day_officer_category,
            },
            "constellation": {
                "char": self.constellation_char,
                "name_ru": self.constellation_name_ru,
                "direction": self.constellation_direction,
                "nature": self.constellation_nature,
            },
            "belt": {
                "type": self.belt_type,
                "stars": self.belt_stars,
            },
            "moon": {
                "phase_name": self.moon_phase_name,
                "phase_pct": self.moon_phase_pct,
            },
            "tongshu_phase": {
                "char": self.tongshu_phase_char,
                "name_ru": self.tongshu_phase_name_ru,
            },
            "ten_gods": {
                "year": self.year_ten_god,
                "month": self.month_ten_god,
                "day": self.day_ten_god,
                "hour": self.hour_ten_god,
            },
            "qi_phases": {
                "year": self.year_qi_phase,
                "month": self.month_qi_phase,
                "day": self.day_qi_phase,
                "hour": self.hour_qi_phase,
            },
            "symbolic_stars": self.symbolic_stars,
            "combinations": {
                "stem": self.stem_combinations,
                "branch": self.branch_combinations,
            },
            "san_qi": self.san_qi,
            "great_sun": {
                "mountain": self.great_sun_mountain,
                "mountain_name": self.great_sun_mountain_name,
            },
        }

    def __repr__(self):
        return f"<TongShuDay {self.target_date} {self.day_pillar or '?'}>"
