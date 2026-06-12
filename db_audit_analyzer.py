#!/usr/bin/env python3
import json
from collections import defaultdict

with open("db_audit_result.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("=" * 80)
print("СВОДКА ПО БАЗЕ ДАННЫХ")
print("=" * 80)
print(f"Файл: {data['db_path']}")
print(f"Размер: {data['db_size_mb']} MB")
print(f"Таблиц: {data['total_tables']}")
print(f"Views: {data['total_views']}")
print(f"Индексов: {data['total_indexes']}")
print()

# Категории
for cat, items in data['summary'].items():
    print(f"[{cat.upper()}] ({len(items)}): {', '.join(items)}")
print()

# Размеры таблиц
print("=" * 80)
print("РАЗМЕРЫ ТАБЛИЦ (топ-30 по размеру)")
print("=" * 80)
sizes = []
for t, info in data['tables'].items():
    rc = info['row_count']
    if isinstance(rc, int):
        sizes.append((t, rc, info['category']))
sizes.sort(key=lambda x: x[1], reverse=True)
for t, rc, cat in sizes[:30]:
    print(f"  {t:45s} {rc:>12,}  [{cat}]")
print()

# Индексы
print("=" * 80)
print("ИНДЕКСЫ")
print("=" * 80)
for tbl, idxs in sorted(data['indexes_by_table'].items()):
    print(f"  {tbl}:")
    for idx in idxs:
        print(f"    - {idx['name']}: {idx['sql']}")
print()

# Таблицы без индексов
print("=" * 80)
print("ТАБЛИЦЫ БЕЗ ИНДЕКСОВ (кроме справочников < 500 строк)")
print("=" * 80)
no_idx = []
for t, info in data['tables'].items():
    rc = info['row_count']
    if t not in data['indexes_by_table'] and (isinstance(rc, int) and rc > 500):
        no_idx.append((t, rc, info['category']))
no_idx.sort(key=lambda x: x[1], reverse=True)
for t, rc, cat in no_idx:
    print(f"  {t:45s} {rc:>12,}  [{cat}]")
print()

# Views
print("=" * 80)
print("VIEWS")
print("=" * 80)
for v in data['views']:
    print(f"  {v['name']}")
print()

# Дубли по названию
print("=" * 80)
print("ПОХОЖИЕ НАЗВАНИЯ (потенциальные дубли)")
print("=" * 80)
all_names = list(data['tables'].keys())
groups = defaultdict(list)
for name in all_names:
    base = name.replace("_hourly", "").replace("_daily", "").replace("_monthly", "").replace("_yearly", "")
    groups[base].append(name)
for base, names in sorted(groups.items()):
    if len(names) > 1:
        print(f"  {base}: {names}")
print()

# Контрольные таблицы
print("=" * 80)
print("КОНТРОЛЬНЫЕ ТАБЛИЦЫ")
print("=" * 80)
controls = data['summary']['control']
print(f"Найдено: {controls}")
main_tables = [t for t in data['summary']['main'] if not t.startswith('t_control_')]
for t in sorted(main_tables):
    expected = f"t_control_{t[2:]}"
    status = "OK" if expected in controls else "ОТСУТСТВУЕТ"
    if status == "ОТСУТСТВУЕТ":
        print(f"  {t:45s} -> {expected:45s} [{status}]")
print()

# Ключевые справочники
print("=" * 80)
print("КЛЮЧЕВЫЕ СПРАВОЧНИКИ - СТРУКТУРА")
print("=" * 80)
key_refs = ['spr_heavenly_stem', 'spr_earthly_branch', 'spr_gods', 'spr_stars',
            'spr_gates', 'spr_solar_term', 'spr_jiazi_extended']
for ref in key_refs:
    if ref in data['tables']:
        info = data['tables'][ref]
        print(f"\n{ref} (rows={info['row_count']}):")
        for col in info['columns']:
            pk = " PK" if col['pk'] else ""
            nn = " NOT NULL" if col['notnull'] else ""
            print(f"  {col['name']:25s} {col['type']:15s}{pk}{nn}")
    else:
        print(f"\n{ref}: ОТСУТСТВУЕТ")
print()

# Поиск удаленных таблиц в VIEW SQL
print("=" * 80)
print("ПРОВЕРКА VIEW НА ССЫЛКИ НА УДАЛЕННЫЕ/ОТСУТСТВУЮЩИЕ ТАБЛИЦЫ")
print("=" * 80)
existing = set(data['tables'].keys())
for v in data['views']:
    sql = v.get('sql') or ""
    for word in sql.split():
        w = word.strip('",\'();')
        if w.startswith(('t_', 'spr_', 'v_')) and w not in existing and w != v['name']:
            print(f"  VIEW {v['name']} ссылается на отсутствующую таблицу: {w}")
print()

# Проверка на пустые типы колонок
print("=" * 80)
print("КОЛОНКИ С ПУСТЫМ ТИПОМ ДАННЫХ")
print("=" * 80)
for t, info in sorted(data['tables'].items()):
    for col in info['columns']:
        if not col['type']:
            print(f"  {t}.{col['name']}")
print()

# Структурное сравнение похожих таблиц (hourly)
print("=" * 80)
print("СТРУКТУРНОЕ СРАВНЕНИЕ: t_bazi_* и t_qimen_*")
print("=" * 80)
hourly = [t for t in data['tables'] if '_hourly' in t]
structs = defaultdict(list)
for t in hourly:
    cols = tuple((c['name'], c['type'], c['pk']) for c in data['tables'][t]['columns'])
    structs[cols].append(t)
for cols, tables in structs.items():
    if len(tables) > 1:
        print(f"\nОдинаковая структура ({len(tables)} таблиц): {tables}")
        for c in cols:
            print(f"  {c[0]:30s} {c[1]:15s} {'PK' if c[2] else ''}")
print()

print("Анализ завершен.")
