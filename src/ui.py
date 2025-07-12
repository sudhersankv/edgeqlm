"""
Basic UI Module
Simple GUI for clipboard history management and search
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
from datetime import datetime
from typing import List, Optional
import threading

import config
from src.utils import setup_logger, truncate_text, format_size, extract_keywords
from src.clipboard_manager import ClipboardManager, ClipboardEntry
from src.audio_recorder import AudioRecorder
from src.background_processor import BackgroundProcessor

logger = setup_logger(__name__)


class ClipboardHistoryUI:
    """Main UI for clipboard history management"""
    
    def __init__(self, clipboard_manager: ClipboardManager, audio_recorder: AudioRecorder, 
                 background_processor: BackgroundProcessor):
        self.clipboard_manager = clipboard_manager
        self.audio_recorder = audio_recorder
        self.background_processor = background_processor
        
        self.root = tk.Tk()
        self.root.title("Edge-QLM - Clipboard History")
        self.root.geometry(f"{config.UI_WINDOW_WIDTH}x{config.UI_WINDOW_HEIGHT}")
        
        # Variables
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_change)
        self.selected_entry = None
        self.search_timer = None
        self.current_entries = []
        
        # UI Components
        self.setup_ui()
        
        # Initial load
        self.refresh_clipboard_list()
        
    def setup_ui(self):
        """Set up the UI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Clipboard History", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Filter dropdown
        self.filter_var = tk.StringVar(value="all")
        filter_combo = ttk.Combobox(search_frame, textvariable=self.filter_var, 
                                   values=["all", "code", "json", "error", "log", "config", "text"])
        filter_combo.pack(side=tk.LEFT, padx=(0, 5))
        filter_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        
        # Refresh button
        refresh_btn = ttk.Button(search_frame, text="Refresh", command=self.refresh_clipboard_list)
        refresh_btn.pack(side=tk.LEFT)
        
        # Content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Clipboard list
        list_frame = ttk.LabelFrame(content_frame, text="Clipboard Entries", padding="5")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.clipboard_listbox = tk.Listbox(list_frame, font=('Courier', 9))
        self.clipboard_listbox.pack(fill=tk.BOTH, expand=True)
        self.clipboard_listbox.bind('<<ListboxSelect>>', self._on_entry_select)
        self.clipboard_listbox.bind('<Double-Button-1>', self._on_entry_double_click)
        
        # Details frame
        details_frame = ttk.LabelFrame(content_frame, text="Entry Details", padding="5")
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Entry content
        self.content_text = scrolledtext.ScrolledText(details_frame, font=('Courier', 9))
        self.content_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Buttons
        button_frame = ttk.Frame(details_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Copy", command=self._copy_selected_entry).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Delete", command=self._delete_selected_entry).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Process", command=self._process_selected_entry).pack(side=tk.LEFT)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.pack(fill=tk.X, pady=(10, 0))
        
        # Menu bar
        self.setup_menu()
        
    def setup_menu(self):
        """Set up the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Clear All", command=self._clear_all_entries)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Audio menu
        audio_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Audio", menu=audio_menu)
        audio_menu.add_command(label="Start Recording", command=self._start_recording)
        audio_menu.add_command(label="Stop Recording", command=self._stop_recording)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _on_search_change(self, *args):
        """Handle search text change"""
        if self.search_timer:
            self.root.after_cancel(self.search_timer)
        self.search_timer = self.root.after(config.UI_SEARCH_DEBOUNCE, self._perform_search)
    
    def _on_filter_change(self, event):
        """Handle filter change"""
        self._perform_search()
    
    def _perform_search(self):
        """Perform the search"""
        search_query = self.search_var.get().strip()
        filter_type = self.filter_var.get()
        
        if filter_type == "all":
            if search_query:
                entries = self.clipboard_manager.search_entries(search_query, config.UI_MAX_DISPLAY_ENTRIES)
            else:
                entries = self.clipboard_manager.get_recent_entries(config.UI_MAX_DISPLAY_ENTRIES)
        else:
            entries = self.clipboard_manager.search_by_type(filter_type, config.UI_MAX_DISPLAY_ENTRIES)
            if search_query:
                entries = [e for e in entries if search_query.lower() in e.content.lower()]
        
        self._update_clipboard_list(entries)
    
    def _update_clipboard_list(self, entries: List[ClipboardEntry]):
        """Update the clipboard list"""
        self.clipboard_listbox.delete(0, tk.END)
        
        for entry in entries:
            timestamp = entry.timestamp.strftime("%H:%M:%S")
            content_preview = truncate_text(entry.content.replace('\n', ' '), 60)
            display_text = f"[{timestamp}] {entry.content_type.upper()}: {content_preview}"
            self.clipboard_listbox.insert(tk.END, display_text)
        
        self.current_entries = entries
        self.status_label.config(text=f"Showing {len(entries)} entries")
    
    def _on_entry_select(self, event):
        """Handle entry selection"""
        selection = self.clipboard_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.current_entries):
                self.selected_entry = self.current_entries[index]
                self._update_entry_details()
    
    def _on_entry_double_click(self, event):
        """Handle double-click"""
        self._copy_selected_entry()
    
    def _update_entry_details(self):
        """Update entry details"""
        if not self.selected_entry:
            return
        
        entry = self.selected_entry
        self.content_text.delete(1.0, tk.END)
        
        # Show metadata
        metadata = f"Timestamp: {entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        metadata += f"Type: {entry.content_type}\n"
        metadata += f"Size: {format_size(entry.size)}\n"
        metadata += f"Labels: {', '.join(entry.labels) if entry.labels else 'None'}\n"
        metadata += f"Summary: {entry.summary if entry.summary else 'Not processed'}\n"
        metadata += "\n" + "="*50 + "\n\n"
        
        self.content_text.insert(1.0, metadata + entry.content)
    
    def _copy_selected_entry(self):
        """Copy selected entry"""
        if self.selected_entry:
            self.clipboard_manager.copy_to_clipboard(self.selected_entry)
            self.status_label.config(text="Copied to clipboard")
            self.root.after(2000, lambda: self.status_label.config(text="Ready"))
    
    def _delete_selected_entry(self):
        """Delete selected entry"""
        if self.selected_entry:
            if messagebox.askyesno("Confirm", "Delete this entry?"):
                self.clipboard_manager.delete_entry(self.selected_entry)
                self.refresh_clipboard_list()
                self.status_label.config(text="Entry deleted")
    
    def _process_selected_entry(self):
        """Process selected entry"""
        if self.selected_entry:
            threading.Thread(target=self._process_entry_background, daemon=True).start()
            self.status_label.config(text="Processing...")
    
    def _process_entry_background(self):
        """Process entry in background"""
        if self.selected_entry:
            try:
                summary = self.background_processor._generate_summary(
                    self.selected_entry.content, 
                    self.selected_entry.content_type
                )
                labels = extract_keywords(self.selected_entry.content)
                
                if summary or labels:
                    self.clipboard_manager.update_entry_summary(self.selected_entry, summary, labels)
                    self.root.after(0, self._update_entry_details)
                    self.root.after(0, lambda: self.status_label.config(text="Entry processed"))
                else:
                    self.root.after(0, lambda: self.status_label.config(text="Processing failed"))
            except Exception as e:
                logger.error(f"Error processing entry: {e}")
                self.root.after(0, lambda: self.status_label.config(text="Processing error"))
    
    def _clear_all_entries(self):
        """Clear all entries"""
        if messagebox.askyesno("Confirm", "Clear all entries?"):
            self.clipboard_manager.clear_all_entries()
            self.refresh_clipboard_list()
            self.status_label.config(text="All entries cleared")
    
    def _start_recording(self):
        """Start recording"""
        title = simpledialog.askstring("Recording", "Enter title:")
        if title and self.audio_recorder.start_recording(title):
            self.status_label.config(text="Recording started")
        else:
            self.status_label.config(text="Failed to start recording")
    
    def _stop_recording(self):
        """Stop recording"""
        recording = self.audio_recorder.stop_recording()
        if recording:
            self.status_label.config(text=f"Recording stopped: {recording.filename}")
        else:
            self.status_label.config(text="No recording in progress")
    
    def _show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "Edge-QLM MVP v0.1.0\nProductivity tool for engineers")
    
    def refresh_clipboard_list(self):
        """Refresh the list"""
        self._perform_search()
    
    def run(self):
        """Run the UI"""
        self.root.mainloop() 