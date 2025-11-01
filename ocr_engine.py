"""
OCR 识别引擎
使用 RapidOCR 识别屏幕指定区域的文字
"""

import re
from typing import List, Optional, Tuple
from PIL import ImageGrab, Image
from rapidocr_onnxruntime import RapidOCR
import numpy as np
from dpi_utils import get_dpi_manager
import config


class OCREngine:
    _shared_instance = None

    @classmethod
    def get_shared(cls):
        """获取共享的 OCR 实例（单例，避免重复加载模型）"""
        if cls._shared_instance is None:
            cls._shared_instance = OCREngine()
        return cls._shared_instance
    def __init__(self):
        """初始化 OCR 引擎"""
        self.last_recognized_word = None
        self.recognition_count = 0
        
        # 获取 DPI 管理器
        self.dpi_manager = get_dpi_manager()
        self._last_image_hash: Optional[int] = None
        
        # 初始化 RapidOCR
        print("   正在加载 RapidOCR 模型...")
        self.ocr = RapidOCR()
        print("   ✅ RapidOCR 加载完成")
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> Image.Image:
        """截取屏幕指定区域
        
        Args:
            x: 区域左上角 X 坐标（逻辑坐标）
            y: 区域左上角 Y 坐标（逻辑坐标）
            width: 区域宽度（逻辑坐标）
            height: 区域高度（逻辑坐标）
        
        Returns:
            PIL Image 对象
        """
        # 应用 DPI 缩放（转换为物理坐标）
        scaled_x, scaled_y, scaled_width, scaled_height = self.dpi_manager.scale_coordinates(
            x, y, width, height
        )
        
        # 调试输出：打印逻辑/物理坐标对照
        try:
            import config
            if getattr(config, 'DEBUG', False):
                print(f"📐 OCR 截图坐标: 逻辑=({x},{y},{width},{height}) → 物理=({scaled_x},{scaled_y},{scaled_width},{scaled_height})")
        except Exception:
            pass
        
        # 截取屏幕区域（使用物理坐标）
        bbox = (scaled_x, scaled_y, scaled_x + scaled_width, scaled_y + scaled_height)
        screenshot = ImageGrab.grab(bbox)
        return screenshot
    
    def recognize_text(self, image: Image.Image) -> str:
        """识别图片中的文字
        
        Args:
            image: PIL Image 对象
        
        Returns:
            识别出的文字
        """
        try:
            # 快速预处理：灰度 + 下采样 + 二值化（再转回RGB，兼容模型）
            if getattr(config, 'OCR_FAST_MODE', True):
                img = image.convert('L')
                w, h = img.size
                # 限制输入大小并按比例缩放
                max_w = getattr(config, 'OCR_MAX_WIDTH', 900)
                scale = getattr(config, 'OCR_DOWNSCALE', 0.75)
                target_w = min(int(w * scale), max_w) if w > 0 else w
                if target_w > 0 and target_w < w:
                    target_h = max(1, int(h * target_w / w))
                    img = img.resize((target_w, target_h), Image.BILINEAR)
                # 二值化
                thr = getattr(config, 'OCR_BIN_THRESHOLD', 180)
                img = img.point(lambda p: 255 if p > thr else 0, mode='1')
                # 转回三通道
                img = img.convert('RGB')
            else:
                img = image.convert('RGB')

            # 转换为 numpy 数组（RapidOCR 需要）
            img_array = np.array(img)
            
            # 使用 RapidOCR 识别
            # result 格式: [[[box], text, confidence], ...]
            result, elapse = self.ocr(img_array)
            
            self.recognition_count += 1
            
            # 如果没有识别结果
            if not result:
                return ""
            
            # 提取所有识别到的文本，用空格连接
            texts = [item[1] for item in result]
            text = ' '.join(texts)
            
            return text.strip()
        
        except Exception as e:
            print(f"❌ OCR 识别错误: {e}")
            return ""

    # ---- 图像变化检测 ----
    def _compute_ahash(self, image: Image.Image) -> int:
        """计算图像的 aHash（平均哈希），返回 64bit 整数"""
        img = image.convert('L').resize((8, 8), Image.BILINEAR)
        arr = np.asarray(img, dtype=np.float32)
        mean = arr.mean()
        bits = (arr > mean).astype(np.uint8).flatten()
        value = 0
        for b in bits:
            value = (value << 1) | int(b)
        return int(value)

    def _hamming_distance(self, a: int, b: int) -> int:
        x = a ^ b
        # Brian Kernighan 技巧
        cnt = 0
        while x:
            x &= x - 1
            cnt += 1
        return cnt
    
    def extract_words(self, text: str) -> List[str]:
        """从识别的文本中提取英文单词
        
        Args:
            text: 识别出的文本
        
        Returns:
            单词列表
        """
        print(text)
        if not text:
            return []
        
        # 使用正则提取所有英文单词（至少2个字母）
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text)
        
        # 转为小写并去重（保持顺序）
        seen = set()
        unique_words = []
        for word in words:
            word_lower = word.lower()
            if word_lower not in seen:
                seen.add(word_lower)
                unique_words.append(word_lower)
        
        return unique_words
    
    def recognize_region(self, x: int, y: int, width: int, height: int) -> List[str]:
        """识别屏幕区域中的单词
        
        Args:
            x: 区域左上角 X 坐标
            y: 区域左上角 Y 坐标
            width: 区域宽度
            height: 区域高度
        
        Returns:
            识别出的单词列表
        """
        # 截取屏幕
        image = self.capture_region(x, y, width, height)
        
        # 屏幕未变化则跳过 OCR
        try:
            current_hash = self._compute_ahash(image)
            if self._last_image_hash is not None:
                diff = self._hamming_distance(self._last_image_hash, current_hash)
                if diff <= getattr(config, 'IMAGE_HASH_DIFF_THRESHOLD', 2):
                    if getattr(config, 'DEBUG', False):
                        print(f"🧩 图像未变化(H={diff})，跳过 OCR")
                    return []
            self._last_image_hash = current_hash
        except Exception:
            pass
        
        # 识别文字
        text = self.recognize_text(image)
        
        # 提取单词
        words = self.extract_words(text)
        
        return words
    
    def get_primary_word(self, words: List[str]) -> Optional[str]:
        """从单词列表中获取主要单词（通常是最长的）
        
        Args:
            words: 单词列表
        
        Returns:
            主要单词，如果列表为空返回 None
        """
        if not words:
            return None
        
        # 返回最长的单词（通常背单词软件会突出显示主单词）
        return max(words, key=len)
    
    def should_update(self, word: Optional[str]) -> bool:
        """判断是否需要更新显示（防抖）
        
        Args:
            word: 当前识别的单词
        
        Returns:
            是否需要更新
        """
        if word is None:
            return False
        
        # 如果和上次识别的单词不同，需要更新
        if word != self.last_recognized_word:
            self.last_recognized_word = word
            return True
        
        return False


