#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的港股下载功能
"""

import sys
from annual_report_downloader import AnnualReportDownloader

def test_hk_fixed():
    """测试修复后的港股下载功能"""
    print("测试修复后的港股下载功能")
    print("=" * 60)
    
    # 测试问题股票
    test_cases = [
        ("00939", [2023, 2024]),  # 建设银行
        ("HK00700", [2023]),      # 腾讯控股（带HK前缀）
        ("00700", [2023]),        # 腾讯控股（不带前缀）
    ]
    
    with AnnualReportDownloader("test_downloads_fixed") as downloader:
        for stock_code, years in test_cases:
            print(f"\n{'='*50}")
            print(f"测试股票: {stock_code}")
            print(f"年份: {years}")
            print(f"{'='*50}")
            
            results = downloader.download_hk_reports(stock_code, years)
            
            print(f"\n📊 下载结果:")
            for result in results:
                print(f"  股票: {result['stock_code']}")
                print(f"  年份: {result['year']}")
                print(f"  状态: {result['status']}")
                if result['status'] == 'success':
                    print(f"  文件: {result['filename']}")
                else:
                    print(f"  错误: {result.get('error', '未知错误')}")
                print()

def main():
    """主函数"""
    try:
        test_hk_fixed()
        print("\n" + "=" * 60)
        print("✓ 测试完成")
        
    except Exception as e:
        print(f"\n✗ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 