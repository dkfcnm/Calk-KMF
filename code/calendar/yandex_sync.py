"""
Модуль синхронизации событий с Яндекс Календарём (CalDAV).

Назначение:
    - Формирование таблицы t_event из данных расчётов (Бацзы / Day Officers).
    - Синхронизация событий с интернет-календарём Яндекса по протоколу CalDAV.

Основные этапы работы (при каждом запуске):
    0. Создание таблицы t_event (если не существует).
    1. Наполнение t_event из t_bazi_hourly + Day Officers (SQL-First, batch INSERT).
    2. Удаление прошедших событий (dt_end < now).
    3. Пересчёт колонки id (MD5-хэш: dt_start + dt_end + calendar + title + comment).
    4. Синхронизация с Яндекс Календарём (окно: now … now + 30 дней):
       а) id совпадает → пропускаем;
       б) id есть в календаре, но нет в t_event → удаляем из календаря;
       в) id есть в t_event, но нет в календаре → создаём в календаре.

Источники событий (все — на весь день, календарь "Ключевые события"):
    1. День Устранения     — офицер дня = Устранение
    2. День Наполнения     — офицер дня = Наполнение
    3. Мытье двери         — офицер дня = Успех / Сбор урожая / Открытие
    4. Грабитель богатства  — небесный ствол дня = 癸
    5. Благородный          — земная ветвь дня = 巳 или 卯

Зависимости:
    - caldav (pip install caldav)
    - vobject (pip install vobject)
    - pg8000 (через code.common.db_manager)

Обновлено: 2026-03-01
"""

import sys
import os
import hashlib
import logging
import time
from datetime import datetime, timedelta, date

import pytz
import caldav

# ═══════════════════════════════════════════════════════════════
# Настройки
# ═══════════════════════════════════════════════════════════════

# Учётные данные Яндекс Календаря
YANDEX_CALDAV_URL = 'https://caldav.yandex.ru'
YANDEX_EMAIL = 'demon-shuvalov@yandex.ru'
YANDEX_APP_PASSWORD = 'uelysftgmyblakps'

# Календарь для автогенерируемых событий из Бацзы
AUTO_CALENDAR_NAME = 'Ключевые события'

# Окно синхронизации (дней вперёд от текущей даты)
SYNC_DAYS_AHEAD = 30

# Временная зона
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

# Продукт для iCalendar
PRODID = '-//Calk_KMF//YandexSync v1.0//RU'

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# Инициализация БД
# ═══════════════════════════════════════════════════════════════

# Подключение к проектной БД
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from code.common.db_manager import db


