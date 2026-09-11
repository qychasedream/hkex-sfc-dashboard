@echo off
title HK Regulatory Dashboard - Refreshing Data
cd /d "%~dp0"
chcp 65001 >nul
where python >nul 2>nul
if %errorlevel%==0 (
    set PY=python
) else (
    set PY=py
)
%PY% -u -X utf8 refresh_all.py
echo.
pause