def main():
    """测试代码"""
    import time
    
    print("OCR 引擎测试")
    print("="*80)
    
    # 提示用户准备测试文本
    print("\n请准备一个显示英文单词的窗口")
    print("程序将在 5 秒后截取屏幕中心 300x100 的区域进行识别...")
    
    for i in range(5, 0, -1):
        print(f"{i}...", end=' ', flush=True)
        time.sleep(1)
    print("\n")
    
    # 创建 OCR 引擎
    ocr = OCREngine()
    
    # 获取屏幕中心区域
    from PIL import ImageGrab
    screen = ImageGrab.grab()
    screen_width, screen_height = screen.size
    
    # 截取中心区域
    x = screen_width // 2 - 150
    y = screen_height // 2 - 50
    width = 300
    height = 100
    
    print(f"截取区域: x={x}, y={y}, width={width}, height={height}")
    
    # 识别
    words = ocr.recognize_region(x, y, width, height)
    
    print(f"\n识别结果:")
    if words:
        print(f"  找到 {len(words)} 个单词: {', '.join(words)}")
        primary = ocr.get_primary_word(words)
        print(f"  主要单词: {primary}")
    else:
        print("  未识别到单词")
    
    print(f"\n识别次数: {ocr.recognition_count}")


if __name__ == '__main__':
    main()

