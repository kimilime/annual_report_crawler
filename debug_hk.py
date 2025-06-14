#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试港股下载问题
"""

import requests
import json
from annual_report_downloader import AnnualReportDownloader

def debug_hk_search(stock_code):
    """调试港股搜索"""
    print(f"=" * 60)
    print(f"调试港股搜索: {stock_code}")
    print(f"=" * 60)
    
    api_url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    params = {
        "stock": "",
        "tabName": "fulltext",
        "pageSize": 10,
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
    
    try:
        print(f"🔍 发送请求...")
        print(f"URL: {api_url}")
        print(f"参数: {params}")
        
        response = requests.post(api_url, headers=headers, data=params, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"响应类型: {type(result)}")
                print(f"响应键: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
                
                announcements = result.get('announcements', [])
                print(f"公告数量: {len(announcements) if announcements else 'None'}")
                
                if announcements:
                    print(f"\n前3条公告:")
                    for i, ann in enumerate(announcements[:3]):
                        print(f"  [{i+1}] 代码: {ann.get('secCode', 'N/A')}")
                        print(f"      名称: {ann.get('secName', 'N/A')}")
                        print(f"      orgId: {ann.get('orgId', 'N/A')}")
                        print(f"      标题: {ann.get('announcementTitle', 'N/A')[:50]}...")
                        print()
                else:
                    print("❌ 没有找到公告")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析错误: {e}")
                print(f"响应内容: {response.text[:500]}...")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text[:500]}...")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def debug_hk_annual_search(company_name, stock_code):
    """调试港股年报搜索"""
    print(f"\n" + "=" * 60)
    print(f"调试年报搜索: {company_name} ({stock_code})")
    print(f"=" * 60)
    
    api_url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # 清理公司名称中的HTML标签
    clean_name = company_name.replace('<em>', '').replace('</em>', '')
    
    search_terms = ["年度报告", "年报"]
    
    for term in search_terms:
        print(f"\n🔍 搜索: {clean_name} {term}")
        
        params = {
            "stock": "",
            "tabName": "fulltext",
            "pageSize": 30,
            "pageNum": 1,
            "column": "",
            "category": "",
            "plate": "",
            "seDate": "2020-01-01~2025-12-31",
            "searchkey": f"{clean_name} {term}",
            "secid": "",
            "sortName": "pubdate",
            "sortType": "desc",
            "isHLtitle": "true"
        }
        
        try:
            response = requests.post(api_url, headers=headers, data=params, timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                announcements = result.get('announcements', [])
                
                if announcements:
                    print(f"  ✓ 找到 {len(announcements)} 条公告")
                    
                    # 查找年报
                    found_years = []
                    for ann in announcements:
                        title = ann.get('announcementTitle', '')
                        sec_code = ann.get('secCode', '')
                        adj_url = ann.get('adjunctUrl', '')
                        
                        # 检查是否是目标公司
                        if sec_code == stock_code:
                            # 检查年份
                            for year in [2021, 2022, 2023, 2024]:
                                if str(year) in title and '年度报告' in title:
                                    found_years.append(year)
                                    print(f"    ★ 找到 {year} 年报: {title}")
                                    print(f"      PDF链接: {adj_url}")
                    
                    if not found_years:
                        print(f"  ❌ 没有找到 {stock_code} 的年报")
                        print(f"  📋 显示前5条公告:")
                        for i, ann in enumerate(announcements[:5]):
                            print(f"    [{i+1}] {ann.get('secCode', 'N/A')} - {ann.get('announcementTitle', 'N/A')[:60]}...")
                else:
                    print(f"  ❌ 无结果")
            else:
                print(f"  ❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ 搜索异常: {e}")

def main():
    """主函数"""
    print("港股下载问题调试")
    print("=" * 80)
    
    # 测试问题股票
    test_cases = [
        ("00939", "建设银行"),
        ("HK00700", "腾讯控股"),
        ("00700", "腾讯控股")
    ]
    
    for stock_code, expected_name in test_cases:
        # 1. 调试搜索
        debug_hk_search(stock_code)
        
        # 2. 如果找到公司，调试年报搜索
        if stock_code == "00939":
            debug_hk_annual_search("建设银行", "00939")
        elif stock_code in ["00700", "HK00700"]:
            debug_hk_annual_search("腾讯控股", "00700")

if __name__ == "__main__":
    main() 