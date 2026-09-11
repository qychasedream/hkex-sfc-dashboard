@echo off
title HK Regulatory Dashboard
cd /d "%~dp0"
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul
if errorlevel 1 (
    start "" /min python -m http.server 8000 --directory docs
    timeout /t 2 /nobreak >nul
)
start "" "http://localhost:8000/regulatory/"
exit
