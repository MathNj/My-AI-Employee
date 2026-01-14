@echo off
REM Stop AI Employee - All Watchers and Posters
REM Windows Batch Script

echo ======================================================================
echo Personal AI Employee - Shutdown Script
echo ======================================================================
echo.

cd /d "%~dp0"

echo Stopping all watchers and posters...
echo.

REM Kill orchestrator and all Python processes related to watchers
taskkill /FI "WINDOWTITLE eq AI Employee Orchestrator" /F >nul 2>&1
taskkill /IM python.exe /FI "WINDOWTITLE eq *watcher*" /F >nul 2>&1

echo.
echo ======================================================================
echo AI Employee Stopped
echo ======================================================================
echo.
echo All watcher processes have been terminated.
echo.
echo Press any key to exit...
pause >nul
