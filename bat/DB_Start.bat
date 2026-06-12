@echo off
echo ==========================================
echo  Calk_KMF - Starting Infrastructure
echo ==========================================
echo.

:: 1. PostgreSQL
echo [1/2] Starting PostgreSQL...
net start postgresql-x64-18
if %errorlevel% neq 0 (
    echo [!] PostgreSQL already running or start failed
) else (
    echo [OK] PostgreSQL started
)

:: 2. Headroom Proxy
echo.
echo [2/2] Starting Headroom Proxy...
echo        URL: http://127.0.0.1:8788
echo        Memory: ENABLED
echo        Code-Aware: ENABLED

:: Check if already running
tasklist | findstr /I "headroom" >nul
if %errorlevel% equ 0 (
    echo [!] Headroom proxy already running
) else (
    start /MIN "" headroom proxy --port 8788 --memory --memory-storage=project --code-aware --memory-db-path .headroom\memory.db --log-file .headroom\logs\proxy.log
    ping -n 4 127.0.0.1 >nul
    tasklist | findstr /I "headroom" >nul
    if %errorlevel% equ 0 (
        echo [OK] Headroom proxy started
    ) else (
        echo [!] Headroom proxy start failed
    )
)

echo.
echo ==========================================
echo  All services started
echo ==========================================
pause
