# Annual Report Crawler - Unified "Hysilens" Version v2

**版本: 2.0.0 (统一"Hysilens"版本)**

一个功能强大的年报下载工具，支持A股、港股和美股。**v2版本整合了两种下载模式到统一界面**，让用户智能选择最适合的下载方式。

**开发者:** Terence WANG

---

## 🎉 v2版本特色

### 🔧 统一"Hysilens"版本优势

**v2版本**整合了原有的Requests "Hanae" Mode和WebDriver "Shio" Mode，提供：

- ✅ **统一界面**: 一个Web界面管理所有下载模式
- ✅ **智能选择**: 根据使用环境选择最佳下载模式  
- ✅ **代码复用**: 避免重复维护，提高开发效率
- ✅ **完整功能**: 保留所有v1版本的功能
- ✅ **易于扩展**: 未来可轻松添加新的下载模式

### 🎯 双模式支持

#### 🌸 Requests "Hanae" Mode
**适用场景**: 个人电脑环境，追求下载速度
- ✅ 下载速度快，内存占用少
- ✅ 无需浏览器依赖
- ❌ 可能遇到文件加密问题

#### 🪸 WebDriver "Shio" Mode
**适用场景**: 企业办公环境，有安全软件限制
- ✅ 避免文件加密问题
- ✅ 兼容企业安全软件
- ❌ 需要Chrome浏览器，速度相对较慢

### 🚀 快速开始
```bash
# 启动v2统一版本
start_web_hysilens.bat

# 访问地址
http://localhost:31425
```

## 核心功能

- 🚀 **全市场支持**: 支持A股（主板、科创板、创业板）、港股、美股。
- 💡 **智能识别**: 自动根据股票代码格式识别市场及板块。
- 📥 **批量下载**: 支持通过Web界面或命令行进行批量下载。
- 📅 **灵活年份**: 支持单年份、年份范围或不连续年份列表。
- ✨ **现代化Web界面**: 操作直观，实时反馈进度、日志和结果。
- 📄 **多格式支持**: A股和港股下载为PDF格式，美股下载为HTML格式的10-K报告。
- 📈 **详细报告**: 任务完成后提供详细的下载统计与失败原因分析。
- 🔒 **企业友好**: 浏览器模式完美适配企业安全环境。

## 🔍 支持的股票类型

### A股市场
- **主板**: 6位数字代码
  - 上海主板: `600XXX`, `601XXX`, `603XXX`, `605XXX` (如: `600519` 贵州茅台)
  - 深圳主板: `000XXX`, `001XXX`, `002XXX` (如: `000001` 平安银行)

- **科创板**: `688XXX` 开头
  - 示例: `688111` 金山办公, `688036` 传音控股

- **创业板**: `300XXX` 开头  
  - 示例: `300750` 宁德时代, `300122` 智飞生物

### 港股市场
- **代码格式**: 5位数字代码 (前面补零)
  - 示例: `00700` 腾讯控股, `00939` 建设银行, `01810` 小米集团

### 美股市场
- **代码格式**: 字母代码 (1-5位字母)
  - 示例: `AAPL` 苹果, `MSFT` 微软, `GOOGL` 谷歌, `TSLA` 特斯拉

## ℹ️ 数据来源说明

