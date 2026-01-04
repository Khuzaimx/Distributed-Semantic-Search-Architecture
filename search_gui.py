
import customtkinter as ctk
import threading
import time
import tkinter as tk
from collections import deque
from indexer import ArticleIndexer
from tfidf import TFIDFRanker
from article_viewers import ArticleViewer1, ArticleViewer2, ArticleViewer3
from data_structures import Stack, Queue, BinarySearchTree, Graph
from navigation import NavigationHistory

 
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class ResultCard(ctk.CTkFrame):
    """Modern result card widget with perfect UX"""
    def __init__(self, parent, article, score, index, click_callback):
        super().__init__(parent, corner_radius=12, fg_color="white", border_width=1, border_color="#e0e0e0")
        self.article = article
        self.click_callback = click_callback
        self.original_bg = "white"
        
        
        self.grid_columnconfigure(0, weight=1)
        self.configure(width=800)  
        
      
        index_label = ctk.CTkLabel(
            self,
            text=str(index),
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4285f4",
            text_color="white",
            width=35,
            height=35,
            corner_radius=17
        )
        index_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
      
        title_label = ctk.CTkLabel(
            self,
            text=article.title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1a0dab",
            anchor="w",
            cursor="hand2",
            wraplength=800
        )
        title_label.grid(row=0, column=0, sticky="ew", padx=(70, 20), pady=(20, 5))
        title_label.bind("<Button-1>", lambda e: self._on_click())
        
        # URL with copy functionality
        url_frame = ctk.CTkFrame(self, fg_color="transparent")
        url_frame.grid(row=1, column=0, sticky="ew", padx=(70, 20), pady=(0, 5))
        url_frame.grid_columnconfigure(0, weight=1)
        
        url_label = ctk.CTkLabel(
            url_frame,
            text=article.url,
            font=ctk.CTkFont(size=14),
            text_color="#006621",
            anchor="w",
            cursor="hand2"
        )
        url_label.grid(row=0, column=0, sticky="w")
        url_label.bind("<Button-1>", lambda e: self._on_click())
        
        # Copy button (appears on hover)
        self.copy_btn = ctk.CTkButton(
            url_frame,
            text="📋",
            width=30,
            height=25,
            fg_color="transparent",
            hover_color="#f0f0f0",
            command=lambda: self._copy_url(),
            font=ctk.CTkFont(size=12)
        )
        self.copy_btn.grid(row=0, column=1, padx=(5, 0))
        self.copy_btn.grid_remove()  # Hidden by default
        
        # Snippet with better formatting
        snippet_text = article.content[:250] + "..." if len(article.content) > 250 else article.content
        snippet_label = ctk.CTkLabel(
            self,
            text=snippet_text,
            font=ctk.CTkFont(size=14),
            text_color="#545454",
            anchor="w",
            justify="left",
            wraplength=800
        )
        snippet_label.grid(row=2, column=0, sticky="ew", padx=(70, 20), pady=(0, 10))
        
        # Metadata with relevance indicator
        relevance_color = "#34a853" if score > 0.1 else "#fbbc04" if score > 0.05 else "#ea4335"
        meta_label = ctk.CTkLabel(
            self,
            text=f"{article.topic} • Relevance: {score:.4f}",
            font=ctk.CTkFont(size=12),
            text_color="#808080",
            anchor="w"
        )
        meta_label.grid(row=3, column=0, sticky="ew", padx=(70, 20), pady=(0, 20))
        
        # Store widgets for hover effects
        self.url_frame = url_frame
        self.url_label = url_label
        
        # Hover effect
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        for widget in [title_label, url_label, snippet_label]:
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        self.configure(fg_color="#f8f9fa", border_color="#4285f4", border_width=2)
        self.copy_btn.grid()  # Show copy button on hover
    
    def _on_leave(self, event):
        self.configure(fg_color="white", border_color="#e0e0e0", border_width=1)
        self.copy_btn.grid_remove()  # Hide copy button
    
    def _copy_url(self):
        """Copy URL to clipboard"""
        self.master.clipboard_clear()
        self.master.clipboard_append(self.article.url)
        # Show feedback
        self.copy_btn.configure(text="✓", fg_color="#34a853")
        self.after(1000, lambda: self.copy_btn.configure(text="📋", fg_color="transparent"))
    
    def _on_click(self):
        if self.click_callback:
            self.click_callback(self.article)

