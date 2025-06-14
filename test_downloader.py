#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
年报下载器测试脚本
用于验证不同股票类型的识别和基本功能
"""

from annual_report_downloader import AnnualReportDownloader, StockType, parse_year_range

def test_stock_type_identification():
    """测试股票类型识别功能"""
    print("🧪 测试股票类型识别")
    print("=" * 40)
    
    downloader = AnnualReportDownloader()
    
    test_cases = [
        ("000001", StockType.A_MAIN),
        ("600519", StockType.A_MAIN), 
        ("688001", StockType.A_STAR),
        ("688009", StockType.A_STAR),
        ("300001", StockType.A_GEM),
        ("300750", StockType.A_GEM),
        ("00700", StockType.HK),
        ("00939", StockType.HK),
        ("HK00700", StockType.HK),
        ("123", StockType.UNKNOWN),
        ("abcdef", StockType.UNKNOWN)
    ]
    
    for stock_code, expected_type in test_cases:
        actual_type = downloader.identify_stock_type(stock_code)
        status = "✓" if actual_type == expected_type else "✗"
        print(f"{status} {stock_code:>8} -> {actual_type}")
    
    print()

def test_year_parsing():
    """测试年份解析功能"""
    print("🧪 测试年份解析")
    print("=" * 40)
    
    test_cases = [
        ("2022", [2022]),
        ("2020-2022", [2020, 2021, 2022]),
        ("2019,2021,2023", [2019, 2021, 2023]),
        ("2020-2021", [2020, 2021])
    ]
    
    for year_str, expected in test_cases:
        try:
            actual = parse_year_range(year_str)
            status = "✓" if actual == expected else "✗"
            print(f"{status} '{year_str}' -> {actual}")
        except Exception as e:
            print(f"✗ '{year_str}' -> 错误: {e}")
    
    print()

def test_orgid_retrieval():
    """测试orgId获取功能"""
    print("🧪 测试orgId获取")
    print("=" * 40)
    
    downloader = AnnualReportDownloader()
    
    test_stocks = ["300750", "688001", "000001"]
    
    for stock in test_stocks:
        print(f"测试股票 {stock}:")
        try:
            org_id = downloader.get_orgid_for_stock(stock)
            if org_id:
                print(f"  ✓ orgId: {org_id}")
            else:
                print(f"  ✗ 无法获取orgId")
        except Exception as e:
            print(f"  ✗ 错误: {e}")
    
    print()

def main():
    """主测试函数"""
    print("🚀 巨潮网年报下载器 - 功能测试")
    print("=" * 50)
    print()
    
    # 运行测试
    test_stock_type_identification()
    test_year_parsing()
    test_orgid_retrieval()
    
    print("📋 测试完成")
    print("\n💡 如需下载年报，请运行:")
    print("   python annual_report_downloader.py -s 000001 -y 2022")

if __name__ == "__main__":
    main() 