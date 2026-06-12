@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

echo ===== Stopping "Chinese Metaphysics Calculator" application =====
echo.

set terminated_processes=0

REM ===== 1. Stopping backend (port 8000) =====
echo Stopping backend (FastAPI on port 8000)...

for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo - Found backend process (PID %%p), terminating...
    taskkill /F /PID %%p > nul 2>&1
    if !errorlevel! equ 0 (
        echo   - Backend process terminated successfully
        set /a terminated_processes+=1
    ) else (
        echo   - Failed to terminate backend process %%p
    )
)

REM ===== 2. Stopping frontend (port 3000) =====
echo.
echo Stopping frontend (React on port 3000)...

for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
    echo - Found frontend process (PID %%p), terminating...
    taskkill /F /PID %%p > nul 2>&1
    if !errorlevel! equ 0 (
        echo   - Frontend process terminated successfully
        set /a terminated_processes+=1
    ) else (
        echo   - Failed to terminate frontend process %%p
    )
)

REM ===== 3. Final information =====
echo.
if !terminated_processes! gtr 0 (
    echo Application successfully stopped! Processes terminated: !terminated_processes!
) else (
    echo Application was not running or was stopped previously.
)
echo.

echo ===== NOTE =====
echo If any application windows remain open,
echo you can close them manually by pressing Ctrl+C in the respective terminal.
echo.

endlocal
