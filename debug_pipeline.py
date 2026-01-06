import time
from web_searcher import WebSearcher
from crawler3 import SimpleCrawler
from indexer import ArticleIndexer, Article

def debug_pipeline():
    query = "python cybersecurity"
    print(f"--- Debugging Search Pipeline for query: '{query}' ---")

    # 1. Test Web Searcher
    print("\n[1] Testing WebSearcher...")
    ws = WebSearcher()
    try:
        urls = ws.get_search_results(query, limit=3)
        print(f"    Result: Found {len(urls)} URLs")
        for i, url in enumerate(urls):
            print(f"      {i+1}. {url}")
            
        if not urls:
            print("    [!] WebSearcher failed to return URLs. Stopping.")
            return
    except Exception as e:
        print(f"    [!] WebSearcher crashed: {e}")
        return

    # 2. Test Crawler
    print("\n[2] Testing Crawler...")
    crawler = SimpleCrawler()
    try:
        articles_data = crawler.crawl_urls(urls)
        print(f"    Result: Crawled {len(articles_data)} articles")
        for article in articles_data:
            print(f"      - {article.get('title', 'No Title')} ({len(article.get('content', ''))} chars)")
        
        if not articles_data:
            print("    [!] Crawler failed to extract content. Stopping.")
            return
    except Exception as e:
        print(f"    [!] Crawler crashed: {e}")
        return

    # 3. Test Indexer
    print("\n[3] Testing Indexer...")
    indexer = ArticleIndexer("debug_articles.json")
    try:
        count = indexer.add_articles(articles_data)
        print(f"    Result: Indexed {count} new articles")
        print(f"    Total articles in index: {indexer.total_articles}")
    except Exception as e:
        print(f"    [!] Indexer crashed: {e}")

if __name__ == "__main__":
    debug_pipeline()
