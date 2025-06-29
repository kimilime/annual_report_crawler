@echo off
echo ================================================================
echo   Annual Report Crawler - Requests "Hanae" Version
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

echo Checking lxml...
python -c "import lxml" >nul 2>&1
if errorlevel 1 (
    echo Installing lxml...
    pip install lxml
) else (
    echo lxml OK
)

echo.
echo All dependencies checked
echo.

echo ================================================================
echo Starting Requests "Hanae" Version Web App...
echo ================================================================
echo Web interface: http://localhost:30820
echo Version: Requests "Hanae" Version
echo Feature: Fast downloads using HTTP requests
echo Note: Suitable for personal computers
echo Note: Uses port 31015 to avoid conflict with Browser version (30331)
echo Press Ctrl+C to stop server
echo ================================================================
echo.

echo Opening browser in 3 seconds...
start /b timeout /t 3 /nobreak >nul && start "" "http://localhost:31015"

python web_app_rq.py

REM 等待用户按键停止服务器
echo.
echo Web服务器已启动，浏览器将自动打开
echo 按任意键停止服务器...
pause >nul

REM 停止Python进程
taskkill /f /im python.exe >nul 2>&1 