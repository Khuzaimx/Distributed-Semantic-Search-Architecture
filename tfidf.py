import math
from collections import Counter
from typing import List, Dict, Tuple, Optional
from data_structures import levenshtein_distance
from indexer import ArticleIndexer, Article

class TFIDFRanker:
    
    def __init__(self, indexer: ArticleIndexer):
        self.indexer = indexer
        self.idf_cache: Dict[str, float] = {}  # Cache IDF values
        self._calculate_idf()
    
    def _calculate_idf(self) -> None:
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
        word_freq = self.indexer.get_article_word_freq(article_id)
        total_words = sum(word_freq.values())
        
        if total_words == 0:
            return 0.0
        
        return word_freq.get(word.lower(), 0) / total_words
    
    def _calculate_tfidf(self, word: str, article_id: str) -> float:
        tf = self._calculate_tf(word, article_id)
        idf = self.idf_cache.get(word.lower(), 0.0)
        return tf * idf
    
    def _tokenize_query(self, query: str) -> List[str]:
        import re
        words = re.findall(r'\b[a-z]+\b', query.lower())
        return words
    
    def rank_articles(self, query: str, top_k: int = 10, min_score: float = 0.001) -> Tuple[List[Tuple[Article, float]], Optional[str]]:
        query_words = self._tokenize_query(query)
        
        if not query_words:
            return [], None
        
        stop_words = {'what', 'is', 'a', 'an', 'the', 'how', 'does', 'do', 'are', 'can', 'i', 'you', 'we', 'they', 'this', 'that', 'these', 'those', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'from', 'by', 'about', 'into', 'through', 'during', 'including', 'against', 'among', 'throughout', 'despite', 'towards', 'upon', 'concerning', 'to', 'of', 'in', 'for', 'on', 'at', 'by', 'with', 'from', 'up', 'about', 'into', 'through', 'during', 'including', 'against', 'among', 'throughout', 'despite', 'towards', 'upon', 'concerning', 'attack', 'attacks'}  # Remove 'attack' as it's too common
        filtered_query = [w for w in query_words if w not in stop_words and len(w) > 2]
        
        if not filtered_query:
            return [], None
            
        # Check for misspellings and build suggestion
        suggestion_parts = []
        has_typo = False
        
        # Get all words from vocabulary if needed (lazy load via trie collection or existing set)
        vocab_words = None
        
        processed_query_words = []
        
        for word in filtered_query:
            # If word is in vocabulary, assume it's correct
            if word in self.indexer.all_words_set:
                suggestion_parts.append(word)
                processed_query_words.append(word)
            else:
                # Word matching failed, try fuzzy search
                if vocab_words is None:
                    vocab_words = self.indexer.vocabulary_trie.collect_all_words()
                
                best_match = None
                min_dist = 3  # Start with max distance allowed + 1
                
                for vocab_word in vocab_words:
                    # Optimization: skip words with large length difference
                    if abs(len(vocab_word) - len(word)) > 2:
                        continue
                        
                    dist = levenshtein_distance(word, vocab_word)
                    if dist <= 2 and dist < min_dist:
                        min_dist = dist
                        best_match = vocab_word
                
                if best_match:
                    suggestion_parts.append(best_match)
                    processed_query_words.append(best_match)
                    has_typo = True
                else:
                    suggestion_parts.append(word)
                    processed_query_words.append(word)
        
        # Construct suggestion string
        suggestion = " ".join(suggestion_parts) if has_typo else None
        
        # Perform search (using original words if no typo, or corrected words if typo found)
        # We search using BOTH original and corrected to be safe, but boost corrected
        
        search_terms = filtered_query + ([w for w in processed_query_words if w not in filtered_query])
        
        # Calculate TF-IDF score for each article
        article_scores: Dict[str, float] = {}
        
        for article in self.indexer.get_all_articles():
            score = 0.0
            matched_words = 0
            important_word_matches = 0
            
            for word in search_terms:
                word_score = self._calculate_tfidf(word, article.unique_id)
                if word_score > 0:
                    score += word_score
                    matched_words += 1
                    if word in article.title.lower() or self.idf_cache.get(word, 0) > 2.0:
                        important_word_matches += 1
            
            if matched_words > 0 and (important_word_matches > 0 or score > 0.05):
                boost = 1 + (matched_words / len(search_terms)) * 0.5
                if important_word_matches > 0:
                    boost += important_word_matches * 0.3
                score = score * boost
                article_scores[article.unique_id] = score
        
        sorted_articles = sorted(
            article_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        if not sorted_articles:
            return [], suggestion
        
        top_score = sorted_articles[0][1]
        
        dynamic_threshold = max(min_score, top_score * 0.05)
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
        
        return results, suggestion
    
    def get_top_articles_for_query(self, query: str, limit: int = 5) -> List[Article]:
        ranked, _ = self.rank_articles(query, top_k=limit)
        return [article for article, score in ranked]
