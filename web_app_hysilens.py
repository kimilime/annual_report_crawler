#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Annual Report Crawler - Unified "Hysilens" Version Web App
年报下载器 - 统一"Hysilens"版本Web应用

整合了Requests "Mizuki" Mode和Browser "Otako" Mode，
用户可以在界面上选择使用哪种下载模式。

Developed by Terence WANG
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

from annual_report_downloader_hysilens import (
    AnnualReportDownloaderHysilens, 
    HysilensDownloadMode,
    parse_year_range
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'annual_report_crawler_hysilens_2025'

# 全局变量存储下载状态
download_status = {
    'running': False,
    'progress': 0,
    'current_stock': '',
    'total_stocks': 0,
    'completed_stocks': 0,
    'results': [],
    'logs': [],
    'download_dir': 'annual_reports',
    'mode': HysilensDownloadMode.MIZUKI  # 默认使用Mizuki模式
}

def run_downloader_hysilens(stock_codes, years, download_dir, mode):
    """运行Hysilens下载器"""
    global download_status
    
    try:
        download_status['running'] = True
        download_status['progress'] = 0
        download_status['results'] = []
        download_status['logs'] = []
        download_status['total_stocks'] = len(stock_codes)
        download_status['completed_stocks'] = 0
        download_status['download_dir'] = download_dir
        download_status['mode'] = mode
        
        # 显示版本信息
        mode_name = 'Requests "Mizuki" Mode' if mode == HysilensDownloadMode.MIZUKI else 'Browser "Otako" Mode'
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': '================================================================'
        })
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': 'Annual Report Crawler - Unified "Hysilens" Version'
        })
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': f'Current Mode: {mode_name}'
        })
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': 'Developed by Terence WANG'
        })
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': '================================================================'
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
            'message': f'⚙️ 使用模式: {mode_name}'
        })
        
        # 创建下载器实例
        with AnnualReportDownloaderHysilens(download_dir, mode) as downloader:
            # 处理每个股票
            for i, stock_code in enumerate(stock_codes):
                if not download_status['running']:
                    download_status['logs'].append({
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'message': '❌ 下载已取消'
                    })
                    break
                
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
                            'message': error_display,
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
        mode_name = 'Requests "Mizuki" Mode' if mode == HysilensDownloadMode.MIZUKI else 'Browser "Otako" Mode'
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': '================================================================'
        })
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': 'Annual Report Crawler - Unified "Hysilens" Version'
        })
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': f'Completed with: {mode_name}'
        })
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': 'Developed by Terence WANG'
        })
        download_status['logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': '================================================================'
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
    return render_template('index_hysilens.html')

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
    mode = data.get('mode', HysilensDownloadMode.MIZUKI)
    
    if not stock_codes or not years:
        return jsonify({'error': '请提供股票代码和年份'}), 400
    
    # 验证模式
    if mode not in [HysilensDownloadMode.MIZUKI, HysilensDownloadMode.OTAKO]:
        return jsonify({'error': f'不支持的下载模式: {mode}'}), 400
    
    # 在后台线程中运行下载器
    thread = threading.Thread(
        target=run_downloader_hysilens,
        args=(stock_codes, years, download_dir, mode)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': '下载任务已启动'})

@app.route('/api/status')
def get_status():
    """获取下载状态"""
    return jsonify(download_status)

@app.route('/api/stop', methods=['POST'])
def stop_download():
    """停止下载"""
    download_status['running'] = False
    return jsonify({'message': '下载任务已停止'})

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

@app.route('/readme')
def readme():
    """提供README.html文件访问"""
    try:
        return send_from_directory('.', 'README.html')
    except FileNotFoundError:
        return jsonify({'error': 'README.html文件未找到'}), 404

if __name__ == '__main__':
    print("================================================================")
    print('Annual Report Crawler - Unified "Hysilens" Version')
    print("Developed by Terence WANG")
    print("================================================================")
    print("🌐 启动Web服务器...")
    print("📱 请在浏览器中访问: http://localhost:31346")
    print('🔧 版本: Unified "Hysilens" Version')
    print('💡 支持两种模式: Requests "Mizuki" Mode & Browser "Otako" Mode')
    print("🛑 按 Ctrl+C 停止服务器")
    print("================================================================")
    
    app.run(debug=True, host='0.0.0.0', port=31346) 