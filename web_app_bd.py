#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Annual Report Crawler - Browser Download Web App
年报下载器 - 浏览器下载版本Web应用
"""

import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory

from annual_report_downloader_bd import AnnualReportDownloader, parse_year_range, load_stock_codes_from_file

app = Flask(__name__)

# 全局变量
downloader = None
download_thread = None
download_status = {
    'running': False,
    'progress': 0,
    'total': 0,
    'current_stock': '',
    'total_stocks': 0,
    'completed_stocks': 0,
    'logs': [],
    'results': []
}

def log_message(message):
    """添加日志消息"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = {
        'timestamp': timestamp,
        'message': message
    }
    download_status['logs'].append(log_entry)
    print(f"[{timestamp}] {message}")
    
    # 保持日志数量在合理范围
    if len(download_status['logs']) > 1000:
        download_status['logs'] = download_status['logs'][-800:]

def download_worker(stock_codes, years, download_dir='annual_reports'):
    """后台下载工作线程"""
    global downloader, download_status
    
    try:
        download_status['running'] = True
        download_status['progress'] = 0
        download_status['total'] = len(stock_codes)
        download_status['total_stocks'] = len(stock_codes)
        download_status['completed_stocks'] = 0
        download_status['logs'] = []
        download_status['results'] = []
        
        log_message("🚀 开始批量下载年报...")
        log_message(f"📊 共 {len(stock_codes)} 只股票，{len(years)} 个年份")
        log_message(f"📁 下载目录: {download_dir}")
        log_message("🌐 使用浏览器下载模式，避免文件加密")
        
        # 创建下载器实例（使用无头模式）
        downloader = AnnualReportDownloader(download_dir, headless=True)
        
        for i, stock_code in enumerate(stock_codes, 1):
            if not download_status['running']:
                log_message("❌ 下载已取消")
                break
                
            download_status['current_stock'] = stock_code
            download_status['progress'] = int(i / len(stock_codes) * 100)
            download_status['completed_stocks'] = i - 1
            
            log_message(f"📈 [{i}/{len(stock_codes)}] 处理股票: {stock_code}")
            
            try:
                results = downloader.download_stock_reports(stock_code, years)
                
                # 转换结果格式
                for result in results:
                    if result['status'] == 'success':
                        download_status['results'].append({
                            'status': 'success',
                            'filename': result.get('filename', ''),
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        })
                    else:
                        download_status['results'].append({
                            'status': 'error',
                            'message': result.get('error', '未知错误'),
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        })
                
                # 统计结果
                success_count = sum(1 for r in results if r['status'] == 'success')
                log_message(f"✅ {stock_code} 完成: {success_count}/{len(results)} 成功")
                
            except Exception as e:
                log_message(f"❌ {stock_code} 处理失败: {str(e)}")
                download_status['results'].append({
                    'status': 'error',
                    'message': f"{stock_code} 处理失败: {str(e)}",
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
                
            time.sleep(1)  # 避免请求过快
        
        log_message("🎉 批量下载完成!")
        
        # 统计总结果
        total_success = sum(1 for r in download_status['results'] if r['status'] == 'success')
        total_failed = len(download_status['results']) - total_success
        log_message(f"📊 总计: 成功 {total_success}, 失败 {total_failed}")
        
        # 更新最终状态
        download_status['progress'] = 100
        download_status['completed_stocks'] = len(stock_codes)
        
    except Exception as e:
        log_message(f"❌ 下载过程中发生错误: {str(e)}")
    finally:
        download_status['running'] = False
        download_status['current_stock'] = ''
        
        # 清理资源
        if downloader:
            try:
                if hasattr(downloader, 'driver') and downloader.driver:
                    downloader.driver.quit()
            except:
                pass

@app.route('/')
def index():
    """主页"""
    return render_template('index_bd.html')

@app.route('/start_download', methods=['POST'])
def start_download():
    """开始下载"""
    global download_thread
    
    if download_status['running']:
        return jsonify({'success': False, 'message': '下载任务已在运行中'})
    
    try:
        data = request.json
        stock_input = data.get('stocks', data.get('stock_codes', '')).strip()
        year_input = data.get('years', '').strip()
        download_dir = data.get('download_dir', 'annual_reports').strip()
        
        if not stock_input or not year_input:
            return jsonify({'success': False, 'message': '请输入股票代码和年份'})
        
        # 解析股票代码
        stock_codes = []
        if stock_input.endswith('.txt'):
            # 从文件读取
            try:
                stock_codes = load_stock_codes_from_file(stock_input)
            except Exception as e:
                return jsonify({'success': False, 'message': f'读取股票代码文件失败: {str(e)}'})
        else:
            # 直接解析
            stock_codes = [code.strip() for code in stock_input.replace(',', ' ').replace('，', ' ').split() if code.strip()]
        
        if not stock_codes:
            return jsonify({'success': False, 'message': '未找到有效的股票代码'})
        
        # 解析年份
        try:
            years = parse_year_range(year_input)
        except Exception as e:
            return jsonify({'success': False, 'message': f'年份格式错误: {str(e)}'})
        
        if not years:
            return jsonify({'success': False, 'message': '未找到有效的年份'})
        
        # 启动下载线程
        download_thread = threading.Thread(target=download_worker, args=(stock_codes, years, download_dir))
        download_thread.daemon = True
        download_thread.start()
        
        return jsonify({'success': True, 'message': '下载任务已启动'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'启动下载失败: {str(e)}'})

@app.route('/stop_download', methods=['POST'])
def stop_download():
    """停止下载"""
    download_status['running'] = False
    return jsonify({'success': True, 'message': '下载任务已停止'})

@app.route('/status')
def get_status():
    """获取下载状态"""
    return jsonify(download_status)

@app.route('/get_status')
def get_status_alias():
    """获取下载状态 - 兼容路由"""
    return jsonify(download_status)

@app.route('/files')
def list_files():
    """列出下载的文件"""
    try:
        # 尝试获取当前下载目录，如果没有就使用默认目录
        current_download_dir = getattr(downloader, 'download_dir', None)
        if current_download_dir:
            download_dir = current_download_dir
        else:
            download_dir = Path("annual_reports")
            
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
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # 按修改时间排序
        files.sort(key=lambda x: x['modified'], reverse=True)
        return jsonify({'files': files})
        
    except Exception as e:
        return jsonify({'files': [], 'error': str(e)})

@app.route('/list_files')
def list_files_alias():
    """列出下载的文件 - 兼容路由"""
    return list_files()

@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    """清空日志"""
    download_status['logs'] = []
    return jsonify({'success': True})

@app.route('/download_file/<path:filepath>')
def download_file(filepath):
    """下载文件"""
    try:
        # 尝试获取当前下载目录，如果没有就使用默认目录
        current_download_dir = getattr(downloader, 'download_dir', None)
        if current_download_dir:
            download_dir = current_download_dir
        else:
            download_dir = Path("annual_reports")
        return send_from_directory(download_dir, filepath, as_attachment=True)
    except Exception as e:
        return f"文件下载失败: {str(e)}", 404

@app.route('/readme')
def readme():
    """提供README.html文件访问"""
    try:
        return send_from_directory('.', 'README.html')
    except FileNotFoundError:
        return jsonify({'error': 'README.html文件未找到'}), 404

@app.route('/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': 'browser_download'
    })

if __name__ == '__main__':
    print("=" * 60)
    print("  年报下载器 - 浏览器下载版本 Web应用")
    print("  Annual Report Crawler - Browser Download Web App")
    print("=" * 60)
    print("🌐 Web界面: http://localhost:5000")
    print("🔧 版本: 浏览器下载版 (Browser Download)")
    print("🚀 特性: 通过浏览器下载，避免文件加密")
    print("-" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 