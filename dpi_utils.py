"""
DPI 工具模块
处理高DPI和缩放问题，确保在不同显示缩放下正常工作
"""

import sys
import platform


class DPIManager:
    """DPI 管理器"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化 DPI 管理器"""
        if DPIManager._initialized:
            return
        
        self.scale_factor = 1.0
        self._setup_dpi_awareness()
        self._get_scale_factor()
        
        DPIManager._initialized = True
    
    def _setup_dpi_awareness(self):
        """设置 DPI 感知（仅 Windows）"""
        if platform.system() != 'Windows':
            return
        
        try:
            import ctypes
            
            # 尝试设置 DPI 感知级别（优先使用最新的API）
            try:
                # Windows 10 1703+ 支持 Per-Monitor V2
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
                print("   ✅ 已启用 Per-Monitor V2 DPI 感知")
            except:
                try:
                    # Windows 8.1+ 支持 Per-Monitor
                    ctypes.windll.shcore.SetProcessDpiAwareness(1)
                    print("   ✅ 已启用 Per-Monitor DPI 感知")
                except:
                    try:
                        # Windows Vista+ 支持 System DPI
                        ctypes.windll.user32.SetProcessDPIAware()
                        print("   ✅ 已启用 System DPI 感知")
                    except:
                        print("   ⚠️ 无法设置 DPI 感知，可能会出现坐标偏移")
        
        except Exception as e:
            print(f"   ⚠️ 设置 DPI 感知时出错: {e}")
    
    def _get_scale_factor(self):
        """获取显示缩放因子"""
        if platform.system() != 'Windows':
            return
        
        try:
            import ctypes
            
            # 获取主显示器的 DPI
            hdc = ctypes.windll.user32.GetDC(0)
            dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # 88 = LOGPIXELSX
            ctypes.windll.user32.ReleaseDC(0, hdc)
            
            # 计算缩放因子（标准DPI是96）
            self.scale_factor = dpi / 96.0
            
            if self.scale_factor != 1.0:
                print(f"   📐 检测到显示缩放: {int(self.scale_factor * 100)}% (DPI: {dpi})")
            else:
                print(f"   📐 显示缩放: 100% (DPI: {dpi})")
        
        except Exception as e:
            print(f"   ⚠️ 获取缩放因子时出错: {e}")
            self.scale_factor = 1.0
    
    def get_scale_factor(self) -> float:
        """获取当前的缩放因子
        
        Returns:
            缩放因子（例如 1.25 表示 125% 缩放）
        """
        return self.scale_factor
    
    def scale_coordinates(self, x: int, y: int, width: int, height: int):
        """将逻辑坐标转换为物理坐标（用于截图）
        
        Args:
            x: X 坐标
            y: Y 坐标
            width: 宽度
            height: 高度
        
        Returns:
            缩放后的坐标元组 (x, y, width, height)
        """
        if self.scale_factor == 1.0:
            return (x, y, width, height)
        
        return (
            int(x * self.scale_factor),
            int(y * self.scale_factor),
            int(width * self.scale_factor),
            int(height * self.scale_factor)
        )
    
    def unscale_coordinates(self, x: int, y: int, width: int, height: int):
        """将物理坐标转换为逻辑坐标
        
        Args:
            x: X 坐标
            y: Y 坐标
            width: 宽度
            height: 高度
        
        Returns:
            反缩放后的坐标元组 (x, y, width, height)
        """
        if self.scale_factor == 1.0:
            return (x, y, width, height)
        
        return (
            int(x / self.scale_factor),
            int(y / self.scale_factor),
            int(width / self.scale_factor),
            int(height / self.scale_factor)
        )


# 全局 DPI 管理器实例
_dpi_manager = None


def get_dpi_manager() -> DPIManager:
    """获取 DPI 管理器实例
    
    Returns:
        DPI 管理器单例
    """
    global _dpi_manager
    if _dpi_manager is None:
        _dpi_manager = DPIManager()
    return _dpi_manager


def setup_tkinter_dpi(root):
    """为 tkinter 窗口设置 DPI 支持
    
    Args:
        root: tkinter 根窗口
    """
    if platform.system() != 'Windows':
        return
    
    try:
        # 在 Windows 上调用 scaling 方法可能会有帮助
        dpi_manager = get_dpi_manager()
        scale = dpi_manager.get_scale_factor()
        
        if scale != 1.0:
            # 某些情况下可能需要调整 tkinter 的缩放
            # root.tk.call('tk', 'scaling', scale)
            pass
    
    except Exception as e:
        print(f"⚠️ 设置 tkinter DPI 时出错: {e}")


if __name__ == '__main__':
    """测试代码"""
    print("=" * 80)
    print("DPI 工具测试")
    print("=" * 80)
    
    # 获取 DPI 管理器
    dpi = get_dpi_manager()
    
    print(f"\n当前缩放因子: {dpi.get_scale_factor()}")
    print(f"当前缩放百分比: {int(dpi.get_scale_factor() * 100)}%")
    
    # 测试坐标转换
    print("\n测试坐标转换:")
    test_coords = (100, 100, 200, 150)
    print(f"  逻辑坐标: {test_coords}")
    
    scaled = dpi.scale_coordinates(*test_coords)
    print(f"  物理坐标（用于截图）: {scaled}")
    
    unscaled = dpi.unscale_coordinates(*scaled)
    print(f"  反转换后: {unscaled}")
    
    print("\n" + "=" * 80)