### A股和港股
- **数据来源**: [巨潮资讯网](http://www.cninfo.com.cn/)
- **下载格式**: PDF
- **覆盖范围**: 
  - A股: 完整覆盖主板、科创板、创业板
  - 港股: 覆盖主要股票，部分可能存在缺漏

⚠️ **港股注意事项**: 由于巨潮资讯网对港股的覆盖未必完整，部分港股年报可能存在缺漏，需要手动补全。

### 美股
- **数据来源**: [美国证券交易委员会 (SEC)](https://www.sec.gov/)
- **下载格式**: HTML (10-K 报告)
- **覆盖范围**: 所有在美国注册的上市公司

### 代码格式示例

```
# A股示例
000001        # 平安银行 (深圳主板)
600519        # 贵州茅台 (上海主板) 
688111        # 金山办公 (科创板)
300750        # 宁德时代 (创业板)

# 港股示例  
00700         # 腾讯控股
00939         # 建设银行
01810         # 小米集团

# 美股示例
AAPL          # 苹果
MSFT          # 微软
GOOGL         # 谷歌
TSLA          # 特斯拉
```

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

### 🖥️ Web界面使用 (v2统一版本 - 推荐)
v2版本在v1核心功能的基础上，提供了一个统一、易用的Web界面，是推荐的使用方式。

1.  **启动服务**:
    *   在项目根目录下，直接双击运行 `start_web_hysilens.bat`。
    *   脚本会自动检查环境、安装依赖，并启动Web服务器。
2.  **访问与使用**:
    *   启动后，脚本会自动在浏览器中打开 `http://localhost:31425`。
    *   在界面上选择模式、输入代码和年份，即可开始下载。

### ⌨️ 命令行使用 (v1核心功能)
v1的两种核心下载逻辑 (`downloader_rq.py` 和 `downloader_bd.py`) 均支持命令行调用，适合自动化和批量处理任务。

1.  **进入v1目录**:
    ```bash
    cd v1
    ```
2.  **选择模式并执行**:
    *   **Hanae模式 (请求)**:
        ```bash
        python annual_report_downloader_rq.py [参数]
        ```
    *   **Shio模式 (浏览器)**:
        ```bash
        python annual_report_downloader_bd.py [参数]
        ```
3.  **命令格式与参数 (两种模式通用)**:
    ```bash
    # 命令格式
    python [downloader_script.py] [-h] (-s STOCK | -f FILE) -y YEARS [-d DIR]
    ```
    | 参数 | 描述 | 示例 |
    | :--- | :--- | :--- |
    | `-s, --stock` | 单个股票代码。 | `-s 000001` |
    | `-f, --file` | 包含多个股票代码的文本文件路径（每行一个）。 | `-f ../all_types_test_stocks.txt` |
    | `-y, --years` | **(必需)** 年份，支持单年(`2023`)、范围(`2021-2023`)。 | `-y 2021-2023` |
    | `-d, --dir` | 下载目录 (默认为 `annual_reports`)。 | `-d ../my_reports` |
    | `-h, --help` | 显示帮助信息。 | |
4.  **使用示例**:
    ```bash
    # 使用Hanae模式下载平安银行2023年年报
    python annual_report_downloader_rq.py -s 000001 -y 2023

    # 使用Shio模式批量下载文件中的所有股票2021至2023的年报
    python annual_report_downloader_bd.py -f ../all_types_test_stocks.txt -y 2021-2023
    ```

---

## 📁 项目结构
```
annual_report_crawler/
├── 📄 README.md & README.html     # 项目说明文档
│
├── 📦 v2 - Web界面封装
│   ├── 🚀 start_web_hysilens.bat    # v2启动脚本
│   ├── 🌐 web_app_hysilens.py        # v2 Web应用 (Flask)
│   └── 📁 templates/
│       └── 📄 index_hysilens.html    # v2前端页面
│
├── 📦 v1 - 核心功能
│   ├── 📁 v1/
│   │   ├── 🐍 annual_report_downloader_rq.py  # Hanae模式核心逻辑 (支持命令行)
│   │   ├── 🐍 annual_report_downloader_bd.py  # Shio模式核心逻辑
│   │   ├── 🌐 web_app_rq.py & web_app_bd.py  # v1的Web应用
│   │   ├── 🚀 start_web_rq.bat & start_web_bd.bat # v1启动脚本
│   │   └── ... (其他v1相关文件)
│
├── ⚙️ chromedriver.exe            # 浏览器驱动
└── 📋 requirements.txt           # Python依赖包
```

## 🆚 版本对比

| 特性 | v1版本 (独立双版本) | v2统一版本 (Hysilens) |
| :--- | :--- | :--- |
| **界面数量** | 2个 (Hanae, Shio) | ✅ **1个统一界面** |
| **代码维护** | 重复代码多，维护困难 | ✅ **代码复用高，易于维护** |
| **模式切换** | 需重启不同应用 | ✅ **界面实时切换，无需重启** |
| **端口管理** | 2个端口 (30605, 30820) | ✅ **单一端口 (31425)** |
| **扩展性** | 困难 | ✅ **易于扩展新模式** |

---

## 📦 开源信息

- **GitHub Repository**: https://github.com/kimilime/annual_report_crawler
- **许可证**: Open Source
- **贡献**: 欢迎提交Issues和Pull Requests

---

**Developed by Terence WANG**
