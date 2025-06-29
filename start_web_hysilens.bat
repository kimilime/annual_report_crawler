@echo off
title Annual Report Crawler - Unified Hysilens Version
color 0A

echo ================================================================
echo    Annual Report Crawler - Unified Hysilens Version
echo                   Developed by Terence WANG
echo ================================================================
echo.
echo Unified Hysilens Version Features:
echo    Integrates Requests Hanae Mode and WebDriver Shio Mode
echo    Smart selection of optimal download mode
echo    Unified interface for all download modes
echo    Complete support for A-shares, HK stocks, US stocks
echo.
echo ================================================================
echo.

echo Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python environment not found
    echo Please install Python 3.7 or higher
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python environment check passed

echo.
echo Checking dependencies...

REM Check required packages
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Missing Flask package, installing...
    pip install flask
)

python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo Missing requests package, installing...
    pip install requests
)

python -c "import selenium" >nul 2>&1
if errorlevel 1 (
    echo Missing selenium package, installing...
    pip install selenium
)

python -c "import beautifulsoup4" >nul 2>&1
if errorlevel 1 (
    echo Missing beautifulsoup4 package, installing...
    pip install beautifulsoup4
)

python -c "import lxml" >nul 2>&1
if errorlevel 1 (
    echo Missing lxml package, installing...
    pip install lxml
)

echo Dependencies check completed

echo.
echo Starting Web server...
echo.
echo Please visit in browser: http://localhost:31425
echo Version: v2.0.0 Unified Hysilens Version
echo Supports two modes: Requests Hanae Mode and WebDriver Shio Mode
echo Press Ctrl+C to stop server
echo.
echo ================================================================
echo.

REM Start Flask application and auto open browser
start "" "http://localhost:31425"
python web_app_hysilens.py

echo.
echo Server stopped
pause 