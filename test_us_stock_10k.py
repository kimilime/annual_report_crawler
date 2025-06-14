#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试美股10-K年报下载功能
"""

import sys
from pathlib import Path
from annual_report_downloader import AnnualReportDownloader

def test_us_stock_10k():
    """测试美股10-K下载功能"""
    print("🇺🇸 开始测试美股10-K下载功能...")
    
    # 测试用例 - 选择一些知名的美股公司
    test_cases = [
        ("AAPL", [2023], "苹果公司"),
        ("MSFT", [2023], "微软公司"),
        ("GOOGL", [2023], "谷歌公司"),
    ]
    
    downloader = AnnualReportDownloader("test_us_reports")
    
    total_tests = len(test_cases)
    successful_tests = 0
    
    try:
        for i, (stock_symbol, years, description) in enumerate(test_cases, 1):
            print(f"\n{'='*60}")
            print(f"测试 {i}/{total_tests}: {description} ({stock_symbol})")
            print(f"{'='*60}")
            
            try:
                # 测试股票类型识别
                stock_type = downloader.identify_stock_type(stock_symbol)
                print(f"    📊 股票类型识别: {stock_type}")
                
                if stock_type != "美股":
                    print(f"    ❌ 股票类型识别错误，期望'美股'，实际'{stock_type}'")
                    continue
                
                # 下载年报
                results = downloader.download_stock_reports(stock_symbol, years)
                
                # 检查结果
                success_count = sum(1 for r in results if r.get('status') == 'success')
                total_count = len(results)
                
                print(f"    📈 下载结果: {success_count}/{total_count} 成功")
                
                if success_count > 0:
                    successful_tests += 1
                    print(f"    ✅ {description} 测试通过")
                    
                    # 显示成功下载的文件
                    for result in results:
                        if result.get('status') == 'success':
                            print(f"    📄 成功下载: {result.get('filename', 'N/A')}")
                else:
                    print(f"    ❌ {description} 测试失败")
                    for result in results:
                        if result.get('status') != 'success':
                            print(f"    🔸 失败原因: {result.get('error', 'Unknown error')}")
                
            except Exception as e:
                print(f"    ❌ 测试过程中出现异常: {e}")
                import traceback
                traceback.print_exc()
    
    finally:
        # 清理资源
        if hasattr(downloader, 'driver') and downloader.driver:
            downloader.driver.quit()
    
    # 输出测试总结
    print(f"\n{'='*60}")
    print(f"🎯 美股10-K下载测试总结")
    print(f"{'='*60}")
    print(f"总测试数: {total_tests}")
    print(f"成功测试: {successful_tests}")
    print(f"失败测试: {total_tests - successful_tests}")
    print(f"成功率: {successful_tests/total_tests*100:.1f}%")
    
    if successful_tests == total_tests:
        print("🎉 所有测试通过！美股10-K下载功能正常工作")
    else:
        print("⚠️  部分测试失败，请检查相关功能")

if __name__ == "__main__":
    test_us_stock_10k() 