"""
Advanced Data Structures Implementation
Implements: Stack, Queue, Tree, Graph
"""
from collections import deque
from typing import List, Dict, Set, Optional, Any, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from indexer import Article


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate the Levenshtein distance between two strings.
    This is the minimum number of single-character edits (insertions, deletions, or substitutions)
    required to change one word into the other.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


class Stack:
   
    
    def __init__(self):
        self.items: List[Any] = []
    
    def push(self, item: Any) -> None:
        """Push item onto stack"""
        self.items.append(item)
    
    def pop(self) -> Optional[Any]:
        """Pop item from stack"""
        if self.is_empty():
            return None
        return self.items.pop()
    
    def peek(self) -> Optional[Any]:
        """Peek at top item without removing"""
        if self.is_empty():
            return None
        return self.items[-1]
    
    def is_empty(self) -> bool:
        """Check if stack is empty"""
        return len(self.items) == 0
    
    def size(self) -> int:
        """Get stack size"""
        return len(self.items)
    
    def __str__(self) -> str:
        return str(self.items)


# ==================== QUEUE ====================
class Queue:
    """Queue implementation using deque (FIFO - First In First Out)"""
    
    def __init__(self):
        self.items: deque = deque()
    
    def enqueue(self, item: Any) -> None:
        """Add item to queue"""
        self.items.append(item)
    
    def dequeue(self) -> Optional[Any]:
        """Remove item from queue"""
        if self.is_empty():
            return None
        return self.items.popleft()
    
    def front(self) -> Optional[Any]:
        """Get front item without removing"""
        if self.is_empty():
            return None
        return self.items[0]
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return len(self.items) == 0
    
    def size(self) -> int:
        """Get queue size"""
        return len(self.items)
    
    def __str__(self) -> str:
        return str(list(self.items))


# ==================== TREE ====================
class TreeNode:
    """Node for binary tree"""
    
    def __init__(self, data: Any):
        self.data = data
        self.left: Optional['TreeNode'] = None
        self.right: Optional['TreeNode'] = None


class BinarySearchTree:
    """Binary Search Tree implementation"""
    
    def __init__(self):
        self.root: Optional[TreeNode] = None
    
    def insert(self, data: Any) -> None:
        """Insert data into BST"""
        self.root = self._insert_recursive(self.root, data)
    
    def _insert_recursive(self, node: Optional[TreeNode], data: Any) -> TreeNode:
        """Recursive insert helper"""
        if node is None:
            return TreeNode(data)
        
        # Compare based on string representation for articles (check for unique_id attribute)
        if hasattr(data, 'unique_id') and hasattr(node.data, 'unique_id'):
            if data.unique_id < node.data.unique_id:
                node.left = self._insert_recursive(node.left, data)
            else:
                node.right = self._insert_recursive(node.right, data)
        elif str(data) < str(node.data):
            node.left = self._insert_recursive(node.left, data)
        else:
            node.right = self._insert_recursive(node.right, data)
        
        return node
    
    def search(self, data: Any) -> Optional[TreeNode]:
        """Search for data in BST"""
        return self._search_recursive(self.root, data)
    
    def _search_recursive(self, node: Optional[TreeNode], data: Any) -> Optional[TreeNode]:
        """Recursive search helper"""
        if node is None:
            return None
        
        # Check if data matches
        if hasattr(data, 'unique_id') and hasattr(node.data, 'unique_id'):
            if data.unique_id == node.data.unique_id:
                return node
            if data.unique_id < node.data.unique_id:
                return self._search_recursive(node.left, data)
            return self._search_recursive(node.right, data)
        
        if node.data == data:
            return node
        
        if str(data) < str(node.data):
            return self._search_recursive(node.left, data)
        return self._search_recursive(node.right, data)
    
    def inorder_traversal(self) -> List[Any]:
        """In-order traversal (left, root, right)"""
        result = []
        self._inorder_recursive(self.root, result)
        return result
    
    def _inorder_recursive(self, node: Optional[TreeNode], result: List[Any]) -> None:
        """Recursive in-order traversal"""
        if node:
            self._inorder_recursive(node.left, result)
            result.append(node.data)
            self._inorder_recursive(node.right, result)
    
    def preorder_traversal(self) -> List[Any]:
        """Pre-order traversal (root, left, right)"""
        result = []
        self._preorder_recursive(self.root, result)
        return result
    
    def _preorder_recursive(self, node: Optional[TreeNode], result: List[Any]) -> None:
        """Recursive pre-order traversal"""
        if node:
            result.append(node.data)
            self._preorder_recursive(node.left, result)
            self._preorder_recursive(node.right, result)


