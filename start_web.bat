@echo off
echo ============================================================
echo   Annual Report Crawler - Web Interface (Simplified)
echo   Developed by Terence WANG  
echo ============================================================
echo.
echo 正在安装依赖包...
pip install -r requirements.txt
echo.
echo 启动Web服务器...
echo 正在自动打开浏览器...
echo 按 Ctrl+C 停止服务器
echo ============================================================
echo.

REM 在后台启动Web服务器
start /B python web_app_simple.py

REM 等待2秒让服务器启动
timeout /t 2 /nobreak >nul

REM 自动打开浏览器
start http://localhost:5000

REM 等待用户按键停止服务器
echo.
echo Web服务器已启动，浏览器将自动打开
echo 按任意键停止服务器...
pause >nul

REM 停止Python进程
taskkill /f /im python.exe >nul 2>&1 