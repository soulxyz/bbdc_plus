"""
悬浮卡片窗口
显示单词的词根词缀信息
支持高DPI和显示缩放
"""

import tkinter as tk
from tkinter import font as tkfont
from typing import Optional, Dict, List, Tuple
import config
from dpi_utils import setup_tkinter_dpi


class FloatingWindow:
    def __init__(self):
        """初始化悬浮窗"""
        self.root = tk.Tk()
        self.root.title("BBDC Plus")
        
        # 设置 DPI 支持
        setup_tkinter_dpi(self.root)
        
        # 设置窗口属性
        self.root.attributes('-topmost', True)  # 置顶
        self.root.attributes('-alpha', config.WINDOW_ALPHA)  # 透明度
        self.root.overrideredirect(True)  # 无边框
        
        # 设置初始大小和位置
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_MIN_HEIGHT}+100+100")
        
        # 设置背景色
        self.root.configure(bg=config.COLOR_BG)
        
        # 创建主容器
        self.main_frame = tk.Frame(
            self.root,
            bg=config.COLOR_BG,
            padx=config.WINDOW_PADDING,
            pady=config.WINDOW_PADDING
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题栏（用于拖动和关闭）
        self._create_title_bar()
        
        # 内容区域
        self.content_frame = tk.Frame(
            self.main_frame,
            bg=config.COLOR_BG
        )
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 初始化字体
        self._init_fonts()
        
        # 显示欢迎信息
        self._show_welcome()
        
        # 用于拖动窗口
        self._drag_data = {"x": 0, "y": 0}
        
        # 隐藏标志
        self.is_hidden = False
    
    def _init_fonts(self):
        """初始化字体"""
        self.font_word = tkfont.Font(
            family=config.FONT_FAMILY,
            size=config.FONT_SIZE_WORD,
            weight='bold'
        )
        self.font_phonetic = tkfont.Font(
            family="Arial",
            size=config.FONT_SIZE_PHONETIC
        )
        self.font_body = tkfont.Font(
            family=config.FONT_FAMILY,
            size=config.FONT_SIZE_BODY
        )
        self.font_root = tkfont.Font(
            family=config.FONT_FAMILY,
            size=config.FONT_SIZE_ROOT
        )
    
    def _create_title_bar(self):
        """创建标题栏"""
        title_bar = tk.Frame(
            self.main_frame,
            bg=config.COLOR_BG,
            height=30
        )
        title_bar.pack(fill=tk.X, pady=(0, 10))
        
        # 标题
        title_label = tk.Label(
            title_bar,
            text="🔍 BBDC Plus",
            font=(config.FONT_FAMILY, 10, 'bold'),
            bg=config.COLOR_BG,
            fg=config.COLOR_SECTION_TITLE
        )
        title_label.pack(side=tk.LEFT)
        
        # 绑定拖动事件
        title_bar.bind('<Button-1>', self._start_drag)
        title_bar.bind('<B1-Motion>', self._on_drag)
        title_label.bind('<Button-1>', self._start_drag)
        title_label.bind('<B1-Motion>', self._on_drag)
        
        # 关闭按钮
        close_btn = tk.Label(
            title_bar,
            text="✕",
            font=(config.FONT_FAMILY, 12, 'bold'),
            bg=config.COLOR_BG,
            fg=config.COLOR_PHONETIC,
            cursor="hand2"
        )
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind('<Button-1>', lambda e: self.hide())
        close_btn.bind('<Enter>', lambda e: close_btn.config(fg='#E74C3C'))
        close_btn.bind('<Leave>', lambda e: close_btn.config(fg=config.COLOR_PHONETIC))
    
    def _start_drag(self, event):
        """开始拖动"""
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
    
    def _on_drag(self, event):
        """拖动窗口"""
        deltax = event.x - self._drag_data["x"]
        deltay = event.y - self._drag_data["y"]
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
    
    def _show_welcome(self):
        """显示欢迎信息"""
        welcome_text = (
            "欢迎使用 BBDC Plus！\n\n"
            "📖 背单词软件增强工具\n\n"
            "快捷键:\n"
            f"  {config.HOTKEY_RESELECT} - 重新选择区域\n"
            f"  {config.HOTKEY_TOGGLE} - 显示/隐藏\n"
            f"  {config.HOTKEY_PAUSE} - 暂停/继续\n"
            f"  {config.HOTKEY_EXIT} - 退出\n\n"
            "等待识别单词..."
        )
        
        label = tk.Label(
            self.content_frame,
            text=welcome_text,
            font=self.font_body,
            bg=config.COLOR_BG,
            fg=config.COLOR_BODY,
            justify=tk.LEFT
        )
        label.pack(pady=20)
    
    def _clear_content(self):
        """清空内容区域"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def _add_separator(self):
        """添加分隔线"""
        sep = tk.Frame(
            self.content_frame,
            height=1,
            bg=config.COLOR_SEPARATOR
        )
        sep.pack(fill=tk.X, pady=8)
    
    def update_word(self, word_info: Dict, related_roots: List[Tuple[str, str]]):
        """更新显示的单词信息
        
        Args:
            word_info: 单词信息字典
            related_roots: 相关词根列表 [(词根, 含义), ...]
        """
        self._clear_content()
        
        # 显示单词和音标
        word_text = word_info['word'].upper()
        
        word_label = tk.Label(
            self.content_frame,
            text=word_text,
            font=self.font_word,
            bg=config.COLOR_BG,
            fg=config.COLOR_WORD
        )
        word_label.pack(anchor=tk.W)

        # 如果是模糊匹配，且原始识别与词库单词不同，显著提示“词库未收录”
        if word_info.get('fuzzy_match') and word_info.get('original_query') and word_info.get('matched_word'):
            original = word_info['original_query']
            matched = word_info['matched_word']
            if original != matched:
                warn = tk.Label(
                    self.content_frame,
                    text=f"⚠️  词库未收录: {original}  · 最接近: {matched}",
                    font=self.font_body,
                    bg=config.COLOR_BG,
                    fg="#F1C40F"
                )
                warn.pack(anchor=tk.W, pady=(2, 8))
        
        phonetic_label = tk.Label(
            self.content_frame,
            text=word_info['phonetic'],
            font=self.font_phonetic,
            bg=config.COLOR_BG,
            fg=config.COLOR_PHONETIC
        )
        phonetic_label.pack(anchor=tk.W, pady=(2, 10))
        
        # 显示词根拆分
        if 'root_split' in word_info and 'root_meaning' in word_info:
            self._add_separator()
            
            section_label = tk.Label(
                self.content_frame,
                text="📖 词根拆分",
                font=self.font_body,
                bg=config.COLOR_BG,
                fg=config.COLOR_SECTION_TITLE
            )
            section_label.pack(anchor=tk.W, pady=(5, 3))
            
            split_label = tk.Label(
                self.content_frame,
                text=f"   {word_info['root_split']}",
                font=self.font_body,
                bg=config.COLOR_BG,
                fg=config.COLOR_BODY
            )
            split_label.pack(anchor=tk.W)
            
            meaning_label = tk.Label(
                self.content_frame,
                text=f"   {word_info['root_meaning']}",
                font=self.font_body,
                bg=config.COLOR_BG,
                fg=config.COLOR_BODY
            )
            meaning_label.pack(anchor=tk.W)
        
        # 显示释义
        if 'definition' in word_info:
            self._add_separator()
            
            section_label = tk.Label(
                self.content_frame,
                text="💡 释义",
                font=self.font_body,
                bg=config.COLOR_BG,
                fg=config.COLOR_SECTION_TITLE
            )
            section_label.pack(anchor=tk.W, pady=(5, 3))
            
            # 处理释义文本（可能很长）
            definition = word_info['definition']
            if len(definition) > 150:
                definition = definition[:150] + "..."
            
            def_label = tk.Label(
                self.content_frame,
                text=f"   {definition}",
                font=self.font_body,
                bg=config.COLOR_BG,
                fg=config.COLOR_BODY,
                wraplength=config.WINDOW_WIDTH - 50,
                justify=tk.LEFT
            )
            def_label.pack(anchor=tk.W)
        
        # 显示真题意群（单独板块）
        if 'examples' in word_info and word_info['examples']:
            self._add_separator()
            section_label = tk.Label(
                self.content_frame,
                text="🧪 真题意群",
                font=self.font_body,
                bg=config.COLOR_BG,
                fg=config.COLOR_SECTION_TITLE
            )
            section_label.pack(anchor=tk.W, pady=(5, 3))

            examples_text = "\n".join([f"   {ex}" for ex in word_info['examples'][:2]])  # 最多显示2个
            example_label = tk.Label(
                self.content_frame,
                text=examples_text,
                font=self.font_root,
                bg=config.COLOR_BG,
                fg=config.COLOR_EXAMPLES,
                wraplength=config.WINDOW_WIDTH - 50,
                justify=tk.LEFT
            )
            example_label.pack(anchor=tk.W, pady=(2, 0))
        
        # 显示相关词根
        if related_roots:
            self._add_separator()
            
            section_label = tk.Label(
                self.content_frame,
                text="🌱 相关词根",
                font=self.font_body,
                bg=config.COLOR_BG,
                fg=config.COLOR_SECTION_TITLE
            )
            section_label.pack(anchor=tk.W, pady=(5, 3))
            
            for root, meaning in related_roots[:5]:  # 最多显示5个
                root_label = tk.Label(
                    self.content_frame,
                    text=f"   △ {root} = {meaning}",
                    font=self.font_root,
                    bg=config.COLOR_BG,
                    fg=config.COLOR_ROOT
                )
                root_label.pack(anchor=tk.W)
        
        # 更新窗口大小
        self.root.update_idletasks()
        height = min(
            max(self.content_frame.winfo_reqheight() + 80, config.WINDOW_MIN_HEIGHT),
            config.WINDOW_MAX_HEIGHT
        )
        self.root.geometry(f"{config.WINDOW_WIDTH}x{height}")
    
    def show_not_found(self, word: str):
        """显示未找到单词的提示
        
        Args:
            word: 查询的单词
        """
        self._clear_content()
        
        label = tk.Label(
            self.content_frame,
            text=f"❌ 未找到单词\n\n识别结果: {word}\n\n可能原因:\n• OCR 识别错误\n• 数据库中没有此单词\n• 请重新选择识别区域",
            font=self.font_body,
            bg=config.COLOR_BG,
            fg=config.COLOR_PHONETIC,
            justify=tk.LEFT
        )
        label.pack(pady=20)
    
    def show(self):
        """显示窗口"""
        if self.is_hidden:
            self.root.deiconify()
            self.is_hidden = False
    
    def hide(self):
        """隐藏窗口"""
        if not self.is_hidden:
            self.root.withdraw()
            self.is_hidden = True
    
    def toggle(self):
        """切换显示/隐藏"""
        if self.is_hidden:
            self.show()
        else:
            self.hide()
    
    def run(self):
        """运行窗口（测试用）"""
        self.root.mainloop()
    
    def destroy(self):
        """销毁窗口"""
        self.root.destroy()


def main():
    """测试代码"""
    window = FloatingWindow()
    
    # 测试数据
    test_word_info = {
        'word': 'abandon',
        'phonetic': '/əˈbændən/',
        'root_split': 'a+ban+don',
        'root_meaning': '×+禁止+给出',
        'definition': 'v.放弃；抛弃',
        'examples': ['abandon hope 放弃希望', 'abandon the plan 放弃计划']
    }
    
    test_roots = [
        ('ban', '禁止'),
        ('don', '给出'),
        ('a', '否定前缀')
    ]
    
    # 3秒后更新显示
    def update_test():
        window.update_word(test_word_info, test_roots)
    
    window.root.after(3000, update_test)
    
    window.run()


if __name__ == '__main__':
    main()

