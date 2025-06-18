#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

巨潮网年报下载器

支持A股主板、科创板、创业板和港股年报下载

"""



import os

import sys

import re

import json

import time

import requests

import argparse

from pathlib import Path

from typing import List, Dict, Tuple, Optional

from selenium import webdriver

from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.chrome.service import Service

from selenium.common.exceptions import TimeoutException, NoSuchElementException

from webdriver_manager.chrome import ChromeDriverManager

import urllib.parse

from selenium.webdriver.common.keys import Keys





class StockType:

    """股票类型枚举"""

    A_MAIN = "A股主板"

    A_STAR = "A股科创板" 

    A_GEM = "A股创业板"

    HK = "港股"

    US = "美股"

    UNKNOWN = "未知"





def enhanced_year_matching(title: str, target_years: List[int]) -> Optional[int]:
    """
    增强的年份匹配函数，支持数字和中文年份格式
    
    Args:
        title: 标题文本
        target_years: 目标年份列表
        
    Returns:
        匹配到的年份，如果未匹配返回None
    """
    # 先检查是否是应该排除的报告类型
    if ('半年' in title or '半年度' in title or '中期' in title or 
        '季度' in title or '季报' in title):
        return None
    
    # 中文数字映射（包含大写和小写）
    chinese_digits = {
        '0': ['〇', '零', 'O', 'o'],
        '1': ['一', '壹'],
        '2': ['二', '贰', '貳'], 
        '3': ['三', '叁', '參'],
        '4': ['四', '肆'],
        '5': ['五', '伍'],
        '6': ['六', '陆', '陸'],
        '7': ['七', '柒'],
        '8': ['八', '捌'],
        '9': ['九', '玖']
    }
    
    for year in target_years:
        year_str = str(year)
        
        # 检查数字格式
        if year_str in title:
            return year
        
        # 检查中文格式 - 生成所有可能的中文年份组合
        def generate_chinese_patterns(digits, pos=0, current=""):
            if pos == len(digits):
                if current in title:
                    return True
                return False
            
            digit = digits[pos]
            for chinese_char in chinese_digits[digit]:
                if generate_chinese_patterns(digits, pos + 1, current + chinese_char):
                    return True
            return False
        
        if generate_chinese_patterns(year_str):
            return year
    
    return None


def enhanced_year_matching_with_date(title: str, target_years: List[int], pub_date: str = None) -> Optional[int]:
    """
    带日期辅助的增强年份匹配函数
    
    Args:
        title: 标题文本
        target_years: 目标年份列表
        pub_date: 发布日期 (格式如 "2025-04-23")
        
    Returns:
        匹配到的年份，如果未匹配返回None
    """
    # 先尝试从标题中匹配年份
    matched_year = enhanced_year_matching(title, target_years)
    if matched_year:
        return matched_year
    
    # 如果标题中没有年份，但标题确实是年报，尝试从发布日期推断
    if pub_date and ('年报' in title or '年度报告' in title):
        try:
            # 处理发布日期（可能是字符串或整数时间戳）
            if isinstance(pub_date, str) and '-' in pub_date:
                # 字符串格式：YYYY-MM-DD
                pub_year = int(pub_date.split('-')[0])
            elif isinstance(pub_date, (int, float)):
                # 时间戳格式，转换为年份
                import datetime
                pub_year = datetime.datetime.fromtimestamp(pub_date / 1000).year
            else:
                # 其他格式，无法处理
                return None
            
            # 年报通常在次年发布，所以年报年份 = 发布年份 - 1
            report_year = pub_year - 1
            
            # 检查推断的年份是否在目标年份中
            if report_year in target_years:
                print(f"    💡 通过日期推断年份: {pub_date} -> {report_year}年年报")
                return report_year
                
        except (ValueError, IndexError, TypeError):
            pass
    
    return None


class AnnualReportDownloader:

    """年报下载器主类"""

    

    def __init__(self, download_dir: str = "annual_reports", headless: bool = True):

        """

        初始化下载器

        

        Args:

            download_dir: 下载目录
            headless: 是否使用无头模式

        """

        self.download_dir = Path(download_dir)

        self.download_dir.mkdir(exist_ok=True)
        self.headless = headless

        

        # 统计信息

        self.stats = {

            "total": 0,

            "success": 0,

            "failed": 0,

            "details": []

        }

        

        # 初始化selenium driver（延迟初始化）

        self.driver = None

        

    def __enter__(self):

        return self

    

    def __del__(self):

        if self.driver:

            try:

                self.driver.quit()

            except:

                pass

    

    def __exit__(self, exc_type, exc_val, exc_tb):

        if self.driver:

            try:

                self.driver.quit()

            except:

                pass

    

    def init_selenium_driver(self):

        """初始化Selenium WebDriver"""

        if self.driver is None:

            # Chrome选项配置

            chrome_options = Options()
            
            # 根据设置决定是否使用无头模式
            if self.headless:
                chrome_options.add_argument('--headless')  # 无头模式

            chrome_options.add_argument('--no-sandbox')

            chrome_options.add_argument('--disable-dev-shm-usage')

            chrome_options.add_argument('--disable-gpu')  # 禁用GPU加速

            chrome_options.add_argument('--disable-web-security')  # 禁用web安全

            chrome_options.add_argument('--disable-features=VizDisplayCompositor')  # 禁用显示合成

            chrome_options.add_argument('--disable-extensions')  # 禁用扩展

            chrome_options.add_argument('--disable-plugins')  # 禁用插件

            chrome_options.add_argument('--disable-images')  # 禁用图片加载
            # 解决WebGL警告
            chrome_options.add_argument('--disable-webgl')
            chrome_options.add_argument('--disable-webgl2')
            chrome_options.add_argument('--disable-3d-apis')
            chrome_options.add_argument('--disable-accelerated-2d-canvas')
            chrome_options.add_argument('--disable-accelerated-jpeg-decoding')
            chrome_options.add_argument('--disable-accelerated-mjpeg-decode')
            chrome_options.add_argument('--disable-accelerated-video-decode')
            chrome_options.add_argument('--disable-gpu-sandbox')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-background-timer-throttling')
            chrome_options.add_argument('--disable-renderer-backgrounding')
            chrome_options.add_argument('--disable-features=TranslateUI')
            chrome_options.add_argument('--disable-ipc-flooding-protection')

            chrome_options.add_argument('--log-level=3')  # 只显示致命错误

            chrome_options.add_argument('--silent')  # 静默模式

            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # 排除日志开关

            chrome_options.add_experimental_option('useAutomationExtension', False)  # 禁用自动化扩展

            chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 禁用自动化控制特征

            

            # 设置下载路径和浏览器下载配置

            prefs = {

                "download.default_directory": str(self.download_dir.absolute()),

                "download.prompt_for_download": False,

                "download.directory_upgrade": True,

                "safebrowsing.enabled": True,

                "profile.default_content_settings.popups": 0,

                "profile.default_content_setting_values.automatic_downloads": 1,

                # 允许下载多个文件

                "profile.default_content_setting_values.notifications": 2,

                # PDF处理设置

                "plugins.always_open_pdf_externally": True,

            }

            chrome_options.add_experimental_option("prefs", prefs)

            

            # 尝试多种方式初始化ChromeDriver

            try:

                # 方法1: 使用当前目录或上级目录下的ChromeDriver

                local_chromedriver_paths = [

                    Path("./chromedriver.exe"),          # 当前目录

                    Path("../chromedriver.exe"),         # 上级目录

                ]

                

                local_chromedriver = None

                for path in local_chromedriver_paths:

                    if path.exists():

                        local_chromedriver = path

                        break

                

                if local_chromedriver:

                    print(f"  🔧 使用ChromeDriver: {local_chromedriver}")

                    service = Service(str(local_chromedriver.absolute()))

                    self.driver = webdriver.Chrome(service=service, options=chrome_options)

                    print("🔧 Selenium WebDriver 初始化成功(本地文件)")

                else:

                    raise Exception("本地ChromeDriver不存在")

                

            except Exception as e1:

                print(f"  本地ChromeDriver失败: {e1}")

                try:

                    # 方法2: 使用webdriver-manager自动管理ChromeDriver

                    print("  🔧 尝试自动下载/更新ChromeDriver...")

                    service = Service(ChromeDriverManager().install())

                    self.driver = webdriver.Chrome(service=service, options=chrome_options)

                    print("🔧 Selenium WebDriver 初始化成功(自动管理)")

                    

                except Exception as e2:

                    print(f"  自动管理ChromeDriver失败: {e2}")

                    try:

                        # 方法3: 使用系统PATH中的ChromeDriver

                        print("  🔧 尝试使用系统PATH中的ChromeDriver...")

                        self.driver = webdriver.Chrome(options=chrome_options)

                        print("🔧 Selenium WebDriver 初始化成功(系统PATH)")

                        

                    except Exception as e3:

                        print(f"所有ChromeDriver初始化方式都失败:")

                        print(f"  本地文件: {e1}")

                        print(f"  自动管理: {e2}")

                        print(f"  系统PATH: {e3}")

                        print("\n解决方案:")

                        print("1. 确保已安装Chrome浏览器")

                        print("2. 确保chromedriver.exe在当前目录或系统PATH")

                        print("3. 检查ChromeDriver版本是否与Chrome版本匹配")

                        print("ChromeDriver下载地址: https://chromedriver.chromium.org/")

                        return False

        return True

    def wait_for_download_complete(self, timeout=60):
        """等待下载完成"""
        print("    ⏳ 等待下载完成...")
        
        start_time = time.time()
        last_file_size = 0
        stable_count = 0
        
        while time.time() - start_time < timeout:
            # 检查下载目录中是否有.crdownload文件（Chrome下载中的临时文件）
            temp_files = list(self.download_dir.glob("*.crdownload"))
            if temp_files:
                # 还有临时文件，继续等待
                time.sleep(1)
                continue
            
            # 没有临时文件，检查最新文件是否稳定
            try:
                all_files = [f for f in self.download_dir.iterdir() if f.is_file()]
                if all_files:
                    latest_file = max(all_files, key=lambda f: f.stat().st_mtime)
                    current_size = latest_file.stat().st_size
                    
                    # 检查文件大小是否稳定（连续3次检查大小不变）
                    if current_size == last_file_size and current_size > 0:
                        stable_count += 1
                        if stable_count >= 3:
                            print("    ✅ 下载完成（文件大小稳定）")
                            return True
                    else:
                        stable_count = 0
                        last_file_size = current_size
                else:
                    stable_count = 0
            except Exception as e:
                print(f"    ⚠️ 检查文件状态时出错: {e}")
                stable_count = 0
            
            time.sleep(1)
        
        print("    ⚠️ 下载超时")
        return False

    def browser_download_file(self, url: str, expected_filename: str = None) -> bool:
        """
        通过浏览器下载文件
        
        Args:
            url: 下载URL
            expected_filename: 期望的文件名（用于验证）
            
        Returns:
            是否下载成功
        """
        try:
            if not self.driver:
                self.init_selenium_driver()
            
            print(f"    🌐 浏览器下载: {url}")
            
            # 记录下载前的文件列表
            files_before = set(f.name for f in self.download_dir.iterdir() if f.is_file())
            
            # 导航到下载URL
            self.driver.get(url)
            
            # 等待下载完成
            if self.wait_for_download_complete():
                # 检查新下载的文件
                files_after = set(f.name for f in self.download_dir.iterdir() if f.is_file())
                new_files = files_after - files_before
                
                if new_files:
                    downloaded_file = list(new_files)[0]
                    print(f"    ✅ 下载成功: {downloaded_file}")
                    
                    # 🔧 修复：再次确认文件不是.crdownload文件
                    if downloaded_file.endswith('.crdownload'):
                        print(f"    ❌ 错误：文件仍为临时状态: {downloaded_file}")
                        return False
                    
                    return True
                else:
                    print("    ❌ 未检测到新文件")
                    return False
            else:
                return False
                
        except Exception as e:
            print(f"    ❌ 浏览器下载失败: {e}")
            return False

    

    def identify_stock_type(self, stock_code: str) -> str:
        """
        识别股票类型
        
        Args:
            stock_code: 股票代码
            
        Returns:
            股票类型
        """
        stock_code = stock_code.strip().upper()
        
        # 港股：5位数字或带HK前缀
        if re.match(r'^\d{5}$', stock_code) or stock_code.startswith('HK'):
            return StockType.HK
        
        # A股：6位数
        if re.match(r'^\d{6}$', stock_code):
            # 科创板：688开头
            if stock_code.startswith('688'):
                return StockType.A_STAR
            # 创业板：300开头 
            elif stock_code.startswith('300'):
                return StockType.A_GEM
            # 主板：其他6位数
            else:
                return StockType.A_MAIN
        
        # 美股：字母开头的股票代码（1-5个字符）
        if re.match(r'^[A-Z]{1,5}$', stock_code):
            return StockType.US
        
        return StockType.UNKNOWN

    

    def get_orgid_dict_szse(self) -> Dict[str, str]:

        """

        获取深圳交易所所有股票的orgId字典

        

        Returns:

            股票代码到orgId的映射字典

        """

        try:

            print("    🔄 正在获取深圳交易所股票orgId映射表..")

            response = requests.get("http://www.cninfo.com.cn/new/data/szse_stock.json", timeout=15)

            response.raise_for_status()

            

            org_dict = {}

            stock_list = response.json().get("stockList", [])

            

            for stock_info in stock_list:

                code = stock_info.get("code")

                org_id = stock_info.get("orgId")

                if code and org_id:

                    org_dict[code] = org_id

            

            print(f"    🔄 获取了{len(org_dict)} 个深圳交易所股票的orgId")

            return org_dict

            

        except Exception as e:

            print(f"    ✗ 获取深圳交易所orgId映射表失败: {e}")

            return {}

    

    def get_orgid_dict_sse(self) -> Dict[str, str]:

        """

        获取上海交易所所有股票的orgId字典

        

        Returns:

            股票代码到orgId的映射字典

        """

        try:

            print("    🔄 正在获取上海交易所股票orgId映射表..")

            response = requests.get("http://www.cninfo.com.cn/new/data/sse_stock.json", timeout=15)

            response.raise_for_status()

            

            org_dict = {}

            stock_list = response.json().get("stockList", [])

            

            for stock_info in stock_list:

                code = stock_info.get("code")

                org_id = stock_info.get("orgId")

                if code and org_id:

                    org_dict[code] = org_id

            

            print(f"    🔄 获取了{len(org_dict)} 个上海交易所股票的orgId")

            return org_dict

            

        except Exception as e:

            print(f"    ✗ 获取上海交易所orgId映射表失败: {e}")

            return {}

    

    def get_all_orgid_dict(self) -> Dict[str, str]:

        """

        获取所有交易所股票的orgId字典

        注意：深圳交易所的数据实际包含了所有股票（包括上海交易所）

        

        Returns:

            股票代码到orgId的映射字典

        """

        # 深圳交易所的数据包含了所有股票

        all_dict = self.get_orgid_dict_szse()

        

        print(f"    📊 总计获取了{len(all_dict)} 个股票的orgId")

        return all_dict

    

    def get_orgid_for_stock(self, stock_code: str) -> Optional[str]:

        """

        获取股票的orgId

        

        Args:

            stock_code: 股票代码

            

        Returns:

            orgId字符串，如果获取失败返回None

        """

        try:

            # 首先尝试从映射表获取orgId

            all_orgid_dict = self.get_all_orgid_dict()

            if stock_code in all_orgid_dict:

                org_id = all_orgid_dict[stock_code]

                print(f"    🔄 从映射表获取了{stock_code} 的orgId: {org_id}")

                return org_id

            

            # 如果映射表中没有，尝试通过搜索API获取

            print(f"    🔍 映射表中未找到{stock_code}，尝试搜索获取orgId...")

            

            # 使用股票代码搜索（通过searchkey）

            api_url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"

            headers = {

                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

            }

            

            params = {

                "stock": "",

                "tabName": "fulltext",

                "pageSize": 50,

                "pageNum": 1,

                "column": "",

                "category": "",

                "plate": "",

                "seDate": "2020-01-01~2025-12-31",

                "searchkey": stock_code,

                "secid": "",

                "sortName": "pubdate",

                "sortType": "desc",

                "isHLtitle": "true"

            }

            

            response = requests.post(api_url, headers=headers, data=params, timeout=15)

            if response.status_code == 200:

                result = response.json()

                announcements = result.get('announcements', [])

                

                if announcements:

                    # 查找匹配的股票代码

                    for ann in announcements:

                        sec_code = ann.get('secCode', '')

                        org_id = ann.get('orgId', '')

                        

                        if sec_code == stock_code and org_id:

                            print(f"    🔄 通过搜索获取了{stock_code} 的orgId: {org_id}")

                            return org_id

            

            print(f"    ✗ 无法获取{stock_code} 的orgId")

            return None

            

        except Exception as e:

            print(f"    ✗ 获取 {stock_code} orgId 时出错: {e}")

            return None

    

    def download_a_stock_main_reports_with_pagination(self, stock_code: str, years: List[int]) -> List[Dict]:
        """
        下载A股主板年报（使用API + 翻页支持）
        
        Args:
            stock_code: 股票代码
            years: 年份列表
            
        Returns:
            下载结果列表
        """
        results = []
        
        try:
            print(f"  📥 使用巨潮API查找 {stock_code} 年报（支持翻页）...")
            
            api_url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # 确定板块和orgId
            if stock_code.startswith('60') or stock_code.startswith('688'):
                plate = 'sse'  # 上海交易所：主板(60xxxx) + 科创板(688xxx)
            else:
                plate = 'szse'  # 深圳交易所：主板(000xxx) + 创业板(300xxx)
            category = 'category_ndbg_szsh;'
            
            # 从映射表获取真实的orgId
            real_org_id = self.get_orgid_for_stock(stock_code)
            if not real_org_id:
                print(f"  ✗ 无法获取{stock_code} 的orgId")
                for year in years:
                    results.append({
                        'stock_code': stock_code,
                        'year': year,
                        'status': 'no_orgid',
                        'error': '无法获取orgId'
                    })
                return results
            
            # 设置搜索日期范围（年报通常在次年-4月发布）
            min_year = min(years)
            max_year = max(years)
            search_start_date = f"{min_year}-01-01"
            search_end_date = f"{max_year + 1}-04-30"
            
            params = {
                "stock": f"{stock_code},{real_org_id}",
                "tabName": "fulltext",
                "pageSize": 50,
                "pageNum": 1,
                "column": plate,
                "category": category,
                "plate": plate,
                "seDate": f"{search_start_date}~{search_end_date}",
                "searchkey": "",
                "secid": "",
                "sortName": "pubdate",
                "sortType": "desc",
                "isHLtitle": "true"
            }
            
            # 支持翻页搜索，最多搜索前3页
            all_announcements = []
            for page_num in range(1, 4):
                params["pageNum"] = page_num
                print(f"    🔍 搜索第{page_num}页...")
                
                response = requests.post(api_url, headers=headers, data=params, timeout=20)
                response.raise_for_status()
                data = response.json()
                
                announcements = data.get('announcements', [])
                if announcements:
                    all_announcements.extend(announcements)
                    print(f"    第{page_num}页找到{len(announcements)}条公告")
                else:
                    print(f"    第{page_num}页无结果，停止翻页")
                    break
            
            if not all_announcements:
                print(f"  ✗ 未找到{stock_code} 的相关报告")
                for year in years:
                    results.append({
                        'stock_code': stock_code,
                        'year': year,
                        'status': 'not_found',
                        'error': '未找到相关报告'
                    })
                return results
            
            print(f"  📊 总共找到{len(all_announcements)}条公告")
            
            # 按年份查找年报
            for year in years:
                print(f"    🔍 查找 {year} 年年报..")
                found = False
                
                for ann in all_announcements:
                    title = ann.get('announcementTitle', '')
                    
                    # 跳过摘要、补充、更正等非正式年报
                    if any(keyword in title for keyword in ["摘要", "取消", "补充", "更正", "第一季度", "半年", "第三季度"]):
                        continue
                    
                    # 使用增强的年份匹配检查是否为指定年份的年度报告
                    matched_year = enhanced_year_matching(title, [year])
                    if matched_year and "年度报告" in title:
                        print(f"    🔄 找到年报: {title}")
                        
                        # 下载PDF
                        adj_url = ann.get('adjunctUrl', '')
                        if adj_url:
                            pdf_url = f"http://static.cninfo.com.cn/{adj_url}"
                            stock_name = ann.get('secName', stock_code)
                            filename = f"{stock_code}_{stock_name}_{year}年报.pdf"
                            
                            filepath = self.download_dir / filename
                            if self.download_pdf(pdf_url, str(filepath)):
                                print(f"    ✓ 成功下载: {filename}")
                                results.append({
                                    'stock_code': stock_code,
                                    'year': year,
                                    'status': 'success',
                                    'filename': filename,
                                    'title': title
                                })
                                found = True
                                break
                            else:
                                results.append({
                                    'stock_code': stock_code,
                                    'year': year,
                                    'status': 'download_failed',
                                    'error': '下载PDF失败'
                                })
                                found = True
                                break
                
                if not found:
                    print(f"    ✗ 未找到{stock_code} {year}年年报")
                    results.append({
                        'stock_code': stock_code,
                        'year': year,
                        'status': 'not_found',
                        'error': '未找到年报'
                    })
                
                time.sleep(0.5)  # 短暂间隔
                
        except Exception as e:
            print(f"  ✗ A股主板API处理失败: {e}")
            for year in years:
                results.append({
                    'stock_code': stock_code,
                    'year': year,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results

    def download_a_stock_main_reports(self, stock_code: str, years: List[int]) -> List[Dict]:

        """

        下载A股主板年报（使用API）

        

        Args:

            stock_code: 股票代码

            years: 年份列表

            

        Returns:

            下载结果列表

        """

        results = []

        

        try:

            print(f"  📥 使用巨潮API查找 {stock_code} 年报...")

            

            api_url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"

            headers = {

                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

            }

            

            # 确定板块和orgId

            if stock_code.startswith('60') or stock_code.startswith('688'):

                plate = 'sse'  # 上海交易所：主板(60xxxx) + 科创板(688xxx)

            else:

                plate = 'szse'  # 深圳交易所：主板(000xxx) + 创业板(300xxx)

            category = 'category_ndbg_szsh;'

            

            # 从映射表获取真实的orgId

            real_org_id = self.get_orgid_for_stock(stock_code)

            if not real_org_id:

                print(f"  ✗ 无法获取{stock_code} 的orgId")

                for year in years:

                    results.append({

                        'stock_code': stock_code,

                        'year': year,

                        'status': 'no_orgid',

                        'error': '无法获取orgId'

                    })

                return results

            

            # 设置搜索日期范围（年报通常在次年-4月发布）

            min_year = min(years)

            max_year = max(years)

            search_start_date = f"{min_year}-01-01"

            search_end_date = f"{max_year + 1}-04-30"

            

            params = {

                "stock": f"{stock_code},{real_org_id}",

                "tabName": "fulltext",

                "pageSize": 50,

                "pageNum": 1,

                "column": plate,

                "category": category,

                "plate": plate,

                "seDate": f"{search_start_date}~{search_end_date}",

                "searchkey": "",

                "secid": "",

                "sortName": "pubdate",

                "sortType": "desc",

                "isHLtitle": "true"

            }

            

            response = requests.post(api_url, headers=headers, data=params, timeout=20)

            response.raise_for_status()

            data = response.json()

            

            if not data.get('announcements'):

                print(f"  ✗ 未找到{stock_code} 的相关报告")

                for year in years:

                    results.append({

                        'stock_code': stock_code,

                        'year': year,

                        'status': 'not_found',

                        'error': '未找到相关报告'

                    })

                return results

            

            # 按年份查找年报

            for year in years:

                print(f"    🔍 查找 {year} 年年报..")

                found = False

                

                for ann in data['announcements']:

                    title = ann.get('announcementTitle', '')

                    

                    # 跳过摘要、补充、更正等非正式年报

                    if any(keyword in title for keyword in ["摘要", "取消", "补充", "更正", "第一季度", "半年", "第三季度"]):

                        continue

                    

                    # 使用增强的年份匹配检查是否为指定年份的年度报告

                    matched_year = enhanced_year_matching(title, [year])

                    if matched_year and "年度报告" in title:

                        print(f"    🔄 找到年报: {title}")

                        

                        # 下载PDF

                        adj_url = ann.get('adjunctUrl', '')

                        if adj_url:

                            pdf_url = f"http://static.cninfo.com.cn/{adj_url}"

                            stock_name = ann.get('secName', stock_code)

                            filename = f"{stock_code}_{stock_name}_{year}年报.pdf"

                            

                            filepath = self.download_dir / filename
                            if self.download_pdf(pdf_url, str(filepath)):

                                print(f"    ✓ 成功下载: {filename}")

                                results.append({

                                    'stock_code': stock_code,

                                    'year': year,

                                    'status': 'success',

                                    'filename': filename,

                                    'title': title

                                })

                                found = True

                                break

                            else:

                                results.append({

                                    'stock_code': stock_code,

                                    'year': year,

                                    'status': 'download_failed',

                                    'error': '下载PDF失败'

                                })

                                found = True

                                break

                

                if not found:

                    print(f"    ✗ 未找到{stock_code} {year}年年报")

                    results.append({

                        'stock_code': stock_code,

                        'year': year,

                        'status': 'not_found',

                        'error': '未找到年报'

                    })

                

                time.sleep(0.5)  # 短暂间隔

                

        except Exception as e:

            print(f"  ✗ A股主板API处理失败: {e}")

            for year in years:

                results.append({

                    'stock_code': stock_code,

                    'year': year,

                    'status': 'error',

                    'error': str(e)

                })

        

        return results

    

    def download_a_stock_with_selenium(self, stock_code: str, years: List[int], stock_type: str) -> List[Dict]:

        """

        使用Selenium下载A股科创板/创业板年报

        

        Args:

            stock_code: 股票代码

            years: 年份列表

            stock_type: 股票类型

            

        Returns:

            下载结果列表

        """

        results = []

        

        if not self.init_selenium_driver():

            return [{'stock_code': stock_code, 'year': 'all', 'status': 'selenium_init_failed', 'error': 'Selenium初始化失败'}]

        

        try:

            # 获取orgId - 使用巨潮网的orgId映射表

            print(f"  🔍 正在获取 {stock_code} 的orgId...")

            

            # 首先尝试从完整映射表获取orgId

            print(f"    💡 尝试从巨潮网映射表获取orgId")

            all_orgid_dict = self.get_all_orgid_dict()

            org_id = all_orgid_dict.get(stock_code)

            

            if org_id:

                print(f"    从映射表获取到orgId: {org_id}")

            else:

                print(f"    ⚠️ 映射表中未找到{stock_code}")

                # 如果映射表中没有，尝试规律生成（仅用于A股主板）

                if stock_type == StockType.A_MAIN:

                    if stock_code.startswith('60'):

                        org_id = f"gssh0{stock_code}"

                        print(f"    💡 尝试上海主板规律生成: {org_id}")

                    else:

                        org_id = f"gssz0{stock_code}"

                        print(f"    💡 尝试深圳主板规律生成: {org_id}")

                else:

                    # 其他情况尝试通用API

                    print(f"    🔄 使用通用API获取...")

                    org_id = self.get_orgid_for_stock(stock_code)

            

            if not org_id:

                return [{'stock_code': stock_code, 'year': 'all', 'status': 'orgid_failed', 'error': '无法获取orgId'}]

                

            print(f"  🔄 最终使用orgId: {org_id}")

            

            # 访问股票页面

            url = f"https://www.cninfo.com.cn/new/disclosure/stock?stockCode={stock_code}&orgId={org_id}&sjstsBond=false#periodicReports"

            print(f"  🌐 访问页面: {url}")

            

            self.driver.get(url)

            time.sleep(3)

            

            # 等待页面加载（增加等待时间并尝试多种元素检测）

            try:

                print("  🔄 等待页面加载...")

                # 尝试等待多种可能的页面元素

                WebDriverWait(self.driver, 20).until(

                    lambda driver: driver.execute_script("return document.readyState") == "complete"

                )

                time.sleep(5)  # 额外等待页面内容加载

                print("🔄 页面加载完成")

            except TimeoutException:

                print(f"🔄 页面加载超时，尝试继续...")

                # 即使超时也尝试继续操作

            

            # 设置搜索参数 - 每个年份单独搜索，提高效率

            for year in years:

                print(f"  📥 正在搜索 {stock_code} {year}年年报..")

                

                try:

                    # 重新访问页面，确保状态干净

                    self.driver.get(url)

                    time.sleep(3)

                    

                    # 港股页面：使用精确搜索

                    print(f"    🔍 使用精确搜索: {year}年度报告...")

                    

                    # 查找搜索框 - 优先找标题关键字搜索

                    search_selectors = [

                        "input[placeholder*='标题关键字']",

                        "input[placeholder*='搜索']", 

                        "input[type='text'][placeholder*='关键']",

                        ".search input",

                        "[class*='search'] input"

                    ]

                    

                    search_box = None

                    for selector in search_selectors:

                        try:

                            search_box = self.driver.find_element(By.CSS_SELECTOR, selector)

                            if search_box and search_box.is_displayed():

                                print(f"    找到搜索框: {selector}")

                                break

                        except:

                            continue

                    

                    # 设置日期筛选器 - 年报通常在次年发布

                    # 暂时禁用日期筛选器，因为界面元素可能发生变化

                    print(f"    🗓🔄 跳过日期筛选器设置，依靠搜索关键词筛选...")

                    

                    # TODO: 以下日期筛选器代码暂时注释，等确认界面元素后再启用

                    # try:

                    #     # 年报在次年发布，设置次年的日期范围

                    #     start_year = year + 1

                    #     end_year = year + 1

                    #     

                    #     start_date_selectors = [

                    #         "input[placeholder*='开始日期']",

                    #         "input[placeholder*='起始']", 

                    #         ".date-picker input:first-child",

                    #         ".start-date input"

                    #     ]

                    #     

                    #     end_date_selectors = [

                    #         "input[placeholder*='结束日期']",

                    #         "input[placeholder*='终止']",

                    #         ".date-picker input:last-child", 

                    #         ".end-date input"

                    #     ]

                    #     

                    #     # 设置起始日期

                    #     for start_sel in start_date_selectors:

                    #         try:

                    #             start_input = self.driver.find_element(By.CSS_SELECTOR, start_sel)

                    #             if start_input and start_input.is_displayed():

                    #                 start_input.clear()

                    #                 start_date = f"{start_year}-01-01"

                    #                 start_input.send_keys(start_date)

                    #                 print(f"    设置起始日期: {start_date}")

                    #                 break

                    #         except:

                    #             continue

                    #     

                    #     # 设置结束日期  

                    #     for end_sel in end_date_selectors:

                    #         try:

                    #             end_input = self.driver.find_element(By.CSS_SELECTOR, end_sel)

                    #             if end_input and end_input.is_displayed():

                    #                 end_input.clear()

                    #                 end_date = f"{end_year}-12-31"

                    #                 end_input.send_keys(end_date)

                    #                 print(f"    设置结束日期: {end_date}")

                    #                 break

                    #         except:

                    #             continue

                    #             

                    # except Exception as e:

                    #     print(f"    日期筛选器设置失败: {e}")

                    

                    if search_box:

                        # 清空搜索框并输入精确的搜索关键词

                        search_box.clear()

                        # 使用年份+年度报告的精确搜索，大幅减少结果数量

                        search_keywords = f"{year}年度报告"

                        search_box.send_keys(search_keywords)

                        print(f"    输入精确搜索关键词: {search_keywords}")

                        

                        # 点击搜索按钮

                        search_btn_selectors = [

                            "button[class*='查询']",

                            "button[class*='search']", 

                            ".search button",

                            "[class*='search'] button",

                            "button[type='submit']",

                            "input[type='submit']"

                        ]

                        

                        search_clicked = False

                        for btn_selector in search_btn_selectors:

                            try:

                                search_btn = self.driver.find_element(By.CSS_SELECTOR, btn_selector)

                                if search_btn and search_btn.is_displayed():

                                    search_btn.click()

                                    print(f"    点击搜索按钮: {btn_selector}")

                                    search_clicked = True

                                    break

                            except:

                                continue

                        

                        if not search_clicked:

                            # 如果找不到搜索按钮，尝试按回车键

                            search_box.send_keys(Keys.ENTER)

                            print(f"    按回车键搜索")

                        

                        time.sleep(5)  # 等待搜索结果加载

                    else:

                        print(f"    ⚠️ 未找到搜索框，跳过此年份")

                        results.append({

                            'stock_code': stock_code,

                            'year': year,

                            'status': 'search_failed',

                            'error': '未找到搜索框'

                        })

                        continue

                    

                    # 查找搜索结果表格 - 精确搜索后应该结果很少

                    table_selectors = [

                        "table tbody tr",

                        ".disclosure-table tbody tr", 

                        "[class*='table'] tbody tr",

                        "tr"

                    ]

                    

                    rows = []

                    for selector in table_selectors:

                        try:

                            rows = self.driver.find_elements(By.CSS_SELECTOR, selector)

                            if rows:

                                print(f"    精确搜索后找到{len(rows)} 行数")

                                break

                        except:

                            continue

                    

                    # 精确搜索后，只需检查前10行结果

                    found_report = False

                    

                    if rows:

                        print(f"    检查前50行精确搜索结果...")

                        

                        for i, row in enumerate(rows[:50]):  # 检查前50行

                            try:

                                print(f"    正在解析第{i+1} 行...")

                                

                                # 先查看表格结果

                                tds = row.find_elements(By.CSS_SELECTOR, "td")

                                print(f"      第{i+1} 行有 {len(tds)} 列")

                                

                                # 尝试获取所有列的文本内容

                                row_texts = []

                                for j, td in enumerate(tds):

                                    text = td.text.strip()

                                    if text:

                                        row_texts.append(f"列{j+1}: {text[:50]}")

                                

                                if row_texts:

                                    print(f"      行内容: {' | '.join(row_texts)}")

                                

                                # 简化选择器，只使用最基本的选择器

                                title = ""

                                date = ""

                                title_element = None

                                

                                # 尝试多种方式获取标题

                                try:

                                    # 方法1: 查找链接

                                    title_element = row.find_element(By.CSS_SELECTOR, "td a")

                                    title = title_element.text.strip()

                                    print(f"      找到标题链接: {title[:40]}...")

                                except:

                                    try:

                                        # 方法2: 查找任何链接

                                        title_element = row.find_element(By.CSS_SELECTOR, "a")

                                        title = title_element.text.strip()

                                        print(f"      找到链接: {title[:40]}...")

                                    except:

                                        try:

                                            # 方法3: 如果没有链接，取第二列的文本(通常是标题列)

                                            if len(tds) >= 2:

                                                title = tds[1].text.strip()

                                                if title:

                                                    print(f"      找到文本标题: {title[:40]}...")

                                                    # 寻找该行中的链接元素

                                                    try:

                                                        title_element = tds[1].find_element(By.CSS_SELECTOR, "a")

                                                    except:

                                                        title_element = None

                                        except:

                                            print(f"      第{i+1} 行无法获取标题")

                                            continue

                                

                                if not title:

                                    print(f"      第{i+1} 行标题为空，跳过")

                                    continue

                                    

                                # 显示所有条目，便于调试

                                print(f"    [{i+1}] 标题: {title[:60]}... 日期: {date}")

                                

                                # 严格的年报匹配条件

                                is_annual_report = (

                                    str(year) in title and 

                                    ('年度报告' in title or '年报' in title or 'Annual Report' in title.title()) and

                                    '摘要' not in title and  # 排除摘要

                                    '监管' not in title and  # 排除监管

                                    '回复' not in title and  # 排除回复

                                    '问询' not in title and  # 排除问询

                                    '各种函件' not in title and    # 排除各种函件

                                    '审计意见' not in title and  # 排除审计意见

                                    '更正' not in title and  # 排除更正公告

                                    '补充' not in title and  # 排除补充公告

                                    '关于xx年报的公告' not in title and  # 排除"关于xx年报的公告"

                                    '自愿性披露公告' not in title and  # 排除自愿性披露公告

                                    '英文' not in title and  # 排除英文

                                    '简报' not in title     # 排除简报

                                )

                                

                                if is_annual_report:

                                    print(f"    🔄 找到年报: {title}")

                                    

                                    # 科创板/创业板/港股：获取链接href并访问详情页

                                    if title_element:

                                        # 获取链接的href属性

                                        try:

                                            detail_href = title_element.get_attribute('href')

                                            print(f"      链接href: {detail_href}")

                                            

                                            if detail_href:

                                                # 直接访问详情页

                                                self.driver.get(detail_href)

                                                time.sleep(3)

                                                

                                                # 获取当前页面URL

                                                detail_url = self.driver.current_url

                                                print(f"      详情页URL: {detail_url}")

                                            else:

                                                # 如果没有href，尝试点击

                                                title_element.click()

                                                time.sleep(3)

                                                detail_url = self.driver.current_url

                                                print(f"      详情页URL: {detail_url}")

                                        except:

                                            # 备用方案：直接点击

                                            title_element.click()

                                            time.sleep(3)

                                            detail_url = self.driver.current_url

                                            print(f"      详情页URL: {detail_url}")

                                        

                                        # 从URL中提取announcementId和announcementTime

                                        try:

                                            from urllib.parse import urlparse, parse_qs

                                            parsed_url = urlparse(detail_url)

                                            query_params = parse_qs(parsed_url.query)

                                            

                                            announcement_id = query_params.get('announcementId', [None])[0]

                                            announcement_time = query_params.get('announcementTime', [None])[0]

                                            

                                            if announcement_id and announcement_time:

                                                # 从announcementTime中只提取日期部分（去掉时间）

                                                announcement_date = announcement_time.split(' ')[0] if ' ' in announcement_time else announcement_time

                                                

                                                # 构造PDF下载URL

                                                pdf_url = f"https://static.cninfo.com.cn/finalpage/{announcement_date}/{announcement_id}.PDF"

                                                print(f"      构造PDF下载链接: {pdf_url}")

                                                

                                                # 尝试获取股票名称（从标题中提取）
                                                company_name = stock_code  # 默认使用股票代码
                                                try:
                                                    # 从标题中提取公司名称
                                                    if "：" in title:
                                                        company_name = title.split("：")[0].strip()
                                                    elif title.startswith("关于"):
                                                        # 处理"关于XXX公司"格式
                                                        parts = title.split("年度报告")
                                                        if len(parts) > 0:
                                                            name_part = parts[0].replace("关于", "").replace(f"{year}", "").strip()
                                                            if name_part:
                                                                company_name = name_part
                                                except:
                                                    pass
                                                
                                                # 构造文件名
                                                filename = f"{stock_code}_{company_name}_{year}年报.pdf"

                                                

                                                # 使用requests下载PDF

                                                filepath = self.download_dir / filename
                                                download_success = self.download_pdf(pdf_url, str(filepath))

                                                

                                                if download_success:

                                                    print(f"    成功下载: {filename}")

                                                    results.append({

                                                        'stock_code': stock_code,

                                                        'year': year,

                                                        'status': 'success',

                                                        'filename': filename,

                                                        'title': title,

                                                        'pdf_url': pdf_url

                                                    })

                                                else:

                                                    print(f"🔄 下载失败: {filename}")

                                                    results.append({

                                                        'stock_code': stock_code,

                                                        'year': year,

                                                        'status': 'download_failed',

                                                        'error': f'PDF下载失败: {pdf_url}',

                                                        'title': title

                                                    })

                                            else:

                                                print(f"      ⚠️ 无法从URL中提取必要参数")

                                                results.append({

                                                    'stock_code': stock_code,

                                                    'year': year,

                                                    'status': 'url_parse_failed',

                                                    'error': '无法解析详情页URL参数',

                                                    'title': title

                                                })

                                        except Exception as url_error:

                                            print(f"      🔄 URL解析出错: {url_error}")

                                            results.append({

                                                'stock_code': stock_code,

                                                'year': year,

                                                'status': 'url_error',

                                                'error': str(url_error),

                                                'title': title

                                            })

                                        

                                        found_report = True

                                        break

                                    

                            except Exception as e:

                                print(f"    解析第{i+1}行时出错: {e}")

                                continue

                    

                    # 解析搜索结果
                    if not found_report:
                        # 如果前50行没找到，尝试翻页搜索
                        print(f"    🔄 前50行未找到年报，尝试翻页搜索...")
                        
                        # 尝试翻页，最多翻3页
                        for page_num in range(2, 5):  # 第2页到第4页
                            try:
                                # 查找下一页按钮
                                next_page_selectors = [
                                    f"a[title='第{page_num}页']",
                                    f"a[data-page='{page_num}']",
                                    f".page-item:nth-child({page_num + 1}) a",
                                    f".pagination a:contains('{page_num}')",
                                    f"a:contains('第{page_num}页')",
                                    f"a:contains('{page_num}')"
                                ]
                                
                                next_button = None
                                for selector in next_page_selectors:
                                    try:
                                        next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                                        if next_button and next_button.is_displayed() and next_button.is_enabled():
                                            print(f"      找到第{page_num}页按钮: {selector}")
                                            break
                                    except:
                                        continue
                                
                                if not next_button:
                                    print(f"      未找到第{page_num}页按钮，停止翻页")
                                    break
                                
                                # 点击翻页
                                self.driver.execute_script("arguments[0].click();", next_button)
                                time.sleep(3)
                                
                                print(f"      已翻到第{page_num}页，重新搜索...")
                                
                                # 重新获取表格行
                                rows = self.driver.find_elements(By.CSS_SELECTOR, "tbody tr, .table tr, tr")
                                if not rows:
                                    print(f"      第{page_num}页无数据")
                                    continue
                                
                                # 检查这一页的前20行
                                for i, row in enumerate(rows[:20]):
                                    try:
                                        # 获取标题
                                        title = ""
                                        title_element = None
                                        
                                        try:
                                            title_element = row.find_element(By.CSS_SELECTOR, "td a")
                                            title = title_element.text.strip()
                                        except:
                                            try:
                                                title_element = row.find_element(By.CSS_SELECTOR, "a")
                                                title = title_element.text.strip()
                                            except:
                                                tds = row.find_elements(By.CSS_SELECTOR, "td")
                                                if len(tds) >= 2:
                                                    title = tds[1].text.strip()
                                                    try:
                                                        title_element = tds[1].find_element(By.CSS_SELECTOR, "a")
                                                    except:
                                                        title_element = None
                                        
                                        if not title:
                                            continue
                                        
                                        # 年报匹配检查
                                        is_annual_report = (
                                            str(year) in title and 
                                            ('年度报告' in title or '年报' in title or 'Annual Report' in title.title()) and
                                            '摘要' not in title and '监管' not in title and '回复' not in title and 
                                            '问询' not in title and '各种函件' not in title and '审计意见' not in title and 
                                            '更正' not in title and '补充' not in title and '关于xx年报的公告' not in title and 
                                            '自愿性披露公告' not in title and '英文' not in title and '简报' not in title
                                        )
                                        
                                        if is_annual_report:
                                            print(f"      🎉 第{page_num}页找到年报: {title}")
                                            found_report = True
                                            
                                            # 处理下载逻辑（复用之前的代码）
                                            if title_element:
                                                try:
                                                    detail_href = title_element.get_attribute('href')
                                                    if detail_href:
                                                        self.driver.get(detail_href)
                                                        time.sleep(3)
                                                        detail_url = self.driver.current_url
                                                        
                                                        # 解析URL参数并下载（复用之前的逻辑）
                                                        from urllib.parse import urlparse, parse_qs
                                                        parsed_url = urlparse(detail_url)
                                                        query_params = parse_qs(parsed_url.query)
                                                        
                                                        if 'announcementId' in query_params and 'orgId' in query_params:
                                                            announcement_id = query_params['announcementId'][0]
                                                            org_id_param = query_params['orgId'][0]
                                                            
                                                            pdf_url = f"http://static.cninfo.com.cn/finalpage/{announcement_id}.PDF"
                                                            
                                                            # 尝试获取股票名称（从标题中提取）
                                                            company_name = stock_code  # 默认使用股票代码
                                                            try:
                                                                # 从标题中提取公司名称
                                                                if "：" in title:
                                                                    company_name = title.split("：")[0].strip()
                                                                elif title.startswith("关于"):
                                                                    # 处理"关于XXX公司"格式
                                                                    parts = title.split("年度报告")
                                                                    if len(parts) > 0:
                                                                        name_part = parts[0].replace("关于", "").replace(f"{year}", "").strip()
                                                                        if name_part:
                                                                            company_name = name_part
                                                            except:
                                                                pass
                                                            
                                                            filename = f"{stock_code}_{company_name}_{year}年报.pdf"
                                                            filepath = self.download_dir / filename
                                                            
                                                            if self.download_pdf(pdf_url, str(filepath)):
                                                                print(f"      ✓ 翻页成功下载: {filename}")
                                                                results.append({
                                                                    'stock_code': stock_code,
                                                                    'year': year,
                                                                    'status': 'success',
                                                                    'filename': filename,
                                                                    'title': title,
                                                                    'pdf_url': pdf_url
                                                                })
                                                            else:
                                                                results.append({
                                                                    'stock_code': stock_code,
                                                                    'year': year,
                                                                    'status': 'download_failed',
                                                                    'error': f'PDF下载失败: {pdf_url}',
                                                                    'title': title
                                                                })
                                                        else:
                                                            results.append({
                                                                'stock_code': stock_code,
                                                                'year': year,
                                                                'status': 'url_parse_failed',
                                                                'error': '无法解析详情页URL参数',
                                                                'title': title
                                                            })
                                                except Exception as e:
                                                    results.append({
                                                        'stock_code': stock_code,
                                                        'year': year,
                                                        'status': 'url_error',
                                                        'error': str(e),
                                                        'title': title
                                                    })
                                            break
                                    except Exception as e:
                                        continue
                                
                                if found_report:
                                    break
                                    
                            except Exception as e:
                                print(f"      翻页到第{page_num}页失败: {e}")
                                break
                        
                        if not found_report:
                            print(f"    ✗ 翻页后仍未找到{stock_code} {year}年年报")
                            results.append({
                                'stock_code': stock_code,
                                'year': year,
                                'status': 'not_found',
                                'error': '未找到年报'
                            })
                    # 如果found_report为True，说明已经找到并处理了，不需要再添加not_found记录
                
                except Exception as e:
                    print(f"🔄 搜索过程出错: {e}")
                    results.append({
                        'stock_code': stock_code,
                        'year': year,
                        'status': 'search_failed',
                        'error': str(e)
                    })
        
        except Exception as e:
            print(f"🔄 Selenium操作出错: {e}")
            results.append({
                'stock_code': stock_code,
                'year': 'all',
                'status': 'selenium_error',
                'error': str(e)
            })
        
        return results

    

    def search_hk_company_by_name(self, company_name_part: str) -> Tuple[str, str, str]:
        """
        通过公司名称片段搜索港股，获取orgId
        
        Args:
            company_name_part: 公司名称片段或股票代码
            
        Returns:
            Tuple[股票代码, 公司名称, orgId]
        """
        api_url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        # 处理HK前缀
        search_term = company_name_part
        original_search_code = company_name_part  # 保存原始输入用于精确匹配
        if search_term.startswith('HK'):
            search_term = search_term[2:]  # 去掉HK前缀
            original_search_code = search_term  # 更新原始代码
        
        params = {
            "stock": "",
            "tabName": "fulltext",
                            "pageSize": 50,
                "pageNum": 1,
            "column": "",
            "category": "",
            "plate": "",
            "seDate": "2020-01-01~2025-12-31",
            "searchkey": search_term,
            "secid": "",
            "sortName": "pubdate",
            "sortType": "desc",
            "isHLtitle": "true"
        }
        
        try:
            print(f"    🔍 搜索港股公司: {search_term} (精确匹配: {original_search_code})")
            response = requests.post(api_url, headers=headers, data=params, timeout=10)
            if response.status_code == 200:
                result = response.json()
                announcements = result.get('announcements')
                
                # 处理None响应
                if announcements is None:
                    print(f"    ⚠️ API返回announcements为None")
                    return None, None, None
                
                # 🔧 修复：收集所有匹配结果，优先精确匹配
                exact_matches = []
                partial_matches = []
                
                for ann in announcements:
                    sec_code = ann.get('secCode', '')
                    sec_name = ann.get('secName', '')
                    org_id = ann.get('orgId', '')
                    
                    # 清理HTML标签
                    clean_name = sec_name.replace('<em>', '').replace('</em>', '') if sec_name else ''
                    
                    # 检查是否是港股（代码长度5位或以HK开头）
                    if sec_code and org_id and (len(sec_code) == 5 or sec_code.startswith('HK')):
                        # 精确匹配：股票代码完全相同
                        if sec_code == original_search_code or sec_code == original_search_code.zfill(5):
                            exact_matches.append((sec_code, clean_name, org_id))
                            print(f"    ✅ 精确匹配: {clean_name} ({sec_code}) - orgId: {org_id}")
                        else:
                            partial_matches.append((sec_code, clean_name, org_id))
                            print(f"    📄 部分匹配: {clean_name} ({sec_code}) - orgId: {org_id}")
                
                # 优先返回精确匹配结果
                if exact_matches:
                    sec_code, clean_name, org_id = exact_matches[0]
                    print(f"    🎯 使用精确匹配结果: {clean_name} ({sec_code})")
                    return sec_code, clean_name, org_id
                elif partial_matches:
                    sec_code, clean_name, org_id = partial_matches[0]
                    print(f"    ⚠️ 无精确匹配，使用部分匹配: {clean_name} ({sec_code})")
                    print(f"    ⚠️ 警告：输入代码 {original_search_code} != 找到代码 {sec_code}")
                    return sec_code, clean_name, org_id
                        
        except Exception as e:
            print(f"    ✗ 搜索港股公司失败: {e}")
        
        return None, None, None

    def download_hk_reports(self, stock_code: str, years: List[int]) -> List[dict]:
        """
        使用API下载港股年报（新版本）
        
        Args:
            stock_code: 港股代码
            years: 年份列表
            
        Returns:
            下载结果列表
        """
        print(f"\n🚀 开始下载港股 {stock_code} 的年报...")
        results = []
        
        # 创建港股下载目录
        hk_dir = self.download_dir / "HK"
        hk_dir.mkdir(exist_ok=True)
        
        try:
            # 先尝试搜索公司信息
            company_name = None
            org_id = None
            
            # 处理HK前缀的股票代码
            search_code = stock_code
            if stock_code.startswith('HK'):
                search_code = stock_code[2:]  # 去掉HK前缀用于搜索
            
            # 尝试用股票代码搜索
            found_code, company_name, org_id = self.search_hk_company_by_name(search_code)
            
            if not org_id:
                # 尝试去掉前导0搜索
                search_code_no_zero = search_code.lstrip('0')
                print(f"    🔄 尝试去掉前导0搜索: {search_code_no_zero}")
                found_code, company_name, org_id = self.search_hk_company_by_name(search_code_no_zero)
            
            if not org_id:
                print(f"  ✗ 无法找到港股 {stock_code} 的公司信息")
                for year in years:
                    results.append({
                        'stock_code': stock_code,
                        'company_name': None,
                        'year': year,
                        'status': 'company_not_found',
                        'error': '无法找到公司信息'
                    })
                return results
            
            print(f"  ✓ 公司信息: {company_name} ({found_code}) - orgId: {org_id}")
            
            # 搜索年报
            api_url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            # 多种搜索策略（动态生成基于目标年份）
            search_strategies = [
                (f"{company_name} 年度报告", "公司名+年度报告"),
                (f"{company_name} 年报", "公司名+年报"),
                (f"{found_code} 年度报告", "股票代码+年度报告"),
                (f"{found_code} 年报", "股票代码+年报"),
            ]
            
            # 动态添加基于目标年份的搜索策略
            for year in years:
                search_strategies.extend([
                    (f"{company_name} {year}", f"公司名+{year}"),
                    (f"{found_code} {year}", f"股票代码+{year}"),
                ])
            
            found_reports = {}
            
            for search_term, strategy_desc in search_strategies:
                print(f"  🔍 使用策略: {strategy_desc} - {search_term}")
                
                params = {
                    "stock": "",
                    "tabName": "fulltext",
                    "pageSize": 50,  # 增加页面大小
                    "pageNum": 1,
                    "column": "",
                    "category": "",
                    "plate": "",
                    "seDate": "2018-01-01~2025-12-31",
                    "searchkey": search_term,
                    "secid": "",
                    "sortName": "pubdate",
                    "sortType": "desc",
                    "isHLtitle": "true"
                }
                
                try:
                    # 支持翻页搜索，最多搜索前3页
                    all_announcements = []
                    for page_num in range(1, 4):
                        params["pageNum"] = page_num
                        
                        response = requests.post(api_url, headers=headers, data=params, timeout=20)
                        
                        if response.status_code == 200:
                            result = response.json()
                            announcements = result.get('announcements', [])
                            
                            if announcements:
                                all_announcements.extend(announcements)
                                print(f"    第{page_num}页找到{len(announcements)}条公告")
                            else:
                                if page_num == 1:
                                    print(f"    ❌ 无结果")
                                else:
                                    print(f"    第{page_num}页无结果，停止翻页")
                                break
                        else:
                            print(f"    ❌ HTTP错误: {response.status_code}")
                            break
                    
                    if all_announcements:
                        print(f"    ✓ 总共找到 {len(all_announcements)} 条公告")
                        
                        for ann in all_announcements:
                            title = ann.get('announcementTitle', '')
                            sec_code = ann.get('secCode', '')
                            sec_name = ann.get('secName', '')
                            adj_url = ann.get('adjunctUrl', '')
                            
                            # 确保是目标公司（匹配港股和对应的A股代码）
                            target_codes = [found_code]
                            # 如果是港股，也匹配对应的A股代码
                            if found_code == '00939':  # 建设银行港股
                                target_codes.append('601939')  # 建设银行A股
                            elif found_code == '00700':  # 腾讯港股
                                # 腾讯没有A股，只有港股
                                pass
                            
                            if sec_code not in target_codes:
                                continue
                                
                            # 清理HTML标签
                            clean_title = title.replace('<em>', '').replace('</em>', '')
                            
                            # 使用增强的年份匹配逻辑（包含日期辅助）
                            matched_year = None
                            if (('年度报告' in clean_title or '年报' in clean_title or '企业年度报告' in clean_title) and
                                '半年' not in clean_title and  # 排除半年报
                                '半年度' not in clean_title and  # 排除半年度报告
                                '中期' not in clean_title and  # 排除中期报告
                                '摘要' not in clean_title and  # 排除摘要
                                '通知信函' not in clean_title and  # 排除通知信函
                                '通告' not in clean_title and  # 排除通告
                                '通函' not in clean_title and  # 排除通函
                                '刊发通知' not in clean_title and  # 排除刊发通知
                                '代表委任表格' not in clean_title and  # 排除代表委任表格
                                '股东周年大会' not in clean_title):  # 排除股东大会相关
                                
                                # 获取发布日期用于辅助判断
                                pub_date = ann.get('announcementTime', '')
                                matched_year = enhanced_year_matching_with_date(clean_title, years, pub_date)
                            
                            if matched_year and matched_year not in found_reports:
                                found_reports[matched_year] = {
                                    'title': title,
                                    'adjunctUrl': adj_url,
                                    'search_term': search_term
                                }
                                print(f"    ★ 找到 {matched_year} 年报: {clean_title}")
                    
                except Exception as e:
                    print(f"    ❌ 搜索异常: {e}")
                
                # 如果已经找到所有年份的年报，可以提前结束
                if len(found_reports) >= len(years):
                    break
            
            # 下载找到的年报
            print(f"  📥 开始下载年报...")
            
            for year in years:
                if year in found_reports:
                    report = found_reports[year]
                    adj_url = report['adjunctUrl']
                    
                    if adj_url:
                        # 构造PDF直接下载链接
                        pdf_url = f"http://static.cninfo.com.cn/{adj_url}"
                        # 使用清理后的公司名称
                        safe_company_name = company_name.replace('/', '_').replace('\\', '_')
                        filename = f"{found_code}_{safe_company_name}_{year}年年度报告.pdf"
                        filepath = hk_dir / filename
                        
                        print(f"    📄 下载 {year} 年报...")
                        print(f"       文件: {report['title']}")
                        
                        if self.download_pdf(pdf_url, str(filepath)):
                            print(f"    ✓ 成功下载: {filename}")
                            results.append({
                                'stock_code': stock_code,
                                'company_name': company_name,
                                'year': year,
                                'status': 'success',
                                'filename': filename,
                                'file_path': str(filepath)
                            })
                        else:
                            print(f"    ✗ 下载失败: {filename}")
                            results.append({
                                'stock_code': stock_code,
                                'company_name': company_name,
                                'year': year,
                                'status': 'download_failed',
                                'error': 'PDF下载失败'
                            })
                    else:
                        print(f"    ✗ {year} 年报无PDF链接")
                        results.append({
                            'stock_code': stock_code,
                            'company_name': company_name,
                            'year': year,
                            'status': 'no_pdf_link',
                            'error': '无PDF链接'
                        })
                else:
                    print(f"    ✗ 未找到 {year} 年报")
                    results.append({
                        'stock_code': stock_code,
                        'company_name': company_name,
                        'year': year,
                        'status': 'not_found',
                        'error': '未找到年报'
                    })
            
            return results
            
        except Exception as e:
            print(f"🔄 港股下载过程出错: {e}")
            for year in years:
                results.append({
                    'stock_code': stock_code,
                    'company_name': None,
                    'year': year,
                    'status': 'error',
                    'error': str(e)
                })
            return results

    def download_hk_reports_old(self, stock_code: str, years: List[int]) -> List[dict]:
        """
        旧版港股下载方法（使用Selenium）
        现在已被新版API方法替代
        """
        return [{'stock_code': stock_code, 'year': 'all', 'status': 'deprecated', 'error': '已使用新版API方法'}]

    def download_pdf(self, url: str, filepath: str) -> bool:
        """
        通过浏览器下载PDF文件
        
        Args:
            url: 下载URL
            filepath: 完整文件路径
            
        Returns:
            是否下载成功
        """
        try:
            # 确保目录存在
            target_path = Path(filepath)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 使用浏览器下载
            filename = target_path.name
            success = self.browser_download_file(url, filename)
            
            if success:
                # 🔧 修复：在浏览器下载目录中查找文件
                downloaded_files = [f for f in self.download_dir.iterdir() if f.is_file()]
                if downloaded_files:
                    # 找到最新下载的文件
                    latest_file = max(downloaded_files, key=lambda f: f.stat().st_mtime)
                    
                    # 增加额外安全检查
                    if latest_file.name.endswith('.crdownload'):
                        print(f"    ❌ 重命名失败：文件仍为临时状态: {latest_file.name}")
                        return False
                    
                    print(f"    📁 浏览器下载文件: {latest_file}")
                    print(f"    📁 目标路径: {target_path}")
                    
                    # 🔧 修复：移动文件到正确目录并重命名
                    try:
                        # 确保目标文件不存在，避免冲突
                        if target_path.exists():
                            print(f"    ⚠️ 目标文件已存在，删除旧文件: {filename}")
                            target_path.unlink()
                        
                        # 移动并重命名文件
                        latest_file.rename(target_path)
                        print(f"    📝 文件移动重命名: {latest_file.name} -> {target_path}")
                        
                        # 验证文件是否真的存在于目标位置
                        if target_path.exists():
                            print(f"    ✅ 文件成功保存到: {target_path}")
                            return True
                        else:
                            print(f"    ❌ 文件移动后未找到: {target_path}")
                            return False
                            
                    except Exception as rename_error:
                        print(f"    ❌ 文件移动重命名失败: {rename_error}")
                        return False
                else:
                    print("    ❌ 未找到下载的文件")
                    return False
            else:
                return False
            
        except Exception as e:
            print(f"    下载失败: {e}")
            return False

    

    def download_stock_reports(self, stock_code: str, years: List[int]) -> List[Dict]:

        """

        下载指定股票的年报

        

        Args:

            stock_code: 股票代码

            years: 年份列表

            

        Returns:

            下载结果列表

        """

        stock_type = self.identify_stock_type(stock_code)

        print(f"📊 处理股票: {stock_code} ({stock_type})")

        

        if stock_type == StockType.A_MAIN:

            return self.download_a_stock_main_reports(stock_code, years)

        elif stock_type in [StockType.A_STAR, StockType.A_GEM]:

            return self.download_a_stock_with_selenium(stock_code, years, stock_type)

        elif stock_type == StockType.HK:

            return self.download_hk_reports(stock_code, years)

        elif stock_type == StockType.US:

            return self.download_us_stock_10k_reports(stock_code, years)

        else:

            print(f"    🔄 不支持的股票类型: {stock_type}")

            return [{'stock_code': stock_code, 'year': 'all', 'status': 'unsupported', 'error': f'不支持的股票类型: {stock_type}'}]

    

    def process_stock_list(self, stock_codes: List[str], years: List[int]):

        """

        批量处理股票列表

        

        Args:

            stock_codes: 股票代码列表

            years: 年份列表

        """

        self.stats["total"] = len(stock_codes) * len(years)

        

        print(f"🚀 开始批量下载，共{len(stock_codes)} 只股票，{len(years)} 个年份")

        print(f"📁 下载目录: {self.download_dir.absolute()}")

        print("=" * 60)

        

        for i, stock_code in enumerate(stock_codes, 1):

            print(f"\n[{i}/{len(stock_codes)}] 处理股票: {stock_code}")

            

            results = self.download_stock_reports(stock_code, years)

            

            # 更新统计

            for result in results:

                self.stats["details"].append(result)

                if result["status"] == "success":

                    self.stats["success"] += 1

                else:

                    self.stats["failed"] += 1

            

            # 显示当前进度

            success_rate = (self.stats["success"] / (self.stats["success"] + self.stats["failed"])) * 100 if (self.stats["success"] + self.stats["failed"]) > 0 else 0

            print(f"  当前成功率 {success_rate:.1f}% ({self.stats['success']}/{self.stats['success'] + self.stats['failed']})")

            

            time.sleep(2)  # 避免请求过快

    

    def print_summary(self):

        """打印下载汇总报告"""

        print("\n" + "=" * 60)

        print("📈 下载汇总报告")

        print("=" * 60)

        

        print(f"总计任务: {self.stats['total']}")

        print(f"成功下载: {self.stats['success']}")

        print(f"失败任务: {self.stats['failed']}")

        

        if self.stats['total'] > 0:

            success_rate = (self.stats['success'] / self.stats['total']) * 100

            print(f"成功率 {success_rate:.1f}%")

        

        # 按状态分组统计

        status_count = {}

        failed_details = []  # 存储失败详情

        

        for detail in self.stats["details"]:

            status = detail.get("status", "unknown")

            status_count[status] = status_count.get(status, 0) + 1

            

            # 收集失败详情

            if status != "success":

                failed_details.append({

                    'stock_code': detail.get('stock_code', ''),

                    'company_name': detail.get('company_name', ''),

                    'year': detail.get('year', ''),

                    'status': status,

                    'error': detail.get('error', ''),

                    'title': detail.get('title', '')

                })

        

        if status_count:

            print(f"\n📊 详细统计:")

            for status, count in status_count.items():

                print(f"  {status}: {count}")

        

        # 详细列出失败任务

        if failed_details:

            print(f"\n失败任务详情 ({len(failed_details)}个):")

            

            # 按失败类型分组

            failure_groups = {}

            for failure in failed_details:

                status = failure['status']

                if status not in failure_groups:

                    failure_groups[status] = []

                failure_groups[status].append(failure)

            

            for status, failures in failure_groups.items():

                print(f"\n🔸 {status} ({len(failures)}个):")

                for failure in failures:

                    stock_code = failure['stock_code']

                    company_name = failure.get('company_name', '')

                    year = failure['year']

                    

                    # 构建显示字符串：股票代码 + 公司名称（如果有）+ 年份

                    if company_name:

                        stock_info = f"{stock_code} {company_name} {year}年"

                    else:

                        stock_info = f"{stock_code} {year}年"

                    

                    error_msg = failure['error']

                    if failure.get('title'):

                        print(f"  {stock_info}: {error_msg} (找到标题: {failure['title'][:50]}...)")

                    else:

                        print(f"  {stock_info}: {error_msg}")

        

        # 成功任务列表（如果不多的话）

        success_details = [d for d in self.stats["details"] if d.get("status") == "success"]

        if success_details and len(success_details) <= 10:  # 只有不超过10个成功时才显示

            print(f"\n成功下载详情 ({len(success_details)}个):")

            for success in success_details:

                stock_year = f"{success.get('stock_code', '')} {success.get('year', '')}"

                filename = success.get('filename', '')

                print(f"  {stock_year}: {filename}")

        

        print(f"\n📁 下载文件保存目录 {self.download_dir.absolute()}")

        print("================================================================")
        print('Annual Report Crawler - WebDriver "Otako" Version')
        print("Developed by Terence WANG")
        print("================================================================")
        print()

    def download_us_stock_10k_reports(self, stock_symbol, years):
        """
        下载美股10-K年报
        
        Args:
            stock_symbol (str): 美股股票代码，如 'AAPL', 'MSFT'
            years (list): 年份列表，如 [2023, 2022, 2021]
        
        Returns:
            List[Dict]: 下载结果列表，与其他函数格式一致
        """
        print(f"\n🇺🇸 开始下载美股 {stock_symbol} 的10-K年报...")
        
        # 创建US文件夹
        us_folder = os.path.join(self.download_dir, "US")
        if not os.path.exists(us_folder):
            os.makedirs(us_folder)
            print(f"    📁 创建US文件夹: {us_folder}")
        
        results = []  # 改为列表格式，与其他函数保持一致
        successful_downloads = 0
        failed_downloads = 0
        
        try:
            # 第一步：获取公司CIK
            cik = self._get_us_stock_cik(stock_symbol)
            if not cik:
                print(f"    ❌ 无法找到股票代码 {stock_symbol} 对应的CIK")
                # 为每个年份创建失败记录
                for year in years:
                    results.append({
                        'stock_code': stock_symbol,
                        'year': year,
                        'status': 'failed',
                        'error': f'无法找到股票代码 {stock_symbol} 对应的CIK',
                        'filename': None
                    })
                return results
            
            print(f"    ✓ 找到CIK: {cik}")
            
            # 第二步：获取10-K报告列表
            filings = self._get_us_10k_filings(cik, years)
            if not filings:
                print(f"    ❌ 未找到任何10-K报告")
                for year in years:
                    results.append({
                        'stock_code': stock_symbol,
                        'year': year,
                        'status': 'failed',
                        'error': '未找到任何10-K报告',
                        'filename': None
                    })
                return results
            
            print(f"    ✓ 找到 {len(filings)} 个10-K报告")
            
            # 为每个请求的年份创建结果记录
            filing_dict = {filing['year']: filing for filing in filings}
            
            # 第三步：下载每个年报
            for year in years:
                if year in filing_dict:
                    filing = filing_dict[year]
                    try:
                        filing_date = filing['filing_date']
                        document_url = filing['document_url']
                        
                        print(f"    📄 下载 {year} 年10-K报告...")
                        
                        # 下载HTML内容
                        html_content = self._download_us_filing_content(document_url)
                        if not html_content:
                            print(f"    ❌ {year} 年报下载失败")
                            results.append({
                                'stock_code': stock_symbol,
                                'year': year,
                                'status': 'failed',
                                'error': '文档内容下载失败',
                                'filename': None
                            })
                            failed_downloads += 1
                            continue
                        
                        # 保存文件（HTML格式）
                        filename = f"{stock_symbol}_{year}_10K_{filing_date}.html"
                        filepath = os.path.join(us_folder, filename)
                        
                        # 直接保存为HTML
                        success = self._save_us_filing_as_html(html_content, filepath, stock_symbol, year)
                        
                        if success:
                            print(f"    ✅ {year} 年报下载成功: {filename}")
                            results.append({
                                'stock_code': stock_symbol,
                                'year': year,
                                'status': 'success',
                                'error': None,
                                'filename': filename
                            })
                            successful_downloads += 1
                        else:
                            print(f"    ❌ {year} 年报保存失败")
                            results.append({
                                'stock_code': stock_symbol,
                                'year': year,
                                'status': 'failed',
                                'error': '文件保存失败',
                                'filename': None
                            })
                            failed_downloads += 1
                            
                        # 添加延迟避免请求过快
                        time.sleep(0.5)
                        
                    except Exception as e:
                        print(f"    ❌ {year} 年报处理失败: {str(e)}")
                        results.append({
                            'stock_code': stock_symbol,
                            'year': year,
                            'status': 'failed',
                            'error': str(e),
                            'filename': None
                        })
                        failed_downloads += 1
                else:
                    # 未找到该年份的报告
                    results.append({
                        'stock_code': stock_symbol,
                        'year': year,
                        'status': 'failed',
                        'error': f'未找到 {year} 年的10-K报告',
                        'filename': None
                    })
                    failed_downloads += 1
            
        except Exception as e:
            print(f"    ❌ 下载过程中发生错误: {str(e)}")
            for year in years:
                results.append({
                    'stock_code': stock_symbol,
                    'year': year,
                    'status': 'failed',
                    'error': str(e),
                    'filename': None
                })
            failed_downloads = len(years)
        
        # 输出结果统计
        print(f"\n📊 美股 {stock_symbol} 10-K年报下载完成:")
        print(f"    ✅ 成功下载: {successful_downloads} 个")
        print(f"    ❌ 下载失败: {failed_downloads} 个")
        
        return results
    
    def _get_us_stock_cik(self, stock_symbol):
        """获取美股公司的CIK"""
        try:
            # 使用SEC公司ticker映射API
            url = "https://www.sec.gov/files/company_tickers.json"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                companies = response.json()
                
                # 查找匹配的股票代码
                for company_data in companies.values():
                    if company_data.get('ticker', '').upper() == stock_symbol.upper():
                        cik = str(company_data.get('cik_str', '')).zfill(10)
                        return cik
                        
        except Exception as e:
            print(f"    ⚠️ 获取CIK时出错: {str(e)}")
        
        return None
    
    def _get_us_10k_filings(self, cik, years):
        """获取指定年份的10-K报告列表"""
        try:
            # 使用SEC submissions API
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                return []
            
            data = response.json()
            filings_data = data.get('filings', {}).get('recent', {})
            
            if not filings_data:
                return []
            
            # 解析报告数据
            forms = filings_data.get('form', [])
            filing_dates = filings_data.get('filingDate', [])
            accession_numbers = filings_data.get('accessionNumber', [])
            primary_documents = filings_data.get('primaryDocument', [])
            
            filings = []
            for i, form in enumerate(forms):
                if form == '10-K' and i < len(filing_dates):
                    filing_date = filing_dates[i]
                    year = int(filing_date.split('-')[0])
                    
                    if year in years:
                        accession_no = accession_numbers[i].replace('-', '')
                        primary_doc = primary_documents[i]
                        
                        # 构建文档URL
                        document_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no}/{primary_doc}"
                        
                        filings.append({
                            'year': year,
                            'filing_date': filing_date,
                            'accession_number': accession_numbers[i],
                            'document_url': document_url,
                            'primary_document': primary_doc
                        })
            
            # 按年份排序
            filings.sort(key=lambda x: x['year'], reverse=True)
            return filings
            
        except Exception as e:
            print(f"    ⚠️ 获取10-K报告列表时出错: {str(e)}")
            return []
    
    def _download_us_filing_content(self, document_url):
        """通过浏览器获取SEC文档内容"""
        try:
            if not self.driver:
                self.init_selenium_driver()
            
            print(f"    🌐 访问SEC文档: {document_url}")
            self.driver.get(document_url)
            
            # 等待页面加载
            time.sleep(3)
            
            # 获取页面HTML内容
            html_content = self.driver.page_source
            
            if html_content and len(html_content) > 1000:  # 确保获取到了有效内容
                return html_content
            else:
                print(f"    ⚠️ 获取到的内容过短或为空")
                return None
                
        except Exception as e:
            print(f"    ⚠️ 获取文档内容时出错: {str(e)}")
            return None
    
    def _save_us_filing_as_html(self, html_content, filepath, stock_symbol, year):
        """将HTML内容保存为HTML文件"""
        try:
            # 清理HTML内容
            cleaned_html = self._clean_html_for_pdf(html_content)
            
            # 添加基本样式
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{stock_symbol} {year} 10-K Annual Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.4; }}
                    .header {{ text-align: center; margin-bottom: 30px; border-bottom: 2px solid #333; padding-bottom: 10px; }}
                    .content {{ max-width: 100%; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .page-break {{ page-break-before: always; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{stock_symbol} - 10-K Annual Report ({year})</h1>
                    <p>Downloaded from SEC EDGAR Database</p>
                </div>
                <div class="content">
                    {cleaned_html}
                </div>
            </body>
            </html>
            """
            
            # 直接保存为HTML文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(styled_html)
            return True
                    
        except Exception as e:
            print(f"    ⚠️ 保存HTML时出错: {str(e)}")
            return False

    def _save_us_filing_as_pdf(self, html_content, filepath, stock_symbol, year):
        """将HTML内容保存为PDF"""
        try:
            # 清理HTML内容
            cleaned_html = self._clean_html_for_pdf(html_content)
            
            # 添加基本样式
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{stock_symbol} {year} 10-K Annual Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.4; }}
                    .header {{ text-align: center; margin-bottom: 30px; border-bottom: 2px solid #333; padding-bottom: 10px; }}
                    .content {{ max-width: 100%; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .page-break {{ page-break-before: always; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{stock_symbol} - 10-K Annual Report ({year})</h1>
                    <p>Downloaded from SEC EDGAR Database</p>
                </div>
                <div class="content">
                    {cleaned_html}
                </div>
            </body>
            </html>
            """
            
            # 使用pdfkit转换为PDF
            try:
                import pdfkit
                
                # 配置wkhtmltopdf路径（Windows）
                config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
                
                options = {
                    'page-size': 'A4',
                    'margin-top': '0.75in',
                    'margin-right': '0.75in',
                    'margin-bottom': '0.75in',
                    'margin-left': '0.75in',
                    'encoding': "UTF-8",
                    'no-outline': None,
                    'enable-local-file-access': None
                }
                
                pdfkit.from_string(styled_html, filepath, options=options, configuration=config)
                return True
                
            except ImportError:
                print("    ⚠️ pdfkit未安装，尝试使用weasyprint...")
                try:
                    from weasyprint import HTML, CSS
                    HTML(string=styled_html).write_pdf(filepath)
                    return True
                except ImportError:
                    print("    ⚠️ weasyprint也未安装，保存为HTML文件...")
                    # 如果都没有安装，保存为HTML
                    html_filepath = filepath.replace('.pdf', '.html')
                    with open(html_filepath, 'w', encoding='utf-8') as f:
                        f.write(styled_html)
                    print(f"    💡 已保存为HTML文件: {html_filepath}")
                    return True
                    
        except Exception as e:
            print(f"    ⚠️ 保存PDF时出错: {str(e)}")
            return False
    
    def _clean_html_for_pdf(self, html_content):
        """清理HTML内容以便转换为PDF"""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 移除脚本和样式标签
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 移除一些可能导致问题的属性
            for tag in soup.find_all():
                if tag.name:
                    # 保留基本属性，移除可能有问题的属性
                    attrs_to_keep = ['href', 'src', 'alt', 'title', 'colspan', 'rowspan']
                    new_attrs = {}
                    for attr in attrs_to_keep:
                        if attr in tag.attrs:
                            new_attrs[attr] = tag.attrs[attr]
                    tag.attrs = new_attrs
            
            # 获取body内容，如果没有body就返回全部
            body = soup.find('body')
            if body:
                return str(body)
            else:
                return str(soup)
                
        except Exception as e:
            print(f"    ⚠️ 清理HTML时出错: {str(e)}")
            # 如果清理失败，返回原始内容
            return html_content
    
    def enhanced_year_matching(self, title, target_year):
        """
        增强的年份匹配函数，支持数字和中文年份格式
        
        Args:
            title (str): 公告标题
            target_year (int): 目标年份
            
        Returns:
            bool: 是否匹配
        """
        if not title or not target_year:
            return False
        
        title_lower = title.lower()
        year_str = str(target_year)
        
        # 1. 直接数字匹配
        if year_str in title:
            return True
        
        # 2. 中文数字映射
        chinese_digits = {
            '0': ['〇', '零', 'O', 'o'],
            '1': ['一', '壹'],
            '2': ['二', '贰', '貳'],
            '3': ['三', '叁', '參'],
            '4': ['四', '肆'],
            '5': ['五', '伍'],
            '6': ['六', '陆', '陸'],
            '7': ['七', '柒'],
            '8': ['八', '捌'],
            '9': ['九', '玖']
        }
        
        def generate_chinese_patterns(year_str):
            """递归生成所有可能的中文数字组合"""
            if not year_str:
                return ['']
            
            first_digit = year_str[0]
            rest_patterns = generate_chinese_patterns(year_str[1:])
            
            patterns = []
            for chinese_char in chinese_digits.get(first_digit, [first_digit]):
                for rest_pattern in rest_patterns:
                    patterns.append(chinese_char + rest_pattern)
            
            return patterns
        
        # 3. 生成所有可能的中文年份格式
        chinese_patterns = generate_chinese_patterns(year_str)
        
        for pattern in chinese_patterns:
            if pattern in title:
                return True
        
        # 4. 港股特殊格式匹配
        hk_patterns = [
            f"{year_str}年度报告",
            f"{year_str}年年度报告", 
            f"{year_str}年报",
            f"{year_str} annual report",
            f"annual report {year_str}",
            f"年度报告{year_str}",
            f"企业年度报告{year_str}",
            f"h股公告年度报告{year_str}"
        ]
        
        for pattern in hk_patterns:
            if pattern in title_lower:
                return True
        
        # 5. 中文年份 + 年度报告格式
        for pattern in chinese_patterns:
            chinese_year_patterns = [
                f"{pattern}年度报告",
                f"{pattern}年年度报告",
                f"{pattern}年报",
                f"年度报告{pattern}",
                f"企业年度报告{pattern}"
            ]
            
            for chinese_pattern in chinese_year_patterns:
                if chinese_pattern in title:
                    return True
        
        return False





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





def main():
    # 打印欢迎信息
    print("================================================================")
    print('Annual Report Crawler - WebDriver "Otako" Version')
    print("Developed by Terence WANG")
    print("================================================================")
    
    parser = argparse.ArgumentParser(description="年报下载器，支持A股、港股和美股。")
    
    # 添加参数
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', '--stock', type=str, help='股票代码（A股6位代码或5位港股代码）')
    group.add_argument('-f', '--file', type=str, help='包含股票代码的文本文件路径')
    
    parser.add_argument('-y', '--years', type=str, required=True,
                       help='年份范围，支持格式 2020 | 2020-2022 | 2020,2021,2022')
    parser.add_argument('-d', '--dir', type=str, default='annual_reports',
                       help='下载目录 (默认: annual_reports)')
    
    args = parser.parse_args()
    
    # 解析年份
    try:
        years = parse_year_range(args.years)
        print(f"📅 目标年份: {years}")
    except Exception as e:
        print(f"🔄 年份格式错误: {e}")
        sys.exit(1)
    
    # 获取股票代码列表
    if args.stock:
        stock_codes = [args.stock]
    else:
        stock_codes = load_stock_codes_from_file(args.file)
    
    if not stock_codes:
        print("🔄 没有找到有效的股票代码")
        sys.exit(1)
    
    # 开始下载
    with AnnualReportDownloader(args.dir) as downloader:
        downloader.process_stock_list(stock_codes, years)
        downloader.print_summary()





if __name__ == "__main__":

    main()

 