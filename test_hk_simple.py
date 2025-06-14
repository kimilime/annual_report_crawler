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
    chrome_options.add_argument('--log-level=3')
    
    # 初始化driver
    local_chromedriver = Path("./chromedriver.exe")
    service = Service(str(local_chromedriver.absolute()))
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # 格式化港股代码
        hk_code = stock_code.zfill(5)
        
        # 使用正确的建设银行orgId
        if stock_code == "00939":
            org_id = "9900003682"  # 建设银行的正确orgId
        else:
            org_id = f"gshk{stock_code.zfill(7)}"
        print(f"使用orgId: {org_id}")
        
        # 访问港股页面
        url = f"https://www.cninfo.com.cn/new/disclosure/stock?stockCode={hk_code}&orgId={org_id}&sjstsBond=false"
        print(f"访问: {url}")
        
        driver.get(url)
        time.sleep(5)
        
        # 查找搜索框 - 使用多种选择器
        search_box = None
        search_selectors = [
            "input[placeholder*='标题关键字']",
            "input[placeholder*='搜索']", 
            "input[type='text']",
            ".search input",
            "[class*='search'] input"
        ]
        
        for selector in search_selectors:
            try:
                search_box = driver.find_element(By.CSS_SELECTOR, selector)
                if search_box and search_box.is_displayed():
                    print(f"找到搜索框: {selector}")
                    break
            except:
                continue
        
        if not search_box:
            print("未找到搜索框")
            return False
        
        # 搜索年度报告 - 不指定年份，看看所有年报
        search_keywords = "年度报告"
        search_box.clear()
        search_box.send_keys(search_keywords)
        print(f"搜索: {search_keywords}")
        
        # 点击搜索
        search_btn = driver.find_element(By.CSS_SELECTOR, "[class*='search'] button")
        search_btn.click()
        time.sleep(5)
        
        # 查找结果
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        print(f"找到 {len(rows)} 行数据")
        
        # 检查前20行，寻找指定年份的年报
        for i, row in enumerate(rows[:20]):
            try:
                tds = row.find_elements(By.CSS_SELECTOR, "td")
                if len(tds) >= 2:
                    # 尝试获取标题 - 通常在第一列或第二列
                    title = ""
                    if len(tds) >= 2:
                        title = tds[0].text.strip() or tds[1].text.strip()
                    
                    print(f"[{i+1}] {title[:80]}...")
                    
                    # 检查是否为年报
                    if (str(year) in title and 
                        ('年度报告' in title or '年报' in title) and
                        '摘要' not in title and '关于' not in title):
                        print(f"✓ 找到年报: {title}")
                        return True
            except Exception as e:
                print(f"[{i+1}] 解析错误: {e}")
                continue
        
        print("未找到年报")
        return False
        
    except Exception as e:
        print(f"错误: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    # 测试建设银行2023年报（应该已经发布）
    success = test_hk_download("00939", 2023)
    print(f"测试结果: {'成功' if success else '失败'}") 