@echo off
REM Double-click to prepare Windows (WSL 2) so Docker Desktop can run.
REM Run this ONCE. It asks for administrator rights and then you must reboot.
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup-requirements.ps1"
