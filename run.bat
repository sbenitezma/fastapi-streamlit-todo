@echo off
REM Double-click = start the application in Docker.
REM For other commands:  run.bat stop | logs | test | rebuild | clean | help
setlocal
cd /d "%~dp0"

set "ACTION=%~1"
if "%ACTION%"=="" set "ACTION=start"

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1" %ACTION%

echo.
pause