class SearchEngineGUI:
    
    
    def __init__(self, root):
        self.root = root
        self.root.title("DSA Search Engine")
        self.root.geometry("1400x900")
        
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Initialize indexer and ranker
        self.indexer = None
        self.ranker = None
        self.is_indexing = True
        
        # Query history using deque
        self.query_history = deque(maxlen=10)
        
        # Current search results
        self.current_results = []
        self.current_query = ""
        
        # Search suggestions
        self.suggestions = []
        self.suggestion_window = None
        
        # Navigation system using Queue and Stack
        self.navigation_history = NavigationHistory()
        
        self._create_widgets()
        self._setup_keyboard_shortcuts()
        self._load_indexer_async()
    
    def _load_indexer_async(self):
        """Load indexer in background thread"""
        def load():
            self.indexer = ArticleIndexer("articles.json")
            self.indexer.index_all()
            self.ranker = TFIDFRanker(self.indexer)
            self.is_indexing = False
            self.root.after(0, self._on_indexing_complete)
        
        thread = threading.Thread(target=load, daemon=True)
        thread.start()
        self._show_loading_screen()
    
    def _show_loading_screen(self):
        """Show loading screen while indexing"""
        self.loading_label.configure(text="Indexing articles... Please wait")
        self.progress_bar.start()
    
    def _on_indexing_complete(self):
        """Called when indexing is complete"""
        self.progress_bar.stop()
        self.loading_label.configure(text="Ready to search! Press Ctrl+K to focus search")
        self.search_entry.configure(state="normal")
        self.compact_search_entry.configure(state="normal")
        self.search_button.configure(state="normal")
        # Load suggestions
        self._load_suggestions()
    
    def _load_suggestions(self):
        """Load search suggestions from predefined queries"""
        if self.indexer:
            queries = self.indexer.get_all_queries()
            self.suggestions = queries[:10]  # Top 10 suggestions
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind("<Control-k>", lambda e: self._focus_search())
        self.root.bind("<Control-K>", lambda e: self._focus_search())
        self.root.bind("<Escape>", lambda e: self._clear_search())
        self.root.bind("<Control-f>", lambda e: self._focus_search())
        self.root.bind("<Control-F>", lambda e: self._focus_search())
        # Back/Forward navigation shortcuts
        self.root.bind("<Alt-Left>", lambda e: self._navigate_back())
        self.root.bind("<Alt-Right>", lambda e: self._navigate_forward())
        self.root.bind("<Button-4>", lambda e: self._navigate_back())  # Mouse back button
        self.root.bind("<Button-5>", lambda e: self._navigate_forward())  # Mouse forward button
    
    def _focus_search(self):
        """Focus search bar"""
        # Focus the visible search entry
        if self.compact_search_frame.winfo_viewable():
            self.compact_search_entry.focus()
            self.compact_search_entry.select_range(0, tk.END)
        else:
            self.search_entry.focus()
            self.search_entry.select_range(0, tk.END)
        return "break"
    
    def _clear_search(self):
        """Clear search"""
        if self.search_entry.get():
            self.search_var.set("")
            self._clear_results()
        return "break"
    
    def _create_widgets(self):
        """Create modern CustomTkinter widgets"""
        # Main container
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=0, pady=0)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Top navigation bar
        nav_bar = ctk.CTkFrame(main_container, height=70, corner_radius=0, fg_color="white")
        nav_bar.pack(fill="x", padx=0, pady=0)
        nav_bar.grid_columnconfigure(1, weight=1)
        
        # Logo with status
        logo_frame = ctk.CTkFrame(nav_bar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=30, pady=20, sticky="w")
        
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="DSA Search",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#5f6368"
        )
        logo_label.pack(side="left", padx=(0, 15))
        
        # Status indicator
        self.status_indicator = ctk.CTkLabel(
            logo_frame,
            text="●",
            font=ctk.CTkFont(size=12),
            text_color="#34a853"
        )
        self.status_indicator.pack(side="left")
        
        # Navigation buttons (Back/Forward) - using Queue and Stack
        nav_buttons_frame = ctk.CTkFrame(nav_bar, fg_color="transparent")
        nav_buttons_frame.grid(row=0, column=1, padx=20, pady=20, sticky="w")
        
        # Back button
        self.back_button = ctk.CTkButton(
            nav_buttons_frame,
            text="◀ Back",
            command=self._navigate_back,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=80,
            height=30,
            fg_color="#f1f3f4",
            hover_color="#e8eaed",
            text_color="#5f6368",
            state="disabled"
        )
        self.back_button.pack(side="left", padx=(0, 5))
        
        # Forward button
        self.forward_button = ctk.CTkButton(
            nav_buttons_frame,
            text="Forward ▶",
            command=self._navigate_forward,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=80,
            height=30,
            fg_color="#f1f3f4",
            hover_color="#e8eaed",
            text_color="#5f6368",
            state="disabled"
        )
        self.forward_button.pack(side="left")
        
        # Keyboard shortcut hint
        shortcut_label = ctk.CTkLabel(
            nav_bar,
            text="Press Ctrl+K to search",
            font=ctk.CTkFont(size=11),
            text_color="#9aa0a6"
        )
        shortcut_label.grid(row=0, column=2, padx=30, pady=20, sticky="e")
        
        # Home search container - centered (large, like Chrome homepage)
        self.home_search_container = ctk.CTkFrame(main_container, fg_color="transparent")
        self.home_search_container.pack(fill="x", padx=250, pady=(120, 60))
        self.home_search_container.grid_columnconfigure(0, weight=1)
        
        # Large search bar for home
        home_search_frame = ctk.CTkFrame(self.home_search_container, corner_radius=30, fg_color="white", border_width=1, border_color="#dfe1e5")
        home_search_frame.pack(fill="x", ipady=5)
        home_search_frame.grid_columnconfigure(1, weight=1)
        
        # Search icon
        home_icon_label = ctk.CTkLabel(
            home_search_frame,
            text="🔍",
            font=ctk.CTkFont(size=20),
            text_color="#9aa0a6",
            width=50
        )
        home_icon_label.grid(row=0, column=0, padx=(20, 10), pady=15)
        
        # Search entry with autocomplete
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            home_search_frame,
            textvariable=self.search_var,
            font=ctk.CTkFont(size=16),
            placeholder_text="Search articles...",
            border_width=0,
            fg_color="transparent",
            height=50,
            state="disabled"
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=15)
        self.search_entry.bind("<Return>", lambda e: self._perform_search())
        self.search_entry.bind("<KeyRelease>", self._on_search_typing)
        self.search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_search_focus_out)
        self.search_entry.bind("<Down>", lambda e: self._navigate_suggestions(1))
        self.search_entry.bind("<Up>", lambda e: self._navigate_suggestions(-1))
        
        # Clear button (appears when text is entered)
        self.clear_btn = ctk.CTkButton(
            home_search_frame,
            text="✕",
            width=30,
            height=30,
            fg_color="transparent",
            hover_color="#f0f0f0",
            command=self._clear_search,
            font=ctk.CTkFont(size=14),
            text_color="#9aa0a6"
        )
        self.clear_btn.grid(row=0, column=2, padx=(0, 15))
        self.clear_btn.grid_remove()
        self.search_var.trace("w", lambda *args: self._on_search_text_change())
        
        # Store reference to home search frame
        self.home_search_frame = home_search_frame
        
        # Search button container
        button_container = ctk.CTkFrame(self.home_search_container, fg_color="transparent")
        button_container.pack(fill="x", pady=(30, 0))
        
        # Modern search button
        self.search_button = ctk.CTkButton(
            button_container,
            text="Search",
            command=self._perform_search,
            font=ctk.CTkFont(size=16, weight="bold"),
            width=150,
            height=45,
            corner_radius=25,
            fg_color="#4285f4",
            hover_color="#357ae8",
            state="disabled"
        )
        self.search_button.pack()
        
        # Loading indicator
        self.progress_bar = ctk.CTkProgressBar(button_container, width=150, height=4)
        self.progress_bar.pack(pady=(10, 0))
        self.progress_bar.set(0)
        
        self.loading_label = ctk.CTkLabel(
            button_container,
            text="Initializing...",
            font=ctk.CTkFont(size=12),
            text_color="#9aa0a6"
        )
        self.loading_label.pack(pady=(5, 0))
        
        # Compact search bar in nav (hidden initially, shown when results appear)
        compact_search_container = ctk.CTkFrame(nav_bar, fg_color="transparent")
        compact_search_container.grid(row=0, column=1, sticky="ew", padx=20, pady=15)
        compact_search_container.grid_columnconfigure(1, weight=1)
        compact_search_container.grid_remove()  # Hidden initially
        self.compact_search_container = compact_search_container
        
        # Compact navigation buttons
        compact_nav_frame = ctk.CTkFrame(compact_search_container, fg_color="transparent")
        compact_nav_frame.grid(row=0, column=0, padx=(0, 10))
        
        self.compact_back_button = ctk.CTkButton(
            compact_nav_frame,
            text="◀",
            command=self._navigate_back,
            font=ctk.CTkFont(size=14),
            width=35,
            height=35,
            fg_color="#f1f3f4",
            hover_color="#e8eaed",
            text_color="#5f6368",
            state="disabled"
        )
        self.compact_back_button.pack(side="left", padx=(0, 5))
        
        self.compact_forward_button = ctk.CTkButton(
            compact_nav_frame,
            text="▶",
            command=self._navigate_forward,
            font=ctk.CTkFont(size=14),
            width=35,
            height=35,
            fg_color="#f1f3f4",
            hover_color="#e8eaed",
            text_color="#5f6368",
            state="disabled"
        )
        self.compact_forward_button.pack(side="left")
        
        self.compact_search_frame = ctk.CTkFrame(compact_search_container, corner_radius=20, fg_color="white", border_width=1, border_color="#dfe1e5", height=40)
        self.compact_search_frame.grid(row=0, column=1, sticky="ew")
        self.compact_search_frame.grid_columnconfigure(1, weight=1)
        
        compact_icon = ctk.CTkLabel(
            self.compact_search_frame,
            text="🔍",
            font=ctk.CTkFont(size=14),
            text_color="#9aa0a6",
            width=30
        )
        compact_icon.grid(row=0, column=0, padx=(10, 5), pady=8)
        
        self.compact_search_entry = ctk.CTkEntry(
            self.compact_search_frame,
            textvariable=self.search_var,
            font=ctk.CTkFont(size=14),
            placeholder_text="Search articles...",
            border_width=0,
            fg_color="transparent",
            height=35,
            state="disabled"
        )
        self.compact_search_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=8)
        self.compact_search_entry.bind("<Return>", lambda e: self._perform_search())
        self.compact_search_entry.bind("<KeyRelease>", self._on_search_typing)
        self.compact_search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self.compact_search_entry.bind("<FocusOut>", self._on_search_focus_out)
        
        compact_clear_btn = ctk.CTkButton(
            self.compact_search_frame,
            text="✕",
            width=25,
            height=25,
            fg_color="transparent",
            hover_color="#f0f0f0",
            command=self._clear_search,
            font=ctk.CTkFont(size=12),
            text_color="#9aa0a6"
        )
        compact_clear_btn.grid(row=0, column=2, padx=(0, 10))
        self.compact_clear_btn = compact_clear_btn
        
        # Results container - takes full space when results appear (Chrome-like)
        self.results_container = ctk.CTkFrame(main_container, fg_color="transparent")
        self.results_container.pack(fill="both", expand=True, padx=180, pady=(5, 15))
        self.results_container.grid_columnconfigure(0, weight=1)
        self.results_container.grid_rowconfigure(1, weight=1)
        self.results_container.pack_forget()  # Hidden initially
        
        # Results info bar
        self.results_label = ctk.CTkLabel(
            self.results_container,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="#70757a",
            anchor="w"
        )
        self.results_label.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        # Scrollable results frame
        self.results_scrollable_frame = ctk.CTkScrollableFrame(
            self.results_container,
            fg_color="transparent",
            corner_radius=0
        )
        self.results_scrollable_frame.grid(row=1, column=0, sticky="nsew")
        self.results_scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Empty state (shown in home mode)
        self.empty_state = ctk.CTkFrame(main_container, fg_color="transparent")
        self.empty_state.pack(fill="both", expand=True, padx=200, pady=(0, 100))
        self.empty_state.grid_columnconfigure(0, weight=1)
        self.empty_state.grid_rowconfigure(0, weight=1)
        
        empty_icon = ctk.CTkLabel(
            self.empty_state,
            text="🔍",
            font=ctk.CTkFont(size=64),
            text_color="#dadce0"
        )
        empty_icon.grid(row=0, column=0, pady=(50, 20))
        
        empty_text = ctk.CTkLabel(
            self.empty_state,
            text="Start typing to search articles",
            font=ctk.CTkFont(size=18),
            text_color="#9aa0a6"
        )
        empty_text.grid(row=1, column=0, pady=(0, 10))
        
        empty_hint = ctk.CTkLabel(
            self.empty_state,
            text="Try: 'What is DDoS attack?' or 'What is phishing?'",
            font=ctk.CTkFont(size=14),
            text_color="#bdc1c6"
        )
        empty_hint.grid(row=2, column=0)
    
    def _on_search_text_change(self):
        """Handle search text changes"""
        text = self.search_var.get()
        if text:
            self.clear_btn.grid()
            if self.compact_search_frame.winfo_viewable():
                self.compact_clear_btn.grid()
        else:
            self.clear_btn.grid_remove()
            if self.compact_search_frame.winfo_viewable():
                self.compact_clear_btn.grid_remove()
    
    def _on_search_typing(self, event):
        """Handle typing in search box"""
        # Don't show suggestions automatically - they're annoying
        # User can manually trigger if needed
        pass
    
    def _show_suggestions(self):
        """Show search suggestions - DISABLED as it's annoying"""
        # Suggestions are disabled - user can type and search directly
        pass
    
    def _hide_suggestions(self):
        """Hide suggestions"""
        if self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None
    
    def _select_suggestion(self, suggestion):
        """Select a suggestion"""
        self.search_var.set(suggestion)
        self._hide_suggestions()
        self._perform_search()
    
    def _navigate_suggestions(self, direction):
        """Navigate suggestions with arrow keys"""
        # Implementation for arrow key navigation
        pass
    
    def _on_search_focus_in(self, event):
        """Handle search focus in"""
        # Change border to blue for both search bars
        for frame in [self.home_search_frame, self.compact_search_frame]:
            if frame.winfo_exists():
                frame.configure(border_color="#4285f4", border_width=2)
        # Don't show suggestions automatically - user can type to see them
    
    def _on_search_focus_out(self, event):
        """Handle search focus out"""
        # Reset border for both search bars
        for frame in [self.home_search_frame, self.compact_search_frame]:
            if frame.winfo_exists():
                frame.configure(border_color="#dfe1e5", border_width=1)
        # Hide suggestions if they exist
        self._hide_suggestions()
    
    def _switch_to_results_mode(self):
        """Switch to results mode - compact search bar, focus on results"""
        # Hide home search container
        self.home_search_container.pack_forget()
        self.empty_state.pack_forget()
        
        # Show compact search container in nav
        self.compact_search_container.grid()
        
        # Show results container
        self.results_container.pack(fill="both", expand=True, padx=180, pady=(5, 15))
        
        # Update navigation buttons
        self._update_navigation_buttons()
        
        # Update shortcut hint
        for widget in self.root.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, ctk.CTkLabel) and "Ctrl+K" in str(grandchild.cget("text")):
                            grandchild.configure(text="")
    
    def _switch_to_home_mode(self):
        """Switch to home mode - large centered search"""
        # Hide compact search container
        self.compact_search_container.grid_remove()
        
        # Hide results container
        self.results_container.pack_forget()
        
        # Show home search container
        self.home_search_container.pack(fill="x", padx=250, pady=(120, 60))
        
        # Show empty state
        self.empty_state.pack(fill="both", expand=True, padx=200, pady=(0, 100))
        
        # Update navigation buttons
        self._update_navigation_buttons()
    
    def _perform_search(self):
        """Perform search using TF-IDF"""
        query = self.search_var.get().strip()
        
        if not query or self.is_indexing:
            return
        
        self._hide_suggestions()
        self.current_query = query
        
        # Add to history using deque
        if query not in self.query_history:
            self.query_history.append(query)
        
        # Add to navigation history (uses Queue and Stack internally)
        self.navigation_history.add_query(query)
        
        # Update navigation buttons state
        self._update_navigation_buttons()
        
        # Add to indexer's search history stack
        if self.indexer:
            self.indexer.add_to_search_history(query)
            self.indexer.enqueue_query(query)
        
        # Show loading
        self._show_search_loading()
        
        # Perform search in background
        def search():
            start_time = time.time()
            ranked_results, suggestion = self.ranker.rank_articles(query, top_k=15, min_score=0.001)
            elapsed = time.time() - start_time
            self.root.after(0, lambda: self._display_results(query, ranked_results, elapsed, suggestion))
        
        thread = threading.Thread(target=search, daemon=True)
        thread.start()
    
    def _show_search_loading(self):
        """Show loading state during search"""
        self.results_label.configure(text="Searching...")
        self.empty_state.grid_remove()
        for widget in self.results_scrollable_frame.winfo_children():
            widget.destroy()
    
    def _clear_results(self):
        """Clear search results"""
        self.current_query = ""
        self.current_results = []
        self.results_label.configure(text="")
        for widget in self.results_scrollable_frame.winfo_children():
            widget.destroy()
        self._switch_to_home_mode()
        self._hide_suggestions()
        # Update clear button visibility
        text = self.search_var.get()
        if text:
            self.clear_btn.grid()
            self.compact_clear_btn.grid()
        else:
            self.clear_btn.grid_remove()
            self.compact_clear_btn.grid_remove()
    
    def _display_results(self, query: str, ranked_results, elapsed_time, suggestion=None):
        """Display search results in modern format"""
        # Switch to results mode
        self._switch_to_results_mode()
        
        # Clear previous results
        for widget in self.results_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Did you mean suggestion
        if suggestion:
            suggestion_frame = ctk.CTkFrame(self.results_scrollable_frame, fg_color="transparent")
            suggestion_frame.pack(fill="x", pady=(0, 20))
            
            did_mean_label = ctk.CTkLabel(
                suggestion_frame,
                text="Did you mean: ",
                font=ctk.CTkFont(size=14, weight="normal"),
                text_color="#ea4335"
            )
            did_mean_label.pack(side="left")
            
            suggestion_link = ctk.CTkLabel(
                suggestion_frame,
                text=suggestion,
                font=ctk.CTkFont(size=14, weight="bold", underline=True),
                text_color="#1a0dab",
                cursor="hand2"
            )
            suggestion_link.pack(side="left")
            
            # Click handler for suggestion
            def on_suggestion_click(e):
                self.search_var.set(suggestion)
                self._perform_search()
                
            suggestion_link.bind("<Button-1>", on_suggestion_click)
        
        if not ranked_results:
            no_results = ctk.CTkFrame(self.results_scrollable_frame, fg_color="transparent")
            no_results.grid(row=0, column=0, pady=50)
            no_results.grid_columnconfigure(0, weight=1)
            
            icon = ctk.CTkLabel(
                no_results,
                text="😕",
                font=ctk.CTkFont(size=48),
                text_color="#dadce0"
            )
            icon.grid(row=0, column=0, pady=(0, 20))
            
            text = ctk.CTkLabel(
                no_results,
                text=f"No results found for '{query}'",
                font=ctk.CTkFont(size=18),
                text_color="#70757a"
            )
            text.grid(row=1, column=0, pady=(0, 10))
            
            hint = ctk.CTkLabel(
                no_results,
                text="Try different keywords or check spelling",
                font=ctk.CTkFont(size=14),
                text_color="#bdc1c6"
            )
            hint.grid(row=2, column=0)
            
            self.results_label.configure(text="")
            return
        
        # Results count with timing
        self.results_label.configure(
            text=f"About {len(ranked_results)} results ({elapsed_time:.3f} seconds)"
        )
        
        # Create result cards with animation
        def make_click_handler(pos):
            """Factory function to create click handler with proper closure"""
            return lambda art: self._on_article_click(art, pos)
        
        # Ensure scrollable frame is properly configured
        self.results_scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Create result cards - use pack for CTkScrollableFrame
        for idx, (article, score) in enumerate(ranked_results, 1):
            position = idx - 1
            
            card = ResultCard(
                self.results_scrollable_frame,
                article,
                score,
                idx,
                make_click_handler(position)
            )
            # Pack cards vertically in scrollable frame
            card.pack(fill="x", pady=(0, 15), padx=0)
        
        # Force update to ensure all cards are visible
        self.results_scrollable_frame.update_idletasks()
    
    def _navigate_back(self):
        """Navigate backward using Stack"""
        previous_query = self.navigation_history.go_back()
        if previous_query:
            self.search_var.set(previous_query)
            self._update_navigation_buttons()
            # Perform search with previous query
            self._perform_search_with_query(previous_query)
        return "break"
    
    def _navigate_forward(self):
        """Navigate forward using Stack"""
        next_query = self.navigation_history.go_forward()
        if next_query:
            self.search_var.set(next_query)
            self._update_navigation_buttons()
            # Perform search with next query
            self._perform_search_with_query(next_query)
        return "break"
    
    def _update_navigation_buttons(self):
        """Update back/forward button states for both home and compact navigation"""
        can_back = self.navigation_history.can_go_back()
        can_forward = self.navigation_history.can_go_forward()
        
        # Update home navigation buttons
        if can_back:
            self.back_button.configure(state="normal", fg_color="#4285f4", text_color="white", hover_color="#357ae8")
        else:
            self.back_button.configure(state="disabled", fg_color="#f1f3f4", text_color="#5f6368", hover_color="#e8eaed")
        
        if can_forward:
            self.forward_button.configure(state="normal", fg_color="#4285f4", text_color="white", hover_color="#357ae8")
        else:
            self.forward_button.configure(state="disabled", fg_color="#f1f3f4", text_color="#5f6368", hover_color="#e8eaed")
        
        # Update compact navigation buttons
        if hasattr(self, 'compact_back_button'):
            if can_back:
                self.compact_back_button.configure(state="normal", fg_color="#4285f4", text_color="white", hover_color="#357ae8")
            else:
                self.compact_back_button.configure(state="disabled", fg_color="#f1f3f4", text_color="#5f6368", hover_color="#e8eaed")
        
        if hasattr(self, 'compact_forward_button'):
            if can_forward:
                self.compact_forward_button.configure(state="normal", fg_color="#4285f4", text_color="white", hover_color="#357ae8")
            else:
                self.compact_forward_button.configure(state="disabled", fg_color="#f1f3f4", text_color="#5f6368", hover_color="#e8eaed")
    
    def _perform_search_with_query(self, query: str):
        """Perform search with a specific query (used for navigation)"""
        if self.is_indexing:
            return
        
        self.current_query = query
        self._hide_suggestions()
        self._show_search_loading()
        
        # Perform search in background
        def search():
            start_time = time.time()
            ranked_results, suggestion = self.ranker.rank_articles(query, top_k=15, min_score=0.001)
            elapsed = time.time() - start_time
            self.root.after(0, lambda: self._display_results(query, ranked_results, elapsed, suggestion))
        
        thread = threading.Thread(target=search, daemon=True)
        thread.start()
    
    def _on_article_click(self, article, position):
        """Handle article click - open in different viewer based on position"""
        # Open different viewer based on position
        if position == 0:
            ArticleViewer1(self.root, article)
        elif position == 1:
            ArticleViewer2(self.root, article)
        elif position == 2:
            ArticleViewer3(self.root, article)
        else:
            ArticleViewer1(self.root, article)
