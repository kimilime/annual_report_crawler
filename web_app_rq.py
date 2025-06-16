#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Annual Report Crawler Web Interface (Simplified)
基于Flask的Web前端，直接调用年报下载器函数
"""

import os
import sys
import json
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
    'logs': [],
    'download_dir': 'annual_reports'  # 存储当前使用的下载目录
}

def run_downloader_direct(stock_codes, years, download_dir):
    """直接调用年报下载器，避免subprocess编码问题"""
    global download_status
    
    try:
        download_status['running'] = True
        download_status['progress'] = 0
        download_status['results'] = []
        download_status['logs'] = []
        download_status['total_stocks'] = len(stock_codes)
        download_status['completed_stocks'] = 0
        download_status['download_dir'] = download_dir  # 保存当前下载目录
        
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': '='*60
        })
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': '  Annual Report Crawler - Developed by Terence WANG'
        })
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': '='*60
        })
        
        # 直接导入并调用下载器
        from annual_report_downloader_rq import AnnualReportDownloader
        
        # 显示版本信息
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': '============================================================'
        })
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': 'Annual Report Crawler - Requests "Mizuki" Version'
        })
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': 'Developed by Terence WANG'
        })
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': '============================================================'
        })
        
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': f'📁 下载目录: {Path(download_dir).absolute()}'
        })
        
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': f'📅 目标年份: {years}'
        })
        
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': f'🚀 开始批量下载，共{len(stock_codes)} 只股票，{len(years)} 个年份'
        })
        
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': '='*60
        })
        
        # 创建下载器实例
        with AnnualReportDownloader(download_dir) as downloader:
            # 处理每个股票
            for i, stock_code in enumerate(stock_codes):
                download_status['current_stock'] = stock_code
                download_status['completed_stocks'] = i
                download_status['progress'] = int(i / len(stock_codes) * 100)
                
                download_status['logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'message': f'[{i+1}/{len(stock_codes)}] 处理股票: {stock_code}'
                })
                
                # 识别股票类型
                stock_type = downloader.identify_stock_type(stock_code)
                download_status['logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'message': f'📊 处理股票: {stock_code} ({stock_type})'
                })
                
                # 下载股票年报
                results = downloader.download_stock_reports(stock_code, years)
                
                # 处理结果
                for result in results:
                    if result['status'] == 'success':
                        filename = result.get('filename', '')
                        download_status['logs'].append({
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'message': f'    ✓ 成功下载: {filename}'
                        })
                        download_status['results'].append({
                            'status': 'success',
                            'filename': filename,
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        })
                    else:
                        error_msg = result.get('error', '未知错误')
                        year = result.get('year', '')
                        company_name = result.get('company_name', '')
                        
                        # 格式化错误信息：股票代码 公司名称 年份: 错误信息
                        if company_name:
                            error_display = f"{stock_code} {company_name} {year}: {error_msg}"
                        else:
                            error_display = f"{stock_code} {year}: {error_msg}"
                        
                        download_status['logs'].append({
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'message': f'    ✗ {error_display}'
                        })
                        download_status['results'].append({
                            'status': 'error',
                            'message': f'    ✗ {error_display}',
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        })
        
        # 完成
        download_status['progress'] = 100
        download_status['completed_stocks'] = len(stock_codes)
        download_status['running'] = False
        
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': '📈 下载完成！'
        })
        
        # 显示结束版本信息
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': '============================================================'
        })
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': 'Annual Report Crawler - Requests "Mizuki" Version'
        })
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': 'Developed by Terence WANG'
        })
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': '============================================================'
        })
            
    except Exception as e:
        download_status['running'] = False
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': f'错误: {str(e)}'
        })
        import traceback
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': f'详细错误: {traceback.format_exc()}'
        })

@app.route('/')
def index():
    """首页"""
    return render_template('index_rq.html')

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
        target=run_downloader_direct,
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
    # 使用当前配置的下载目录
    download_dir = Path(download_status.get('download_dir', 'annual_reports'))
    
    # 递归查找文件
    for root, dirs, files in os.walk(download_dir):
        if filename in files:
            return send_from_directory(root, filename, as_attachment=True)
    
    return jsonify({'error': '文件未找到'}), 404

@app.route('/list_files')
def list_files():
    """列出下载的文件"""
    try:
        # 获取当前下载目录
        download_dir = Path(download_status.get('download_dir', 'annual_reports'))
        
        if not download_dir.exists():
            return jsonify({'files': []})
        
        files = []
        for file_path in download_dir.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(download_dir)
                files.append({
                    'name': file_path.name,
                    'path': str(relative_path),
                    'size': file_path.stat().st_size,
                    'modified': file_path.stat().st_mtime * 1000  # 转换为毫秒时间戳
                })
        
        # 按修改时间排序
        files.sort(key=lambda x: x['modified'], reverse=True)
        return jsonify({'files': files})
        
    except Exception as e:
        return jsonify({'files': [], 'error': str(e)})

@app.route('/readme')
def readme():
    """提供README.html文件访问"""
    try:
        return send_from_directory('.', 'README.html')
    except FileNotFoundError:
        return jsonify({'error': 'README.html文件未找到'}), 404

if __name__ == '__main__':
    print("="*60)
    print('  Annual Report Crawler - Requests "Mizuki" Version Web App')
    print("  Developed by Terence WANG")
    print("="*60)
    print("🌐 启动Web服务器...")
    print("📱 请在浏览器中访问: http://localhost:31015")
    print('🔧 版本: Requests "Mizuki" Version')
    print('💡 注意: Requests "Mizuki" Version使用端口31015，避免与Browser版本(30331)冲突')
    print("🛑 按 Ctrl+C 停止服务器")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=31015) 