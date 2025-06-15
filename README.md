# 巨潮网年报下载器

这是一个从巨潮资讯网（cninfo.com.cn）和美国SEC网站批量下载各类年报的Python脚本。

## 功能特性

- 🚀 **全市场支持**: 支持A股、港股、美股等多个市场
- 📊 **智能识别**: 自动根据股票代码格式识别股票类型
- 📥 **批量下载**: 支持单个股票或批量股票文件
- 📅 **年份范围**: 支持单年份、年份范围或年份列表
- 🔍 **实时进度**: 显示下载进度和详细状态
- 📈 **详细汇总**: 提供完整的下载统计报告
- 📄 **PDF输出**: 支持真正的PDF格式输出

## 支持的股票类型

| 股票类型 | 代码格式 | 示例 | 下载方式 | 文档类型 |
|---------|---------|------|---------|----------|
| A股主板 | 6位数字 (非688/300开头) | 000001, 600519 | API + requests | 年报PDF |
| A股科创板 | 688开头6位数字 | 688001, 688009 | Selenium | 年报PDF |
| A股创业板 | 300开头6位数字 | 300001, 300750 | Selenium | 年报PDF |
| 港股 | 5位数字或HK前缀 | 00700, HK00939 | Selenium | 年报PDF |
| 美股 | 字母代码 | AAPL, MSFT, GOOGL | SEC API | 10-K报告HTML |

## 安装要求

### Python环境
- Python 3.7+

### 依赖包
```bash
pip install -r requirements.txt
```

### PDF转换依赖（必需）

为了生成真正的PDF文件，需要安装以下系统依赖：

#### Windows系统
1. 下载并安装 `wkhtmltopdf`：
   - 访问：https://wkhtmltopdf.org/downloads.html
   - 下载 Windows 64位版本
   - 运行安装程序（默认安装到 `C:\Program Files\wkhtmltopdf\`）

#### Linux系统
```bash
# Ubuntu/Debian
sudo apt-get install wkhtmltopdf

# CentOS/RHEL
sudo yum install wkhtmltopdf

# 或者从官网下载对应版本
```

#### macOS系统
```bash
# 使用Homebrew
brew install wkhtmltopdf

# 或者从官网下载pkg安装包
```

### 浏览器要求（用于科创板/创业板/港股）
- Chrome浏览器
- ChromeDriver（需要与Chrome版本匹配）

**ChromeDriver安装:**
1. 查看Chrome版本：在Chrome地址栏输入 `chrome://version/`
2. 下载对应版本的ChromeDriver：https://chromedriver.chromium.org/
3. 将ChromeDriver添加到系统PATH中，或放在项目目录下

## 使用方法

有两种使用方式：Web界面（推荐新手）和命令行方式（适合高级用户）。

### 🌐 Web界面方式（推荐）

**简单三步，无需命令行知识：**

1. **启动Web服务器**
   ```bash
   # Windows用户
   双击运行 start_web.bat
   
   # Linux/Mac用户
   ./start_web.sh
   
   # 或手动启动
   python web_app.py
   ```

2. **打开浏览器**
   - 访问 `http://localhost:5000`
   - 支持手机和平板访问

3. **开始下载**
   - 在网页中输入股票代码和年份
   - 点击"开始下载"按钮
   - 实时查看下载进度和日志
   - 下载完成后直接点击下载文件

**Web界面特色功能：**
- 📊 **实时进度显示** - 可视化进度条和当前处理状态
- 📋 **运行日志** - 实时显示详细的下载日志  
- 📥 **一键下载** - 完成后直接点击下载文件
- 📱 **响应式设计** - 支持手机、平板访问
- 🎯 **用户友好** - 直观的界面，无需记忆命令

详细使用说明请参考：[Web界面使用指南](WEB_USAGE.md)

### 💻 命令行方式

### 基本语法
```bash
python annual_report_downloader.py [-h] (-s STOCK | -f FILE) -y YEARS [-d DIR]
```

### 参数说明

