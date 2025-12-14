"""
TF-IDF Ranking Module
Uses: list, dict, tuple, set, Counter
"""
import math
from collections import Counter
from typing import List, Dict, Tuple
from indexer import ArticleIndexer, Article

class TFIDFRanker:
    """TF-IDF based ranking system"""
    
    def __init__(self, indexer: ArticleIndexer):
        self.indexer = indexer
        self.idf_cache: Dict[str, float] = {}  # Cache IDF values
        self._calculate_idf()
    
    def _calculate_idf(self) -> None:
        """Pre-calculate IDF values for all words"""
        total_docs = self.indexer.total_articles
        
        for word in self.indexer.all_words_set:
            # Number of documents containing this word
            doc_freq = len(self.indexer.get_articles_by_word(word))
            if doc_freq > 0:
                # IDF = log(total_docs / doc_freq)
                self.idf_cache[word] = math.log(total_docs / doc_freq)
            else:
                self.idf_cache[word] = 0.0
    
    def _calculate_tf(self, word: str, article_id: str) -> float:
        """Calculate Term Frequency for a word in an article"""
        word_freq = self.indexer.get_article_word_freq(article_id)
        total_words = sum(word_freq.values())
        
        if total_words == 0:
            return 0.0
        
        # TF = count of word / total words in document
        return word_freq.get(word.lower(), 0) / total_words
    
    def _calculate_tfidf(self, word: str, article_id: str) -> float:
        """Calculate TF-IDF score for a word in an article"""
        tf = self._calculate_tf(word, article_id)
        idf = self.idf_cache.get(word.lower(), 0.0)
        return tf * idf
    
    def _tokenize_query(self, query: str) -> List[str]:
        """Tokenize query into words"""
        import re
        words = re.findall(r'\b[a-z]+\b', query.lower())
        return words
    
    def rank_articles(self, query: str, top_k: int = 10, min_score: float = 0.001) -> List[Tuple[Article, float]]:
        """
        Rank articles based on query using TF-IDF
        Returns list of tuples: (Article, score) sorted by score descending
        Only returns articles with score above minimum threshold
        """
        query_words = self._tokenize_query(query)
        
        if not query_words:
            return []
        
        # Filter stop words (common words that don't add meaning)
        stop_words = {'what', 'is', 'a', 'an', 'the', 'how', 'does', 'do', 'are', 'can', 'i', 'you', 'we', 'they', 'this', 'that', 'these', 'those', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'from', 'by', 'about', 'into', 'through', 'during', 'including', 'against', 'among', 'throughout', 'despite', 'towards', 'upon', 'concerning', 'to', 'of', 'in', 'for', 'on', 'at', 'by', 'with', 'from', 'up', 'about', 'into', 'through', 'during', 'including', 'against', 'among', 'throughout', 'despite', 'towards', 'upon', 'concerning', 'attack', 'attacks'}  # Remove 'attack' as it's too common
        query_words = [w for w in query_words if w not in stop_words and len(w) > 2]
        
        if not query_words:
            return []
        
        # Calculate TF-IDF score for each article
        article_scores: Dict[str, float] = {}
        
        for article in self.indexer.get_all_articles():
            score = 0.0
            matched_words = 0
            important_word_matches = 0
            
            for word in query_words:
                word_score = self._calculate_tfidf(word, article.unique_id)
                if word_score > 0:
                    score += word_score
                    matched_words += 1
                    # Check if this is an important word (appears in title or has high IDF)
                    if word in article.title.lower() or self.idf_cache.get(word, 0) > 2.0:
                        important_word_matches += 1
            
            # Only include articles that match at least one important query word
            # or have significant overall score
            if matched_words > 0 and (important_word_matches > 0 or score > 0.05):
                # Boost score if multiple query words match, especially important ones
                boost = 1 + (matched_words / len(query_words)) * 0.5
                if important_word_matches > 0:
                    boost += important_word_matches * 0.3
                score = score * boost
                article_scores[article.unique_id] = score
        
        # Sort articles by score (descending)
        sorted_articles = sorted(
            article_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        if not sorted_articles:
            return []
        
        # Get top score to calculate relative threshold
        top_score = sorted_articles[0][1]
        
        # Dynamic threshold: show articles with score >= 5% of top score
        # This ensures we show more relevant articles
        dynamic_threshold = max(min_score, top_score * 0.05)
        
        # Return top K articles with scores above threshold
        results = []
        for article_id, score in sorted_articles:
            # Only filter out if score is very low and we already have good results
            if score < dynamic_threshold and len(results) >= 10:
                break
            
            article = self.indexer.get_article(article_id)
            if article and score > 0:
                results.append((article, score))
                if len(results) >= top_k:
                    break
        
        return results
    
    def get_top_articles_for_query(self, query: str, limit: int = 5) -> List[Article]:
        """Get top ranked articles for a query"""
        ranked = self.rank_articles(query, top_k=limit)
        return [article for article, score in ranked]
