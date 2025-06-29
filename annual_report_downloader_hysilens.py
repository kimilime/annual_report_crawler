#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Annual Report Crawler - Unified "Hysilens" Version
年报下载器 - 统一"Hysilens"版本

这个版本整合了Requests "Hanae" Mode和WebDriver "Shio" Mode两种下载方式，
用户可以在界面上选择使用哪种模式。

Developed by Terence WANG
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Optional

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class HysilensDownloadMode:
    """下载模式枚举"""
    HANAE = "hanae"      # Requests模式
    SHIO = "shio"        # WebDriver模式

class AnnualReportDownloaderHysilens:
    """统一的年报下载器，支持两种下载模式"""
    
    def __init__(self, download_dir: str = "annual_reports", mode: str = HysilensDownloadMode.HANAE):
        """
        初始化下载器
        
        Args:
            download_dir: 下载目录
            mode: 下载模式，'hanae' 或 'shio'
        """
        self.download_dir = Path(download_dir)
        self.mode = mode
        self._downloader = None
        
        # 根据模式导入对应的下载器
        if mode == HysilensDownloadMode.HANAE:
            from v1.annual_report_downloader_rq import AnnualReportDownloader
            self._downloader = AnnualReportDownloader(download_dir)
        elif mode == HysilensDownloadMode.SHIO:
            from v1.annual_report_downloader_bd import AnnualReportDownloader
            self._downloader = AnnualReportDownloader(download_dir, headless=True)
        else:
            raise ValueError(f"不支持的下载模式: {mode}")
    
    def __enter__(self):
        """上下文管理器入口"""
        if hasattr(self._downloader, '__enter__'):
            self._downloader.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if hasattr(self._downloader, '__exit__'):
            self._downloader.__exit__(exc_type, exc_val, exc_tb)
    
    def identify_stock_type(self, stock_code: str) -> str:
        """识别股票类型"""
        return self._downloader.identify_stock_type(stock_code)
    
    def download_stock_reports(self, stock_code: str, years: List[int]) -> List[Dict]:
        """
        下载股票年报
        
        Args:
            stock_code: 股票代码
            years: 年份列表
            
        Returns:
            下载结果列表
        """
        return self._downloader.download_stock_reports(stock_code, years)
    
    def get_mode_name(self) -> str:
        """获取当前模式的显示名称"""
        if self.mode == HysilensDownloadMode.HANAE:
            return 'Requests "Hanae" Mode'
        elif self.mode == HysilensDownloadMode.SHIO:
            return 'WebDriver "Shio" Mode'
        else:
            return f'Unknown Mode ({self.mode})'

def parse_year_range(year_str: str) -> List[int]:
    """
    解析年份范围字符串
    
    Args:
        year_str: 年份字符串，支持格式: "2020", "2020-2022", "2020,2021,2022"
        
    Returns:
        年份列表
    """
    years = []
    
    if '-' in year_str:
        # 范围格式: 2020-2022
        start, end = year_str.split('-')
        years = list(range(int(start), int(end) + 1))
    elif ',' in year_str:
        # 列表格式: 2020,2021,2022
        years = [int(y.strip()) for y in year_str.split(',')]
    else:
        # 单个年份: 2020
        years = [int(year_str)]
    
    return years

def load_stock_codes_from_file(filepath: str) -> List[str]:
    """
    从文件加载股票代码列表
    
    Args:
        filepath: 文件路径
        
    Returns:
        股票代码列表
    """
    stock_codes = []
    
    try:
        # 尝试多种编码方式
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
        content = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    content = f.read()
                used_encoding = encoding
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            raise Exception("无法解码文件，尝试了多种编码方式")
        
        for line in content.splitlines():
            code = line.strip()
            if code and not code.startswith('#'):  # 跳过空行和注释
                stock_codes.append(code)
        
        print(f"🔄 从文件{filepath} 加载了{len(stock_codes)} 个股票代码 (编码: {used_encoding})")
        
    except Exception as e:
        print(f"🔄 读取文件 {filepath} 失败: {e}")
        sys.exit(1)
    
    return stock_codes 