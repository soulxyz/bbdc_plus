# 📁 项目结构说明

## 目录结构

```
bbdc_plus/
│
├── 📄 核心模块
│   ├── main.py                 # 主程序入口，整合所有模块
│   ├── database.py             # 数据库解析和查询
│   ├── screen_selector.py      # 屏幕区域选择工具
│   ├── ocr_engine.py           # OCR 识别引擎
│   ├── floating_window.py      # 悬浮卡片窗口
│   └── config.py               # 配置文件
│
├── 📚 数据文件
│   ├── 词汇新修版讲义.txt      # 文本格式数据（存在换行问题）
│   ├── 词汇新修版讲义.htm      # HTML 框架文件
│   └── 词汇新修版讲义_files/   # HTML 数据目录
│       ├── content.htm         # ★ 主要数据源（2547 单词 + 712 词根）
│       ├── bookmarks.htm       # 书签导航
│       └── Image_*.png         # 图片资源
│
├── 🚀 启动脚本
│   ├── install.bat             # Windows 安装脚本
│   └── run.bat                 # Windows 启动脚本
│
├── 📖 文档
│   ├── README.md               # 完整使用说明
│   ├── QUICK_START.md          # 快速开始指南
│   ├── PROJECT_STRUCTURE.md    # 项目结构说明（本文件）
│   └── requirements.txt        # Python 依赖列表
│
└── 🔧 配置
    └── .gitignore              # Git 忽略规则
```

## 模块详解

### 1. main.py - 主控制器

**功能：**
- 初始化所有模块
- 注册全局快捷键
- 管理 OCR 识别循环
- 协调各模块交互

**关键类：**
- `BBDCPlus`: 主应用类

**主要方法：**
- `select_region()`: 选择屏幕区域
- `_ocr_loop()`: OCR 识别循环（后台线程）
- `_on_*()`: 快捷键回调函数

### 2. database.py - 数据库模块

**功能：**
- 解析 HTML 文件中的单词和词根
- 构建内存索引（快速查询）
- 支持精确匹配和模糊匹配

**关键类：**
- `WordDatabase`: 数据库管理器

**数据结构：**
```python
word_dict = {
    'abandon': {
        'word': 'abandon',
        'phonetic': '/əˈbændən/',
        'root_split': 'a+ban+don',
        'root_meaning': '×+禁止+给出',
        'definition': 'v.放弃',
        'examples': ['...'],
        'raw_text': '...'
    }
}

root_dict = {
    'ban': '禁止',
    'don': '给予',
    ...
}
```

**主要方法：**
- `lookup(word, fuzzy=True)`: 查询单词
- `lookup_root(root)`: 查询词根
- `get_related_roots(word_info)`: 获取相关词根

### 3. screen_selector.py - 区域选择

**功能：**
- 全屏半透明覆盖层
- 鼠标拖拽选择矩形
- 实时显示区域尺寸

**关键类：**
- `ScreenSelector`: 区域选择器

**返回值：**
```python
(x, y, width, height)  # 左上角坐标 + 尺寸
```

### 4. ocr_engine.py - OCR 引擎

**功能：**
- 截取屏幕指定区域
- Tesseract OCR 文字识别
- 提取英文单词
- 防抖处理（相同单词不重复）

**关键类：**
- `OCREngine`: OCR 管理器

**主要方法：**
- `capture_region()`: 截取屏幕
- `recognize_text()`: 识别文字
- `extract_words()`: 提取单词
- `recognize_region()`: 一键识别

**优化：**
- 仅识别英文字符
- 图像预处理（灰度化）
- 防止重复识别

### 5. floating_window.py - 悬浮窗

**功能：**
- 无边框透明置顶窗口
- 拖动功能
- 动态内容更新
- 自适应高度

**关键类：**
- `FloatingWindow`: 悬浮窗管理器

**显示内容：**
- 标题栏（拖动 + 关闭）
- 单词和音标
- 词根拆分和含义
- 释义
- 真题例句
- 相关词根

**配置：**
- 透明度、颜色、字体等在 `config.py` 中设置

### 6. config.py - 配置中心

**可配置项：**

```python
# OCR 参数
OCR_INTERVAL = 0.5  # 识别间隔（秒）

# 窗口外观
WINDOW_ALPHA = 0.95       # 透明度
WINDOW_WIDTH = 400        # 宽度
FONT_FAMILY = "Microsoft YaHei"

# 颜色主题
COLOR_BG = "#2C3E50"      # 背景
COLOR_WORD = "#ECF0F1"    # 单词
COLOR_ROOT = "#F39C12"    # 词根

# 快捷键
HOTKEY_RESELECT = 'F2'
HOTKEY_TOGGLE = 'F3'
HOTKEY_PAUSE = 'F4'
HOTKEY_EXIT = 'ESC'

# Tesseract 路径
TESSERACT_CMD = None      # 自动检测

# 调试
DEBUG = False
```

## 数据流程

```
┌─────────────┐
│ 用户启动程序 │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ 加载数据库       │ ← content.htm (2547 词 + 712 根)
│ WordDatabase    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ 选择屏幕区域     │ → (x, y, width, height)
│ ScreenSelector  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ OCR 识别循环     │
│ (后台线程)       │
└──────┬──────────┘
       │
       ├─→ 截取屏幕 (OCREngine.capture_region)
       │
       ├─→ OCR 识别 (pytesseract)
       │
       ├─→ 提取单词 (extract_words)
       │
       ├─→ 查询数据库 (database.lookup)
       │   │
       │   ├─→ 精确匹配
       │   └─→ 模糊匹配 (difflib)
       │
       └─→ 更新悬浮窗 (FloatingWindow.update_word)
```

## 依赖关系

```
main.py
 ├─→ database.py
 │    └─→ BeautifulSoup4
 │
 ├─→ screen_selector.py
 │    └─→ tkinter (内置)
 │
 ├─→ ocr_engine.py
 │    ├─→ pytesseract
 │    ├─→ Pillow
 │    └─→ Tesseract OCR (外部软件)
 │
 ├─→ floating_window.py
 │    └─→ tkinter (内置)
 │
 └─→ keyboard (全局快捷键)
```

## 性能特点

### 内存使用
- 数据库加载：约 5-10 MB
- 运行时内存：约 50-100 MB
- 适合长时间运行

### CPU 使用
- 空闲时：< 1%
- OCR 识别时：5-15%（取决于区域大小）
- 多线程设计，不阻塞 GUI

### 响应速度
- 区域选择：即时
- OCR 识别：0.2-0.5 秒/次
- 数据库查询：< 0.01 秒
- 界面更新：即时

## 扩展建议

### 可以添加的功能

1. **数据源扩展**
   - 支持自定义词库导入
   - 在线词典 API 集成

2. **识别优化**
   - 支持多区域同时识别
   - 自适应 OCR 参数调优

3. **界面增强**
   - 历史记录功能
   - 收藏夹
   - 学习进度统计

4. **导出功能**
   - 生成学习笔记
   - 导出 Anki 卡片

### 代码规范

- 遵循 PEP 8 风格
- 类型注解（Type Hints）
- 详细的文档字符串
- 异常处理

---

**更新日期：** 2025-11-01  
**版本：** 1.0.0

