@echo off
echo ==========================================
echo  Calk_KMF - Stopping Infrastructure
echo ==========================================
echo.

:: 1. Headroom Proxy
echo [1/2] Stopping Headroom Proxy...
tasklist | findstr /I "headroom" >nul
if %errorlevel% equ 0 (
    taskkill /F /IM headroom.exe >nul 2>&1
    echo [OK] Headroom proxy stopped
) else (
    echo [!] Headroom proxy not running
)

:: 2. PostgreSQL
echo.
echo [2/2] Stopping PostgreSQL...
net stop postgresql-x64-18
if %errorlevel% neq 0 (
    echo [!] PostgreSQL already stopped or stop failed
) else (
    echo [OK] PostgreSQL stopped
)

echo.
echo ==========================================
echo  All services stopped
echo ==========================================
pause
