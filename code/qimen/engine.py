from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from ..common.config import ProjectConfig

@dataclass
class QimenChart:
    hour_id: str
    chart_num: int
    yin_yang: str
    palaces: Dict[int, "PalaceData"]

@dataclass
class PalaceData:
    palace_no: int
    earth_stem: str
    is_fou_tou_earth: int
    heaven_stem: str
    is_fou_tou_heaven: int
    star: str
    is_main_star: int
    gate: str
    is_main_gate: int
    spirit: str

class QimenEngine:
    def __init__(self, config: ProjectConfig):
        self.config = config

    def _get_jiazi_index(self, stem: str, branch: str) -> int:
        s_idx = self.config.stems.index(stem)
        b_idx = self.config.branches.index(branch)
        return (6 * s_idx - 5 * b_idx + 60) % 60

    def compute_chart(
        self,
        hour_id: str,
        solar_term_id: int,
        day_stem: str,
        day_branch: str,
        hour_stem: str,
        hour_branch: str,
        *,
        chart_type: str = "Часовой",
        forced_ju: Optional[int] = None,
        forced_yin_yang: Optional[str] = None
    ) -> QimenChart:
        
        # 1. Определение Ju и Yin/Yang
        if forced_ju is not None and forced_yin_yang is not None:
             ju_num = forced_ju
             yin_yang = forced_yin_yang
             is_yang = (yin_yang == "Yang")
        else:
            # Стандартная логика Часового расклада
            # 1. Инь / Ян Дунь
            if solar_term_id in range(10, 22):
                yin_yang = "Yin"
                is_yang = False
            else:
                yin_yang = "Yang"
                is_yang = True

            # 2. Юань (Верхний/Средний/Нижний)
            day_cycle_idx = self._get_jiazi_index(day_stem, day_branch)
            yuan_idx = (day_cycle_idx // 5) % 3
            
            # 3. Номер Ju
            if solar_term_id not in self.config.solar_term_ju:
                 ju_num = 1
            else:
                 ju_num = self.config.solar_term_ju[solar_term_id][yuan_idx]

        # 4. Расположение на доске
        focus_stem = hour_stem
        focus_branch = hour_branch
        
        return self._layout_board(
            hour_id=hour_id,
            ju_num=ju_num,
            yin_yang=yin_yang,
            is_yang=is_yang,
            focus_stem=focus_stem,
            focus_branch=focus_branch
        )

    def _layout_board(self, hour_id: str, ju_num: int, yin_yang: str, is_yang: bool, focus_stem: str, focus_branch: str) -> QimenChart:
        # 4. Земная Тарелка (Ди Пань)
        pai_stems = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]
        
        earth_plate = {} # дворец -> ствол
        
        curr_palace = ju_num
        for stem in pai_stems:
            earth_plate[curr_palace] = stem
            if is_yang:
                curr_palace += 1
                if curr_palace > 9: curr_palace = 1
            else:
                curr_palace -= 1
                if curr_palace < 1: curr_palace = 9
                
        # 5. Поиск Лидера (Сюнь Шоу)
        cycle_idx = self._get_jiazi_index(focus_stem, focus_branch)
        
        leader_group = cycle_idx // 10 # 0..5
        leader_stem = self.config.leader_stems[leader_group]
        
        # 6. Поиск дворца Лидера на Земной Тарелке
        leader_palace = 0
        for p, s in earth_plate.items():
            if s == leader_stem:
                leader_palace = p
                break
        
        origin_palace_for_leader = leader_palace
        if origin_palace_for_leader == 5:
            origin_palace_for_leader = 2 
            
        zhi_fu_star = self._get_star_at_palace(origin_palace_for_leader)
        zhi_shi_gate = self._get_gate_at_palace(origin_palace_for_leader)
        
        # 7. Небесная Тарелка (Тянь Пань)
        target_stem = focus_stem
        if focus_stem == "甲":
            target_stem = leader_stem
            
        target_palace = 0
        for p, s in earth_plate.items():
            if s == target_stem:
                target_palace = p
                break
        
        star_sequence = [1, 8, 3, 4, 9, 2, 7, 6]
        
        start_star_palace = origin_palace_for_leader
        if start_star_palace == 5: start_star_palace = 2
        
        try:
            start_idx = star_sequence.index(start_star_palace)
        except ValueError:
            start_idx = 0

        target_palace_effective = target_palace
        if target_palace_effective == 5: target_palace_effective = 2
        
        try:
            target_idx = star_sequence.index(target_palace_effective)
        except ValueError:
            target_idx = 0
            
        offset = (target_idx - start_idx) % 8
        
        heaven_plate_map = {} 
        heaven_plate_map_center = {}
        star_plate_map = {}
        
        for i, original_palace in enumerate(star_sequence):
            new_idx = (i + offset) % 8
            new_palace = star_sequence[new_idx]
            
            stem_moving = earth_plate.get(original_palace)
            heaven_plate_map[new_palace] = stem_moving
            
            if original_palace == 2:
                stem_center = earth_plate.get(5)
                if stem_center:
                    heaven_plate_map_center[new_palace] = stem_center

            star_plate_map[new_palace] = self._get_star_at_palace(original_palace)
            
        # 8. Тарелка Врат
        diff = cycle_idx - (leader_group * 10)
        
        curr_gate_palace = leader_palace 
        
        for _ in range(diff):
            if is_yang:
                curr_gate_palace += 1
                if curr_gate_palace > 9: curr_gate_palace = 1
            else:
                curr_gate_palace -= 1
                if curr_gate_palace < 1: curr_gate_palace = 9
        
        target_gate_palace = curr_gate_palace
        gate_sequence = [1, 8, 3, 4, 9, 2, 7, 6]
        
        start_gate_palace = leader_palace
        if start_gate_palace == 5: start_gate_palace = 2
        
        effective_target_gate_palace = target_gate_palace
        if effective_target_gate_palace == 5: effective_target_gate_palace = 2
        
        try:
            g_start_idx = gate_sequence.index(start_gate_palace)
        except ValueError:
            g_start_idx = 0
            
        try:
            g_target_idx = gate_sequence.index(effective_target_gate_palace)
        except ValueError:
            g_target_idx = 0
            
        g_offset = (g_target_idx - g_start_idx) % 8
        
        gate_plate_map = {}
        for i, original_palace in enumerate(gate_sequence):
            new_idx = (i + g_offset) % 8
            new_palace = gate_sequence[new_idx]
            gate_plate_map[new_palace] = self._get_gate_at_palace(original_palace)
            
        # 9. Тарелка Духов
        gods_list = self.config.gods_ru
        
        ring_sequence = [1, 8, 3, 4, 9, 2, 7, 6]
        try:
            god_start_idx = ring_sequence.index(target_palace_effective)
        except ValueError:
            god_start_idx = 0
            
        god_plate_map = {}
        for i, god_name in enumerate(gods_list):
            if is_yang:
                p_idx = (god_start_idx + i) % 8
            else:
                p_idx = (god_start_idx - i) % 8
            palace = ring_sequence[p_idx]
            god_plate_map[palace] = god_name

        # 10. Сборка
        palaces_data = {}
        for p in range(1, 10):
            e_stem = earth_plate.get(p, "")
            h_stem = heaven_plate_map.get(p, "")
            h_center = heaven_plate_map_center.get(p, "")
            
            if p == 5:
                h_stem_display = "" 
            else:
                h_stem_display = h_stem
            
            is_fou_tou_e = 1 if e_stem == leader_stem else 0
            is_fou_tou_h = 1 if (h_stem == leader_stem or h_center == leader_stem) else 0
            
            star_name = star_plate_map.get(p, "")
            if p == 5: star_name = "禽"
            
            gate_name = gate_plate_map.get(p, "")
            spirit_name = god_plate_map.get(p, "")
            
            is_main_s = 1 if star_name == zhi_fu_star else 0
            is_main_g = 1 if gate_name == zhi_shi_gate else 0
            
            palaces_data[p] = PalaceData(
                palace_no=p,
                earth_stem=e_stem,
                is_fou_tou_earth=is_fou_tou_e,
                heaven_stem=h_stem_display,
                is_fou_tou_heaven=is_fou_tou_h,
                star=star_name,
                is_main_star=is_main_s,
                gate=gate_name,
                is_main_gate=is_main_g,
                spirit=spirit_name
            )

        return QimenChart(
            hour_id=hour_id,
            chart_num=ju_num,
            yin_yang=yin_yang,
            palaces=palaces_data
        )

    def _get_star_at_palace(self, p: int) -> str:
        return self.config.stars_ru.get(p, "")

    def _get_gate_at_palace(self, p: int) -> str:
        return self.config.gates_ru.get(p, "")
