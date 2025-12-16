from typing import List, Set, Optional
from collections import deque
import re

class TrieNode:
    
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
class Trie:
    
    def __init__(self):
        self.root=TrieNode()
    
    def insert(self, word: str) -> None:
        
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
    
    def search(self, word: str) -> bool:
        
        node = self.root
        for char in word.lower():
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

class QueryProcessor:
    
    
    def __init__(self):
        
        self.stop_words_trie = Trie()
        self._initialize_stop_words()
        
    def _initialize_stop_words(self) -> None:
       

        stop_words_list = [
            'what', 'is', 'a', 'an', 'the', 'how', 'does', 'do', 'are', 'can', 
            'i', 'you', 'we', 'they', 'this', 'that', 'these', 'those', 'in', 
            'on', 'at', 'to', 'for', 'of', 'with', 'from', 'by', 'about', 
            'into', 'through', 'during', 'including', 'against', 'among', 
            'throughout', 'despite', 'towards', 'upon', 'concerning', 'up',
            'attack', 'attacks'  
        ]
        for word in stop_words_list:
            self.stop_words_trie.insert(word)
            
    def tokenize(self, text: str)->List[str]:
       
        if not text:
            return []
        return re.findall(r'\b[a-z]+\b', text.lower())
    
    def process_query(self,query: str) -> List[str]:
        
        if not query:
            return []
            
       
        raw_tokens = self.tokenize(query)
        
      
        token_queue = deque(raw_tokens)
        processed_tokens: List[str] = []
        
        while token_queue:
            token = token_queue.popleft()
            
            
            if len(token) <= 2:
                continue
                
           

            if not self.stop_words_trie.search(token):
                processed_tokens.append(token)
                
        return processed_tokens
