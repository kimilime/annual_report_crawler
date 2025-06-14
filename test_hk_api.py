#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试港股API下载功能
"""

import sys
from annual_report_downloader import AnnualReportDownloader

def test_hk_search():
    """测试港股公司搜索功能"""
    print("=" * 50)
    print("测试港股公司搜索功能")
    print("=" * 50)
    
    with AnnualReportDownloader("test_downloads") as downloader:
        # 测试搜索不同的港股代码
        test_codes = [
            "00700",  # 腾讯控股
            "00388",  # 香港交易所
            "01211",  # 比亚迪股份
            "03690",  # 美团
            "09988",  # 阿里巴巴
        ]
        
        for code in test_codes:
            print(f"\n🔍 测试搜索港股: {code}")
            found_code, company_name, org_id = downloader.search_hk_company_by_name(code)
            
            if found_code:
                print(f"  ✓ 找到公司: {company_name}")
                print(f"  ✓ 股票代码: {found_code}")
                print(f"  ✓ orgId: {org_id}")
            else:
                print(f"  ✗ 未找到公司信息")

def test_hk_download():
    """测试港股年报下载"""
    print("\n" + "=" * 50)
    print("测试港股年报下载功能")
    print("=" * 50)
    
    # 测试腾讯控股2023年年报
    test_stock = "00700"
    test_years = [2023]
    
    with AnnualReportDownloader("test_downloads") as downloader:
        results = downloader.download_hk_reports(test_stock, test_years)
        
        print(f"\n📊 下载结果:")
        for result in results:
            print(f"  股票: {result['stock_code']}")
            print(f"  年份: {result['year']}")
            print(f"  状态: {result['status']}")
            if result['status'] == 'success':
                print(f"  文件: {result['filename']}")
            else:
                print(f"  错误: {result.get('error', '未知错误')}")

def main():
    """主函数"""
    print("港股API下载功能测试")
    print("=" * 60)
    
    try:
        # 1. 测试搜索功能
        test_hk_search()
        
        # 2. 测试下载功能
        test_hk_download()
        
        print("\n" + "=" * 60)
        print("✓ 测试完成")
        
    except Exception as e:
        print(f"\n✗ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 