| 参数 | 描述 | 必需 | 示例 |
|------|------|------|------|
| `-s, --stock` | 单个股票代码 | 与-f互斥 | `-s 000001` |
| `-f, --file` | 股票代码文件路径 | 与-s互斥 | `-f all_types_test_stocks.txt` |
| `-y, --years` | 年份范围 | 是 | `-y 2022` 或 `-y 2020-2022` |
| `-d, --dir` | 下载目录 | 否 | `-d ./downloads` |

### 年份格式支持

| 格式 | 说明 | 示例 | 结果 |
|------|------|------|------|
| 单年份 | 下载指定年份 | `2022` | [2022] |
| 年份范围 | 连续年份范围 | `2020-2022` | [2020, 2021, 2022] |
| 年份列表 | 指定多个年份 | `2020,2022,2023` | [2020, 2022, 2023] |

## 使用示例

### 1. 下载单个股票年报
```bash
# 下载平安银行2022年年报（A股主板）
python annual_report_downloader.py -s 000001 -y 2022

# 下载宁德时代2020-2022年年报（A股创业板）
python annual_report_downloader.py -s 300750 -y 2020-2022

# 下载腾讯控股2021,2022年年报（港股）
python annual_report_downloader.py -s 00700 -y 2021,2022

# 下载苹果公司2023年10-K报告（美股）
python annual_report_downloader.py -s AAPL -y 2023
```

### 2. 批量下载多种类型股票年报
```bash
# 使用全类型股票测试文件
python annual_report_downloader.py -f all_types_test_stocks.txt -y 2023

# 指定下载目录
python annual_report_downloader.py -f all_types_test_stocks.txt -y 2022-2023 -d ./my_reports
```

### 3. 股票代码文件格式
使用提供的 `all_types_test_stocks.txt` 文件，或创建自定义文件，每行一个股票代码：
```txt
# A股主板
000001  # 平安银行
600519  # 贵州茅台

# A股科创板
688111  # 金山办公

# A股创业板
300750  # 宁德时代

# 港股
00700   # 腾讯控股

# 美股
AAPL    # 苹果公司
MSFT    # 微软公司
```

## 输出说明

### 控制台输出
脚本运行时会显示详细的进度信息：
- 📊 股票类型识别
- 📥 年报查找状态
- ✓ 下载成功信息（PDF格式）
- ✗ 错误和失败信息
- 📈 实时成功率统计

### 下载文件结构
```
annual_reports/
├── A股主板/
│   ├── 000001_平安银行_2023年报.pdf
│   └── 600519_贵州茅台_2023年报.pdf
├── A股科创板/
│   └── 688111_金山办公_2023年报.pdf
├── A股创业板/
│   └── 300750_宁德时代_2023年报.pdf
├── 港股/
│   └── 00700_腾讯控股_2023年报.pdf
└── US/
    ├── AAPL_2023_10K_2023-11-03.html
    └── MSFT_2023_10K_2023-07-27.html
```

### 文件命名规则
- **A股/港股**: `股票代码_公司名称_年份年报.pdf`
- **美股**: `股票代码_年份_10K_提交日期.html`

### 汇总报告
下载完成后显示详细统计：
- 总任务数、成功数、失败数
- 成功率百分比
- 按股票类型分组的统计
- 失败任务的详细错误信息

## 技术实现细节

### A股主板
- 使用巨潮网公开API
- 通过HTTP请求获取公告列表
- 直接下载PDF文件

### A股科创板/创业板
- 使用Selenium自动化浏览器
- 自动获取orgId参数
- 模拟用户操作进行下载

### 港股
- 使用Selenium访问港股页面
- 通过公司名称搜索年报
- 自动触发下载操作

### 美股
- 使用SEC EDGAR API获取公司信息
- 自动查找10-K报告
- 下载HTML内容并转换为PDF格式
- 支持pdfkit和weasyprint两种PDF转换方式

## 常见问题

### 1. 港股年报识别问题
**现象**: 港股下载时识别到"致非登记股东之通知信函"等非年报文档

**解决方案**: 当前版本已修复此问题，增加了严格的年报过滤条件：
- 排除通知信函、通告、通函等文档类型
- 排除股东大会、代表委任表格等相关文档  
- 确保下载的是真正的年度报告文档

