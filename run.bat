@echo off
chcp 65001 >nul

if defined PROMPT (
    for /f "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (
        set "DEL=%%a"
    )
)

REM Task Manager launch script

echo ==========================================
echo   Launching Task Manager
echo ==========================================
echo.

REM Checking for Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    echo Please install Python 3.7 or higher
    echo.
    pause
    exit /b 1
)

REM Showing Python version
echo ✓ Python found:
python --version
echo.

REM Checking for tkcalendar
echo 🔍 Checking dependencies...
python -c "import tkcalendar" >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  tkcalendar not installed
    echo 📦 Installing tkcalendar for calendar widget...
    python -m pip install tkcalendar
    if %errorlevel% equ 0 (
        echo ✓ tkcalendar installed successfully
    ) else (
        echo ⚠️  Failed to install tkcalendar
        echo    Calendar won't work, but the application will start
        echo    Install manually: pip install tkcalendar
    )
) else (
    echo ✓ tkcalendar is installed
)
echo.

REM Changing to application directory
cd /d "%~dp0todo_app"

REM Launching the application
echo 🚀 Launching application...
echo.
python main_gui.py

REM If an error occurred
if %errorlevel% neq 0 (
    echo.
    echo ❌ An error occurred while launching the application
    echo.
    pause
)