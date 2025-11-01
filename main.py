"""
BBDC Plus - 背单词增强工具
主控制器，整合所有模块
"""

import sys
import threading
import time
import queue
from typing import Optional, Tuple
import keyboard
import config

# 导入自定义模块
from database import WordDatabase
from screen_selector import ScreenSelector
from ocr_engine import OCREngine
from floating_window import FloatingWindow
from dpi_utils import get_dpi_manager


class BBDCPlus:
    def __init__(self):
        """初始化应用"""
        print("="*80)
        print("🚀 BBDC Plus - 背单词增强工具")
        print("="*80)
        
        # 初始化 DPI 管理器
        print("\n🖥️  初始化 DPI 设置...")
        self.dpi_manager = get_dpi_manager()
        
        # 初始化各个模块
        print("\n📚 正在加载数据库...")
        self.database = WordDatabase(config.DATABASE_FILE)
        
        print("🔍 初始化 OCR 引擎...")
        # 使用共享实例，避免重复加载模型
        self.ocr = OCREngine.get_shared()
        
        print("🖼️  创建悬浮窗...")
        self.window = FloatingWindow()
        
        # 状态变量
        self.selected_region: Optional[Tuple[int, int, int, int]] = None
        self.is_running = True
        self.is_paused = False
        self.ocr_thread: Optional[threading.Thread] = None
        
        # 命令队列（用于线程安全的快捷键处理）
        self.command_queue = queue.Queue()
        
        # 注册全局快捷键
        self._register_hotkeys()
        
        print("\n✅ 初始化完成！")
    
    def _register_hotkeys(self):
        """注册全局快捷键"""
        print(f"\n⌨️  注册快捷键:")
        print(f"   {config.HOTKEY_RESELECT} - 重新选择区域")
        print(f"   {config.HOTKEY_TOGGLE} - 显示/隐藏悬浮窗")
        print(f"   {config.HOTKEY_PAUSE} - 暂停/继续识别")
        print(f"   {config.HOTKEY_EXIT} - 退出程序")
        
        try:
            keyboard.add_hotkey(config.HOTKEY_RESELECT, self._on_reselect)
            keyboard.add_hotkey(config.HOTKEY_TOGGLE, self._on_toggle)
            keyboard.add_hotkey(config.HOTKEY_PAUSE, self._on_pause)
            keyboard.add_hotkey(config.HOTKEY_EXIT, self._on_exit)
        except Exception as e:
            print(f"⚠️  快捷键注册失败: {e}")
            print("   提示：请以管理员权限运行程序")
    
    def _on_reselect(self):
        """重新选择屏幕区域"""
        # 将命令放入队列，由主线程处理
        self.command_queue.put('reselect')
    
    def _on_toggle(self):
        """切换悬浮窗显示/隐藏"""
        # 将命令放入队列，由主线程处理
        self.command_queue.put('toggle')
    
    def _on_pause(self):
        """暂停/继续识别"""
        # 这个操作不涉及 GUI，可以直接执行
        self.is_paused = not self.is_paused
        state = "暂停" if self.is_paused else "继续"
        print(f"\n⏸️  识别已{state}")
    
    def _on_exit(self):
        """退出程序"""
        # 将命令放入队列，由主线程处理
        print("\n👋 正在退出...")
        self.is_running = False
        self.command_queue.put('exit')
    
    def _process_commands(self):
        """处理命令队列（在主线程中周期性调用）"""
        try:
            while not self.command_queue.empty():
                command = self.command_queue.get_nowait()
                
                if command == 'reselect':
                    print("\n🖱️  重新选择屏幕区域...")
                    self.select_region()
                
                elif command == 'toggle':
                    self.window.toggle()
                    state = "隐藏" if self.window.is_hidden else "显示"
                    print(f"\n👁️  悬浮窗已{state}")
                
                elif command == 'exit':
                    self.window.destroy()
                    sys.exit(0)
        
        except queue.Empty:
            pass
        
        # 继续周期性检查命令队列
        if self.is_running:
            self.window.root.after(100, self._process_commands)
    
    def select_region(self) -> bool:
        """选择屏幕识别区域
        
        Returns:
            是否成功选择区域
        """
        selector = ScreenSelector(master=self.window.root)
        region = selector.select_region()
        
        if region:
            self.selected_region = region
            x, y, width, height = region
            print(f"\n✅ 已选择区域: 位置({x}, {y})  尺寸({width}×{height})")
            return True
        else:
            print("\n❌ 未选择区域")
            return False
    
    def _ocr_loop(self):
        """OCR 识别循环（在后台线程运行）"""
        if not self.selected_region:
            return
        
        x, y, width, height = self.selected_region
        last_word = None
        loop_count = 0
        
        print(f"\n🔄 开始识别循环（每 {config.OCR_INTERVAL} 秒）")
        print("   按 F4 暂停/继续，按 ESC 退出\n")
        
        while self.is_running:
            try:
                loop_count += 1
                
                # 如果暂停，跳过识别
                if self.is_paused:
                    time.sleep(0.5)
                    continue
                
                # 显示识别进度（每5次显示一次）
                if config.DEBUG and loop_count % 5 == 0:
                    print(f"⏱️  正在识别... (第 {loop_count} 次)")
                
                # 识别屏幕区域
                words = self.ocr.recognize_region(x, y, width, height)
                
                if config.DEBUG:
                    print(f"🔍 识别结果: {words if words else '(空)'}")
                
                if not words:
                    time.sleep(config.OCR_INTERVAL)
                    continue
                
                # 获取主要单词
                primary_word = self.ocr.get_primary_word(words)
                
                if config.DEBUG:
                    print(f"   → 主单词: {primary_word}")
                
                # 如果和上次相同，跳过
                if not self.ocr.should_update(primary_word):
                    if config.DEBUG:
                        print(f"   → 和上次相同，跳过")
                    time.sleep(config.OCR_INTERVAL)
                    continue
                
                # 查询数据库
                if config.DEBUG:
                    print(f"📚 查询数据库: {primary_word}")
                
                word_info = self.database.lookup(primary_word, fuzzy=True)
                
                if word_info:
                    # 获取相关词根
                    related_roots = self.database.get_related_roots(word_info)
                    
                    # 更新悬浮窗
                    self.window.root.after(0, lambda: self.window.update_word(word_info, related_roots))
                    
                    # 输出日志
                    match_info = ""
                    if word_info.get('fuzzy_match'):
                        match_info = f" (模糊匹配: {word_info['matched_word']})"
                    print(f"✅ {primary_word}{match_info} - {word_info.get('definition', '')[:50]}")
                else:
                    # 未找到
                    self.window.root.after(0, lambda w=primary_word: self.window.show_not_found(w))
                    print(f"❌ 未找到: {primary_word}")
                
                last_word = primary_word
                
            except Exception as e:
                print(f"❌ 识别错误: {e}")
                if config.DEBUG:
                    import traceback
                    traceback.print_exc()
            
            # 等待下一次识别
            time.sleep(config.OCR_INTERVAL)
    
    def run(self):
        """运行应用"""
        print("\n" + "="*80)
        print("请选择要识别的屏幕区域...")
        print("="*80)
        
        # 选择屏幕区域
        if not self.select_region():
            print("未选择区域，程序退出")
            return
        
        # 启动 OCR 识别线程
        self.ocr_thread = threading.Thread(target=self._ocr_loop, daemon=True)
        self.ocr_thread.start()
        
        # 启动命令处理循环
        self.window.root.after(100, self._process_commands)
        
        # 运行 GUI 主循环
        try:
            self.window.run()
        except KeyboardInterrupt:
            print("\n\n👋 程序已退出")
        finally:
            self.is_running = False


def main():
    """主函数"""
    try:
        # 创建并运行应用
        app = BBDCPlus()
        app.run()
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")


if __name__ == '__main__':
    main()

