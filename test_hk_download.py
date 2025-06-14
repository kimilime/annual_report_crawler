#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from pathlib import Path

def test_hk_download(stock_code, year):
    """测试港股年报下载"""
    
    # Chrome选项配置
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-plugins')
    chrome_options.add_argument('--disable-images')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--silent')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    # 初始化driver
    local_chromedriver = Path("./chromedriver.exe")
    service = Service(str(local_chromedriver.absolute()))
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # 格式化港股代码
        if stock_code.startswith('HK'):
            hk_code = stock_code[2:].zfill(5)
        else:
            hk_code = stock_code.zfill(5)
        
        # 动态获取orgId
        print(f"🔍 正在获取 {hk_code} 的真实orgId...")
        
        # 方法1: 通过API获取
        api_url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        params = {
            "stock": hk_code,
            "tabName": "fulltext", 
            "pageSize": 5,
            "pageNum": 1,
            "column": "szse",
            "category": "",
            "plate": "",
            "seDate": "2020-01-01~2025-12-31",
            "searchkey": "",
            "secid": "",
            "sortName": "pubdate",
            "sortType": "desc",
            "isHLtitle": "true"
        }
        
        response = requests.post(api_url, headers=headers, data=params, timeout=15)
        org_id = None
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('announcements') and len(result['announcements']) > 0:
                    org_id = result['announcements'][0].get('orgId')
                    if org_id:
                        print(f"✓ 通过API获取到 {hk_code} 的真实orgId: {org_id}")
            except Exception as e:
                print(f"⚠️ 解析API响应失败: {e}")
        
        # 方法2: 搜索页面获取
        if not org_id:
            print(f"⚠️ 无法获取真实orgId，尝试使用通用方法...")
            try:
                search_url = f"https://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&lastPage=index"
                driver.get(search_url)
                time.sleep(3)
                
                search_selectors = [
                    "input[placeholder*='证券代码']",
                    "input[placeholder*='证券']",
                    "input[type='text']"
                ]
                
                for selector in search_selectors:
                    try:
                        search_input = driver.find_element(By.CSS_SELECTOR, selector)
                        if search_input:
                            search_input.clear()
                            search_input.send_keys(hk_code)
                            search_input.send_keys(Keys.ENTER)
                            time.sleep(3)
                            
                            links = driver.find_elements(By.CSS_SELECTOR, "a[href*='orgId']")
                            if links:
                                href = links[0].get_attribute('href')
                                if 'orgId=' in href:
                                    org_id = href.split('orgId=')[1].split('&')[0]
                                    print(f"✓ 从搜索结果获取到orgId: {org_id}")
                                    break
                            break
                    except:
                        continue
            except Exception as e:
                print(f"⚠️ 搜索页面获取orgId失败: {e}")
        
        # 方法3: 备用格式
        if not org_id:
            if stock_code.startswith('HK'):
                hk_org_code = stock_code[2:].zfill(7)
            else:
                hk_org_code = stock_code.zfill(7)
            org_id = f"gshk{hk_org_code}"
            print(f"⚠️ 使用备用orgId格式: {org_id}")
        
        # 访问港股页面
        url = f"https://www.cninfo.com.cn/new/disclosure/stock?stockCode={hk_code}&orgId={org_id}&sjstsBond=false"
        print(f"🌐 访问港股页面: {url}")
        
        driver.get(url)
        time.sleep(3)
        
        print(f"📥 正在搜索 {stock_code} {year}年年报...")
        
        # 重新访问页面，确保状态干净
        driver.get(url)
        time.sleep(3)
        
        # 使用精确搜索
        print(f"🔍 使用精确搜索: {year}年度报告...")
        
        # 查找搜索框
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
                search_box = driver.find_element(By.CSS_SELECTOR, selector)
                if search_box and search_box.is_displayed():
                    print(f"找到搜索框: {selector}")
                    break
            except:
                continue
        
        # 跳过日期筛选器设置，依靠搜索关键词筛选
        print(f"🗓️ 跳过日期筛选器设置，依靠搜索关键词筛选...")
        
        if search_box:
            # 清空搜索框并输入精确的搜索关键词
            search_box.clear()
            search_keywords = f"{year}年度报告"
            search_box.send_keys(search_keywords)
            print(f"输入精确搜索关键词: {search_keywords}")
            
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
                    search_btn = driver.find_element(By.CSS_SELECTOR, btn_selector)
                    if search_btn and search_btn.is_displayed():
                        search_btn.click()
                        print(f"点击搜索按钮: {btn_selector}")
                        search_clicked = True
                        break
                except:
                    continue
            
            if not search_clicked:
                search_box.send_keys(Keys.ENTER)
                print(f"按回车键搜索")
            
            time.sleep(5)
        else:
            print(f"⚠️ 未找到搜索框，跳过此年份")
            return False
        
        # 查找搜索结果表格
        table_selectors = [
            "table tbody tr",
            ".disclosure-table tbody tr", 
            "[class*='table'] tbody tr",
            "tr"
        ]
        
        rows = []
        for selector in table_selectors:
            try:
                rows = driver.find_elements(By.CSS_SELECTOR, selector)
                if rows:
                    print(f"精确搜索后找到 {len(rows)} 行数据")
                    break
            except:
                continue
        
        # 检查前20行结果
        found_report = False
        
        if rows:
            print(f"检查前20行精确搜索结果...")
            
            for i, row in enumerate(rows[:20]):  # 检查前20行
                try:
                    print(f"正在解析第 {i+1} 行...")
                    
                    # 先查看表格结构
                    tds = row.find_elements(By.CSS_SELECTOR, "td")
                    print(f"  第 {i+1} 行有 {len(tds)} 列")
                    
                    # 尝试获取所有列的文本内容
                    row_texts = []
                    for j, td in enumerate(tds):
                        text = td.text.strip()
                        if text:
                            row_texts.append(f"列{j+1}: {text[:50]}")
                    
                    if row_texts:
                        print(f"  行内容: {' | '.join(row_texts)}")
                    
                    # 获取标题
                    title = ""
                    title_element = None
                    
                    try:
                        title_element = row.find_element(By.CSS_SELECTOR, "td a")
                        title = title_element.text.strip()
                        print(f"  找到标题链接: {title[:40]}...")
                    except:
                        try:
                            title_element = row.find_element(By.CSS_SELECTOR, "a")
                            title = title_element.text.strip()
                            print(f"  找到链接: {title[:40]}...")
                        except:
                            try:
                                if len(tds) >= 2:
                                    title = tds[1].text.strip()
                                    if title:
                                        print(f"  找到文本标题: {title[:40]}...")
                                        try:
                                            title_element = tds[1].find_element(By.CSS_SELECTOR, "a")
                                        except:
                                            title_element = None
                            except:
                                print(f"  第 {i+1} 行无法获取标题")
                                continue
                    
                    if not title:
                        print(f"  第 {i+1} 行标题为空，跳过")
                        continue
                        
                    # 显示所有条目，便于调试
                    print(f"[{i+1}] 标题: {title[:60]}...")
                    
                    # 严格的年报匹配条件
                    is_annual_report = (
                        str(year) in title and 
                        ('年度报告' in title or '年报' in title or 'Annual Report' in title.title()) and
                        '摘要' not in title and
                        '监管' not in title and
                        '回复' not in title and
                        '问询' not in title and
                        '函' not in title and
                        '意见' not in title and
                        '更正' not in title and
                        '补充' not in title and
                        '关于' not in title and
                        '自愿性' not in title and
                        '披露公告' not in title and
                        '英文' not in title and
                        '简版' not in title
                    )
                    
                    if is_annual_report:
                        print(f"✓ 找到年报: {title}")
                        found_report = True
                        
                        if title_element:
                            try:
                                detail_href = title_element.get_attribute('href')
                                print(f"  链接href: {detail_href}")
                                
                                if detail_href:
                                    driver.get(detail_href)
                                    time.sleep(3)
                                    detail_url = driver.current_url
                                    print(f"  详情页URL: {detail_url}")
                                    
                                    # 从URL中提取参数
                                    from urllib.parse import urlparse, parse_qs
                                    parsed_url = urlparse(detail_url)
                                    query_params = parse_qs(parsed_url.query)
                                    
                                    announcement_id = query_params.get('announcementId', [None])[0]
                                    announcement_time = query_params.get('announcementTime', [None])[0]
                                    
                                    if announcement_id and announcement_time:
                                        announcement_date = announcement_time.split(' ')[0] if ' ' in announcement_time else announcement_time
                                        pdf_url = f"https://static.cninfo.com.cn/finalpage/{announcement_date}/{announcement_id}.PDF"
                                        print(f"  构造PDF下载链接: {pdf_url}")
                                        
                                        # 测试PDF链接是否有效
                                        pdf_response = requests.head(pdf_url, timeout=10)
                                        if pdf_response.status_code == 200:
                                            print(f"✓ PDF链接有效，可以下载")
                                            return True
                                        else:
                                            print(f"✗ PDF链接无效: {pdf_response.status_code}")
                                    else:
                                        print(f"⚠️ 无法从URL中提取必要参数")
                            except Exception as e:
                                print(f"✗ 处理链接时出错: {e}")
                        
                        break
                        
                except Exception as e:
                    print(f"解析第{i+1}行时出错: {e}")
                    continue
        
        if not found_report:
            print(f"✗ 未找到 {stock_code} {year}年年报")
            return False
            
    except Exception as e:
        print(f"✗ 测试过程出错: {e}")
        return False
    finally:
        driver.quit()
    
    return found_report

if __name__ == "__main__":
    # 测试建设银行2024年报
    success = test_hk_download("00939", 2024)
    print(f"\n测试结果: {'成功' if success else '失败'}") 