# ==================== GRAPH ====================
class Graph:
    """Graph implementation using adjacency list"""
    
    def __init__(self, directed: bool = False):
        self.adjacency_list: Dict[Any, List[Any]] = {}
        self.directed = directed
        self.vertices: Set[Any] = set()
    
    def add_vertex(self, vertex: Any) -> None:
        """Add vertex to graph"""
        if vertex not in self.adjacency_list:
            self.adjacency_list[vertex] = []
            self.vertices.add(vertex)
    
    def add_edge(self, vertex1: Any, vertex2: Any, weight: float = 1.0) -> None:
        """Add edge between two vertices"""
        self.add_vertex(vertex1)
        self.add_vertex(vertex2)
        
        # Add edge from vertex1 to vertex2
        if vertex2 not in self.adjacency_list[vertex1]:
            self.adjacency_list[vertex1].append((vertex2, weight))
        
        # If undirected, add reverse edge
        if not self.directed:
            if vertex1 not in self.adjacency_list[vertex2]:
                self.adjacency_list[vertex2].append((vertex1, weight))
    
    def get_neighbors(self, vertex: Any) -> List[Any]:
        """Get neighbors of a vertex"""
        if vertex not in self.adjacency_list:
            return []
        return [neighbor for neighbor, _ in self.adjacency_list[vertex]]
    
    def get_edge_weight(self, vertex1: Any, vertex2: Any) -> Optional[float]:
        """Get weight of edge between two vertices"""
        if vertex1 not in self.adjacency_list:
            return None
        for neighbor, weight in self.adjacency_list[vertex1]:
            if neighbor == vertex2:
                return weight
        return None
    
    def bfs(self, start_vertex: Any) -> List[Any]:
        """Breadth-First Search traversal"""
        if start_vertex not in self.adjacency_list:
            return []
        
        visited: Set[Any] = set()
        queue: deque = deque([start_vertex])
        result: List[Any] = []
        
        visited.add(start_vertex)
        
        while queue:
            vertex = queue.popleft()
            result.append(vertex)
            
            for neighbor, _ in self.adjacency_list[vertex]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return result
    
    def dfs(self, start_vertex: Any) -> List[Any]:
        """Depth-First Search traversal"""
        if start_vertex not in self.adjacency_list:
            return []
        
        visited: Set[Any] = set()
        result: List[Any] = []
        
        def dfs_recursive(vertex: Any):
            visited.add(vertex)
            result.append(vertex)
            
            for neighbor, _ in self.adjacency_list[vertex]:
                if neighbor not in visited:
                    dfs_recursive(neighbor)
        
        dfs_recursive(start_vertex)
        return result
    
    def get_all_vertices(self) -> Set[Any]:
        """Get all vertices in graph"""
        return self.vertices.copy()
    
    def get_all_edges(self) -> List[tuple]:
        """Get all edges in graph"""
        edges = []
        for vertex in self.adjacency_list:
            for neighbor, weight in self.adjacency_list[vertex]:
                if self.directed or vertex < neighbor:  # Avoid duplicates in undirected
                    edges.append((vertex, neighbor, weight))
        return edges


# ==================== TREE NODE FOR TOPIC HIERARCHY ====================
class TopicTreeNode:
    """Node for topic hierarchy tree"""
    
    def __init__(self, topic: str, articles: Optional[List[Any]] = None):
        self.topic = topic
        self.articles: List[Any] = articles or []
        self.children: List['TopicTreeNode'] = []
        self.parent: Optional['TopicTreeNode'] = None
    
    def add_child(self, child: 'TopicTreeNode') -> None:
        """Add child node"""
        child.parent = self
        self.children.append(child)
    
    def get_all_articles(self) -> List[Any]:
        """Get all articles in this node and its children"""
        all_articles = self.articles.copy()
        for child in self.children:
            all_articles.extend(child.get_all_articles())
        return all_articles


class TopicTree:
    """Tree structure for organizing articles by topic"""
    
    def __init__(self):
        self.root: Optional[TopicTreeNode] = None
        self.nodes: Dict[str, TopicTreeNode] = {}
    
    def add_topic(self, topic: str, parent_topic: Optional[str] = None, articles: Optional[List[Any]] = None) -> None:
        """Add topic to tree"""
        if topic in self.nodes:
            if articles:
                self.nodes[topic].articles.extend(articles)
            return
        
        node = TopicTreeNode(topic, articles or [])
        self.nodes[topic] = node
        
        if parent_topic and parent_topic in self.nodes:
            self.nodes[parent_topic].add_child(node)
        elif self.root is None:
            self.root = node
    
    def get_topic_node(self, topic: str) -> Optional[TopicTreeNode]:
        """Get node for a topic"""
        return self.nodes.get(topic)
    
    def get_articles_by_topic(self, topic: str) -> List[Any]:
        """Get all articles for a topic and its subtopics"""
        node = self.nodes.get(topic)
        if node:
            return node.get_all_articles()
        return []

# ==================== TRIE ====================
class TrieNode:
    """Node for Trie data structure"""
    
    def __init__(self):
        self.children: Dict[str, TrieNode] = {}
        self.is_end_of_word: bool = False


class Trie:
    """Trie (Prefix Tree) implementation for efficient string retrieval"""
    
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word: str) -> None:
        """Insert a word into the trie"""
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
    
    def search(self, word: str) -> bool:
        """Check if word exists in trie"""
        node = self.root
        for char in word.lower():
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

    def starts_with(self, prefix: str) -> bool:
        """Check if any word in trie starts with prefix"""
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return False
            node = node.children[char]
        return True

    def collect_all_words(self) -> List[str]:
        """Collect all words in the trie"""
        words = []
        self._collect_words_recursive(self.root, "", words)
        return words
    
    def _collect_words_recursive(self, node: TrieNode, current_prefix: str, words: List[str]) -> None:
        if node.is_end_of_word:
            words.append(current_prefix)
        
        for char, child_node in node.children.items():
            self._collect_words_recursive(child_node, current_prefix + char, words)
