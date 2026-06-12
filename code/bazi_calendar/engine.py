from datetime import datetime, timedelta, timezone
from bisect import bisect_right
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any

from .lunar import calc_lunar_components, LunarDateNotExist
from .solar_terms import tz_from_offset

@dataclass
class Pillar:
    stem: str
    branch: str
    
    def __str__(self):
        return f"{self.stem}{self.branch}"

class BaziEngine:
    def __init__(self, conn: Any):
        self.conn = conn
        self._load_reference_data()
        
    def _load_reference_data(self):
        cursor = self.conn.cursor()
        
        # 1. Переходы солнечных сезонов (с учетом HKO)
        # Загружаем всё в память, так как данных немного (~24 * 200 лет = 4800 записей)
        
        # Base data
        cursor.execute("SELECT crossing_utc, solar_term_id FROM t_solar_term_time ORDER BY crossing_utc")
        base_data = []
        for row in cursor.fetchall():
            dt = row[0]
            if isinstance(dt, str):
                dt = datetime.fromisoformat(dt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            base_data.append((dt, row[1]))
            
        # HKO overrides
        try:
            cursor.execute("SELECT crossing_utc, solar_term_id FROM t_solar_term_time_hko")
            overrides = {} # (year, term_id) -> dt
            for row in cursor.fetchall():
                dt = row[0]
                if isinstance(dt, str):
                    dt = datetime.fromisoformat(dt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                else:
                    dt = dt.astimezone(timezone.utc)
                overrides[(dt.year, row[1])] = dt
        except Exception:
            overrides = {}
            
        # Merge
        # Для простоты, если есть HKO для (год, term), заменяем запись из base_data
        # Но base_data - это список. 
        # Проще пересобрать.
        
        self.solar_transitions = []
        
        # Индексируем base_data по (год, term) для замены, или просто используем overrides при построении
        # Но base_data уже отсортирован.
        # Давайте сделаем словарь для base_data тоже, потом смержим и отсортируем.
        
        transitions_map = {}
        for dt, tid in base_data:
            transitions_map[(dt.year, tid)] = dt
            
        # Применяем overrides
        for key, dt in overrides.items():
            transitions_map[key] = dt
            
        # Convert back to sorted list
        # Note: keys are (year, tid). We sort by dt.
        merged = []
        for (y, tid), dt in transitions_map.items():
            merged.append((dt, tid))
            
        merged.sort(key=lambda x: x[0])
        self.solar_transitions = merged
            
        # 2. Названия солнечных сезонов
        cursor.execute("SELECT solar_term_id, solar_term_name_ru FROM spr_solar_term")
        self.st_names = {r[0]: r[1] for r in cursor.fetchall()}
        
        # 3. Циклы (Цзя Цзы)
        # spr_pillar_cycle: cycle_index, stem_char, branch_char
        cursor.execute("""
            SELECT pc.cycle_index, hs.stem_char, eb.branch_char 
            FROM spr_pillar_cycle pc
            JOIN spr_heavenly_stem hs ON hs.stem_id = pc.stem_id
            JOIN spr_earthly_branch eb ON eb.branch_id = pc.branch_id
            ORDER BY pc.cycle_index
        """)
        self.jiazi_cycle = {r[0]: Pillar(r[1], r[2]) for r in cursor.fetchall()}
        
        # 4. Правила Месяца (Пять Тигров)
        # spr_pillar_month_rule: year_stem_id, month_index, month_stem_id
        # Нам нужно отображение символов.
        cursor.execute("""
            SELECT hs_y.stem_char, pmr.month_index, hs_m.stem_char
            FROM spr_pillar_month_rule pmr
            JOIN spr_heavenly_stem hs_y ON hs_y.stem_id = pmr.year_stem_id
            JOIN spr_heavenly_stem hs_m ON hs_m.stem_id = pmr.month_stem_id
        """)
        self.month_rules = {} # (year_stem_char, month_index) -> month_stem_char
        for r in cursor.fetchall():
            self.month_rules[(r[0], r[1])] = r[2]
            
        # Отображение Ветвей Месяца (ID солнечного сезона -> Ветвь Месяца)
        cursor.execute("""
            SELECT st.solar_term_id, eb.branch_char
            FROM spr_solar_term st
            JOIN spr_earthly_branch eb ON eb.branch_id = st.month_branch_id
        """)
        self.st_month_branches = {r[0]: r[1] for r in cursor.fetchall()}

        # 5. Правила Часа (Пять Крыс)
        cursor.execute("""
            SELECT hs_d.stem_char, eb_h.branch_char, hs_h.stem_char
            FROM spr_pillar_hour_rule phr
            JOIN spr_heavenly_stem hs_d ON hs_d.stem_id = phr.day_stem_id
            JOIN spr_earthly_branch eb_h ON eb_h.branch_id = phr.hour_branch_id
            JOIN spr_heavenly_stem hs_h ON hs_h.stem_id = phr.hour_stem_id
        """)
        self.hour_rules = {} # (day_stem_char, hour_branch_char) -> hour_stem_char
        for r in cursor.fetchall():
            self.hour_rules[(r[0], r[1])] = r[2]
            
        # Определения Ветвей Часа
        cursor.execute("SELECT branch_char, start_hour, end_hour FROM spr_earthly_branch WHERE start_hour IS NOT NULL")
        self.hour_defs = []
        for r in cursor.fetchall():
            self.hour_defs.append({
                'branch': r[0],
                'start': r[1],
                'end': r[2]
            })
            
        # 6. Офицеры и Мастер Дано (REMOVED - moved to Rule Engine)
        # Офицер Дня (REMOVED - moved to Rule Engine)
        # Мастер Дано (REMOVED - moved to Rule Engine)
            
        # 7. Кэши
        self.lunar_cache = {}
        self._tz_cache = {}
        
    def find_solar_term_id(self, dt_utc: datetime) -> int:
        """Находит ID активного солнечного сезона для заданного времени UTC."""
        if not self.solar_transitions:
            return 1
        
        # Ensure dt_utc is comparable
        if dt_utc.tzinfo is None:
            dt_utc = dt_utc.replace(tzinfo=timezone.utc)
        else:
            dt_utc = dt_utc.astimezone(timezone.utc)
            
        idx = bisect_right(self.solar_transitions, (dt_utc, 999))
        if idx == 0:
            return self.solar_transitions[0][1]
        return self.solar_transitions[idx-1][1]
        
    def calc_pillars(self, dt_utc: datetime, tz_offset: int):
        # dt_iso = dt_utc.strftime("%Y-%m-%d %H:%M:%S") # Deprecated usage
        local_tz = self._tz_cache.get(tz_offset)
        if local_tz is None:
            local_tz = tz_from_offset(tz_offset)
            self._tz_cache[tz_offset] = local_tz
        dt_local = dt_utc.astimezone(local_tz)
        
        # 1. Солнечный сезон
        st_id = self.find_solar_term_id(dt_utc)
        st_name = self.st_names.get(st_id, "")
        
        # 2. Столп Года
        bazi_year_num = dt_local.year
        
        # Солнечный Год начинается с Ли Чунь (Сезон 1).
        # Сезоны 23 (Малые Холода) и 24 (Большие Холода) находятся в начале Григорианского года, но в конце Солнечного года.
        # Сезон 22 (Зимнее Солнцестояние) охватывает дек/янв. Если это январь, то это конец Солнечного года.
        if st_id in (23, 24):
            bazi_year_num -= 1
        elif st_id == 22 and dt_local.month == 1:
            bazi_year_num -= 1
            
        # Расчет Индекса Цикла для Года
        # База: 1864 = Цзя Цзы (0).
        cycle_idx_y = (bazi_year_num - 1864) % 60
        year_pillar = self.jiazi_cycle[cycle_idx_y]
        
        # 3. Столп Месяца
        # Сезон 1,2 -> Месяц 1 (Инь)
        # Сезон 21,22 -> Месяц 11 (Цзы)
        # Сезон 23,24 -> Месяц 12 (Чоу)
        month_idx = (st_id + 1) // 2
        
        month_stem_char = self.month_rules.get((year_pillar.stem, month_idx))
        m_branch_char = self.st_month_branches.get(st_id)
        
        if not month_stem_char:
             # Фоллбэк или обработка ошибок
             pass
             
        month_pillar = Pillar(month_stem_char, m_branch_char)
        
        # 4. Столп Дня
        # Дни с базовой эпохи.
        # База: 1864-02-05 (Цзя Цзы, 0) - это примерно начало.
        # Лучшая база: 1900-01-01?
        # Использованный код: якорь 1864-02-05 = Гэн Цзы (36)? Нет, код говорил, что 1864-02-05 - это Гэн Цзы?
        # Давайте проверим логику кода `pillars.py`.
        # "anchor_date = datetime(1864, 2, 5).date() # 庚子 (36)"
        # "delta_days = ... cycle_index = (36 + delta) % 60"
        # Нам нужно учитывать "смену часа Цзы" (23:00).
        # `dt_local` - это время. Если час >= 23, это следующий день для Столпа.
        
        day_calc_dt = dt_local
        if dt_local.hour >= 23:
            day_calc_dt = dt_local + timedelta(days=1)
            
        anchor_date = datetime(1864, 2, 5).date()
        anchor_idx = 36 # Geng Zi
        
        delta = (day_calc_dt.date() - anchor_date).days
        cycle_idx_d = (anchor_idx + delta) % 60
        day_pillar = self.jiazi_cycle[cycle_idx_d]
        
        # 5. Столп Часа
        # Ветвь определяется `hour_defs` (местное время).
        h = dt_local.hour
        h_branch = None
        for rule in self.hour_defs:
            # Простая проверка диапазонов.
            # Цзы - это 23-01. Обрабатывается как: начало 23, конец 1.
            if rule['start'] > rule['end']: # Пересекает полночь (23-1)
                if h >= rule['start'] or h < rule['end']:
                    h_branch = rule['branch']
                    break
            else:
                if rule['start'] <= h < rule['end']:
                    h_branch = rule['branch']
                    break
                    
        h_stem = self.hour_rules.get((day_pillar.stem, h_branch), "")
        hour_pillar = Pillar(h_stem, h_branch)
        
        # 6. Индикаторы
        # REMOVED: master = self.master_dano_map.get((month_pillar.branch, day_pillar.stem, day_pillar.branch), (None, None, None))
        
        # 7. Лунный
        cache_key = (dt_utc, tz_offset)
        if cache_key in self.lunar_cache:
            lunar = self.lunar_cache[cache_key]
        else:
            try:
                lunar = calc_lunar_components(dt_utc, tz_offset_hours=tz_offset)
            except:
                lunar = (0, 0, 0)
            self.lunar_cache[cache_key] = lunar
            
        return {
            'year': year_pillar,
            'month': month_pillar,
            'day': day_pillar,
            'hour': hour_pillar,
            'solar_term_id': st_id,
            'solar_term_name': st_name,
            # 'master': master, # REMOVED
            'lunar': lunar # (month, day, leap)
        }
