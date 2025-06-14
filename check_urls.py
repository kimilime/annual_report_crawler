#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查映射表URL
"""

import requests

def check_urls():
    """检查映射表URL"""
    urls = [
        "http://www.cninfo.com.cn/new/data/szse_stock.json",
        "http://www.cninfo.com.cn/new/data/sse_stock.json",
        "http://static.cninfo.com.cn/finalpage/stock-list/szse_stock.json",
        "http://static.cninfo.com.cn/finalpage/stock-list/sse_stock.json",
    ]
    
    for url in urls:
        print(f"检查URL: {url}")
        try:
            response = requests.get(url, timeout=10)
            print(f"  状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  数据类型: {type(data)}")
                if isinstance(data, dict):
                    print(f"  键: {list(data.keys())}")
                    if 'stockList' in data:
                        print(f"  股票数量: {len(data['stockList'])}")
                        if data['stockList']:
                            sample = data['stockList'][0]
                            print(f"  样本: {sample}")
                elif isinstance(data, list):
                    print(f"  列表长度: {len(data)}")
                    if data:
                        print(f"  样本: {data[0]}")
        except Exception as e:
            print(f"  错误: {e}")
        print()

if __name__ == "__main__":
    check_urls() 