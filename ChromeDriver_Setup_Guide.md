# ChromeDriver 安装指南

如果你需要下载科创板、创业板或港股年报，需要安装ChromeDriver。

## 自动安装 (推荐)

如果网络正常，脚本会自动下载ChromeDriver。如果遇到网络问题，请尝试手动安装。

## 手动安装 ChromeDriver

### 步骤1: 查看Chrome版本
1. 打开Chrome浏览器
2. 在地址栏输入: `chrome://version/`
3. 记下版本号，例如: `120.0.6099.109`

### 步骤2: 下载对应版本的ChromeDriver
1. 访问: https://chromedriver.chromium.org/downloads
2. 选择与你的Chrome版本对应的ChromeDriver
3. 下载适合你操作系统的版本

### 步骤3: 安装ChromeDriver

#### Windows
1. 解压下载的zip文件
2. 将 `chromedriver.exe` 复制到一个文件夹，例如 `C:\chromedriver\`
3. 将该路径添加到系统环境变量PATH中:
   - 右键"此电脑" → "属性" → "高级系统设置"
   - 点击"环境变量"
   - 在"系统变量"中找到"Path"，点击"编辑"
   - 点击"新建"，输入 `C:\chromedriver\`
   - 点击"确定"保存

#### macOS
```bash
# 使用Homebrew安装
brew install chromedriver

# 或手动安装
sudo mv chromedriver /usr/local/bin/
```

#### Linux
```bash
# 解压并移动到系统路径
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

### 步骤4: 验证安装
打开命令行，输入:
```bash
chromedriver --version
```

如果显示版本信息，说明安装成功。

## 当前功能状态

| 股票类型 | 状态 | 备注 |
|---------|------|------|
| A股主板 | ✅ 完全正常 | 使用API，无需ChromeDriver |
| A股科创板 | ⚠️ 需要ChromeDriver | 使用Selenium |
| A股创业板 | ⚠️ 需要ChromeDriver | 使用Selenium |
| 港股 | ⚠️ 需要ChromeDriver | 使用Selenium |

## 推荐使用方式

1. **仅下载A股主板**: 无需安装ChromeDriver，直接使用即可
2. **下载科创板/创业板/港股**: 请按照本指南安装ChromeDriver

## 示例命令

```bash
# A股主板 - 直接可用
python annual_report_downloader.py -s 000001 -y 2023
python annual_report_downloader.py -f a_stock_main.txt -y 2022,2023

# 科创板 - 需要ChromeDriver
python annual_report_downloader.py -s 688001 -y 2023

# 创业板 - 需要ChromeDriver  
python annual_report_downloader.py -s 300750 -y 2023

# 港股 - 需要ChromeDriver
python annual_report_downloader.py -s 00700 -y 2023
``` 