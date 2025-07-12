"""
Clipboard Manager Module
Handles clipboard monitoring, storage, and management
"""
import json
import re
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import pyperclip
import psutil

import config
from src.utils import setup_logger, detect_content_type

logger = setup_logger(__name__)


class ClipboardEntry:
    """Represents a single clipboard entry"""
    
    def __init__(self, content: str, timestamp: datetime = None):
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.content_type = detect_content_type(content)
        self.summary = None
        self.labels = []
        self.size = len(content.encode('utf-8'))
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary for JSON serialization"""
        return {
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'content_type': self.content_type,
            'summary': self.summary,
            'labels': self.labels,
            'size': self.size
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClipboardEntry':
        """Create entry from dictionary"""
        entry = cls(data['content'], datetime.fromisoformat(data['timestamp']))
        entry.content_type = data.get('content_type', 'text')
        entry.summary = data.get('summary')
        entry.labels = data.get('labels', [])
        entry.size = data.get('size', len(data['content'].encode('utf-8')))
        return entry


class ClipboardManager:
    """Manages clipboard monitoring and storage"""
    
    def __init__(self):
        self.entries: List[ClipboardEntry] = []
        self.current_clipboard = ""
        self.running = False
        self.monitor_thread = None
        self.lock = threading.Lock()
        
        # Load existing entries
        self.load_entries()
        
    def start_monitoring(self):
        """Start clipboard monitoring in a separate thread"""
        if self.running:
            logger.warning("Clipboard monitoring already running")
            return
            
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_clipboard, daemon=True)
        self.monitor_thread.start()
        logger.info("Clipboard monitoring started")
        
    def stop_monitoring(self):
        """Stop clipboard monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logger.info("Clipboard monitoring stopped")
        
    def _monitor_clipboard(self):
        """Monitor clipboard for changes"""
        while self.running:
            try:
                clipboard_content = pyperclip.paste()
                if clipboard_content != self.current_clipboard and clipboard_content.strip():
                    self.current_clipboard = clipboard_content
                    self.add_entry(clipboard_content)
                    
                time.sleep(config.CLIPBOARD_MONITOR_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error monitoring clipboard: {e}")
                time.sleep(config.CLIPBOARD_MONITOR_INTERVAL)
                
    def add_entry(self, content: str):
        """Add a new clipboard entry"""
        if not content.strip():
            return
            
        with self.lock:
            # Check if this content already exists as the last entry
            if self.entries and self.entries[-1].content == content:
                return
                
            entry = ClipboardEntry(content)
            self.entries.append(entry)
            
            logger.info(f"Added clipboard entry: {entry.content_type} ({entry.size} bytes)")
            
            # Clean up old entries if needed
            self._cleanup_entries()
            
            # Save to file
            self.save_entries()
            
    def _cleanup_entries(self):
        """Clean up old entries if threshold exceeded"""
        if len(self.entries) > config.CLIPBOARD_CLEANUP_THRESHOLD:
            # Keep only the most recent entries
            entries_to_keep = config.CLIPBOARD_MAX_ENTRIES
            self.entries = self.entries[-entries_to_keep:]
            logger.info(f"Cleaned up clipboard entries, keeping {entries_to_keep}")
            
    def search_entries(self, query: str, limit: int = 50) -> List[ClipboardEntry]:
        """Search clipboard entries by content"""
        if not query:
            return self.entries[-limit:]
            
        query_lower = query.lower()
        matches = []
        
        with self.lock:
            for entry in reversed(self.entries):
                if query_lower in entry.content.lower():
                    matches.append(entry)
                    if len(matches) >= limit:
                        break
                        
        return matches
        
    def search_by_type(self, content_type: str, limit: int = 50) -> List[ClipboardEntry]:
        """Search clipboard entries by content type"""
        matches = []
        
        with self.lock:
            for entry in reversed(self.entries):
                if entry.content_type == content_type:
                    matches.append(entry)
                    if len(matches) >= limit:
                        break
                        
        return matches
        
    def get_recent_entries(self, limit: int = 50) -> List[ClipboardEntry]:
        """Get most recent clipboard entries"""
        with self.lock:
            return self.entries[-limit:]
            
    def copy_to_clipboard(self, entry: ClipboardEntry):
        """Copy an entry back to clipboard"""
        try:
            pyperclip.copy(entry.content)
            self.current_clipboard = entry.content
            logger.info(f"Copied entry to clipboard: {entry.content_type}")
        except Exception as e:
            logger.error(f"Failed to copy to clipboard: {e}")
            
    def delete_entry(self, entry: ClipboardEntry):
        """Delete a specific entry"""
        with self.lock:
            if entry in self.entries:
                self.entries.remove(entry)
                self.save_entries()
                logger.info("Deleted clipboard entry")
                
    def clear_all_entries(self):
        """Clear all clipboard entries"""
        with self.lock:
            self.entries.clear()
            self.save_entries()
            logger.info("Cleared all clipboard entries")
            
    def get_entries_for_processing(self, limit: int = None) -> List[ClipboardEntry]:
        """Get entries that need processing (summarization/labeling)"""
        limit = limit or config.PROCESSING_BATCH_SIZE
        unprocessed = []
        
        with self.lock:
            for entry in reversed(self.entries):
                if entry.summary is None and len(entry.content) > 200:
                    unprocessed.append(entry)
                    if len(unprocessed) >= limit:
                        break
                        
        return unprocessed
        
    def update_entry_summary(self, entry: ClipboardEntry, summary: str, labels: List[str]):
        """Update entry with summary and labels"""
        with self.lock:
            entry.summary = summary
            entry.labels = labels
            self.save_entries()
            
    def save_entries(self):
        """Save entries to JSON file"""
        try:
            data = [entry.to_dict() for entry in self.entries]
            with open(config.CLIPBOARD_LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save clipboard entries: {e}")
            
    def load_entries(self):
        """Load entries from JSON file"""
        try:
            if config.CLIPBOARD_LOG_FILE.exists():
                with open(config.CLIPBOARD_LOG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.entries = [ClipboardEntry.from_dict(entry_data) for entry_data in data]
                    logger.info(f"Loaded {len(self.entries)} clipboard entries")
        except Exception as e:
            logger.error(f"Failed to load clipboard entries: {e}")
            self.entries = []
            
    def get_stats(self) -> Dict[str, Any]:
        """Get clipboard statistics"""
        with self.lock:
            total_entries = len(self.entries)
            total_size = sum(entry.size for entry in self.entries)
            
            type_counts = {}
            for entry in self.entries:
                type_counts[entry.content_type] = type_counts.get(entry.content_type, 0) + 1
                
            return {
                'total_entries': total_entries,
                'total_size': total_size,
                'type_counts': type_counts,
                'oldest_entry': self.entries[0].timestamp.isoformat() if self.entries else None,
                'newest_entry': self.entries[-1].timestamp.isoformat() if self.entries else None
            } 