def ensure_event_table():
    """Создаёт таблицу t_event, если не существует.
    
    Колонки:
        id       — MD5-хэш (dt_start + dt_end + calendar + title + comment)
        dt_start — начало события (timestamp)
        dt_end   — конец события (timestamp)
        calendar — название календаря Яндекс
        title    — заголовок события
        comment  — описание / комментарии
    
    Обновлено: 2026-02-28
    """
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS t_event (
            id       TEXT PRIMARY KEY,
            dt_start TIMESTAMP NOT NULL,
            dt_end   TIMESTAMP NOT NULL,
            calendar TEXT NOT NULL,
            title    TEXT NOT NULL,
            comment  TEXT
        )
    """)
    logger.info("Таблица t_event проверена/создана.")


# ═══════════════════════════════════════════════════════════════
# Наполнение t_event из данных Бацзы
# ═══════════════════════════════════════════════════════════════

def populate_events():
    """Наполняет t_event из t_bazi_hourly + Day Officers. SQL-First подход.
    
    Стратегия: DELETE + INSERT (полная перезапись).
    Для ~600 строк/год это занимает <1 сек и гарантирует консистентность.
    
    5 типов событий:
        1. День Устранения     (офицер = Устранение)
        2. День Наполнения     (офицер = Наполнение)
        3. Мытье двери         (офицер = Успех / Сбор урожая / Открытие)
        4. Грабитель богатства  (НС дня = 癸)
        5. Благородный          (ЗВ дня = 巳 или 卯)
    
    Возвращает количество вставленных строк.
    
    Обновлено: 2026-02-28
    """
    # Удаляем только автогенерируемые события (ручные в других календарях сохраняются)
    db.execute_query("DELETE FROM t_event WHERE calendar = %s", [AUTO_CALENDAR_NAME])
    
    sql = """
    INSERT INTO t_event (id, dt_start, dt_end, calendar, title, comment)
    WITH events_raw AS (
        -- ═══ Офицеры дня: Устранение, Наполнение, Мытье двери ═══
        SELECT DISTINCT
            date(h.slot_start_date_local) as event_date,
            CASE iv.name_ru 
                WHEN 'Устранение' THEN 'День Устранения'
                WHEN 'Наполнение' THEN 'День Наполнения'
                ELSE 'Мытье двери'
            END as title,
            iv.name_ru || ' (' || h.day_pillar || ')' as comment
        FROM t_bazi_hourly h
        JOIN spr_earthly_branch mb ON h.month_branch = mb.branch_char
        JOIN spr_earthly_branch db_br ON h.day_branch = db_br.branch_char
        JOIN spr_day_officer_mapping dom 
            ON mb.branch_id = dom.month_branch_id 
            AND db_br.branch_id = dom.day_branch_id
        JOIN spr_indicator_value iv ON dom.officer_value_id = iv.value_id
        WHERE h.hour_branch = '午'
        AND iv.name_ru IN ('Устранение', 'Наполнение', 'Успех', 'Сбор урожая', 'Открытие')
        
        UNION ALL
        
        -- ═══ Грабитель богатства: НС дня = 癸 ═══
        SELECT DISTINCT
            date(h.slot_start_date_local),
            'Грабитель богатства',
            'НС дня: 癸 (' || h.day_pillar || ')'
        FROM t_bazi_hourly h
        WHERE h.hour_branch = '午' AND h.day_stem = '癸'
        
        UNION ALL
        
        -- ═══ Благородный: ЗВ дня = 巳 или 卯 ═══
        SELECT DISTINCT
            date(h.slot_start_date_local),
            'Благородный',
            'ЗВ дня: ' || h.day_branch || ' (' || h.day_pillar || ')'
        FROM t_bazi_hourly h
        WHERE h.hour_branch = '午' AND h.day_branch IN ('巳', '卯')
    )
    SELECT
        md5(
            event_date::timestamp::text 
            || (event_date + interval '1 day')::timestamp::text 
            || '""" + AUTO_CALENDAR_NAME + """' 
            || title 
            || COALESCE(comment, '')
        ) as id,
        event_date::timestamp as dt_start,
        (event_date + interval '1 day')::timestamp as dt_end,
        '""" + AUTO_CALENDAR_NAME + """' as calendar,
        title,
        comment
    FROM events_raw
    ON CONFLICT (id) DO NOTHING
    """
    db.execute_query(sql)
    
    # Подсчёт автогенерируемых событий
    auto_count = db.fetch_one("SELECT COUNT(*) FROM t_event WHERE calendar = %s", [AUTO_CALENDAR_NAME])[0]
    total_count = db.fetch_one("SELECT COUNT(*) FROM t_event")[0]
    logger.info(f"t_event: {auto_count} авто + {total_count - auto_count} ручных = {total_count} всего.")
    return total_count


# ═══════════════════════════════════════════════════════════════
# Очистка и пересчёт ID
# ═══════════════════════════════════════════════════════════════

def cleanup_past_events():
    """Удаляет прошедшие события из t_event (dt_end < текущая дата/время МСК).
    
    Возвращает количество удалённых строк.
    
    Обновлено: 2026-02-28
    """
    now = datetime.now(MOSCOW_TZ).replace(tzinfo=None)  # naive для сравнения с timestamp
    
    # Подсчёт перед удалением
    count_before = db.fetch_one("SELECT COUNT(*) FROM t_event")[0]
    
    db.execute_query(
        "DELETE FROM t_event WHERE dt_end < %s",
        [now.strftime('%Y-%m-%d %H:%M:%S')]
    )
    
    count_after = db.fetch_one("SELECT COUNT(*) FROM t_event")[0]
    deleted = count_before - count_after
    
    if deleted > 0:
        logger.info(f"Удалено прошедших событий: {deleted}")
    return deleted


def recalculate_ids():
    """Пересчитывает колонку id для всех строк t_event.
    
    id = MD5(dt_start::text || dt_end::text || calendar || title || COALESCE(comment, ''))
    
    Стратегия: writable CTE — DELETE RETURNING + INSERT в одном SQL-запросе.
    Это обходит проблему нарушения PK при UPDATE SET id = ... 
    и работает в рамках одной транзакции / одного соединения.
    
    Обновлено: 2026-02-28
    """
    # Writable CTE: DELETE всех строк → INSERT с пересчитанным id (один SQL, одна транзакция)
    db.execute_query("""
        WITH old_data AS (
            DELETE FROM t_event RETURNING dt_start, dt_end, calendar, title, comment
        )
        INSERT INTO t_event (id, dt_start, dt_end, calendar, title, comment)
        SELECT
            md5(dt_start::text || dt_end::text || calendar || title || COALESCE(comment, '')),
            dt_start, dt_end, calendar, title, comment
        FROM old_data
        ON CONFLICT (id) DO NOTHING
    """)
    logger.info("ID событий пересчитаны.")


# ═══════════════════════════════════════════════════════════════
# Синхронизация с Яндекс Календарём
# ═══════════════════════════════════════════════════════════════

def _is_allday(dt_start, dt_end):
    """Определяет, является ли событие «на весь день».
    
    Критерий: оба timestamp имеют время 00:00:00 и разница = ровно N дней.
    
    Обновлено: 2026-03-01
    """
    if isinstance(dt_start, datetime) and isinstance(dt_end, datetime):
        start_midnight = (dt_start.hour == 0 and dt_start.minute == 0 and dt_start.second == 0)
        end_midnight = (dt_end.hour == 0 and dt_end.minute == 0 and dt_end.second == 0)
        diff = dt_end - dt_start
        return start_midnight and end_midnight and diff.seconds == 0 and diff.days >= 1
    return False


def _build_vevent(event_id, dt_start, dt_end, title, comment):
    """Формирует iCalendar строку для события (all-day или с временем).
    
    Параметры:
        event_id — UID события (MD5-хэш из t_event)
        dt_start — начало события (datetime)
        dt_end   — конец события (datetime)
        title    — заголовок (SUMMARY)
        comment  — описание (DESCRIPTION), может быть None
    
    Автоматически определяет тип события:
        - All-day: DTSTART;VALUE=DATE / DTEND;VALUE=DATE
        - С временем: DTSTART;TZID=Europe/Moscow / DTEND;TZID=Europe/Moscow
    
    Возвращает строку в формате iCalendar (RFC 5545).
    
    Обновлено: 2026-03-01
    """
    allday = _is_allday(dt_start, dt_end)
    
    if allday:
        ds_line = f'DTSTART;VALUE=DATE:{dt_start.strftime("%Y%m%d")}'
        de_line = f'DTEND;VALUE=DATE:{dt_end.strftime("%Y%m%d")}'
    else:
        # Событие с конкретным временем (МСК)
        ds_line = f'DTSTART;TZID=Europe/Moscow:{dt_start.strftime("%Y%m%dT%H%M%S")}'
        de_line = f'DTEND;TZID=Europe/Moscow:{dt_end.strftime("%Y%m%dT%H%M%S")}'
    
    # Экранирование спецсимволов в iCalendar
    safe_title = (title or '').replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')
    safe_comment = (comment or '').replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')
    
    lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        f'PRODID:{PRODID}',
        'BEGIN:VEVENT',
        f'UID:{event_id}',
        ds_line,
        de_line,
        f'SUMMARY:{safe_title}',
    ]
    if safe_comment:
        lines.append(f'DESCRIPTION:{safe_comment}')
    lines.extend([
        'END:VEVENT',
        'END:VCALENDAR'
    ])
    return '\r\n'.join(lines)


def sync_to_yandex():
    """Синхронизирует t_event с Яндекс Календарём.
    
    Обрабатывает ВСЕ календари, найденные в t_event (не только автогенерируемые).
    
    Алгоритм (окно: now … now + SYNC_DAYS_AHEAD, для каждого календаря):
        1. Загружаем события из t_event за окно.
        2. Загружаем события из Яндекс Календаря за то же окно.
        3. Сравниваем по id (UID):
           а) id совпадает → пропускаем
           б) id в календаре, нет в t_event → удаляем из календаря
           в) id в t_event, нет в календаре → создаём в календаре
    
    Возвращает словарь статистики: {kept, created, deleted, calendars_synced}.
    
    Обновлено: 2026-03-01
    """
    now = datetime.now(MOSCOW_TZ)
    end = now + timedelta(days=SYNC_DAYS_AHEAD)
    now_naive = now.replace(tzinfo=None)
    end_naive = end.replace(tzinfo=None)
    
    # --- 1. Все события из t_event за окно, сгруппированные по календарю ---
    db_events = db.fetch_all(
        """SELECT id, dt_start, dt_end, calendar, title, comment 
           FROM t_event 
           WHERE dt_start >= %s AND dt_start < %s
           ORDER BY calendar, dt_start""",
        [now_naive.strftime('%Y-%m-%d'), end_naive.strftime('%Y-%m-%d')]
    )
    
    # Группируем по имени календаря
    cal_events = {}
    for row in db_events:
        cal_name = row[3]
        if cal_name not in cal_events:
            cal_events[cal_name] = {}
        cal_events[cal_name][row[0]] = row  # id → row
    
    # --- 2. Подключение к Яндекс Календарю ---
    client = caldav.DAVClient(
        url=YANDEX_CALDAV_URL,
        username=YANDEX_EMAIL,
        password=YANDEX_APP_PASSWORD
    )
    principal = client.principal()
    yandex_calendars = {cal.name: cal for cal in principal.calendars()}
    
    # --- 3. Синхронизация каждого календаря ---
    stats = {'kept': 0, 'created': 0, 'deleted': 0, 'calendars_synced': 0}
    
    for cal_name, db_ids in cal_events.items():
        target_cal = yandex_calendars.get(cal_name)
        if not target_cal:
            logger.warning(f"Календарь '{cal_name}' не найден в Яндексе, пропускаем {len(db_ids)} событий. "
                          f"Доступные: {list(yandex_calendars.keys())}")
            continue
        
        # Получаем существующие события из Яндекс Календаря за окно
        yandex_events = target_cal.search(start=now, end=end, expand=True)
        yandex_ids = {}
        for ev in yandex_events:
            try:
                vevent = ev.vobject_instance.vevent
                uid = str(vevent.uid.value)
                yandex_ids[uid] = ev
            except Exception as e:
                logger.warning(f"Не удалось прочитать UID события в '{cal_name}': {e}")
        
        # Сравнение и синхронизация
        db_id_set = set(db_ids.keys())
        yx_id_set = set(yandex_ids.keys())
        
        # а) ID совпадают → ничего не делаем
        common = db_id_set & yx_id_set
        stats['kept'] += len(common)
        
        # б) В календаре, но нет в t_event → удалить
        for uid in (yx_id_set - db_id_set):
            try:
                yandex_ids[uid].delete()
                stats['deleted'] += 1
                logger.debug(f"[{cal_name}] Удалено: {uid}")
            except Exception as e:
                logger.error(f"[{cal_name}] Ошибка удаления {uid}: {e}")
        
        # в) В t_event, но нет в календаре → создать
        for uid in (db_id_set - yx_id_set):
            row = db_ids[uid]
            event_id, dt_start, dt_end, _, title, comment = row
            ical_data = _build_vevent(event_id, dt_start, dt_end, title, comment)
            try:
                target_cal.save_event(ical_data)
                stats['created'] += 1
                logger.debug(f"[{cal_name}] Создано: {uid} | {title}")
            except Exception as e:
                logger.error(f"[{cal_name}] Ошибка создания {uid} ({title}): {e}")
        
        stats['calendars_synced'] += 1
        logger.info(f"[{cal_name}] kept={len(common)}, created={len(db_id_set - yx_id_set)}, deleted={len(yx_id_set - db_id_set)}")
    
    logger.info(f"Итого: календарей={stats['calendars_synced']}, kept={stats['kept']}, created={stats['created']}, deleted={stats['deleted']}")
    return stats


# ═══════════════════════════════════════════════════════════════
# Главная функция
# ═══════════════════════════════════════════════════════════════

def run_sync():
    """Полный цикл синхронизации.
    
    Порядок выполнения:
        0. Создание таблицы t_event (если нужно)
        1. Наполнение t_event из Бацзы-данных
        2. Удаление прошедших событий
        3. Пересчёт ID
        4. Синхронизация с Яндекс Календарём
    
    Обновлено: 2026-02-28
    """
    t0 = time.time()
    print("=" * 60)
    print("Синхронизация событий с Яндекс Календарём")
    print("=" * 60)
    
    # 0. Таблица
    print("\n[0] Проверка таблицы t_event...")
    ensure_event_table()
    
    # 1. Наполнение автогенерируемых событий (ручные сохраняются)
    print(f"[1] Наполнение t_event из данных Бацзы (авто: '{AUTO_CALENDAR_NAME}')...")
    count = populate_events()
    print(f"    Всего событий в таблице: {count}")
    
    # 2. Очистка
    print("[2] Удаление прошедших событий...")
    deleted = cleanup_past_events()
    print(f"    Удалено: {deleted}")
    
    # 3. Пересчёт ID
    print("[3] Пересчёт ID...")
    recalculate_ids()
    remaining = db.fetch_one("SELECT COUNT(*) FROM t_event")[0]
    print(f"    Событий после пересчёта: {remaining}")
    
    # 4. Синхронизация (все календари из t_event)
    print("[4] Синхронизация с Яндекс Календарём (все календари)...")
    now = datetime.now(MOSCOW_TZ)
    print(f"    Окно: {now.strftime('%Y-%m-%d')} ... {(now + timedelta(days=SYNC_DAYS_AHEAD)).strftime('%Y-%m-%d')}")
    stats = sync_to_yandex()
    print(f"    Результат: календарей={stats['calendars_synced']}, оставлено={stats['kept']}, создано={stats['created']}, удалено={stats['deleted']}")
    
    elapsed = time.time() - t0
    print(f"\nГотово за {elapsed:.1f} сек.")
    print("=" * 60)
    
    return stats


# ═══════════════════════════════════════════════════════════════
# Точка входа
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    
    # Кодировка для Windows-консоли
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    run_sync()
