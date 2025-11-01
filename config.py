"""
配置文件
"""

# OCR 识别间隔（秒）
OCR_INTERVAL = 0.5

# 悬浮窗配置
WINDOW_ALPHA = 0.95  # 透明度（0-1）
WINDOW_WIDTH = 400   # 默认宽度
WINDOW_MIN_HEIGHT = 200  # 最小高度
WINDOW_MAX_HEIGHT = 600  # 最大高度
WINDOW_PADDING = 15  # 内边距

# 字体配置
FONT_FAMILY = "Microsoft YaHei"  # 微软雅黑
FONT_SIZE_WORD = 16      # 单词字体大小
FONT_SIZE_PHONETIC = 12  # 音标字体大小
FONT_SIZE_BODY = 11      # 正文字体大小
FONT_SIZE_ROOT = 10      # 词根字体大小

# 颜色配置
COLOR_BG = "#2C3E50"           # 背景色（深蓝灰）
COLOR_WORD = "#ECF0F1"         # 单词颜色（浅灰白）
COLOR_PHONETIC = "#95A5A6"     # 音标颜色（灰色）
COLOR_SECTION_TITLE = "#3498DB"  # 标题颜色（蓝色）
COLOR_BODY = "#E8E8E8"         # 正文颜色（浅灰）
COLOR_ROOT = "#F39C12"         # 词根颜色（橙色）
COLOR_SEPARATOR = "#34495E"    # 分隔线颜色（深灰）

# 快捷键配置
HOTKEY_RESELECT = 'F2'     # 重新选择区域
HOTKEY_TOGGLE = 'F3'       # 显示/隐藏悬浮窗
HOTKEY_PAUSE = 'F4'        # 暂停/继续识别
HOTKEY_EXIT = 'ESC'        # 退出程序

# Tesseract OCR 路径（Windows 用户可能需要配置）
# 如果 Tesseract 不在系统 PATH 中，请取消注释并设置正确路径
# TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
TESSERACT_CMD = None

# 数据库文件路径
DATABASE_FILE = "词汇新修版讲义_files/content.htm"

# 模糊匹配阈值（0-1，越高越严格）
FUZZY_MATCH_THRESHOLD = 0.8

# 调试模式
DEBUG = False

