# Annual Report Crawler - v1 Legacy Versions

## 📁 v1版本说明

这个文件夹包含了年报下载器的第一代版本，分为两个独立的版本：

### 🌸 Requests "Hanae" Version
- **文件**: `annual_report_downloader_rq.py`, `web_app_rq.py`
- **启动**: `start_web_rq.bat`
- **端口**: 31015
- **特点**: 使用requests库，下载速度快

### 🪸 WebDriver "Shio" Version  
- **文件**: `annual_report_downloader_bd.py`, `web_app_bd.py`
- **启动**: `start_web_bd.bat`
- **端口**: 30331
- **特点**: 使用浏览器下载，避免文件加密

## 🚀 如何运行v1版本

### 方法1: 使用启动脚本
```bash
# 在v1文件夹中运行
start_web_rq.bat    # Hanae版本 (端口30820)
start_web_bd.bat    # Shio版本 (端口30605)
```

### 方法2: 直接运行Python文件
```bash
# 在v1文件夹中运行
cd v1
python web_app_rq.py    # Hanae版本
python web_app_bd.py    # Shio版本
```

## 📋 文件说明

- `annual_report_downloader_rq.py` - Hanae版本下载器
- `annual_report_downloader_bd.py` - Shio版本下载器
- `web_app_rq.py` - Hanae版本Web应用
- `web_app_bd.py` - Shio版本Web应用
- `start_web_rq.bat` - Hanae版本启动脚本
- `start_web_bd.bat` - Shio版本启动脚本
- `chromedriver.exe` - Chrome浏览器驱动（Shio版本需要）
- `templates/` - HTML模板文件夹

## ⚠️ 重要说明

1. **chromedriver.exe**: 已复制到v1文件夹，确保Shio版本能正常运行
2. **模板文件**: templates文件夹也已复制到v1中
3. **独立运行**: v1版本可以独立运行，不依赖根目录的v2文件

## 🔄 迁移到v2

建议使用根目录的**Unified "Hysilens" Version v2**：
- 统一界面
- 智能模式选择
- 更好的维护性
- 相同的功能覆盖

启动v2版本：
```bash
# 回到根目录运行
cd ..
start_web_hysilens.bat
```

---

**注意**: v1版本仅作为备份和参考，推荐使用v2统一版本。 