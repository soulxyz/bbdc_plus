"""
OCR 识别引擎
使用 Tesseract OCR 识别屏幕指定区域的文字
"""

import re
from typing import List, Optional, Tuple
from PIL import ImageGrab, Image
import pytesseract


class OCREngine:
    def __init__(self):
        """初始化 OCR 引擎"""
        self.last_recognized_word = None
        self.recognition_count = 0
        
        # 配置 Tesseract（如果需要指定路径）
        # Windows 用户可能需要设置 Tesseract 路径
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> Image.Image:
        """截取屏幕指定区域
        
        Args:
            x: 区域左上角 X 坐标
            y: 区域左上角 Y 坐标
            width: 区域宽度
            height: 区域高度
        
        Returns:
            PIL Image 对象
        """
        # 截取屏幕区域
        bbox = (x, y, x + width, y + height)
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
            # 图片预处理（提高识别率）
            # 1. 转为灰度图
            image = image.convert('L')
            
            # 2. 可选：增强对比度
            # from PIL import ImageEnhance
            # enhancer = ImageEnhance.Contrast(image)
            # image = enhancer.enhance(2.0)
            
            # 使用 Tesseract 识别（只识别英文，提高速度）
            # --psm 6: 假设文本是单个统一的文本块
            # --oem 3: 默认 OCR 引擎模式
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            text = pytesseract.image_to_string(image, lang='eng', config=custom_config)
            
            self.recognition_count += 1
            return text.strip()
        
        except Exception as e:
            print(f"❌ OCR 识别错误: {e}")
            return ""
    
    def extract_words(self, text: str) -> List[str]:
        """从识别的文本中提取英文单词
        
        Args:
            text: 识别出的文本
        
        Returns:
            单词列表
        """
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

