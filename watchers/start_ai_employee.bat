@echo off
REM Start AI Employee - All Watchers and Posters
REM Windows Batch Script

echo ======================================================================
echo Personal AI Employee - Startup Script
echo ======================================================================
echo.

cd /d "%~dp0"

echo Starting orchestrator...
echo.

REM Start orchestrator in background
start "AI Employee Orchestrator" python orchestrator.py

echo.
echo ======================================================================
echo AI Employee Started
echo ======================================================================
echo.
echo The orchestrator is now running in a separate window.
echo It will manage all watchers automatically.
echo.
echo To check status: python orchestrator_cli.py status
echo To stop all:     python orchestrator_cli.py stop
echo.
echo Press any key to continue...
pause >nul
