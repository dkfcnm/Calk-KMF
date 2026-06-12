#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Tong Shu daily API service directly (no FastAPI server needed).
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'api', 'app'))

from services.tongshu_daily_service import get_day_data, get_month_data
from datetime import date

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_tongshu_api_output.txt')

def main():
    with open(OUTPUT, 'w', encoding='utf-8') as out:
        out.write("=== Test get_day_data ===\n")
        day = get_day_data(date(2026, 5, 16))
        out.write(f"Date: {day['calendar_date']}\n")
        out.write(f"Day pillar: {day['day_pillar']}\n")
        out.write(f"Officer: {day['day_officer_char']} ({day['day_officer_name_ru']})\n")
        out.write(f"Constellation: {day['constellation_char']} ({day['constellation_name_ru']})\n")
        out.write(f"Belt: {day['belt_type']} / {day['belt_stars']}\n")
        out.write(f"Moon: {day['moon_phase_name']} ({day['moon_phase_pct']}%)\n")
        
        out.write("\n=== Test get_month_data ===\n")
        month = get_month_data(2026, 5)
        out.write(f"Total days: {len(month)}\n")
        for d in month[:5]:
            out.write(f"  {d['calendar_date']}: {d['day_pillar']} | Officer: {d['day_officer_char']} | Const: {d['constellation_char']} | Belt: {d['belt_type']}\n")
        
        out.write("\n=== Full JSON for 2026-05-16 ===\n")
        out.write(json.dumps(day, ensure_ascii=False, indent=2))
        out.write("\n")
    
    print(f"Output written to {OUTPUT}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
