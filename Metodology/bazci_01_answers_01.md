1.  Цель первого шага: автоматизация бацзы календаря, но с прицелом на последующее обогащение для полноценного календаря Тун Шу (12 офицеров, наинь, Сюнь Кун Да Гуа, символические звезды и т.д.) и расчетов Ци Мэнь (по различным методологиям)
2.  Формула «текущий год + 2 следующих» - временное ограничение пока идет этап разработки
3.  Расчет за предыдущие периоды не нужен
4.  Нужен точный астрономический расчет долготы солнца. Для стартового примера (можно использовать другие библиотеки или подход. это только иллюстрация)

```Python
from importlib import reload
import sqlite3
import pandas as pd
from datetime import datetime, timedelta, date

import numpy as np
from astropy.time import Time
from astropy.coordinates import get_sun, GeocentricTrueEcliptic
from astropy import units as u

tb_nm = 't_spr_sun_dt'
sql = f"""
CREATE TABLE "{tb_nm}" (
    god INTEGER,
    mes INTEGER,
    den INTEGER,
    chas INTEGER,
    minuta INTEGER,
    dt INTEGER,
    deg INTEGER,
    god_cha integer,
    mes_cha integer
);
"""
MT.drop_table(tb_nm)
MT.gp_execute(sql)

def find_sun_crossing(year, degrees):
    # Начало и конец года
    start_time = Time(f'{year}-01-01 00:00:00')
    end_time = Time(f'{year}-12-31 23:59:59')
    
    # Временной интервал для поиска пересечений
    dt = end_time - start_time
    
    # Создаем массив временных точек для проверки положения Солнца
    times = start_time + dt * np.linspace(0, 1, 100000)
    
    # Получаем положение Солнца в каждый из этих моментов
    sun_positions = get_sun(times).transform_to(GeocentricTrueEcliptic())
    
    # Эклиптическая долгота Солнца
    sun_longitudes = sun_positions.lon.wrap_at(360 * u.deg).degree
    
    results = []
    
    for degree in degrees:
        # Найдем время, когда Солнце ближе всего к заданному градусу
        idx = (np.abs(sun_longitudes - degree)).argmin()
        closest_time = times[idx].iso
        closest_degree = sun_longitudes[idx]
        results.append((degree, closest_time, closest_degree))
    
    return results

degrees = [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345]


for year in range(year_st, year_en):
    print(f"Year: {year}")
    crossings = find_sun_crossing(year, degrees)
    for degree, time, actual_degree in crossings:
        dt = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
        if degree in (315, 330, 345, 0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270):
            god_cha = dt.year 
            mes_cha = dt.month - 1
        elif degree in (285, 300):
            god_cha = dt.year - 1
            mes_cha = 12
        MT.insert_data(tb = tb_nm, column = ['god', 'mes', 'den', 'chas', 'minuta', 'dt', 'deg', 'god_cha', 'mes_cha'], value = [dt.year
                                                                                            , dt.month
                                                                                            , dt.day
                                                                                            , dt.hour
                                                                                            , dt.minute
                                                                                            , time
                                                                                            , degree
                                                                                            , god_cha
                                                                                            , mes_cha
                                                                                            ])
        print(f"Degree: {degree}° - Time: {time}, Actual Degree: {actual_degree:.2f}°")
    print("\n")
```

5\. Точность момента смены сезонов минуты  
6\. Если астрономическое время смены сезона совпадает с границей часа, то относить к новому сезону.  
7\. Все расчеты приводим к GMT+0. В будущем адаптация под запрос будет через расчет и указание временной поправки и часового пояса  
8\. 1864 просто опорный год, когда точно известно, что столп года состоит из 1го небесного ствола 甲 и первой Земной ветви 子. Это не стандарт, просто известная дата. Можно использовать 1984 год.
9\. Да, если найдешь точные проверочные данные, то можно использовать.  
10\. Для столпа месяца используем классическую схему: от столпа года и земной ветви месяца по стандартной таблице (1‑й месяц Инь и т.п.)  
11\. Аналогичная стандартная схема для столпа Часа.  
12\. DuckDB — это целевой и единственный движок  
13\. `VIEW` должен быть чисто логическим (без материализации), и расчёты будут происходить «на лету»  
14\. предложи консистентную схему именования  
15\. Под каждую методологию, новый модуль будет отдельный файл