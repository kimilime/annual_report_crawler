# 年报下载器 (Annual Report Crawler)

**版本: 2.0.0 (Otako & Mizuki)**

一个功能强大的年报下载工具，支持A股、港股和美股，提供两种模式以适应不同使用环境。

---

## 🔥 两大版本

本项目提供两种核心版本，以满足不同用户的需求。

### 🌐 Browser "Otako" Version (浏览器模式)
**核心特性**:
- ✅ **环境兼容**: 通过模拟浏览器下载，能有效规避部分企业环境（如绿盾、域之盾）下的文件加密或拦截问题。
- ✅ **过程透明**: 可选择显示浏览器窗口，直观看到下载过程。
- ✅ **功能完整**: 支持全市场年报下载。

**启动方式**:
- 双击运行 `start_web_bd.bat`
- 浏览器访问 `http://localhost:30331`

### 📊 Requests "Mizuki" Version (请求模式)
**核心特性**:
- ✅ **高效快速**: 采用经典的 `requests` 库进行HTTP请求，下载速度更快，资源占用更少。
- ✅ **经典稳定**: 历经考验的下载方式，适合绝大多数个人使用场景。
- ✅ **命令行友好**: 核心脚本可直接通过命令行调用，方便集成与自动化。

**启动方式**:
- 双击运行 `start_web_rq.bat`
- 或命令行执行 `python annual_report_downloader_rq.py`

## 核心功能

- 🚀 **全市场支持**: 支持A股（主板、科创板、创业板）、港股、美股。
- 💡 **智能识别**: 自动根据股票代码格式识别市场及板块。
- 📥 **批量下载**: 支持通过Web界面或命令行进行批量下载。
- 📅 **灵活年份**: 支持单年份、年份范围或不连续年份列表。
- ✨ **现代化Web界面**: 操作直观，实时反馈进度、日志和结果。
- 📄 **多格式支持**: A股和港股下载为PDF格式，美股下载为HTML格式的10-K报告。
- 📈 **详细报告**: 任务完成后提供详细的下载统计与失败原因分析。
- 🔒 **企业友好**: 浏览器模式完美适配企业安全环境。

## 部署与安装

#### 1. 基础环境

- **Python**: 3.7+
- **自动安装依赖**: 各版本的启动脚本 (`.bat`) 会自动检测并安装所需依赖包。

#### 2. 浏览器与驱动 (用于部分市场)

A股的科创板、创业板以及港股的下载依赖于 [Selenium](https://www.selenium.dev/) 自动化浏览器操作。

- **浏览器**: 请确保您已安装 **Google Chrome** 浏览器。
- **驱动程序 (ChromeDriver)**:
    - **自动安装**: 脚本在首次运行时会尝试自动下载与您Chrome版本匹配的ChromeDriver。**请优先尝试此方式。**
    - **手动安装**: 如果自动下载失败，请参考 `README.html` 中的详细手动安装步骤。

---

## 使用指南

### 方式一：Web 界面 (推荐)

两个版本都提供了现代化的Web界面，这是最简单直观的使用方式。

1.  **启动服务**:
    - **浏览器模式**: 双击运行 `start_web_bd.bat`。
    - **请求模式**: 双击运行 `start_web_rq.bat`。

2.  **访问界面**:
    - 脚本启动后，会自动在浏览器中打开对应界面：
        - **Browser "Otako" Version**: `http://localhost:30331`
        - **Requests "Mizuki" Version**: `http://localhost:31015`
    - 您也可以在局域网内的其他设备上通过 `http://[运行电脑的IP地址]:[端口号]` 来访问。

### 方式二：命令行 (适用于请求模式)

`Requests "Mizuki" Version` 的核心逻辑可以被命令行直接调用。

#### 命令格式
```bash
python annual_report_downloader_rq.py [-h] (-s STOCK | -f FILE) -y YEARS [-d DIR]
```

#### 参数详解

| 参数          | 描述                                     | 必需     | 示例                                     |
|---------------|------------------------------------------|----------|------------------------------------------|
| `-s, --stock` | 单个股票代码                               | 与`-f`互斥 | `-s 000001`                              |
| `-f, --file`  | 包含多个股票代码的文本文件路径（每行一个） | 与`-s`互斥 | `-f all_types_test_stocks.txt`           |
| `-y, --years` | 年份，支持单年、范围、列表                 | **是**   | `-y 2024` 或 `-y 2022-2024` 或 `-y 2022,2024` |
| `-d, --dir`   | 下载报告的存放目录（默认为`annual_reports`） | 否       | `-d ./my_reports`                        |

---

## 项目结构

```
annual_report_crawler/
├── 🚀 核心应用
│   ├── annual_report_downloader_bd.py  # Browser "Otako" Version 核心逻辑
│   ├── web_app_bd.py                   # Browser "Otako" Version Web应用
│   ├── annual_report_downloader_rq.py  # Requests "Mizuki" Version 核心逻辑
│   └── web_app_rq.py                   # Requests "Mizuki" Version Web应用
├── 🏁 启动脚本
│   ├── start_web_bd.bat                # "Otako" 版本 (浏览器) 启动器
│   └── start_web_rq.bat                # "Mizuki" 版本 (请求) 启动器
├── 🎨 网页模板
│   └── templates/
│       ├── index_bd.html               # "Otako" 版本界面
│       └── index_rq.html               # "Mizuki" 版本界面
├── 📄 文档与资源
│   ├── README.md                       # 项目说明 (Markdown)
│   ├── README.html                     # 项目说明 (网页版)
│   └── all_types_test_stocks.txt       # 股票代码测试文件
└── 📂 下载目录 (自动生成)
    └── annual_reports/
```

---

## 版本对比

| 特性 | Requests "Mizuki" Version | Browser "Otako" Version |
| :--- | :--- | :--- |
| **核心技术** | HTTP Requests | Selenium Webdriver |
| **下载速度** | 较快 | 常规 |
| **企业环境兼容性** | 可能被拦截/加密 | **高** |
| **资源占用** | 低 | 较高 |
| **适用场景** | 个人电脑、服务器 | 有安全软件的公司电脑 |

---

**Developed by Terence WANG**
