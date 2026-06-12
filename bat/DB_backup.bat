@echo off
setlocal

:: --- НАСТРОЙКИ ---
:: Путь к pg_dump (проверьте версию в пути)
set PG_BIN="D:\Program Files\PostgreSQL\18\bin\pg_dump.exe"

:: Реквизиты доступа
set PG_HOST=localhost
set PG_PORT=5432
set PG_USER=postgres
:: ВАЖНО: Пароль лучше задать через файл pgpass, но для домашнего скрипта можно так:
set PGPASSWORD=1Dct,eltn!

:: Имя базы данных (или all для всех)
set DB_NAME=calk_kmf

:: Папка для бэкапов на HDD (сначала локально)
set BACKUP_DIR=e:\Project\Calk_KMF\backup\

:: --- ПОЛУЧЕНИЕ ДАТЫ (ISO формат YYYY-MM-DD без зависимости от настроек Windows) ---
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set YYYY=%datetime:~0,4%
set MM=%datetime:~4,2%
set DD=%datetime:~6,2%
set FILE_DATE=%YYYY%-%MM%-%DD%

:: Имя файла
set FILENAME=%DB_NAME%_%FILE_DATE%.backup

:: --- ВЫПОЛНЕНИЕ ---
:: 1. Создаем дамп в формате Custom (-Fc). Это сжатый формат, лучший для восстановления.
%PG_BIN% -h %PG_HOST% -p %PG_PORT% -U %PG_USER% -F c -b -v -f "%BACKUP_DIR%\%FILENAME%" %DB_NAME%

:: 2. (Опционально) Удаляем из локальной папки файлы старше 30 дней, чтобы не забить HDD
forfiles /p "%BACKUP_DIR%" /s /m *.backup /D -30 /C "cmd /c del @path"

endlocal
