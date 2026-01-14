@echo off
REM Setup Auto-Start for AI Employee on Windows
REM Creates a Windows Task Scheduler task to run watchdog on startup

echo ======================================================================
echo AI Employee - Auto-Start Setup
echo ======================================================================
echo.
echo This will create a Windows Task Scheduler task to automatically
echo start your AI Employee (watchdog) when Windows boots.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

cd /d "%~dp0"

echo.
echo Creating task...
echo.

REM Create the scheduled task
schtasks /Create /TN "AI Employee Watchdog" /TR "python %CD%\watchdog.py" /SC ONSTART /RU "%USERNAME%" /RL HIGHEST /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================================================
    echo [OK] Auto-start configured successfully!
    echo ======================================================================
    echo.
    echo The AI Employee watchdog will now start automatically when you
    echo log into Windows. The watchdog will ensure all watchers stay running.
    echo.
    echo To remove auto-start: schtasks /Delete /TN "AI Employee Watchdog" /F
    echo To run now:           schtasks /Run /TN "AI Employee Watchdog"
    echo.
) else (
    echo.
    echo ======================================================================
    echo [ERROR] Failed to create scheduled task
    echo ======================================================================
    echo.
    echo You may need to run this script as Administrator.
    echo Right-click this file and select "Run as administrator"
    echo.
)

echo Press any key to exit...
pause >nul
