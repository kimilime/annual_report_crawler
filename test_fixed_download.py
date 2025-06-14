#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的下载功能
"""

from annual_report_downloader import AnnualReportDownloader

def test_fixed_download():
    """测试修复后的下载功能"""
    print("=" * 80)
    print("测试修复后的科创板和创业板下载功能")
    print("=" * 80)
    
    # 测试股票
    test_stocks = [
        ("688001", "科创板", "华兴源创"),
        ("300750", "创业板", "宁德时代"),
    ]
    
    downloader = AnnualReportDownloader("test_downloads")
    
    for stock_code, board_type, company_name in test_stocks:
        print(f"\n{'='*60}")
        print(f"测试股票: {stock_code} ({board_type} - {company_name})")
        print(f"{'='*60}")
        
        # 测试下载2023年年报
        years = [2023]
        results = downloader.download_a_stock_main_reports(stock_code, years)
        
        print(f"\n📋 下载结果:")
        for result in results:
            year = result['year']
            status = result['status']
            if status == 'success':
                filename = result.get('filename', '')
                print(f"  ✓ {year}年: {filename}")
            else:
                error = result.get('error', '未知错误')
                print(f"  ❌ {year}年: {status} - {error}")

def main():
    """主函数"""
    test_fixed_download()

if __name__ == "__main__":
    main() 