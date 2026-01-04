import sys
import unittest
from data_structures import levenshtein_distance
from query_processor import QueryProcessor
from indexer import ArticleIndexer
from tfidf import TFIDFRanker

# Mock articles for testing
class TestFuzzySearch(unittest.TestCase):
    def setUp(self):
        # We need a dummy json file or we can mock the loading process
        # For simplicity, let's test the components we can easily test
        pass

    def test_levenshtein(self):
        print("\nTesting Levenshtein Distance...")
        self.assertEqual(levenshtein_distance("kitten", "sitting"), 3)
        self.assertEqual(levenshtein_distance("phising", "phishing"), 1)
        self.assertEqual(levenshtein_distance("malware", "malware"), 0)
        self.assertEqual(levenshtein_distance("abc", ""), 3)
        print("Levenshtein Distance: PASS")

    def test_query_processor_trie(self):
        print("\nTesting Query Processor / Trie...")
        qp = QueryProcessor()
        # Check if stop words are loaded
        self.assertEqual(qp.process_query("what is a ddos attack"), ["ddos"])
        print("Query Processor Stop Words: PASS")

if __name__ == '__main__':
    unittest.main()