### 2. PDF转换相关错误
**错误**: `OSError: wkhtmltopdf reported an error`

**解决方案**: 
- 确保已正确安装wkhtmltopdf
- Windows: 检查是否安装到 `C:\Program Files\wkhtmltopdf\`
- Linux/Mac: 使用 `which wkhtmltopdf` 检查安装

### 2. ChromeDriver相关错误
**错误**: `selenium.common.exceptions.WebDriverException: 'chromedriver' executable needs to be in PATH`

**解决方案**: 
- 确保已安装Chrome浏览器
- 下载对应版本的ChromeDriver
- 将ChromeDriver添加到系统PATH中

### 3. 网络连接问题
**错误**: 请求超时或连接失败

**解决方案**:
- 检查网络连接
- 对于美股，确保可以访问SEC网站（sec.gov）
- 增加脚本中的超时时间
- 考虑使用代理

### 4. 找不到年报
**现象**: 显示"未找到年报"

**可能原因**:
- 该股票在指定年份未发布年报
- 美股的10-K报告可能还未提交
- 网站结构发生变化
- 股票代码或年份有误

### 5. 下载速度慢
**解决方案**:
- 脚本内置了请求间隔以避免被封IP
- 美股下载涉及PDF转换，相对较慢
- 建议分批次下载大量股票
- 可以只下载HTML格式以提高速度

## 项目结构

```
annual_report_crawler/
├── annual_report_downloader.py    # 主程序（命令行版本）
├── web_app.py                    # Web界面应用
├── start_web.bat                 # Windows Web启动脚本
├── start_web.sh                  # Linux/Mac Web启动脚本
├── templates/
│   └── index.html               # Web界面模板
├── requirements.txt             # Python依赖
├── all_types_test_stocks.txt    # 全类型股票测试文件
├── WEB_USAGE.md                 # Web界面使用指南
├── ChromeDriver_Setup_Guide.md  # Chrome驱动安装指南
├── tests_and_examples/          # 测试脚本和示例（被gitignore）
├── annual_reports/              # 默认下载目录（被gitignore）
└── README.md                    # 本文件
```

## 注意事项

1. **合规使用**: 本脚本仅用于学习和研究目的，请遵守相关网站的使用条款
2. **频率控制**: 脚本内置了请求间隔，请勿修改以免被网站封禁
3. **数据准确性**: 下载的文件请以官方发布为准
4. **环境要求**: 确保Python环境和依赖包版本兼容
5. **PDF依赖**: 必须正确安装wkhtmltopdf才能生成PDF文件
6. **美股限制**: SEC网站可能有访问限制，建议合理控制请求频率

## 更新日志

### v2.1.1 (2025-01-16)
- 🐛 修复Web界面中文编码问题
- 📝 更新版权年份到2025
- 🔧 增强文件读取的编码兼容性

### v2.1.0 (2024-12-16)
- ✨ 新增Web界面功能！支持浏览器操作
- 🌐 提供用户友好的Web界面，无需命令行知识
- 📊 实时进度显示和运行日志
- 📥 Web界面一键下载文件功能
- 📱 响应式设计，支持手机和平板访问
- 🚀 简化使用流程：启动服务器 → 打开浏览器 → 开始下载

### v2.0.1 (2024-12-16)
- 🐛 修复港股年报识别误判问题
- 📝 增强港股年报过滤逻辑，排除通知信函等非年报文档
- ✅ 确保港股下载的是真正的年度报告

### v2.0.0 (2024-12-16)
- ✨ 新增美股10-K报告下载功能
- ✨ 支持真正的PDF格式输出
- ✨ 添加wkhtmltopdf和weasyprint PDF转换支持
- 🐛 修复返回值格式不统一的问题
- 📝 更新README和项目结构
- 🗂️ 整理测试文件到独立目录

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持A股主板、科创板、创业板和港股
- 实现批量下载和进度显示
- 添加详细的错误处理和汇总报告

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。如果您发现任何bug或有功能建议，请创建一个Issue。 