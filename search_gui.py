
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
from web_searcher import WebSearcher
from crawler3 import SimpleCrawler
from history_manager import HistoryManager

 
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class ResultCard(ctk.CTkFrame):
    """Modern result card widget matching Google/Bing aesthetic"""
    def __init__(self, parent, article, score, index, click_callback):
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.article = article
        self.click_callback = click_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.configure(width=600)  
        
        # URL Frame (Favicon placeholder + Site Name + URL)
        url_frame = ctk.CTkFrame(self, fg_color="transparent")
        url_frame.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Simplified "Favicon" (Circle)
        favicon = ctk.CTkLabel(
            url_frame,
            text="",
            width=26,
            height=26,
            fg_color="#f1f3f4",
            corner_radius=13
        )
        favicon.pack(side="left", padx=(0, 10))
        
        # Site Name / URL
        site_name = ctk.CTkLabel(
            url_frame,
            text=article.url.split('/')[2] if '//' in article.url else "Website",
            font=ctk.CTkFont(size=14, weight="normal"),
            text_color="#202124"
        )
        site_name.pack(side="left", padx=(0, 5))
        
        url_text = ctk.CTkLabel(
            url_frame,
            text=article.url,
            font=ctk.CTkFont(size=12),
            text_color="#5f6368"
        )
        url_text.pack(side="left")

        # Title (Blue link style)
        title_label = ctk.CTkLabel(
            self,
            text=article.title,
            font=ctk.CTkFont(family="Arial", size=20, weight="normal"),
            text_color="#1a0dab",
            anchor="w",
            cursor="hand2",
            wraplength=600
        )
        title_label.grid(row=1, column=0, sticky="ew", pady=(0, 2))
        title_label.bind("<Button-1>", lambda e: self._on_click())
        title_label.bind("<Enter>", lambda e: title_label.configure(font=ctk.CTkFont(family="Arial", size=20, underline=True)))
        title_label.bind("<Leave>", lambda e: title_label.configure(font=ctk.CTkFont(family="Arial", size=20, underline=False)))
        
        # Snippet
        snippet_text = article.content[:200] + "..." if len(article.content) > 200 else article.content
        snippet_label = ctk.CTkLabel(
            self,
            text=snippet_text,
            font=ctk.CTkFont(family="Arial", size=14),
            text_color="#4d5156",
            anchor="w",
            justify="left",
            wraplength=600
        )
        snippet_label.grid(row=2, column=0, sticky="ew", pady=(0, 15))

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
        self.web_searcher = WebSearcher()
        self.crawler = SimpleCrawler()
        
        # Query history from persistent storage
        self.query_history = deque(HistoryManager.load_history(), maxlen=20)
        
        # Current search results
        self.current_results = []
        self.current_query = ""
        self.current_sort_option = "Relevance"
        
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
        if hasattr(self, 'loading_label'):
            self.loading_label.configure(text="Indexing articles... Please wait")
        
        if hasattr(self, 'home_progress_bar'):
            self.home_progress_bar.pack(pady=(10, 0))
            self.home_progress_bar.start()
    
    def _on_indexing_complete(self):
        """Called when indexing is complete"""
        if hasattr(self, 'home_progress_bar'):
            self.home_progress_bar.stop()
            self.home_progress_bar.pack_forget()
        
        if hasattr(self, 'loading_label'):
             self.loading_label.configure(text="")
             
        self.search_entry.configure(state="normal")
        self.header_entry.configure(state="normal")
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
        """Create modern SearchEngine Dashboard widgets"""
        # Main container
        self.main_container = ctk.CTkFrame(self.root, fg_color="#f8f9fa") # Light gray background
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # ==================== HOME PAGE ====================
        self.home_frame = ctk.CTkFrame(self.main_container, fg_color="#ffffff")
        self.home_frame.grid(row=0, column=0, sticky="nsew")
        self.home_frame.grid_columnconfigure(0, weight=1)
        # Row 0: Nav, Row 1: Spacer, Row 2: Search, Row 3: Trending, Row 4: Spacer
        self.home_frame.grid_rowconfigure(0, weight=0) # Nav
        self.home_frame.grid_rowconfigure(1, weight=1) # Top Spacer
        self.home_frame.grid_rowconfigure(4, weight=2) # Bottom Spacer

        # --- Top Navigation Bar ---
        nav_bar = ctk.CTkFrame(self.home_frame, fg_color="transparent", height=60)
        nav_bar.grid(row=0, column=0, sticky="ew", padx=40, pady=20)
        nav_bar.grid_columnconfigure(1, weight=1) # Spacer between left and right

        # Logo (Saturn Icon + Text)
        logo_frame = ctk.CTkFrame(nav_bar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, sticky="w")
        
        logo_icon = ctk.CTkLabel(
            logo_frame, 
            text="🪐", 
            font=ctk.CTkFont(size=28),
            text_color="#6366f1" # Indigo-ish
        )
        logo_icon.pack(side="left", padx=(0, 10))
        
        logo_text = ctk.CTkLabel(
            logo_frame,
            text="SearchEngine",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            text_color="#1f2937"
        )
        logo_text.pack(side="left")

        # Center Nav Links
        nav_links_frame = ctk.CTkFrame(nav_bar, fg_color="transparent")
        nav_links_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        for link in ["Images", "Videos", "Shopping", "News"]:
            btn = ctk.CTkButton(
                nav_links_frame,
                text=link,
                fg_color="transparent",
                text_color="#4b5563",
                font=ctk.CTkFont(size=15),
                hover_color="#f3f4f6",
                width=80
            )
            btn.pack(side="left", padx=5)

        # Right Profile
        profile_frame = ctk.CTkFrame(nav_bar, fg_color="transparent")
        profile_frame.grid(row=0, column=2, sticky="e")
        
        # Profile Pic (Circle Placeholder using Label with corner radius workaround or just simple unicode)
        profile_pic = ctk.CTkLabel(
            profile_frame,
            text="👤", 
            font=ctk.CTkFont(size=20),
            width=40,
            height=40,
            fg_color="#e0e7ff",
            text_color="#4338ca",
            corner_radius=20
        )
        profile_pic.pack(side="left", padx=(0, 10))
        
        profile_name = ctk.CTkLabel(
            profile_frame,
            text="Sofia Perez",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1f2937"
        )
        profile_name.pack(side="left")
        
        arrow = ctk.CTkLabel(
            profile_frame,
            text="⌄",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#6b7280"
        )
        arrow.pack(side="left", padx=(5, 0))

        # --- Center Search Area ---
        center_area = ctk.CTkFrame(self.home_frame, fg_color="transparent")
        center_area.grid(row=2, column=0, sticky="ew", padx=20)
        center_area.grid_columnconfigure(0, weight=1)

        # Search Bar Container (Rounded, Gray)
        self.home_search_bar = ctk.CTkFrame(
            center_area,
            corner_radius=30,
            fg_color="#f3f4f6", # Light gray
            border_width=0,
            width=700,
            height=60
        )
        self.home_search_bar.pack(pady=(0, 60))
        self.home_search_bar.pack_propagate(False)

        # Search Icon
        search_icon = ctk.CTkLabel(
            self.home_search_bar,
            text="🔍",
            font=ctk.CTkFont(size=20),
            text_color="#9ca3af"
        )
        search_icon.place(x=25, y=15)

        # Entry
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self.home_search_bar,
            textvariable=self.search_var,
            font=ctk.CTkFont(family="Arial", size=18),
            placeholder_text="Search everything",
            placeholder_text_color="#9ca3af",
            border_width=0,
            fg_color="transparent",
            width=500,
            height=50
        )
        self.search_entry.place(x=60, y=5)
        self.search_entry.bind("<Return>", lambda e: self._perform_search())
        self.search_var.trace("w", lambda *args: self._on_home_text_change())

        # Right Icons (Image, Mic)
        right_icons = ctk.CTkFrame(self.home_search_bar, fg_color="transparent")
        right_icons.place(relx=1.0, rely=0.5, anchor="e", x=-20)
        
        img_btn = ctk.CTkLabel(right_icons, text="🖼️", font=ctk.CTkFont(size=20), cursor="hand2")
        img_btn.pack(side="left", padx=10)
        mic_btn = ctk.CTkLabel(right_icons, text="🎤", font=ctk.CTkFont(size=20), cursor="hand2")
        mic_btn.pack(side="left", padx=10)

        # Clear Button (re-using logic)
        self.home_clear_btn = ctk.CTkButton(
            self.home_search_bar,
            text="✕",
            width=20,
            fg_color="transparent",
            hover_color="#e5e7eb",
            text_color="#6b7280",
            command=self._clear_search
        )
        self.home_clear_btn.place(x=640, y=15)
        self.home_clear_btn.place_forget() # Initially hidden

        # Loading (Hidden)
        self.loading_label = ctk.CTkLabel(center_area, text="", font=ctk.CTkFont(size=12), text_color="#6b7280")
        self.loading_label.pack()
        self.home_progress_bar = ctk.CTkProgressBar(center_area, width=200, height=3, progress_color="#6366f1")
        self.home_progress_bar.pack(pady=5)
        self.home_progress_bar.set(0)
        self.home_progress_bar.pack_forget()


        # --- Trending Section ---
        trending_frame = ctk.CTkFrame(self.home_frame, fg_color="transparent")
        trending_frame.grid(row=3, column=0, sticky="ew", padx=100)
        trending_frame.grid_columnconfigure(0, weight=1)

        trending_title = ctk.CTkLabel(
            trending_frame,
            text="Today's trending searches",
            font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
            text_color="#1f2937"
        )
        trending_title.pack(pady=(0, 30))

        # Cards Grid
        cards_grid = ctk.CTkFrame(trending_frame, fg_color="transparent")
        cards_grid.pack()
        
        # Mock Data
        trends = [
            ("Major Tech Breakthrough", "120K searches", "🎵"),
            ("Environmental Progress 2025", "110K searches", "🌿"),
            ("Morning Affirmations", "110K searches", "☀️"),
            ("Best Spring Travel", "100K searches", "✈️"),
            ("Home Workouts", "90K searches", "💪"),
            ("Top Fashion Styles", "80K searches", "👗")
        ]

        for i, (title, stats, icon) in enumerate(trends):
            row = i // 3
            col = i % 3
            
            card = ctk.CTkFrame(
                cards_grid, 
                fg_color="white", 
                border_width=1, 
                border_color="#f3f4f6", 
                corner_radius=16,
                width=300,
                height=120
            )
            card.grid(row=row, column=col, padx=15, pady=15)
            card.pack_propagate(False)
            
            # Icon Box
            icon_box = ctk.CTkFrame(card, fg_color="#f3f4f6", width=60, height=60, corner_radius=12)
            icon_box.place(x=15, y=15)
            icon_label = ctk.CTkLabel(icon_box, text=icon, font=ctk.CTkFont(size=24))
            icon_label.place(relx=0.5, rely=0.5, anchor="center")
            
            # Content
            content_box = ctk.CTkFrame(card, fg_color="transparent")
            content_box.place(x=90, y=15, relwidth=0.65)
            
            t_label = ctk.CTkLabel(
                content_box, 
                text=title, 
                font=ctk.CTkFont(size=14, weight="bold"), 
                text_color="#1f2937",
                anchor="w",
                justify="left",
                wraplength=180
            )
            t_label.pack(anchor="w")
            
            stats_pill = ctk.CTkLabel(
                content_box,
                text=f"🔍 {stats}",
                font=ctk.CTkFont(size=11),
                text_color="#6b7280",
                fg_color="#f9fafb",
                corner_radius=10,
                padx=8,
                pady=2
            )
            stats_pill.pack(anchor="w", pady=(5, 0))


        # ==================== RESULTS PAGE ====================
        self.results_frame = ctk.CTkFrame(self.main_container, fg_color="white")
        self.results_frame.grid(row=0, column=0, sticky="nsew")
        self.results_frame.grid_columnconfigure(0, weight=1)
        self.results_frame.grid_rowconfigure(1, weight=1)
        
        # Sticky Header
        self.header_frame = ctk.CTkFrame(self.results_frame, fg_color="white", height=70, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_propagate(False)
        
        # Header Logo
        header_logo = ctk.CTkLabel(
            self.header_frame,
            text="SearchEngine 🪐",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            text_color="#6366f1",
            cursor="hand2"
        )
        header_logo.place(x=30, y=20)
        header_logo.bind("<Button-1>", lambda e: self._switch_to_home_mode())

        # Header Search Bar (Clean updated style)
        self.header_search_bar = ctk.CTkFrame(
            self.header_frame,
            corner_radius=20,
            fg_color="#f3f4f6",
            border_width=0,
            width=690,
            height=44
        )
        self.header_search_bar.place(x=220, y=13)

        # Header Entry
        self.header_entry = ctk.CTkEntry(
            self.header_search_bar,
            textvariable=self.search_var,
            font=ctk.CTkFont(family="Arial", size=16),
            border_width=0,
            fg_color="transparent",
            width=600,
            height=36
        )
        self.header_entry.place(x=20, y=4)
        self.header_entry.bind("<Return>", lambda e: self._perform_search())
        
        # Header Clear
        self.header_clear_btn = ctk.CTkButton(
            self.header_search_bar,
            text="✕",
            width=20,
            fg_color="transparent",
            hover_color="#e5e7eb",
            text_color="#6b7280",
            command=self._clear_search
        )
        self.header_clear_btn.place(x=650, y=8)

        # Loading Bar (Top of results)
        self.progress_bar = ctk.CTkProgressBar(self.header_frame, width=150, height=2, progress_color="#6366f1")
        self.progress_bar.place(relx=0, rely=1, relwidth=1, anchor="sw")
        self.progress_bar.set(0)
        self.progress_bar.place_forget() # Hide initially

        # --- Options Bar (Sorting, etc.) ---
        self.options_frame = ctk.CTkFrame(self.results_frame, height=50, fg_color="white", corner_radius=0)
        self.options_frame.grid(row=1, column=0, sticky="ew")
        self.options_frame.grid_columnconfigure(0, weight=1)
        
        # Sort Dropdown
        self.sort_var = ctk.StringVar(value="Relevance")
        self.sort_combo = ctk.CTkComboBox(
            self.options_frame, 
            values=["Relevance", "Newest", "Oldest", "A-z"],
            command=self._on_sort_change,
            width=120,
            state="readonly",
            font=ctk.CTkFont(size=12)
        )
        self.sort_combo.pack(side="right", padx=(0, 150), pady=10)
        
        sort_label = ctk.CTkLabel(self.options_frame, text="Sort by:", font=ctk.CTkFont(size=12), text_color="#5f6368")
        sort_label.pack(side="right", padx=(0, 10), pady=10)

        # Status Label (Searching web...)
        self.results_label = ctk.CTkLabel(self.options_frame, text="", font=ctk.CTkFont(size=12, slant="italic"), text_color="#6366f1")
        self.results_label.pack(side="left", padx=20)

        # Results Area
        self.results_scrollable_frame = ctk.CTkScrollableFrame(
            self.results_frame,
            fg_color="white",
            corner_radius=0
        )
        self.results_scrollable_frame.grid(row=2, column=0, sticky="nsew", padx=150) # Left margin like Google
        self.results_scrollable_frame.grid_columnconfigure(0, weight=1)

        # Initialize in Home Mode
        self._switch_to_home_mode()

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
        if not self.suggestion_window or not self.suggestions:
            return
            
        # TODO: Implement proper selection visual state
        # For now, just setting text to next suggestion as basic nav
        current_text = self.search_var.get()
        try:
            if current_text in self.suggestions:
                idx = self.suggestions.index(current_text)
                new_idx = (idx + 1) if direction == 'down' else (idx - 1)
                new_idx = max(0, min(new_idx, len(self.suggestions) - 1))
                self.search_var.set(self.suggestions[new_idx])
            else:
                 self.search_var.set(self.suggestions[0])
        except ValueError:
            pass

    def _on_home_text_change(self, *args):
        if self.search_var.get():
            self.home_clear_btn.place(x=540, y=10)
        else:
            self.home_clear_btn.place_forget()

    def _switch_to_home_mode(self):
        self.results_frame.grid_remove()
        self.home_frame.grid()
        self.search_entry.focus()
    
    def _switch_to_results_mode(self):
        self.home_frame.grid_remove()
        self.results_frame.grid()
        self.header_entry.focus()
    
    def _perform_search(self):
        """Perform search using TF-IDF"""
        query = self.search_var.get().strip()
        
        if not query or self.is_indexing:
            return
        
        self._hide_suggestions()
        self.current_query = query
        
        # Add to history using manager
        if query and query not in self.query_history:
             self.query_history = deque(HistoryManager.add_to_history(query), maxlen=20)
        
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
            
            # --- Real-Time Web Search ---
            # Update UI from thread (careful with Tkinter)
            self.root.after(0, lambda: self.results_label.configure(text="Searching the web..."))
            
            try:
                # Fetch URLs from Google/Web
                urls = self.web_searcher.get_search_results(query, limit=3)
                
                if urls:
                    self.root.after(0, lambda: self.results_label.configure(text=f"Found {len(urls)} results. Crawling content..."))
                    
                    # Crawl content
                    new_articles = self.crawler.crawl_urls(urls)
                    
                    if new_articles:
                        self.root.after(0, lambda: self.results_label.configure(text=f"Indexing {len(new_articles)} new articles..."))
                        
                        # Add to Indexer
                        if self.indexer:
                            self.indexer.add_articles(new_articles)
                            
                            # Update Ranker IDF
                            if self.ranker:
                                self.ranker.update_idf()
            except Exception as e:
                print(f"Web search failed: {e}")
            
            # --- Final Ranking ---
            self.root.after(0, lambda: self.results_label.configure(text="Ranking results..."))
            
            if self.ranker:
                ranked_results, suggestion = self.ranker.rank_articles(query, top_k=15, min_score=0.001)
                elapsed = time.time() - start_time
                self.root.after(0, lambda: self._display_results(query, ranked_results, elapsed, suggestion))
        
        thread = threading.Thread(target=search, daemon=True)
        thread.start()
    
    def _show_search_loading(self):
        """Show loading state during search"""
        if hasattr(self, 'results_label'):
             self.results_label.configure(text="Searching...")
        
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
        """Update back/forward button states"""
        can_back = self.navigation_history.can_go_back()
        can_forward = self.navigation_history.can_go_forward()
        
        # We only have compact navigation buttons in the new UI
        if hasattr(self, 'compact_back_button'):
            if can_back:
                self.compact_back_button.configure(state="normal", fg_color="transparent", text_color="#5f6368", hover_color="#f1f3f4")
            else:
                self.compact_back_button.configure(state="disabled", fg_color="transparent", text_color="#dadce0", hover_color="#ffffff")
        
        if hasattr(self, 'compact_forward_button'):
            if can_forward:
                self.compact_forward_button.configure(state="normal", fg_color="transparent", text_color="#5f6368", hover_color="#f1f3f4")
            else:
                self.compact_forward_button.configure(state="disabled", fg_color="transparent", text_color="#dadce0", hover_color="#ffffff")

    def _perform_search_with_query(self, query: str):
        """Perform search with a specific query (used for navigation)"""
        if self.is_indexing:
            return
        
        self.current_query = query
        self.search_var.set(query)
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

    def _show_search_loading(self):
        """Show loading state during search"""
        if hasattr(self, 'progress_bar'):
             self.progress_bar.place(relx=0, rely=1, relwidth=1, anchor="sw")
             self.progress_bar.start()
        
        # Switch to results view but show nothing yet?
        # Or just show "Searching..." in title
        self._switch_to_results_mode()
        for widget in self.results_scrollable_frame.winfo_children():
            widget.destroy()

    def _clear_results(self):
        """Clear search results"""
        self.current_query = ""
        self.current_results = []
        self.search_var.set("")
        
        for widget in self.results_scrollable_frame.winfo_children():
            widget.destroy()
            
        self._switch_to_home_mode()
        self._hide_suggestions()
        
        if hasattr(self, 'progress_bar'):
            self.progress_bar.stop()
            self.progress_bar.place_forget()

    def _display_results(self, query: str, ranked_results, elapsed_time, suggestion=None):
        """Display search results in modern Google format"""
        self._switch_to_results_mode()
        
        # Store for sorting
        self.current_results = ranked_results
        
        # Sort if needed (default is Relevance which is already sorted by score)
        if self.current_sort_option != "Relevance":
             self._sort_results()
             ranked_results = self.current_results
        
        # Stop loading
        if hasattr(self, 'progress_bar'):
            self.progress_bar.stop()
            self.progress_bar.place_forget()
        
        # Clear previous results
        for widget in self.results_scrollable_frame.winfo_children():
            widget.destroy()
        
        # "Did you mean" suggestion
        if suggestion:
            suggestion_frame = ctk.CTkFrame(self.results_scrollable_frame, fg_color="transparent")
            suggestion_frame.pack(fill="x", pady=(0, 20), anchor="w")
            
            did_mean_label = ctk.CTkLabel(
                suggestion_frame,
                text="Did you mean: ",
                font=ctk.CTkFont(family="Arial", size=16, weight="normal"),
                text_color="#d93025" # Google red for caution/correction
            )
            did_mean_label.pack(side="left")
            
            suggestion_link = ctk.CTkLabel(
                suggestion_frame,
                text=suggestion,
                font=ctk.CTkFont(family="Arial", size=16, weight="bold", italic=True),
                text_color="#1a0dab", # Google blue link
                cursor="hand2"
            )
            suggestion_link.pack(side="left")
            suggestion_link.bind("<Button-1>", lambda e: self._select_suggestion(suggestion))
        
        # Stats bar (About X results)
        stats_label = ctk.CTkLabel(
            self.results_scrollable_frame,
            text=f"About {len(ranked_results)} results ({elapsed_time:.2f} seconds)",
            font=ctk.CTkFont(family="Arial", size=14),
            text_color="#70757a"
        )
        stats_label.pack(anchor="w", pady=(0, 20))

        if not ranked_results:
            no_results = ctk.CTkFrame(self.results_scrollable_frame, fg_color="transparent")
            no_results.pack(pady=40, anchor="w")
            
            text = ctk.CTkLabel(
                no_results,
                text=f"Your search - {query} - did not match any documents.",
                font=ctk.CTkFont(family="Arial", size=16),
                text_color="#202124"
            )
            text.pack(anchor="w", pady=(0, 10))
            
            hint = ctk.CTkLabel(
                no_results,
                text="Suggestions:\n\n• Make sure that all words are spelled correctly.\n• Try different keywords.\n• Try more general keywords.",
                font=ctk.CTkFont(family="Arial", size=14),
                text_color="#202124",
                justify="left"
            )
            hint.pack(anchor="w")
            return
        
        # Results
        for idx, (article, score) in enumerate(ranked_results, 1):
             card = ResultCard(
                self.results_scrollable_frame,
                article,
                score,
                idx,
                lambda a, pos=idx-1: self._on_article_click(a, pos) # correct closure
            )
             card.pack(fill="x", pady=(0, 25))

    def _on_article_click(self, article, position):
        """Handle article click"""
        # Open different viewer based on position
        if position == 0:
            ArticleViewer1(self.root, article)
        elif position == 1:
            ArticleViewer2(self.root, article)
        elif position == 2:
            ArticleViewer3(self.root, article)
        else:
            ArticleViewer1(self.root, article)
    def _on_sort_change(self, choice):
        """Handle sort option change"""
        self.current_sort_option = choice
        if self.current_results:
             # Redisplay (will trigger sorting)
             # We pass 0 as time since we are just re-ordering
             self._display_results(self.current_query, self.current_results, 0.0)

    def _sort_results(self):
        """Sort current results in place based on option"""
        if not self.current_results:
            return

        if self.current_sort_option == "Newest":
             # Sort by timestamp (descending)
             # Handle missing timestamps by treating them as old
             self.current_results.sort(key=lambda x: x.article.timestamp if x.article.timestamp else "", reverse=True)
        elif self.current_sort_option == "Oldest":
             self.current_results.sort(key=lambda x: x.article.timestamp if x.article.timestamp else "9999")
        elif self.current_sort_option == "A-z":
             self.current_results.sort(key=lambda x: x.article.title)
        # Relevance is default (no sort needed as ranker returns sorted)
