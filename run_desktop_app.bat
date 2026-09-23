@echo off
title IT Helpdesk Call Logger - Debug Mode
cd /d "%~dp0"
echo Starting IT Helpdesk Call Logger (Modern UI) in Debug Mode...

:: Wait 2 seconds for Flask to initialize, then launch in Standalone App Mode
start /b cmd /c "ping 127.0.0.1 -n 3 >nul && (if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app=http://127.0.0.1:5000) else (if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (start "" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --app=http://127.0.0.1:5000) else (start msedge --app=http://127.0.0.1:5000)))"

python app.py
pause
