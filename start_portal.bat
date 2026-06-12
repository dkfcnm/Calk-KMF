@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title Calk_KMF Portal

set "PROJECT_ROOT=%~dp0"
set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

set "BACKEND_HOST=0.0.0.0"
set "BACKEND_PORT=8000"
set "FRONTEND_URL=http://localhost:3000"
set "BACKEND_URL=http://127.0.0.1:%BACKEND_PORT%"

echo ==========================================
echo   Calk_KMF Portal - Starting...
echo ==========================================
echo.

REM === Check Python ===
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH.
    echo Please install Python and add it to PATH.
    pause
    exit /b 1
)
echo [OK] Python found

REM === Check Node.js and npm ===
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found in PATH.
    echo Please install Node.js and add it to PATH.
    pause
    exit /b 1
)
echo [OK] Node.js found

where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm not found in PATH.
    echo Please reinstall Node.js with default settings.
    pause
    exit /b 1
)
echo [OK] npm found

REM === Check PostgreSQL ===
net start 2>nul | findstr /I "postgresql" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] PostgreSQL service is running
) else (
    echo [INFO] PostgreSQL service not detected as running.
    echo Starting infrastructure via bat\DB_Start.bat...
    start /MIN "" "%~dp0bat\DB_Start.bat"
    echo Waiting for PostgreSQL to initialize...
    timeout /t 5 /nobreak >nul

    net start 2>nul | findstr /I "postgresql" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] PostgreSQL service is now running
    ) else (
        echo [WARN] PostgreSQL still not detected. Please start it manually with bat\DB_Start.bat.
        pause
    )
)

REM === Check backend availability ===
curl -s --max-time 2 %BACKEND_URL%/ >nul 2>&1
if %errorlevel% == 0 (
    echo [WARN] Backend already running on port %BACKEND_PORT%
    set "START_BACKEND=0"
) else (
    echo [1/2] Starting FastAPI backend on %BACKEND_URL% (dev mode with reload)...
    set "START_BACKEND=1"
)

if "%START_BACKEND%"=="1" (
    REM IMPORTANT: launch from api\ to avoid code/calendar shadowing stdlib calendar.
    start "Calk_KMF Backend" cmd /k "cd /d %PROJECT_ROOT%\api && python -m uvicorn app.main:app --reload --host %BACKEND_HOST% --port %BACKEND_PORT%"
    echo Waiting for backend initialization...
    timeout /t 5 /nobreak >nul
)

REM === Check frontend availability ===
curl -s --max-time 2 %FRONTEND_URL%/ >nul 2>&1
if %errorlevel% == 0 (
    echo [WARN] Frontend already running on port 3000
    set "START_FRONTEND=0"
) else (
    echo [2/2] Starting React frontend on %FRONTEND_URL%...
    set "START_FRONTEND=1"
)

if "%START_FRONTEND%"=="1" (
    start "Calk_KMF Frontend" cmd /k "cd /d %PROJECT_ROOT%\frontend && npm start"
    echo Waiting for frontend initialization...
    timeout /t 5 /nobreak >nul
)

echo.
echo [3/3] Checking services...
curl -s --max-time 3 %BACKEND_URL%/ >nul 2>&1
if %errorlevel% == 0 (
    echo   [OK] Backend:   %BACKEND_URL%
) else (
    echo   [FAIL] Backend not responding
)

curl -s --max-time 3 %FRONTEND_URL%/ >nul 2>&1
if %errorlevel% == 0 (
    echo   [OK] Frontend:  %FRONTEND_URL%
) else (
    echo   [FAIL] Frontend not responding
)

echo.
echo ==========================================
echo   Portal started!
echo   Frontend: %FRONTEND_URL%
echo   API Docs: %BACKEND_URL%/docs
echo   Stop:     stop_app.bat
echo ==========================================
echo.
echo Press any key to close this window...
pause >nul
endlocal
