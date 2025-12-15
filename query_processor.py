from typing import List, Set, Optional
from collections import deque
import re

class TrieNode:
    
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
