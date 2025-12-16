 
import customtkinter as ctk
import webbrowser
import tkinter as tk
from indexer import Article

 
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class ArticleViewer1(ctk.CTkToplevel):
   
    
    def __init__(self, parent, article: Article):
        super().__init__(parent)
        self.article = article
        self.title(f"Article Viewer - {article.title[:50]}...")
        self.geometry("1000x750")
        
        
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
      
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Control-w>", lambda e: self.destroy())
        self.bind("<Control-o>", lambda e: webbrowser.open(article.url))
        self.bind("<Control-c>", lambda e: self._copy_url())
        
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        
        header_frame = ctk.CTkFrame(self, height=120, corner_radius=0, fg_color="#4285f4")
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(20, 10))
        title_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text=article.title,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white",
            anchor="w",
            wraplength=800,
            justify="left"
        )
        title_label.grid(row=0, column=0, sticky="ew")
        
        
        action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_frame.grid(row=1, column=0, sticky="ew", padx=40, pady=(0, 20))
        
        copy_btn = ctk.CTkButton(
            action_frame,
            text="📋 Copy URL",
            command=self._copy_url,
            fg_color="transparent",
            hover_color="rgba(255,255,255,0.1)",
            text_color="white",
            font=ctk.CTkFont(size=12),
            width=100,
            height=30
        )
        copy_btn.pack(side="left", padx=(0, 10))
        
        open_btn = ctk.CTkButton(
            action_frame,
            text="🔗 Open in Browser",
            command=lambda: webbrowser.open(article.url),
            fg_color="transparent",
            hover_color="rgba(255,255,255,0.1)",
            text_color="white",
            font=ctk.CTkFont(size=12),
            width=140,
            height=30
        )
        open_btn.pack(side="left")
        
        # Content container
        content_container = ctk.CTkFrame(self, fg_color="#f8f9fa")
        content_container.grid(row=1, column=0, sticky="nsew")
        content_container.grid_columnconfigure(0, weight=1)
        content_container.grid_rowconfigure(0, weight=1)
        
        # Content frame
        content_frame = ctk.CTkFrame(content_container, corner_radius=0, fg_color="white")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(3, weight=1)
        
        # Metadata badges
        meta_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        meta_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(30, 25))
        
        topic_badge = ctk.CTkLabel(
            meta_frame,
            text=article.topic,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#e8f0fe",
            text_color="#1a73e8",
            corner_radius=15,
            padx=15,
            pady=8
        )
        topic_badge.pack(side="left", padx=(0, 10))
        
        id_badge = ctk.CTkLabel(
            meta_frame,
            text=article.unique_id,
            font=ctk.CTkFont(size=11),
            fg_color="#f1f3f4",
            text_color="#5f6368",
            corner_radius=15,
            padx=15,
            pady=8
        )
        id_badge.pack(side="left")
        
        # URL link
        url_label = ctk.CTkLabel(
            content_frame,
            text="🔗 " + article.url,
            font=ctk.CTkFont(size=13),
            text_color="#1a73e8",
            anchor="w",
            cursor="hand2"
        )
        url_label.grid(row=1, column=0, sticky="ew", padx=40, pady=(0, 20))
        url_label.bind("<Button-1>", lambda e: webbrowser.open(article.url))
        
        # Content text area
        content_text = ctk.CTkTextbox(
            content_frame,
            font=ctk.CTkFont(size=13),
            fg_color="white",
            text_color="#202124",
            corner_radius=0,
            border_width=0
        )
        content_text.grid(row=3, column=0, sticky="nsew", padx=40, pady=(0, 20))
        content_text.insert("1.0", article.content)
        content_text.configure(state="normal")  # Allow selection
        
        # Footer with shortcuts
        footer_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        footer_frame.grid(row=4, column=0, sticky="ew", padx=40, pady=(0, 30))
        footer_frame.grid_columnconfigure(1, weight=1)
        
        shortcuts_label = ctk.CTkLabel(
            footer_frame,
            text="Press Esc to close • Ctrl+O to open URL • Ctrl+C to copy URL",
            font=ctk.CTkFont(size=10),
            text_color="#9aa0a6"
        )
        shortcuts_label.grid(row=0, column=0, sticky="w")
        
        close_btn = ctk.CTkButton(
            footer_frame,
            text="Close",
            command=self.destroy,
            fg_color="#ea4335",
            hover_color="#d33b2c",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=120,
            height=40,
            corner_radius=20
        )
        close_btn.grid(row=0, column=2, sticky="e")
    
    def _copy_url(self):
        """Copy URL to clipboard"""
        self.clipboard_clear()
        self.clipboard_append(self.article.url)
        # Show toast notification
        toast = ctk.CTkToplevel(self)
        toast.overrideredirect(True)
        toast.configure(fg_color="#34a853")
        toast.geometry("200x50+{}+{}".format(
            self.winfo_x() + 400,
            self.winfo_y() + 50
        ))
        label = ctk.CTkLabel(
            toast,
            text="✓ URL Copied!",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        label.pack(expand=True)
        toast.after(2000, toast.destroy)


class ArticleViewer2(ctk.CTkToplevel):
    """Second article viewer - Minimalist clean interface"""
    
    def __init__(self, parent, article: Article):
        super().__init__(parent)
        self.article = article
        self.title(f"Article Viewer - {article.title[:50]}...")
        self.geometry("900x700")
        
        # Center window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        # Keyboard shortcuts
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Control-w>", lambda e: self.destroy())
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Minimalist header
        header_frame = ctk.CTkFrame(self, height=100, corner_radius=0, fg_color="white")
        header_frame.grid(row=0, column=0, sticky="ew", padx=50, pady=(40, 20))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=article.title,
            font=ctk.CTkFont(size=22, weight="normal"),
            text_color="#202124",
            anchor="w",
            wraplength=800,
            justify="left"
        )
        title_label.grid(row=0, column=0, sticky="ew", pady=20)
        
        # Separator
        separator = ctk.CTkFrame(self, height=2, fg_color="#e8eaed", corner_radius=0)
        separator.grid(row=0, column=0, sticky="ew", padx=50, pady=(140, 0))
        
        # Content area
        content_text = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(size=13),
            fg_color="white",
            text_color="#3c4043",
            corner_radius=0,
            border_width=0
        )
        content_text.grid(row=1, column=0, sticky="nsew", padx=50, pady=30)
        content_text.insert("1.0", article.content)
        content_text.configure(state="normal")
        
        # Minimalist footer
        footer_frame = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color="#f8f9fa")
        footer_frame.grid(row=2, column=0, sticky="ew")
        footer_frame.grid_columnconfigure(1, weight=1)
        
        info_label = ctk.CTkLabel(
            footer_frame,
            text=f"{article.topic} • {article.unique_id}",
            font=ctk.CTkFont(size=11),
            text_color="#5f6368"
        )
        info_label.grid(row=0, column=0, padx=50, pady=15, sticky="w")
        
        url_btn = ctk.CTkButton(
            footer_frame,
            text="Open Source",
            command=lambda: webbrowser.open(article.url),
            fg_color="white",
            text_color="#1a73e8",
            border_width=1,
            border_color="#dadce0",
            font=ctk.CTkFont(size=12),
            width=120,
            height=35,
            corner_radius=18,
            hover_color="#f8f9fa"
        )
        url_btn.grid(row=0, column=2, padx=50, pady=10, sticky="e")


