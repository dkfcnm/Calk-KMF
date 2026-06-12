@echo off
echo ==========================================
echo  Headroom Proxy - Context Optimization
echo  URL: http://127.0.0.1:8788
echo ==========================================
echo.

:: Check if already running
tasklist | findstr /I "headroom" >nul
if %errorlevel% equ 0 (
    echo [!] Headroom proxy already running
    echo     Check: curl http://127.0.0.1:8788/livez
    pause
    exit /b
)

set HEADROOM_PORT=8788
set HEADROOM_MODE=token
set HEADROOM_CODE_AWARE_ENABLED=1

headroom proxy ^
  --port 8788 ^
  --memory ^
  --memory-storage=project ^
  --code-aware ^
  --memory-db-path .headroom\memory.db ^
  --log-file .headroom\logs\proxy.log

pause
