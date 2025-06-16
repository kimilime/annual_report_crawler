@echo off
echo ================================================================
echo   Annual Report Crawler - Browser "Otako" Version
echo ================================================================
echo.

echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.7+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo Python OK

echo.
echo Checking dependencies...

echo Checking requests...
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo Installing requests...
    pip install requests
) else (
    echo requests OK
)

echo Checking selenium...
python -c "import selenium" >nul 2>&1
if errorlevel 1 (
    echo Installing selenium...
    pip install selenium
) else (
    echo selenium OK
)

echo Checking webdriver-manager...
python -c "import webdriver_manager" >nul 2>&1
if errorlevel 1 (
    echo Installing webdriver-manager...
    pip install webdriver-manager
) else (
    echo webdriver-manager OK
)

echo Checking flask...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing flask...
    pip install flask
) else (
    echo flask OK
)

echo Checking beautifulsoup4...
python -c "import bs4" >nul 2>&1
if errorlevel 1 (
    echo Installing beautifulsoup4...
    pip install beautifulsoup4
) else (
    echo beautifulsoup4 OK
)

echo.
echo All dependencies checked
echo.

echo ================================================================
echo Starting Browser "Otako" Version Web App...
echo ================================================================
echo Web interface: http://localhost:30331
echo Version: Browser "Otako" Version
echo Feature: Download via browser to avoid file encryption
echo Note: Downloads use headless browser mode
echo Note: Uses port 30331 to avoid conflict with Requests version (31015)
echo Press Ctrl+C to stop server
echo ================================================================
echo.

echo Opening browser in 3 seconds...
start /b timeout /t 3 /nobreak >nul && start "" "http://localhost:30331"

python web_app_bd.py

pause 