class ArticleViewer3(ctk.CTkToplevel):
    """Third article viewer - Card-based modern interface"""
    
    def __init__(self, parent, article: Article):
        super().__init__(parent)
        self.article = article
        self.title(f"Article Viewer - {article.title[:50]}...")
        self.geometry("950x750")
        
        # Center window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        # Keyboard shortcuts
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Control-w>", lambda e: self.destroy())
        
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="#f1f3f4")
        main_container.pack(fill="both", expand=True, padx=30, pady=30)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Card frame
        card_frame = ctk.CTkFrame(main_container, corner_radius=15, fg_color="white")
        card_frame.grid(row=0, column=0, sticky="nsew")
        card_frame.grid_columnconfigure(0, weight=1)
        card_frame.grid_rowconfigure(1, weight=1)
        
        # Card header
        header = ctk.CTkFrame(card_frame, height=100, corner_radius=15, fg_color="#34a853")
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header,
            text=article.title,
            font=ctk.CTkFont(size=19, weight="bold"),
            text_color="white",
            anchor="w",
            wraplength=850,
            justify="left"
        )
        title_label.grid(row=0, column=0, sticky="ew", padx=40, pady=30)
        
        # Card body
        body_frame = ctk.CTkFrame(card_frame, fg_color="white", corner_radius=0)
        body_frame.grid(row=1, column=0, sticky="nsew")
        body_frame.grid_columnconfigure(0, weight=1)
        body_frame.grid_rowconfigure(1, weight=1)
        
        # Tags
        tags_frame = ctk.CTkFrame(body_frame, fg_color="transparent")
        tags_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(30, 20))
        
        topic_tag = ctk.CTkLabel(
            tags_frame,
            text=article.topic,
            fg_color="#e8f5e9",
            text_color="#2e7d32",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=15,
            padx=15,
            pady=8
        )
        topic_tag.pack(side="left", padx=(0, 10))
        
        id_tag = ctk.CTkLabel(
            tags_frame,
            text=article.unique_id,
            fg_color="#f5f5f5",
            text_color="#616161",
            font=ctk.CTkFont(size=11),
            corner_radius=15,
            padx=15,
            pady=8
        )
        id_tag.pack(side="left")
        
        # Content
        content_text = ctk.CTkTextbox(
            body_frame,
            font=ctk.CTkFont(size=13),
            fg_color="white",
            text_color="#202124",
            corner_radius=0,
            border_width=0
        )
        content_text.grid(row=1, column=0, sticky="nsew", padx=40, pady=(0, 20))
        content_text.insert("1.0", article.content)
        content_text.configure(state="normal")
        
        # Action buttons
        button_frame = ctk.CTkFrame(body_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 30))
        
        url_btn = ctk.CTkButton(
            button_frame,
            text="Visit Source",
            command=lambda: webbrowser.open(article.url),
            fg_color="#34a853",
            hover_color="#2d8f47",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=140,
            height=40,
            corner_radius=20
        )
        url_btn.pack(side="left")
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.destroy,
            fg_color="#ea4335",
            hover_color="#d33b2c",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=140,
            height=40,
            corner_radius=20
        )
        close_btn.pack(side="right")
