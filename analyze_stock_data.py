#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析股票数据
"""

import requests

def analyze_stock_data():
    """分析股票数据"""
    print("分析深圳交易所数据...")
    
    try:
        response = requests.get("http://www.cninfo.com.cn/new/data/szse_stock.json", timeout=10)
        data = response.json()
        stock_list = data.get('stockList', [])
        
        print(f"总股票数量: {len(stock_list)}")
        
        # 按股票代码前缀分类
        prefixes = {}
        for stock in stock_list:
            code = stock.get('code', '')
            if code:
                prefix = code[:3]
                if prefix not in prefixes:
                    prefixes[prefix] = []
                prefixes[prefix].append(stock)
        
        print("\n按前缀分类:")
        for prefix in sorted(prefixes.keys()):
            stocks = prefixes[prefix]
            print(f"  {prefix}xxx: {len(stocks)} 个股票")
            if len(stocks) <= 3:
                for stock in stocks:
                    print(f"    {stock['code']} - {stock.get('zwjc', '')}")
        
        # 检查是否有科创板和上海主板
        sse_stocks = []
        for stock in stock_list:
            code = stock.get('code', '')
            if code.startswith('60') or code.startswith('688'):
                sse_stocks.append(stock)
        
        print(f"\n上海交易所股票数量: {len(sse_stocks)}")
        if sse_stocks:
            print("样本:")
            for stock in sse_stocks[:5]:
                print(f"  {stock['code']} - {stock.get('zwjc', '')} - orgId: {stock.get('orgId', '')}")
        
        # 检查科创板
        star_stocks = [s for s in stock_list if s.get('code', '').startswith('688')]
        print(f"\n科创板股票数量: {len(star_stocks)}")
        if star_stocks:
            print("科创板样本:")
            for stock in star_stocks[:5]:
                print(f"  {stock['code']} - {stock.get('zwjc', '')} - orgId: {stock.get('orgId', '')}")
        
        # 检查创业板
        gem_stocks = [s for s in stock_list if s.get('code', '').startswith('300')]
        print(f"\n创业板股票数量: {len(gem_stocks)}")
        if gem_stocks:
            print("创业板样本:")
            for stock in gem_stocks[:5]:
                print(f"  {stock['code']} - {stock.get('zwjc', '')} - orgId: {stock.get('orgId', '')}")
                
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    analyze_stock_data() 