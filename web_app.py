#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Annual Report Crawler Web Interface
基于Flask的Web前端，调用年报下载器脚本
"""

import os
import sys
import json
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'annual_report_crawler_2025'

# 全局变量存储下载状态
download_status = {
    'running': False,
    'progress': 0,
    'current_stock': '',
    'total_stocks': 0,
    'completed_stocks': 0,
    'results': [],
    'logs': []
}

def run_downloader(stock_codes, years, download_dir):
    """在后台运行年报下载器"""
    global download_status
    
    try:
        download_status['running'] = True
        download_status['progress'] = 0
        download_status['results'] = []
        download_status['logs'] = []
        download_status['total_stocks'] = len(stock_codes)
        download_status['completed_stocks'] = 0
        
        # 构建命令
        cmd = [sys.executable, 'annual_report_downloader.py']
        
        # 清理之前可能存在的临时文件
        temp_file = Path('temp_stocks.txt')
        if temp_file.exists():
            temp_file.unlink()
        
        # 添加股票代码参数
        if len(stock_codes) == 1:
            cmd.extend(['-s', stock_codes[0]])
            download_status['logs'].append({
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'message': f'使用单股票模式: -s {stock_codes[0]}'
            })
        else:
            # 创建临时股票文件
            with open(temp_file, 'w', encoding='utf-8', newline='\n') as f:
                for code in stock_codes:
                    f.write(f"{code}\n")
            cmd.extend(['-f', str(temp_file)])
            download_status['logs'].append({
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'message': f'使用文件模式: -f {temp_file} ({len(stock_codes)}个股票)'
            })
        
        # 添加年份参数
        years_str = ','.join(map(str, years))
        cmd.extend(['-y', years_str])
        
        # 添加下载目录参数
        cmd.extend(['-d', download_dir])
        
        # 执行命令
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': f'执行命令: {" ".join(cmd)}'
        })
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            bufsize=1,
            universal_newlines=True,
            cwd=os.getcwd(),  # 确保工作目录正确
            env=os.environ.copy()  # 复制环境变量
        )
        
        # 实时读取输出
        for line in process.stdout:
            line = line.strip()
            if line:
                download_status['logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'message': line
                })
                
                # 解析进度信息
                if '[' in line and ']' in line and '处理股票:' in line:
                    try:
                        parts = line.split(']')[0].split('[')[1].split('/')
                        current = int(parts[0])
                        total = int(parts[1])
                        download_status['completed_stocks'] = current - 1
                        download_status['progress'] = int((current - 1) / total * 100)
                        
                        # 提取当前股票代码
                        if '处理股票:' in line:
                            stock_part = line.split('处理股票:')[1].strip()
                            download_status['current_stock'] = stock_part
                    except:
                        pass
                
                # 解析成功/失败信息
                if '✓ 成功下载:' in line:
                    filename = line.split('✓ 成功下载:')[1].strip()
                    download_status['results'].append({
                        'status': 'success',
                        'filename': filename,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
                elif '✗' in line and ('失败' in line or '错误' in line):
                    download_status['results'].append({
                        'status': 'error',
                        'message': line,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
        
        process.wait()
        
        # 完成
        download_status['progress'] = 100
        download_status['completed_stocks'] = download_status['total_stocks']
        download_status['running'] = False
        
        # 清理临时文件
        temp_file = Path('temp_stocks.txt')
        if temp_file.exists():
            temp_file.unlink()
            
    except Exception as e:
        download_status['running'] = False
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': f'错误: {str(e)}'
        })

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/api/download', methods=['POST'])
def start_download():
    """开始下载"""
    global download_status
    
    if download_status['running']:
        return jsonify({'error': '下载任务正在进行中'}), 400
    
    data = request.json
    stock_codes = data.get('stock_codes', [])
    years = data.get('years', [])
    download_dir = data.get('download_dir', 'annual_reports')
    
    if not stock_codes or not years:
        return jsonify({'error': '请提供股票代码和年份'}), 400
    
    # 在后台线程中运行下载器
    thread = threading.Thread(
        target=run_downloader,
        args=(stock_codes, years, download_dir)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': '下载任务已启动'})

@app.route('/api/status')
def get_status():
    """获取下载状态"""
    return jsonify(download_status)

@app.route('/api/stop')
def stop_download():
    """停止下载（暂不实现具体停止逻辑）"""
    return jsonify({'message': '停止功能暂未实现'})

@app.route('/downloads/<path:filename>')
def download_file(filename):
    """下载文件"""
    download_dir = Path('annual_reports')
    
    # 递归查找文件
    for root, dirs, files in os.walk(download_dir):
        if filename in files:
            return send_from_directory(root, filename, as_attachment=True)
    
    return jsonify({'error': '文件未找到'}), 404

if __name__ == '__main__':
    print("="*60)
    print("  Annual Report Crawler Web Interface")
    print("  Developed by Terence WANG")
    print("="*60)
    print("🌐 启动Web服务器...")
    print("📱 请在浏览器中访问: http://localhost:5000")
    print("🛑 按 Ctrl+C 停止服务器")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 