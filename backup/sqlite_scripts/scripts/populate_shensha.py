#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Наполнение spr_tongshu_shensha_rule данными из bazci_star.md
"""

import sqlite3
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "calk_kmf.sqlite")

def populate_shensha():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("DELETE FROM spr_tongshu_shensha_rule")
    
    rules = []
    
    # ============================================================
    # 1. По Небесному Стволу дня или года
    # ============================================================
    
    # Благородный человек (阴贵人)
    noble_yin = {
        '甲': '丑', '乙': '申', '丙': '亥', '丁': '亥',
        '戊': '丑', '己': '申', '庚': '丑', '辛': '午',
        '壬': '辰', '癸': '辰'
    }
    for stem, branch in noble_yin.items():
        rules.append(("Благородный человек (阴)", "day_stem", stem, "day_branch", branch, "Также по year_stem"))
    
    # Благородный человек (阳贵人)
    noble_yang = {
        '甲': '未', '乙': '子', '丙': '酉', '丁': '酉',
        '戊': '未', '己': '子', '庚': '未', '辛': '寅',
        '壬': '巳', '癸': '巳'
    }
    for stem, branch in noble_yang.items():
        rules.append(("Благородный человек (阳)", "day_stem", stem, "day_branch", branch, "Также по year_stem"))
    
    # 10 небесных стволов (禄)
    lu = {
        '甲': '寅', '乙': '卯', '丙': '巳', '丁': '午',
        '戊': '巳', '己': '午', '庚': '申', '辛': '酉',
        '壬': '亥', '癸': '子'
    }
    for stem, branch in lu.items():
        rules.append(("10 небесных стволов (禄)", "day_stem", stem, "day_branch", branch, "Также по year_stem"))
    
    # Звезда академика (文昌)
    wenchang = {
        '甲': '巳', '乙': '午', '丙': '申', '丁': '酉',
        '戊': '申', '己': '酉', '庚': '亥', '辛': '子',
        '壬': '寅', '癸': '卯'
    }
    for stem, branch in wenchang.items():
        rules.append(("Звезда академика (文昌)", "day_stem", stem, "day_branch", branch, "Также по year_stem"))
    
    # Овечий нож 1
    yangren1 = {
        '甲': '卯', '乙': '辰', '丙': '午', '丁': '未',
        '戊': '午', '己': '未', '庚': '酉', '辛': '戌',
        '壬': '子', '癸': '丑'
    }
    for stem, branch in yangren1.items():
        rules.append(("Овечий нож (羊刃)", "day_stem", stem, "day_branch", branch, "Также по year_stem"))
    
    # Овечий нож 2 (дополнительные)
    yangren2 = {
        '乙': '寅', '丁': '巳', '辛': '申', '癸': '亥'
    }
    for stem, branch in yangren2.items():
        rules.append(("Овечий нож 2 (羊刃)", "day_stem", stem, "day_branch", branch, "Также по year_stем"))
    
    # Ша цветущего персика (桃花煞)
    taohuasha = {
        '甲': '子', '乙': '子', '丙': '寅', '丁': '未',
        '戊': '辰', '己': '辰', '庚': '戌', '辛': '酉',
        '壬': '子', '癸': '申'
    }
    for stem, branch in taohuasha.items():
        rules.append(("Ша цветущего персика (桃花煞)", "day_stem", stem, "day_branch", branch, "Также по year_stem"))
    
    # Небесный чиновник 1
    tianguan1 = {
        '甲': '酉', '乙': '申', '丙': '子', '丁': '亥',
        '戊': '卯', '己': '寅', '庚': '午', '辛': '巳',
        '壬': '未', '癸': '辰'
    }
    for stem, branch in tianguan1.items():
        rules.append(("Небесный чиновник (天官)", "day_stem", stem, "day_branch", branch, "Также по year_stem"))
    
    # Небесный чиновник 2
    tianguan2 = {
        '壬': '丑', '癸': '戌'
    }
    for stem, branch in tianguan2.items():
        rules.append(("Небесный чиновник 2 (天官)", "day_stem", stem, "day_branch", branch, "Также по year_stem"))
    
    # Золотая карета (金舆)
    jinyu = {
        '甲': '辰', '乙': '巳', '丙': '未', '丁': '申',
        '戊': '未', '己': '申', '庚': '戌', '辛': '亥',
        '壬': '丑', '癸': '寅'
    }
    for stem, branch in jinyu.items():
        rules.append(("Золотая карета (金舆)", "day_stem", stem, "day_branch", branch, "Также по year_stem"))
    
    # ============================================================
    # 2. По Земной Ветви дня и/или года (триады)
    # ============================================================
    
    # Цветок персика (桃花)
    taohua_triads = [
        (['申', '子', '辰'], '酉'),
        (['亥', '卯', '未'], '子'),
        (['寅', '午', '戌'], '卯'),
        (['巳', '酉', '丑'], '午'),
    ]
    for sources, target in taohua_triads:
        for src in sources:
            rules.append(("Цветок персика (桃花)", "day_branch", src, "day_branch", target, "Триада; также по year_branch"))
    
    # Почтовая лошадь (驿马)
    yima_triads = [
        (['申', '子', '辰'], '寅'),
        (['亥', '卯', '未'], '巳'),
        (['寅', '午', '戌'], '申'),
        (['巳', '酉', '丑'], '亥'),
    ]
    for sources, target in yima_triads:
        for src in sources:
            rules.append(("Почтовая лошадь (驿马)", "day_branch", src, "day_branch", target, "Триада; также по year_branch"))
    
    # Звезда генерала (将星)
    jiangxing_triads = [
        (['申', '子', '辰'], '子'),
        (['亥', '卯', '未'], '卯'),
        (['寅', '午', '戌'], '午'),
        (['巳', '酉', '丑'], '酉'),
    ]
    for sources, target in jiangxing_triads:
        for src in sources:
            rules.append(("Звезда генерала (将星)", "day_branch", src, "day_branch", target, "Триада; также по year_branch"))
    
    # Звезда искусств (华盖)
    huagai_triads = [
        (['申', '子', '辰'], '辰'),
        (['亥', '卯', '未'], '未'),
        (['寅', '午', '戌'], '戌'),
        (['巳', '酉', '丑'], '丑'),
    ]
    for sources, target in huagai_triads:
        for src in sources:
            rules.append(("Звезда искусств (华盖)", "day_branch", src, "day_branch", target, "Триада; также по year_branch"))
    
    # Ангел смерти (亡神)
    wangshen_triads = [
        (['申', '子', '辰'], '亥'),
        (['亥', '卯', '未'], '寅'),
        (['寅', '午', '戌'], '巳'),
        (['巳', '酉', '丑'], '申'),
    ]
    for sources, target in wangshen_triads:
        for src in sources:
            rules.append(("Ангел смерти (亡神)", "day_branch", src, "day_branch", target, "Триада; также по year_branch"))
    
    # Три ша (三煞) - пары из файла
    san_sha_pairs = [
        ("巳", "申"), ("巳", "子"), ("巳", "辰"),
        ("午", "申"), ("午", "子"), ("午", "辰"),
        ("未", "申"), ("未", "子"), ("未", "辰"),
        ("申", "亥"), ("申", "卯"), ("申", "未"),
        ("酉", "亥"), ("酉", "卯"), ("酉", "未"),
        ("戌", "亥"), ("戌", "卯"), ("戌", "未"),
        ("寅", "亥"), ("午", "亥"), ("戌", "亥"),
        ("寅", "子"), ("午", "子"), ("戌", "子"),
        ("寅", "丑"), ("午", "丑"), ("戌", "丑"),
        ("巳", "寅"), ("酉", "寅"), ("丑", "寅"),
        ("巳", "卯"), ("酉", "卯"), ("丑", "卯"),
        ("巳", "辰"), ("酉", "辰"), ("丑", "辰"),
    ]
    for master, target in san_sha_pairs:
        rules.append(("Три ша (三煞)", "day_branch", master, "day_branch", target, "Также по year_branch"))
    
    # ============================================================
    # 3. По Земной Ветви года
    # ============================================================
    
    # Одинокая планета (孤辰)
    guchen = {
        '亥': '寅', '午': '寅', '丑': '寅',
        '寅': '巳', '卯': '巳', '辰': '巳',
    }
    for year_branch, target in guchen.items():
        rules.append(("Одинокая планета (孤辰)", "year_branch", year_branch, "day_branch", target, ""))
    
    # Приют одиночества (寡宿)
    guasu = {
        '亥': '戌', '午': '戌', '丑': '戌',
    }
    for year_branch, target in guasu.items():
        rules.append(("Приют одиночества (寡宿)", "year_branch", year_branch, "day_branch", target, ""))
    
    # ============================================================
    # 4. По Земной Ветви месяца
    # ============================================================
    
    # Небесная добродетель (天德)
    tiande = {
        '寅': '丁', '卯': '申', '辰': '壬', '巳': '辛',
        '午': '亥', '未': '甲', '申': '癸', '酉': '寅',
        '戌': '丙', '亥': '乙', '子': '巳', '丑': '庚'
    }
    for branch, stem in tiande.items():
        rules.append(("Небесная добродетель (天德)", "month_branch", branch, "day_stem", stem, ""))
    
    # Месячная добродетель (月德)
    yuede = {
        '寅': '丙', '卯': '甲', '辰': '壬', '巳': '庚',
        '午': '丙', '未': '甲', '申': '壬', '酉': '庚',
        '戌': '丙', '亥': '甲', '子': '壬', '丑': '庚'
    }
    for branch, stem in yuede.items():
        rules.append(("Месячная добродетель (月德)", "month_branch", branch, "day_stem", stem, ""))
    
    # Небесный доктор (天医)
    tianyi = {
        '寅': '丑', '卯': '寅', '辰': '卯', '巳': '辰',
        '午': '巳', '未': '午', '申': '未', '酉': '申',
        '戌': '酉', '亥': '戌', '子': '亥', '丑': '子'
    }
    for branch, target in tianyi.items():
        rules.append(("Небесный доктор (天医)", "month_branch", branch, "day_branch", target, ""))
    
    # ============================================================
    # 5. По Земной Ветви года (другие)
    # ============================================================
    
    # Красный луань (红鸾)
    hongluan = {
        '子': '卯', '丑': '寅', '寅': '丑', '卯': '子',
        '辰': '亥', '巳': '戌', '午': '酉', '未': '申',
        '申': '未', '酉': '午', '戌': '巳', '亥': '辰'
    }
    for branch, target in hongluan.items():
        rules.append(("Красный луань (红鸾)", "year_branch", branch, "day_branch", target, ""))
    
    # Исходное созвездие 1 (元辰) — муж ян / жен инь
    yuanchen1 = {
        '子': '未', '丑': '申', '寅': '酉', '卯': '戌',
        '辰': '亥', '巳': '子', '午': '丑', '未': '寅',
        '申': '卯', '酉': '辰', '戌': '巳', '亥': '午'
    }
    for branch, target in yuanchen1.items():
        rules.append(("Исходное созвездие 1 (元辰)", "year_branch", branch, "day_branch", target, "Мужчина ян, женщина инь"))
    
    # Исходное созвездие 2 (元辰) — муж инь / жен ян
    yuanchen2 = {
        '子': '巳', '丑': '午', '寅': '未', '卯': '申',
        '辰': '酉', '巳': '戌', '午': '亥', '未': '子',
        '申': '丑', '酉': '卯', '戌': '卯', '亥': '辰'
    }
    for branch, target in yuanchen2.items():
        rules.append(("Исходное созвездие 2 (元辰)", "year_branch", branch, "day_branch", target, "Мужчина инь, женщина ян. Возможны опечатки в исходном файле (酉→卯, 戌→卯)"))
    
    # ============================================================
    # 6. Комбинации Ствол + Ветвь
    # ============================================================
    
    # Куйган (魁罡)
    kuigang = [
        ('庚', '辰'), ('庚', '戌'), ('壬', '辰'), ('戊', '戌')
    ]
    for stem, branch in kuigang:
        rules.append(("Куйган (魁罡)", "day_stem", stem, "day_branch", branch, ""))
    
    # Ошибка Инь Янь (阴阳差错)
    yinyang_errors = [
        ('丙', '子'), ('丁', '丑'), ('戊', '寅'), ('辛', '卯'),
        ('壬', '辰'), ('癸', '巳'), ('丙', '午'), ('丁', '未'),
        ('戊', '申'), ('辛', '酉'), ('壬', '戌'), ('癸', '亥')
    ]
    for stem, branch in yinyang_errors:
        rules.append(("Ошибка Инь Янь (阴阳差错)", "day_stem", stem, "day_branch", branch, ""))
    
    # Сети небеси ловушка земли (天罗地网)
    tianluo = [
        ('戊', '亥'), ('辰', '巳')
    ]
    for stem, branch in tianluo:
        rules.append(("Сети небеси ловушка земли (天罗地网)", "day_stem", stem, "day_branch", branch, ""))
    
    # ============================================================
    # Insert all rules
    # ============================================================
    cursor.executemany(
        "INSERT INTO spr_tongshu_shensha_rule (star_name, master_scope, master_value, target_scope, target_value, notes) VALUES (?, ?, ?, ?, ?, ?)",
        rules
    )
    
    conn.commit()
    print(f"Inserted {len(rules)} shensha rules.")
    conn.close()

if __name__ == "__main__":
    populate_shensha()
