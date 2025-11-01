"""
屏幕区域选择工具
允许用户通过鼠标拖拽选择屏幕上的矩形区域
支持高DPI和显示缩放
"""

import tkinter as tk
from typing import Tuple, Optional, Callable
from dpi_utils import get_dpi_manager, setup_tkinter_dpi


class ScreenSelector:
    def __init__(self, callback: Optional[Callable] = None, master: Optional[tk.Misc] = None):
        """初始化屏幕选择器
        
        Args:
            callback: 选择完成后的回调函数，接收 (x, y, width, height) 参数
            master: 可选，已有的 tkinter 根窗口/顶层窗口。若提供，将使用 Toplevel 避免多 Tk 冲突
        """
        self.callback = callback
        self.master = master
        self.selected_region: Optional[Tuple[int, int, int, int]] = None
        
        # 获取 DPI 管理器
        self.dpi_manager = get_dpi_manager()
        
        self.root = None
        self.canvas = None
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.text = None
    
    def select_region(self) -> Tuple[int, int, int, int]:
        """显示选择界面，返回选中的区域
        
        Returns:
            (x, y, width, height) 元组（逻辑坐标）
        """
        self.selected_region = None
        
        # 创建全屏透明窗口
        if self.master is not None:
            # 使用 Toplevel，避免创建第二个 Tk 根窗口
            self.root = tk.Toplevel(self.master)
        else:
            self.root = tk.Tk()
        
        # 设置 DPI 支持
        setup_tkinter_dpi(self.root)
        
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)  # 半透明
        self.root.attributes('-topmost', True)
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 创建画布
        self.canvas = tk.Canvas(
            self.root,
            width=screen_width,
            height=screen_height,
            bg='black',
            highlightthickness=0,
            cursor='cross'
        )
        self.canvas.pack()
        
        # 显示提示文字
        hint_text = self.canvas.create_text(
            screen_width // 2,
            50,
            text="拖拽鼠标选择识别区域，释放完成选择\n按 ESC 取消",
            font=('Arial', 20, 'bold'),
            fill='white'
        )
        
        # 绑定鼠标事件
        self.canvas.bind('<Button-1>', self._on_mouse_down)
        self.canvas.bind('<B1-Motion>', self._on_mouse_move)
        self.canvas.bind('<ButtonRelease-1>', self._on_mouse_up)
        
        # 绑定键盘事件
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        
        # 运行事件循环
        if self.master is not None:
            # 模态行为，阻塞直到关闭
            try:
                self.root.grab_set()
            except Exception:
                pass
            self.root.focus_set()
            self.root.wait_window()
        else:
            self.root.mainloop()
        
        return self.selected_region
    
    def _on_mouse_down(self, event):
        """鼠标按下事件"""
        self.start_x = event.x
        self.start_y = event.y
        
        # 创建矩形
        if self.rect:
            self.canvas.delete(self.rect)
        if self.text:
            self.canvas.delete(self.text)
    
    def _on_mouse_move(self, event):
        """鼠标移动事件"""
        if self.start_x is None or self.start_y is None:
            return
        
        # 更新矩形
        if self.rect:
            self.canvas.delete(self.rect)
        if self.text:
            self.canvas.delete(self.text)
        
        # 绘制新矩形
        self.rect = self.canvas.create_rectangle(
            self.start_x,
            self.start_y,
            event.x,
            event.y,
            outline='red',
            width=3,
            fill='white',
            stipple='gray50'  # 半透明填充
        )
        
        # 显示尺寸信息
        width = abs(event.x - self.start_x)
        height = abs(event.y - self.start_y)
        info_text = f"{width} × {height}"
        
        # 文字位置在矩形上方
        text_x = (self.start_x + event.x) / 2
        text_y = min(self.start_y, event.y) - 10
        
        self.text = self.canvas.create_text(
            text_x,
            text_y,
            text=info_text,
            font=('Arial', 14, 'bold'),
            fill='red'
        )
    
    def _on_mouse_up(self, event):
        """鼠标释放事件"""
        if self.start_x is None or self.start_y is None:
            return
        
        # 计算选中区域（确保 x, y 是左上角坐标）
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)
        
        width = x2 - x1
        height = y2 - y1
        
        # 验证区域大小
        if width < 10 or height < 10:
            print("⚠️ 选择区域太小，请重新选择")
            self.start_x = None
            self.start_y = None
            if self.rect:
                self.canvas.delete(self.rect)
            if self.text:
                self.canvas.delete(self.text)
            return
        
        # 将物理坐标转换成逻辑坐标再返回，避免后续重复缩放
        lx, ly, lw, lh = self.dpi_manager.unscale_coordinates(x1, y1, width, height)
        self.selected_region = (int(lx), int(ly), int(lw), int(lh))
        
        # 调用回调函数
        if self.callback:
            self.callback(int(lx), int(ly), int(lw), int(lh))
        
        # 关闭窗口
        self.root.destroy()


def main():
    """测试代码"""
    print("启动屏幕区域选择工具...")
    print("请在屏幕上拖拽选择一个矩形区域")
    
    def on_region_selected(x, y, width, height):
        print(f"\n✅ 选择完成！")
        print(f"   位置: ({x}, {y})")
        print(f"   尺寸: {width} × {height}")
    
    selector = ScreenSelector(callback=on_region_selected)
    region = selector.select_region()
    
    if region:
        x, y, width, height = region
        print(f"\n返回值: x={x}, y={y}, width={width}, height={height}")
    else:
        print("\n❌ 未选择区域（可能按了 ESC）")


if __name__ == '__main__':
    main()

