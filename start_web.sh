#!/bin/bash
echo "============================================================"
echo "  Annual Report Crawler - Web Interface (Simplified)"
echo "  Developed by Terence WANG"
echo "============================================================"
echo ""
echo "正在安装依赖包..."
pip install -r requirements.txt
echo ""
echo "启动Web服务器..."
echo "正在自动打开浏览器..."
echo "按 Ctrl+C 停止服务器"
echo "============================================================"
echo ""

# 在后台启动Web服务器
python web_app_simple.py &
WEB_PID=$!

# 等待2秒让服务器启动
sleep 2

# 自动打开浏览器
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:5000
elif command -v open > /dev/null; then
    open http://localhost:5000
else
    echo "请手动在浏览器中访问: http://localhost:5000"
fi

echo ""
echo "Web服务器已启动，浏览器将自动打开"
echo "按 Ctrl+C 停止服务器..."

# 等待用户中断
trap "kill $WEB_PID; exit" INT
wait $WEB_PID 