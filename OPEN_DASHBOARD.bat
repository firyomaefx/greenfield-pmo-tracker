@echo off
echo =========================================
echo OPENING GREENFIELD FACTORY DASHBOARD
echo =========================================
echo.

REM Try to open with default browser via start command
start "" "%~dp0dashboard.html"

REM If that fails, try with Chrome
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    timeout /t 2 /nobreak >nul
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" "%~dp0dashboard.html"
    goto :opened
)

REM Try with Edge
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    timeout /t 2 /nobreak >nul
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" "%~dp0dashboard.html"
    goto :opened
)

REM Try with Edge (new path)
if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
    timeout /t 2 /nobreak >nul
    start "" "C:\Program Files\Microsoft\Edge\Application\msedge.exe" "%~dp0dashboard.html"
    goto :opened
)

:opened
echo Dashboard opened in your browser!
echo.
echo If nothing appeared:
echo 1. Right-click dashboard.html
echo 2. Open With ^> Microsoft Edge (or Chrome)
echo.
pause
