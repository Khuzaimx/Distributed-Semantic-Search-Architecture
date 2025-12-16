 
from data_structures import Stack, Queue
from typing import Optional, List

class NavigationHistory:
     
    
    def __init__(self):
         
        self.back_stack: Stack = Stack()
        
        
        self.forward_stack: Stack = Stack()
        
        
        self.history_queue: Queue = Queue()
        
        
        self.current_query: Optional[str] = None
    
    def add_query(self, query: str) -> None:
         
        if query == self.current_query:
            return  
        
         
        if self.current_query:
            self.back_stack.push(self.current_query)
            self.history_queue.enqueue(self.current_query)
        
        
        self.forward_stack = Stack()
        
         
        self.current_query = query
    
    def go_back(self) -> Optional[str]:
        """Navigate backward"""
        if self.back_stack.is_empty():
            return None
        
        
        if self.current_query:
            self.forward_stack.push(self.current_query)
        
        
        self.current_query = self.back_stack.pop()
        return self.current_query
    
    def go_forward(self) -> Optional[str]:
        
        if self.forward_stack.is_empty():
            return None
        
        
        if self.current_query:
            self.back_stack.push(self.current_query)
        
        
        self.current_query = self.forward_stack.pop()
        return self.current_query
    
    def can_go_back(self) -> bool:
         
        return not self.back_stack.is_empty()
    
    def can_go_forward(self) -> bool:
        
        return not self.forward_stack.is_empty()
    
    def get_history_list(self) -> List[str]:
        
        return []
    
    def clear_forward(self) -> None:
        
        self.forward_stack = Stack()
    
    def get_current(self) -> Optional[str]:
        
        return self.current_query

