@echo off
cd /d "C:\Users\Pedot\OneDrive\Documents"
echo ========================================
echo  GREENFIELD FACTORY DASHBOARD LAUNCHER
echo  Kulim & Batu Kawan Project Tracker
echo ========================================
echo.

REM Detect correct Python with streamlit installed
set "PYTHON_CMD="
for /f "delims=" %%i in ('where python 2^>nul') do (
    "%%i" -c "import streamlit" 2^>nul && (
        set "PYTHON_CMD=%%i"
        goto :found_python
    )
)

REM Fallback to common Python paths
for %%p in (
    "C:\Users\Pedot\AppData\Local\Programs\Python\Python312\python.exe"
    "C:\Users\Pedot\AppData\Local\Python\Python312\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
) do (
    if exist %%p (
        %%p -c "import streamlit" 2^>nul && (
            set "PYTHON_CMD=%%p"
            goto :found_python
        )
    )
)

:not_found
echo ERROR: Could not find Python with streamlit installed.
echo.
echo Please install Python 3.12 and run:
echo   pip install -r requirements.txt
echo.
pause
exit /b 1

:found_python
echo Found Python: %PYTHON_CMD%
echo.
echo Installing required packages (first time only)...
%PYTHON_CMD% -m pip install -r requirements.txt --quiet
echo.
echo Starting dashboard...
echo This will open your browser automatically.
echo.
echo Press Ctrl+C to stop, then close this window.
echo ========================================
%PYTHON_CMD% -m streamlit run dashboard.py
echo.
echo Dashboard stopped. Press any key to close.
pause >nul
