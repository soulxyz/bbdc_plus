"""
数据库解析模块
解析 HTML 文件中的单词和词根数据，构建索引字典
"""

import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import difflib


class WordDatabase:
    def __init__(self, html_file: str):
        """初始化数据库，解析 HTML 文件"""
        self.html_file = html_file
        self.word_dict: Dict[str, dict] = {}  # 单词 -> 完整信息
        self.root_dict: Dict[str, str] = {}   # 词根 -> 含义
        self.word_list: List[str] = []        # 所有单词列表（用于模糊匹配）
        
        self._parse_html()
        print(f"✅ 数据库加载完成：{len(self.word_dict)} 个单词，{len(self.root_dict)} 个词根")
    
    def _parse_html(self):
        """解析 HTML 文件"""
        with open(self.html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        paragraphs = soup.find_all('p')
        
        for p in paragraphs:
            text = p.get_text(strip=True)
            
            # 跳过空行和短行
            if not text or len(text) < 3:
                continue
            
            # 识别词根条目（以 △ 开头）
            if text.startswith('△'):
                self._parse_root(text)
            # 识别单词条目（包含音标斜杠）
            elif '/' in text and re.match(r'^[a-zA-Z]', text):
                self._parse_word(text)
    
    def _parse_root(self, text: str):
        """解析词根条目
        格式: △ act=做 驱使
        """
        # 移除 △ 符号
        text = text.replace('△', '').strip()
        
        if '=' in text:
            parts = text.split('=', 1)
            if len(parts) == 2:
                root_variants = parts[0].strip()
                meaning = parts[1].strip()
                
                # 处理多个词根变体（如 "al alter altern"）
                roots = root_variants.split()
                for root in roots:
                    root = root.strip()
                    if root:
                        self.root_dict[root.lower()] = meaning
    
    def _parse_word(self, text: str):
        """解析单词条目
        格式: word /phonetic/=root_split=root_meaning=definition...
        """
        # 匹配基本格式: 单词 + 音标
        match = re.match(r'^([a-zA-Z]+(?:\s+[a-zA-Z]+)?)\s*/([^/]+)/(.*)$', text)
        if not match:
            return
        
        word, phonetic, rest = match.groups()
        word = word.strip().lower()
        phonetic = phonetic.strip()
        
        # 解析等号分隔的部分
        parts = rest.split('=')
        
        word_info = {
            'word': word,
            'phonetic': f'/{phonetic}/',
            'raw_text': text
        }
        
        # 尝试提取结构化信息
        if len(parts) >= 1:
            # 找到第一个包含+号的部分（词根拆分）
            root_split_index = -1
            for i, part in enumerate(parts):
                if '+' in part.strip():
                    root_split_index = i
                    break
            
            if root_split_index >= 0 and root_split_index + 2 < len(parts):
                # 找到了词根拆分结构
                word_info['root_split'] = parts[root_split_index].strip()
                word_info['root_meaning'] = parts[root_split_index + 1].strip()
                word_info['definition'] = parts[root_split_index + 2].strip()
                
                # 如果还有更多内容
                if root_split_index + 3 < len(parts):
                    word_info['extra'] = '='.join(parts[root_split_index + 3:])
            else:
                # 没有词根拆分，直接取释义
                # 跳过空的部分
                for part in parts:
                    part = part.strip()
                    if part and len(part) > 0:
                        word_info['definition'] = part
                        break
        else:
            # 没有词根拆分的单词，直接放剩余内容
            word_info['definition'] = rest.strip()
        
        # 提取【真题意群】
        examples = re.findall(r'【真题意群】([^【]+)', text)
        if examples:
            word_info['examples'] = [ex.strip() for ex in examples]
        
        # 提取同义词/反义词（通常在末尾）
        synonyms = re.findall(r'(?:同义|近义)[：:]?\s*([a-zA-Z\s,;]+)', text)
        if synonyms:
            word_info['synonyms'] = [s.strip() for s in re.split(r'[,;]', synonyms[0]) if s.strip()]
        
        # 存储到字典
        self.word_dict[word] = word_info
        self.word_list.append(word)
    
    def lookup(self, word: str, fuzzy: bool = True) -> Optional[dict]:
        """查询单词
        
        Args:
            word: 要查询的单词
            fuzzy: 是否启用模糊匹配
        
        Returns:
            单词信息字典，如果未找到返回 None
        """
        word = word.lower().strip()
        
        # 精确匹配
        if word in self.word_dict:
            return self.word_dict[word]
        
        # 模糊匹配
        if fuzzy and len(word) > 3:
            # 使用 difflib 找到最接近的单词
            matches = difflib.get_close_matches(word, self.word_list, n=1, cutoff=0.8)
            if matches:
                matched_word = matches[0]
                result = self.word_dict[matched_word].copy()
                result['fuzzy_match'] = True
                result['original_query'] = word
                result['matched_word'] = matched_word
                return result
        
        return None
    
    def lookup_root(self, root: str) -> Optional[str]:
        """查询词根含义
        
        Args:
            root: 词根
        
        Returns:
            词根含义，如果未找到返回 None
        """
        root = root.lower().strip()
        return self.root_dict.get(root)
    
    def get_related_roots(self, word_info: dict) -> List[tuple]:
        """获取单词相关的词根信息
        
        Args:
            word_info: 单词信息字典
        
        Returns:
            [(词根, 含义), ...] 列表
        """
        if 'root_split' not in word_info:
            return []
        
        root_split = word_info['root_split']
        # 提取词根（以 + 分隔）
        roots = re.findall(r'[a-zA-Z]+', root_split)
        
        related = []
        for root in roots:
            root_lower = root.lower()
            if root_lower in self.root_dict:
                related.append((root, self.root_dict[root_lower]))
        
        return related


if __name__ == '__main__':
    # 测试代码
    print("正在加载数据库...")
    db = WordDatabase("词汇新修版讲义_files/content.htm")
    
    # 测试查询
    test_words = ['abandon', 'amateur', 'anniversary', 'act', 'react']
    
    print("\n" + "="*80)
    print("测试单词查询")
    print("="*80)
    
    for word in test_words:
        print(f"\n查询: {word}")
        result = db.lookup(word)
        if result:
            print(f"  单词: {result['word']}")
            print(f"  音标: {result['phonetic']}")
            if 'root_split' in result:
                print(f"  词根拆分: {result['root_split']}")
                print(f"  词根含义: {result['root_meaning']}")
            print(f"  释义: {result.get('definition', 'N/A')[:100]}")
            
            # 查询相关词根
            related_roots = db.get_related_roots(result)
            if related_roots:
                print(f"  相关词根:")
                for root, meaning in related_roots:
                    print(f"    △ {root} = {meaning}")
        else:
            print(f"  ❌ 未找到")
    
    # 测试模糊匹配
    print("\n" + "="*80)
    print("测试模糊匹配")
    print("="*80)
    
    test_fuzzy = ['abandan', 'reacton', 'amatuer']
    for word in test_fuzzy:
        print(f"\n查询: {word} (拼写错误)")
        result = db.lookup(word, fuzzy=True)
        if result and result.get('fuzzy_match'):
            print(f"  → 找到相似单词: {result['matched_word']}")
            print(f"  音标: {result['phonetic']}")

