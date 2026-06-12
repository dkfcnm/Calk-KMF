#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for TongShuDay class.
"""

import sqlite3
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code.tongshu.core.tongshu_day import TongShuDay

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'calk_kmf.sqlite')
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_tongshu_day_output.txt')

def main():
    conn = sqlite3.connect(DB_PATH)
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as out:
        out.write(f"DB: {DB_PATH}\n")
        
        # Test for today (2026-05-16)
        test_date = "2026-05-16"
        out.write(f"\n=== Testing TongShuDay for {test_date} ===\n")
        day = TongShuDay.for_date(test_date, conn)
        
        out.write(f"Day pillar: {day.day_pillar}\n")
        out.write(f"Year pillar: {day.year_pillar}\n")
        out.write(f"Month pillar: {day.month_pillar}\n")
        out.write(f"Solar term: {day.solar_term_char} ({day.solar_term_name_ru})\n")
        out.write(f"Na Yin: {day.nayin_element} / {day.nayin_name}\n")
        out.write(f"Day Officer: {day.day_officer_char} ({day.day_officer_name_ru}) [{day.day_officer_category}]\n")
        out.write(f"Constellation: {day.constellation_char} ({day.constellation_name_ru}) [{day.constellation_nature}]\n")
        out.write(f"Belt: {day.belt_type} / stars: {day.belt_stars}\n")
        out.write(f"Moon: {day.moon_phase_name} ({day.moon_phase_pct}%)\n")
        out.write(f"Tong Shu Phase: {day.tongshu_phase_char} ({day.tongshu_phase_name_ru})\n")
        
        # Full dict output
        out.write("\n=== Full dict ===\n")
        data = day.to_dict()
        out.write(json.dumps(data, ensure_ascii=False, indent=2))
        out.write("\n")
        
        # Test another date
        out.write("\n=== Testing 2026-05-01 ===\n")
        day2 = TongShuDay.for_date("2026-05-01", conn)
        out.write(f"Day pillar: {day2.day_pillar}\n")
        out.write(f"Day Officer: {day2.day_officer_char} ({day2.day_officer_name_ru})\n")
        out.write(f"Constellation: {day2.constellation_char} ({day2.constellation_name_ru})\n")
    
    conn.close()
    print(f"Output written to {OUTPUT_PATH}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
