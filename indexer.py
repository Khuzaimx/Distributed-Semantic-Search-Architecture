 
import json
import re
from collections import deque, OrderedDict, defaultdict, Counter, namedtuple
from typing import List, Dict, Set, Tuple, Optional
from data_structures import Stack, Queue, BinarySearchTree, Graph, TopicTree, Trie
from query_processor import QueryProcessor

 
Article = namedtuple('Article', ['unique_id', 'title', 'content', 'url', 'timestamp', 'topic'])

class ArticleIndexer:
    """Indexer that pre-processes and indexes all articles"""
    
    def __init__(self, json_file: str):
        self.json_file = json_file
      
        self.articles_list: List[Article] = []  
        self.articles_dict: Dict[str, Article] = {}  
        self.word_to_articles: Dict[str, Set[str]] = defaultdict(set)  
        self.article_word_counts: Dict[str, Counter] = {}  
        self.all_words_set: Set[str] = set()  
        self.topic_to_articles: Dict[str, List[str]] = defaultdict(list)  
        self.query_queue: deque = deque() 
        self.article_order: OrderedDict = OrderedDict() 
        self.total_articles: int = 0
        
       
        self.search_history_stack: Stack = Stack()  
        self.query_processing_queue: Queue = Queue()  
        self.article_bst: BinarySearchTree = BinarySearchTree()  
        self.article_graph: Graph = Graph(directed=False)  
        self.article_graph: Graph = Graph(directed=False)  
        self.topic_tree: TopicTree = TopicTree()  
        self.vocabulary_trie: Trie = Trie()
        self.query_processor: QueryProcessor = QueryProcessor()
        
    def _tokenize(self, text: str) -> List[str]:
       
        return self.query_processor.tokenize(text)
    
    def _load_articles(self) -> None:
       
        with open(self.json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        article_id = 0
        for topic_data in data:
            topic = topic_data['topic']
            for article_data in topic_data['articles']:
              
                content = article_data.get('content', f"{article_data['title']} {topic}")
                
                article = Article(
                    unique_id=article_data['unique_id'],
                    title=article_data['title'],
                    content=content,
                    url=article_data['url'],
                    timestamp=article_data['timestamp'],
                    topic=topic
                )
                
               
                self.articles_list.append(article)
                
             
                self.articles_dict[article.unique_id] = article
                
              
                self.article_order[article.unique_id] = article
                
          
                self.topic_to_articles[topic].append(article.unique_id)
             
                self.article_bst.insert(article)
                
         
                self.topic_tree.add_topic(topic, articles=[article])
                
            
                self.article_graph.add_vertex(article.unique_id)
                
                article_id += 1
        
        self.total_articles = len(self.articles_list)
        
      
        self._build_article_graph()
    
    def _build_inverted_index(self) -> None:
  
        for article in self.articles_list:
          
            text = f"{article.title} {article.content}"
            words = self._tokenize(text)
            
        
            word_counter = Counter(words)
            self.article_word_counts[article.unique_id] = word_counter
            
            # Add to inverted index
            for word in words:
                self.word_to_articles[word].add(article.unique_id)
                self.all_words_set.add(word)
    
    def _build_article_graph(self) -> None:
        """Build graph of article relationships based on shared topics and words"""
     
        for topic, article_ids in self.topic_to_articles.items():
            for i, article_id1 in enumerate(article_ids):
                for article_id2 in article_ids[i+1:]:
                
                    self.article_graph.add_edge(article_id1, article_id2, weight=1.0)
        
     
        important_words = {word for word, articles in self.word_to_articles.items() 
                          if len(articles) <= 5}  # Words that appear in few articles
        
        for word in important_words:
            article_ids = list(self.word_to_articles[word])
            for i, article_id1 in enumerate(article_ids):
                for article_id2 in article_ids[i+1:]:
                 
                    current_weight = self.article_graph.get_edge_weight(article_id1, article_id2)
                    if current_weight is None:
                        self.article_graph.add_edge(article_id1, article_id2, weight=0.5)
                    else:
                      
                        self.article_graph.add_edge(article_id1, article_id2, weight=current_weight + 0.3)
    
    def index_all(self) -> None:
        """Main indexing function - pre-indexes all articles"""
        print("Loading articles...")
        self._load_articles()
        print(f"Loaded {self.total_articles} articles")
        
        print("Building inverted index...")
        self._build_inverted_index()
        print(f"Indexed {len(self.all_words_set)} unique words")
        
        print("Building vocabulary trie...")
        self._build_vocabulary_trie()
        
        print("Indexing complete!")

    def _build_vocabulary_trie(self) -> None:
        """Build Trie for all words in vocabulary"""
        for word in self.all_words_set:
            self.vocabulary_trie.insert(word)
    
    def get_article(self, article_id: str) -> Article:
       
        return self.articles_dict.get(article_id)
    
    def get_articles_by_word(self, word: str) -> Set[str]:
       
        return self.word_to_articles.get(word.lower(), set())
    
    def get_all_articles(self) -> List[Article]:
        """Get all articles as list"""
        return self.articles_list
    
    def get_article_word_freq(self, article_id: str) -> Counter:
       
        return self.article_word_counts.get(article_id, Counter())
    
    def get_all_queries(self) -> List[str]:
       
        queries_list = []
        with open(self.json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for topic_data in data:
            queries_list.extend(topic_data['queries'])
        
        return queries_list
    
    def add_to_search_history(self, query: str) -> None:
      
        self.search_history_stack.push(query)
    
    def get_previous_search(self) -> Optional[str]:
     
        return self.search_history_stack.pop()
    
    def peek_search_history(self) -> Optional[str]:
       
        return self.search_history_stack.peek()
    
    def enqueue_query(self, query: str) -> None:
        
        self.query_processing_queue.enqueue(query)
    
    def dequeue_query(self) -> Optional[str]:
     
        return self.query_processing_queue.dequeue()
    
    def get_related_articles(self, article_id: str, limit: int = 5) -> List[str]:
        
        neighbors = self.article_graph.get_neighbors(article_id)
    
        related = []
        for neighbor in neighbors:
            weight = self.article_graph.get_edge_weight(article_id, neighbor)
            related.append((neighbor, weight or 0.0))
        
       
        related.sort(key=lambda x: x[1], reverse=True)
        return [article_id for article_id, _ in related[:limit]]
    
    def get_articles_by_topic_tree(self, topic: str) -> List[Article]:
       
        return self.topic_tree.get_articles_by_topic(topic)
    
    def search_article_bst(self, article_id: str) -> Optional[Article]:
        
        dummy = Article(article_id, "", "", "", "", "")
        result = self.article_bst.search(dummy)
        if result:
            return result.data
        return None

