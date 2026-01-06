import json
import os
from typing import List

HISTORY_FILE = "search_history.json"
MAX_HISTORY = 20

class HistoryManager:
    """Manages persistent search history."""
    
    @staticmethod
    def load_history() -> List[str]:
        """Load search history from JSON file."""
        if not os.path.exists(HISTORY_FILE):
            return []
        
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
                return history if isinstance(history, list) else []
        except (json.JSONDecodeError, IOError):
            return []

    @staticmethod
    def save_history(history: List[str]):
        """Save search history to JSON file."""
        # Ensure uniqueness while preserving order (Python 3.7+ dicts preserve insertion order)
        # We want the most recent queries at the start? Or end?
        # Typically "recent searches" list has newest at top.
        # But for saving/loading list, let's just save the list as passed.
        
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history[:MAX_HISTORY], f, indent=2)
        except IOError as e:
            print(f"Error saving history: {e}")

    @staticmethod
    def add_to_history(query: str):
        """Add a query to history, ensuring uniqueness and max size."""
        history = HistoryManager.load_history()
        
        # Remove if exists (to move to top/front)
        if query in history:
            history.remove(query)
        
        # Add to front (newest first)
        history.insert(0, query)
        
        # Trim
        if len(history) > MAX_HISTORY:
            history = history[:MAX_HISTORY]
            
        HistoryManager.save_history(history)
        return history

    @staticmethod
    def clear_history():
        """Clear all history."""
        try:
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)
        except OSError:
            pass
