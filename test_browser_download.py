#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试浏览器下载功能
"""

from annual_report_downloader_bd import AnnualReportDownloader

def test_browser_download():
    """测试浏览器下载功能"""
    print("🧪 开始测试浏览器下载功能...")
    
    # 创建下载器实例
    downloader = AnnualReportDownloader("test_downloads")
    
    try:
        # 测试A股主板股票（例如：000001 平安银行）
        print("\n📊 测试A股主板股票下载...")
        results = downloader.download_stock_reports("000001", [2023])
        
        print(f"\n📈 测试结果:")
        for result in results:
            print(f"  股票: {result['stock_code']}")
            print(f"  年份: {result['year']}")
            print(f"  状态: {result['status']}")
            if result.get('filename'):
                print(f"  文件: {result['filename']}")
            if result.get('error'):
                print(f"  错误: {result['error']}")
            print()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    finally:
        # 清理资源
        if hasattr(downloader, 'driver') and downloader.driver:
            downloader.driver.quit()
        print("✅ 测试完成")

if __name__ == "__main__":
    test_browser_download() 