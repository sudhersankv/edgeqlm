"""
Simple UI Module
Clean, focused interface for clipboard and audio management
"""
import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, 
                             QListWidget, QListWidgetItem, QTabWidget, QGroupBox, 
                             QCheckBox, QSpinBox, QComboBox, QSystemTrayIcon, QMenu, 
                             QStatusBar, QMessageBox, QSplitter, QFormLayout)
from PyQt6.QtCore import Qt, QTimer, QSettings
from PyQt6.QtGui import QIcon, QAction, QFont
import logging
from typing import Dict, List, Optional, Any
import requests
import subprocess

from .utils import setup_logger
from .hotkey_manager import HotkeyManager


class SimpleEdgeQLMWindow(QMainWindow):
    """Simplified main window focusing on clipboard and audio"""
    
    def __init__(self, clipboard_manager, audio_recorder, config):
        super().__init__()
        self.clipboard_manager = clipboard_manager
        self.audio_recorder = audio_recorder
        self.config = config
        
        # Setup logger
        self.logger = setup_logger(__name__)
        
        # Initialize settings
        self.settings = QSettings('EdgeQLM', 'Simple')
        
        # Initialize hotkey manager
        self.hotkey_manager = HotkeyManager(self.config, self.audio_recorder)
        
        # Setup UI
        self.setup_ui()
        self.setup_system_tray()
        self.setup_timers()
        
        # Apply clean dark theme
        self.apply_clean_theme()
        
        self.logger.info("Simple Edge-QLM UI initialized")
    
    def setup_ui(self):
        """Setup the simplified user interface"""
        self.setWindowTitle("Edge-QLM - Simple")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create simplified tabs
        self.create_clipboard_tab()
        self.create_audio_tab()
        self.create_simple_settings_tab()
        
        # Setup status bar
        self.setup_status_bar()
    
    def create_clipboard_tab(self):
        """Create the clipboard management tab"""
        clipboard_widget = QWidget()
        layout = QVBoxLayout(clipboard_widget)
        
        # Header with stats
        header_layout = QHBoxLayout()
        
        self.clipboard_count_label = QLabel("Total entries: 0")
        self.clipboard_count_label.setStyleSheet("font-weight: bold; color: #0078d4;")
        header_layout.addWidget(self.clipboard_count_label)
        
        header_layout.addStretch()
        
        self.clear_clipboard_btn = QPushButton("Clear History")
        self.clear_clipboard_btn.clicked.connect(self.clear_clipboard_history)
        header_layout.addWidget(self.clear_clipboard_btn)
        
        layout.addLayout(header_layout)
        
        # Search
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search clipboard history...")
        self.search_input.textChanged.connect(self.filter_clipboard_history)
        search_layout.addWidget(self.search_input)
        
        self.content_type_filter = QComboBox()
        self.content_type_filter.addItems(["All", "Code", "Error", "Log", "Config", "JSON", "Text"])
        self.content_type_filter.currentTextChanged.connect(self.filter_clipboard_history)
        search_layout.addWidget(self.content_type_filter)
        
        layout.addLayout(search_layout)
        
        # Clipboard history with details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # History list
        self.clipboard_list = QListWidget()
        self.clipboard_list.itemClicked.connect(self.show_clipboard_details)
        self.clipboard_list.setMinimumWidth(300)
        splitter.addWidget(self.clipboard_list)
        
        # Details panel
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        details_header = QLabel("Content Details")
        details_header.setStyleSheet("font-weight: bold; font-size: 14px;")
        details_layout.addWidget(details_header)
        
        self.clipboard_details = QTextEdit()
        self.clipboard_details.setReadOnly(True)
        details_layout.addWidget(self.clipboard_details)
        
        # Actions for selected item
        actions_layout = QHBoxLayout()
        
        self.copy_selected_btn = QPushButton("Copy Selected")
        self.copy_selected_btn.clicked.connect(self.copy_selected_item)
        actions_layout.addWidget(self.copy_selected_btn)
        
        self.delete_selected_btn = QPushButton("Delete Selected")
        self.delete_selected_btn.clicked.connect(self.delete_selected_item)
        actions_layout.addWidget(self.delete_selected_btn)
        
        details_layout.addLayout(actions_layout)
        
        splitter.addWidget(details_widget)
        splitter.setSizes([300, 500])
        
        layout.addWidget(splitter)
        
        self.tab_widget.addTab(clipboard_widget, "Clipboard")
    
    def create_audio_tab(self):
        """Create the audio recording tab"""
        audio_widget = QWidget()
        layout = QVBoxLayout(audio_widget)
        
        # Recording controls
        controls_group = QGroupBox("Recording")
        controls_layout = QVBoxLayout(controls_group)
        
        # Recording status
        status_layout = QHBoxLayout()
        
        self.recording_status = QLabel("Ready")
        self.recording_status.setStyleSheet("font-weight: bold; font-size: 16px; color: #00aa00;")
        status_layout.addWidget(self.recording_status)
        
        status_layout.addStretch()
        
        # Recording buttons
        self.record_btn = QPushButton("🎤 Record")
        self.record_btn.clicked.connect(self.toggle_recording)
        status_layout.addWidget(self.record_btn)
        
        self.transcribe_btn = QPushButton("📝 Transcribe")
        self.transcribe_btn.clicked.connect(self.transcribe_last_recording)
        status_layout.addWidget(self.transcribe_btn)
        
        controls_layout.addLayout(status_layout)
        
        # Hotkey info
        hotkey_info = QLabel(f"Hotkeys: {getattr(self.config, 'RECORD_HOTKEY', 'F9')} to record, {getattr(self.config, 'STOP_HOTKEY', 'F10')} to stop")
        hotkey_info.setStyleSheet("color: #666; font-style: italic;")
        controls_layout.addWidget(hotkey_info)
        
        layout.addWidget(controls_group)
        
        # Audio history and transcription
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Recordings list
        recordings_widget = QWidget()
        recordings_layout = QVBoxLayout(recordings_widget)
        
        recordings_header = QLabel("Recordings")
        recordings_header.setStyleSheet("font-weight: bold; font-size: 14px;")
        recordings_layout.addWidget(recordings_header)
        
        self.recordings_list = QListWidget()
        self.recordings_list.itemClicked.connect(self.show_recording_details)
        recordings_layout.addWidget(self.recordings_list)
        
        clear_recordings_btn = QPushButton("Clear All")
        clear_recordings_btn.clicked.connect(self.clear_recordings)
        recordings_layout.addWidget(clear_recordings_btn)
        
        splitter.addWidget(recordings_widget)
        
        # Transcription panel
        transcription_widget = QWidget()
        transcription_layout = QVBoxLayout(transcription_widget)
        
        transcription_header = QLabel("Transcription")
        transcription_header.setStyleSheet("font-weight: bold; font-size: 14px;")
        transcription_layout.addWidget(transcription_header)
        
        self.transcription_output = QTextEdit()
        self.transcription_output.setReadOnly(True)
        transcription_layout.addWidget(self.transcription_output)
        
        # Transcription actions
        trans_actions_layout = QHBoxLayout()
        
        self.copy_transcription_btn = QPushButton("Copy Text")
        self.copy_transcription_btn.clicked.connect(self.copy_transcription)
        trans_actions_layout.addWidget(self.copy_transcription_btn)
        
        self.save_transcription_btn = QPushButton("Save as Note")
        self.save_transcription_btn.clicked.connect(self.save_transcription)
        trans_actions_layout.addWidget(self.save_transcription_btn)
        
        self.transcribe_selected_btn = QPushButton("Transcribe Selected")
        self.transcribe_selected_btn.clicked.connect(self.transcribe_selected)
        trans_actions_layout.addWidget(self.transcribe_selected_btn)
        
        transcription_layout.addLayout(trans_actions_layout)
        
        splitter.addWidget(transcription_widget)
        splitter.setSizes([250, 550])
        
        layout.addWidget(splitter)
        
        self.tab_widget.addTab(audio_widget, "Audio")
    
    def create_simple_settings_tab(self):
        """Create simplified settings tab"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        # Clipboard settings
        clipboard_group = QGroupBox("Clipboard Settings")
        clipboard_layout = QFormLayout(clipboard_group)
        
        self.auto_start_cb = QCheckBox("Start with Windows")
        self.auto_start_cb.setChecked(self.settings.value("auto_start", False, bool))
        clipboard_layout.addRow("Startup:", self.auto_start_cb)
        
        self.max_entries_spin = QSpinBox()
        self.max_entries_spin.setRange(100, 10000)
        self.max_entries_spin.setValue(getattr(self.config, 'MAX_CLIPBOARD_ENTRIES', 5000))
        clipboard_layout.addRow("Max Entries:", self.max_entries_spin)
        
        self.min_to_tray_cb = QCheckBox("Minimize to tray")
        self.min_to_tray_cb.setChecked(self.settings.value("minimize_to_tray", True, bool))
        clipboard_layout.addRow("Window:", self.min_to_tray_cb)
        
        layout.addWidget(clipboard_group)
        
        # Audio settings
        audio_group = QGroupBox("Audio Settings")
        audio_layout = QFormLayout(audio_group)
        
        self.record_hotkey_input = QLineEdit()
        self.record_hotkey_input.setText(getattr(self.config, 'RECORD_HOTKEY', 'F9'))
        audio_layout.addRow("Record Hotkey:", self.record_hotkey_input)
        
        self.stop_hotkey_input = QLineEdit()
        self.stop_hotkey_input.setText(getattr(self.config, 'STOP_HOTKEY', 'F10'))
        audio_layout.addRow("Stop Hotkey:", self.stop_hotkey_input)
        
        self.whisper_model_combo = QComboBox()
        self.whisper_model_combo.addItems(["tiny", "base", "small", "medium"])
        self.whisper_model_combo.setCurrentText(getattr(self.config, 'WHISPER_MODEL_SIZE', 'base'))
        audio_layout.addRow("Whisper Model:", self.whisper_model_combo)
        
        self.cpu_threshold_spin = QSpinBox()
        self.cpu_threshold_spin.setRange(5, 80)
        self.cpu_threshold_spin.setValue(getattr(self.config, 'CPU_THRESHOLD', 30))
        audio_layout.addRow("CPU Threshold (%):", self.cpu_threshold_spin)
        
        layout.addWidget(audio_group)
        
        # Ollama settings
        ollama_group = QGroupBox("Ollama Settings")
        ollama_layout = QFormLayout(ollama_group)
        
        self.model_combo = QComboBox()
        self.update_models_list()
        ollama_layout.addRow("Model:", self.model_combo)
        
        self.install_model_input = QLineEdit()
        self.install_model_input.setPlaceholderText("Enter model name to install...")
        ollama_layout.addRow("Install New:", self.install_model_input)
        
        install_btn = QPushButton("Install Model")
        install_btn.clicked.connect(self.install_model)
        ollama_layout.addWidget(install_btn)
        
        layout.addWidget(ollama_group)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        self.save_settings_btn = QPushButton("Save Settings")
        self.save_settings_btn.clicked.connect(self.save_settings)
        actions_layout.addWidget(self.save_settings_btn)
        
        self.export_data_btn = QPushButton("Export Data")
        self.export_data_btn.clicked.connect(self.export_clipboard_data)
        actions_layout.addWidget(self.export_data_btn)
        
        layout.addLayout(actions_layout)
        
        layout.addStretch()
        
        self.tab_widget.addTab(settings_widget, "Settings")
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add permanent widgets
        self.clipboard_status_label = QLabel("Clipboard: Active")
        self.clipboard_status_label.setStyleSheet("color: #00aa00;")
        self.status_bar.addPermanentWidget(self.clipboard_status_label)
        
        self.audio_status_label = QLabel("Audio: Ready")
        self.audio_status_label.setStyleSheet("color: #00aa00;")
        self.status_bar.addPermanentWidget(self.audio_status_label)
        
        self.status_bar.showMessage("Ready")
    
    def setup_system_tray(self):
        """Setup system tray"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        self.tray_icon = QSystemTrayIcon(self)
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        record_action = QAction("🎤 Record", self)
        record_action.triggered.connect(self.toggle_recording)
        tray_menu.addAction(record_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()
    
    def setup_timers(self):
        """Setup update timers"""
        # Update clipboard display
        self.clipboard_timer = QTimer()
        self.clipboard_timer.timeout.connect(self.update_clipboard_display)
        self.clipboard_timer.start(3000)  # Every 3 seconds
        
        # Update status
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Every 5 seconds
    
    def apply_clean_theme(self):
        """Apply clean dark theme"""
        style = """
        QMainWindow {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QWidget {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QTabWidget::pane {
            border: 1px solid #404040;
            background-color: #2d2d2d;
        }
        QTabBar::tab {
            background-color: #404040;
            color: #ffffff;
            padding: 10px 20px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #0078d4;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #404040;
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #106ebe;
        }
        QPushButton:pressed {
            background-color: #005a9e;
        }
        QLineEdit, QTextEdit, QSpinBox, QComboBox {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #404040;
            padding: 6px;
            border-radius: 4px;
        }
        QLineEdit:focus, QTextEdit:focus {
            border-color: #0078d4;
        }
        QListWidget {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #404040;
            border-radius: 4px;
        }
        QListWidget::item {
            padding: 8px;
            border-bottom: 1px solid #404040;
        }
        QListWidget::item:selected {
            background-color: #0078d4;
        }
        QListWidget::item:hover {
            background-color: #404040;
        }
        QCheckBox {
            color: #ffffff;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            background-color: #2d2d2d;
            border: 1px solid #404040;
        }
        QCheckBox::indicator:checked {
            background-color: #0078d4;
        }
        QStatusBar {
            background-color: #1e1e1e;
            color: #ffffff;
            border-top: 1px solid #404040;
        }
        QSplitter::handle {
            background-color: #404040;
        }
        """
        self.setStyleSheet(style)
    
    # Event handlers
    def update_clipboard_display(self):
        """Update clipboard display"""
        try:
            if hasattr(self.clipboard_manager, 'get_recent_entries'):
                entries = self.clipboard_manager.get_recent_entries(200)
                
                # Update count
                self.clipboard_count_label.setText(f"Total entries: {len(entries)}")
                
                # Update list if needed
                if len(entries) != self.clipboard_list.count():
                    self.clipboard_list.clear()
                    
                    for entry in entries:
                        item = QListWidgetItem()
                        timestamp = entry.timestamp.strftime('%H:%M:%S') if hasattr(entry, 'timestamp') else ''
                        content_type = getattr(entry, 'content_type', 'text')
                        content = getattr(entry, 'content', '')
                        
                        # Create preview
                        preview = content.replace('\n', ' ').replace('\r', ' ')
                        if len(preview) > 80:
                            preview = preview[:77] + '...'
                        
                        item.setText(f"[{timestamp}] {content_type}: {preview}")
                        item.setData(Qt.ItemDataRole.UserRole, entry)
                        self.clipboard_list.addItem(item)
                        
        except Exception as e:
            self.logger.error(f"Error updating clipboard display: {e}")
    
    def update_status(self):
        """Update status indicators"""
        try:
            # Update clipboard status
            if hasattr(self.clipboard_manager, 'is_running') and self.clipboard_manager.is_running:
                self.clipboard_status_label.setText("Clipboard: Active")
                self.clipboard_status_label.setStyleSheet("color: #00aa00;")
            else:
                self.clipboard_status_label.setText("Clipboard: Stopped")
                self.clipboard_status_label.setStyleSheet("color: #ff4444;")
            
            # Update audio status
            if hasattr(self.audio_recorder, 'is_recording') and self.audio_recorder.is_recording:
                self.audio_status_label.setText("Audio: Recording")
                self.audio_status_label.setStyleSheet("color: #ffaa00;")
            else:
                self.audio_status_label.setText("Audio: Ready")
                self.audio_status_label.setStyleSheet("color: #00aa00;")
                
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")
    
    def filter_clipboard_history(self):
        """Filter clipboard history"""
        search_text = self.search_input.text().lower()
        content_type = self.content_type_filter.currentText()
        
        for i in range(self.clipboard_list.count()):
            item = self.clipboard_list.item(i)
            entry = item.data(Qt.ItemDataRole.UserRole)
            
            if not entry:
                continue
                
            # Check search text
            entry_content = getattr(entry, 'content', '').lower()
            entry_type = getattr(entry, 'content_type', '').lower()
            text_match = search_text in entry_content or search_text in entry_type
            
            # Check content type
            type_match = content_type == "All" or entry_type == content_type.lower()
            
            item.setHidden(not (text_match and type_match))
    
    def show_clipboard_details(self, item):
        """Show clipboard item details"""
        entry = item.data(Qt.ItemDataRole.UserRole)
        if entry:
            timestamp = entry.timestamp.strftime('%Y-%m-%d %H:%M:%S') if hasattr(entry, 'timestamp') else 'Unknown'
            content_type = getattr(entry, 'content_type', 'text')
            content = getattr(entry, 'content', '')
            
            details = f"Time: {timestamp}\n"
            details += f"Type: {content_type}\n"
            details += f"Size: {len(content)} characters\n"
            details += f"Lines: {content.count(chr(10)) + 1}\n\n"
            details += "Content:\n" + content
            
            self.clipboard_details.setText(details)
    
    def copy_selected_item(self):
        """Copy selected clipboard item"""
        current_item = self.clipboard_list.currentItem()
        if current_item:
            entry = current_item.data(Qt.ItemDataRole.UserRole)
            if entry:
                content = getattr(entry, 'content', '')
                QApplication.clipboard().setText(content)
                self.status_bar.showMessage("Copied to clipboard", 2000)
    
    def delete_selected_item(self):
        """Delete selected clipboard item"""
        current_item = self.clipboard_list.currentItem()
        if current_item:
            reply = QMessageBox.question(self, "Delete Item", 
                                       "Delete this clipboard entry?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.clipboard_list.takeItem(self.clipboard_list.row(current_item))
                self.clipboard_details.clear()
                self.status_bar.showMessage("Item deleted", 2000)
    
    def clear_clipboard_history(self):
        """Clear all clipboard history"""
        reply = QMessageBox.question(self, "Clear History", 
                                   "Clear all clipboard history?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self.clipboard_manager, 'clear_history'):
                self.clipboard_manager.clear_history()
            self.clipboard_list.clear()
            self.clipboard_details.clear()
            self.status_bar.showMessage("History cleared", 2000)
    
    def toggle_recording(self):
        """Toggle audio recording"""
        try:
            if hasattr(self.audio_recorder, 'is_recording') and self.audio_recorder.is_recording:
                self.audio_recorder.stop_recording()
                self.recording_status.setText("Processing...")
                self.recording_status.setStyleSheet("font-weight: bold; font-size: 16px; color: #ffaa00;")
                self.record_btn.setText("🎤 Record")
                
                # Auto-transcribe
                QTimer.singleShot(1000, self.transcribe_last_recording)
            else:
                self.audio_recorder.start_recording()
                self.recording_status.setText("Recording...")
                self.recording_status.setStyleSheet("font-weight: bold; font-size: 16px; color: #ff4444;")
                self.record_btn.setText("⏹️ Stop")
                
        except Exception as e:
            self.logger.error(f"Error toggling recording: {e}")
            self.recording_status.setText("Error")
            self.recording_status.setStyleSheet("font-weight: bold; font-size: 16px; color: #ff4444;")
    
    def transcribe_last_recording(self):
        """Transcribe last recording"""
        try:
            if hasattr(self.audio_recorder, 'transcribe_last_recording'):
                result = self.audio_recorder.transcribe_last_recording()
                if result:
                    self.transcription_output.setText(result)
                    self.recording_status.setText("Ready")
                    self.recording_status.setStyleSheet("font-weight: bold; font-size: 16px; color: #00aa00;")
                    
                    # Update recordings list
                    self.update_recordings_list()
                else:
                    self.transcription_output.setText("Transcription failed or no recording found.")
                    
        except Exception as e:
            self.logger.error(f"Error transcribing: {e}")
            self.transcription_output.setText(f"Error: {str(e)}")
    
    def update_recordings_list(self):
        self.recordings_list.clear()
        recordings = self.audio_recorder.get_recordings()
        recordings.sort(key=lambda r: r.timestamp, reverse=True)
        for recording in recordings:
            item = QListWidgetItem(f"{recording.title} ({recording.status})")
            item.setData(Qt.ItemDataRole.UserRole, recording)
            self.recordings_list.addItem(item)
    
    def show_recording_details(self, item):
        recording = item.data(Qt.ItemDataRole.UserRole)
        if recording:
            text = recording.transcription if recording.transcription else "Not transcribed yet."
            self.transcription_output.setText(text)
    
    def transcribe_selected(self):
        current_item = self.recordings_list.currentItem()
        if current_item:
            recording = current_item.data(Qt.ItemDataRole.UserRole)
            if recording:
                self.audio_recorder.transcribe_recording(recording)
                self.update_recordings_list()
                self.show_recording_details(current_item)
    
    def copy_transcription(self):
        """Copy transcription text"""
        text = self.transcription_output.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.status_bar.showMessage("Transcription copied", 2000)
    
    def save_transcription(self):
        """Save transcription as note"""
        text = self.transcription_output.toPlainText()
        if text:
            # Add to clipboard as a note
            if hasattr(self.clipboard_manager, 'add_manual_entry'):
                self.clipboard_manager.add_manual_entry(text, 'transcription')
            QApplication.clipboard().setText(text)
            self.status_bar.showMessage("Transcription saved and copied", 2000)
    
    def clear_recordings(self):
        """Clear all recordings"""
        reply = QMessageBox.question(self, "Clear Recordings", 
                                   "Clear all audio recordings?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self.audio_recorder, 'clear_recordings'):
                self.audio_recorder.clear_recordings()
            self.recordings_list.clear()
            self.status_bar.showMessage("Recordings cleared", 2000)
    
    def save_settings(self):
        """Save settings"""
        try:
            # Save to QSettings
            self.settings.setValue("auto_start", self.auto_start_cb.isChecked())
            self.settings.setValue("minimize_to_tray", self.min_to_tray_cb.isChecked())
            self.settings.setValue("max_entries", self.max_entries_spin.value())
            self.settings.setValue("record_hotkey", self.record_hotkey_input.text())
            self.settings.setValue("stop_hotkey", self.stop_hotkey_input.text())
            self.settings.setValue("whisper_model", self.whisper_model_combo.currentText())
            setattr(self.config, 'CPU_THRESHOLD', self.cpu_threshold_spin.value())
            setattr(self.config, 'OLLAMA_MODEL', self.model_combo.currentText())
            
            # Update hotkeys
            if hasattr(self, 'hotkey_manager'):
                self.hotkey_manager.update_hotkeys()
            
            self.status_bar.showMessage("Settings saved", 2000)
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            QMessageBox.warning(self, "Error", f"Failed to save settings: {str(e)}")
    
    def export_clipboard_data(self):
        """Export clipboard data"""
        try:
            if hasattr(self.clipboard_manager, 'export_data'):
                filename = f"clipboard_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                self.clipboard_manager.export_data(filename)
                self.status_bar.showMessage(f"Data exported to {filename}", 3000)
            else:
                QMessageBox.information(self, "Export", "Export feature not available")
                
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            QMessageBox.warning(self, "Error", f"Failed to export data: {str(e)}")
    
    def update_models_list(self):
        try:
            response = requests.get(f"{self.config.OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                self.model_combo.clear()
                for model in models:
                    self.model_combo.addItem(model['name'])
                current = getattr(self.config, 'OLLAMA_MODEL', 'codellama:7b')
                self.model_combo.setCurrentText(current)
        except:
            pass
    
    def install_model(self):
        model_name = self.install_model_input.text().strip()
        if model_name:
            try:
                subprocess.run(['ollama', 'pull', model_name], check=True)
                self.update_models_list()
                self.install_model_input.clear()
                QMessageBox.information(self, "Success", f"Model {model_name} installed.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to install model: {str(e)}")
    
    def show_window(self):
        """Show main window"""
        self.show()
        self.raise_()
        self.activateWindow()
    
    def on_tray_activated(self, reason):
        """Handle tray activation"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show_window()
    
    def closeEvent(self, event):
        """Handle close event"""
        if self.min_to_tray_cb.isChecked() and hasattr(self, 'tray_icon'):
            self.hide()
            event.ignore()
        else:
            self.quit_application()
    
    def quit_application(self):
        """Quit application"""
        # Cleanup
        if hasattr(self, 'hotkey_manager'):
            self.hotkey_manager.cleanup()
        
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        
        QApplication.quit()


class SimpleEdgeQLMApp:
    """Simple application class"""
    
    def __init__(self, clipboard_manager, audio_recorder, config):
        self.clipboard_manager = clipboard_manager
        self.audio_recorder = audio_recorder
        self.config = config
        
        # Initialize Qt application
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Create main window
        self.main_window = SimpleEdgeQLMWindow(
            clipboard_manager, audio_recorder, config
        )
    
    def run(self):
        """Run the application"""
        self.main_window.show()
        return self.app.exec()


def create_simple_ui(clipboard_manager, audio_recorder, config):
    """Create simple UI"""
    return SimpleEdgeQLMApp(clipboard_manager, audio_recorder, config) 