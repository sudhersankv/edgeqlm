import logging
import threading
from typing import Dict, Callable, Optional
import keyboard
import pynput
from pynput import keyboard as pynput_keyboard
from pynput.keyboard import Key, Listener
import time

from .utils import setup_logger


class HotkeyManager:
    """Manages global hotkeys for the Edge-QLM application"""
    
    def __init__(self, config, audio_recorder):
        self.config = config
        self.audio_recorder = audio_recorder
        self.logger = setup_logger(__name__)
        
        # Hotkey mappings
        self.hotkeys = {}
        self.listeners = []
        self.ptt_active = False
        self.ptt_thread = None
        
        # Initialize default hotkeys
        self.setup_default_hotkeys()
        
        # Start hotkey monitoring
        self.start_monitoring()
    
    def setup_default_hotkeys(self):
        """Setup default hotkey mappings"""
        try:
            # Get hotkey settings from config
            record_hotkey = getattr(self.config, 'RECORD_HOTKEY', 'F9')
            stop_hotkey = getattr(self.config, 'STOP_HOTKEY', 'F10')
            ptt_mode = getattr(self.config, 'PUSH_TO_TALK_MODE', False)
            
            # Configure recording hotkeys
            if ptt_mode:
                self.hotkeys[record_hotkey] = {
                    'callback': self.start_ptt_recording,
                    'callback_release': self.stop_ptt_recording,
                    'mode': 'push_to_talk'
                }
            else:
                self.hotkeys[record_hotkey] = {
                    'callback': self.toggle_recording,
                    'mode': 'toggle'
                }
                self.hotkeys[stop_hotkey] = {
                    'callback': self.stop_recording,
                    'mode': 'action'
                }
            
            self.logger.info(f"Hotkeys configured: Record={record_hotkey}, Stop={stop_hotkey}, PTT={ptt_mode}")
            
        except Exception as e:
            self.logger.error(f"Error setting up hotkeys: {e}")
    
    def start_monitoring(self):
        """Start monitoring for hotkeys"""
        try:
            # Stop existing monitoring
            self.stop_monitoring()
            
            # Start keyboard listener for global hotkeys
            self.keyboard_listener = Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release
            )
            self.keyboard_listener.start()
            self.listeners.append(self.keyboard_listener)
            
            # Also use keyboard library for additional hotkey support
            self.setup_keyboard_hotkeys()
            
            self.logger.info("Hotkey monitoring started")
            
        except Exception as e:
            self.logger.error(f"Error starting hotkey monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop hotkey monitoring"""
        try:
            # Stop all listeners
            for listener in self.listeners:
                if hasattr(listener, 'stop'):
                    listener.stop()
            
            # Clear keyboard hotkeys
            keyboard.unhook_all()
            
            self.listeners.clear()
            self.logger.info("Hotkey monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping hotkey monitoring: {e}")
    
    def setup_keyboard_hotkeys(self):
        """Setup hotkeys using keyboard library"""
        try:
            for hotkey_str, hotkey_config in self.hotkeys.items():
                if hotkey_config['mode'] == 'toggle' or hotkey_config['mode'] == 'action':
                    keyboard.add_hotkey(
                        hotkey_str.lower(),
                        hotkey_config['callback'],
                        suppress=True
                    )
                    
        except Exception as e:
            self.logger.error(f"Error setting up keyboard hotkeys: {e}")
    
    def on_key_press(self, key):
        """Handle key press events"""
        try:
            key_str = self.key_to_string(key)
            
            # Check if this is a registered hotkey
            for hotkey_str, hotkey_config in self.hotkeys.items():
                if key_str.lower() == hotkey_str.lower():
                    if hotkey_config['mode'] == 'push_to_talk':
                        if not self.ptt_active:
                            hotkey_config['callback']()
                            self.ptt_active = True
                    break
                    
        except Exception as e:
            self.logger.error(f"Error handling key press: {e}")
    
    def on_key_release(self, key):
        """Handle key release events"""
        try:
            key_str = self.key_to_string(key)
            
            # Check if this is a registered hotkey
            for hotkey_str, hotkey_config in self.hotkeys.items():
                if key_str.lower() == hotkey_str.lower():
                    if hotkey_config['mode'] == 'push_to_talk':
                        if self.ptt_active and 'callback_release' in hotkey_config:
                            hotkey_config['callback_release']()
                            self.ptt_active = False
                    break
                    
        except Exception as e:
            self.logger.error(f"Error handling key release: {e}")
    
    def key_to_string(self, key):
        """Convert key object to string representation"""
        try:
            if hasattr(key, 'name'):
                return key.name
            elif hasattr(key, 'char') and key.char:
                return key.char
            else:
                return str(key)
        except:
            return str(key)
    
    def toggle_recording(self):
        """Toggle audio recording"""
        try:
            if hasattr(self.audio_recorder, 'toggle_recording'):
                self.audio_recorder.toggle_recording()
                self.logger.info("Recording toggled via hotkey")
            else:
                self.logger.warning("Audio recorder not available")
        except Exception as e:
            self.logger.error(f"Error toggling recording: {e}")
    
    def start_recording(self):
        """Start audio recording"""
        try:
            if hasattr(self.audio_recorder, 'start_recording'):
                self.audio_recorder.start_recording()
                self.logger.info("Recording started via hotkey")
            else:
                self.logger.warning("Audio recorder not available")
        except Exception as e:
            self.logger.error(f"Error starting recording: {e}")
    
    def stop_recording(self):
        """Stop audio recording"""
        try:
            if hasattr(self.audio_recorder, 'stop_recording'):
                self.audio_recorder.stop_recording()
                self.logger.info("Recording stopped via hotkey")
            else:
                self.logger.warning("Audio recorder not available")
        except Exception as e:
            self.logger.error(f"Error stopping recording: {e}")
    
    def start_ptt_recording(self):
        """Start push-to-talk recording"""
        try:
            if hasattr(self.audio_recorder, 'start_recording'):
                self.audio_recorder.start_recording()
                self.logger.info("PTT recording started")
            else:
                self.logger.warning("Audio recorder not available")
        except Exception as e:
            self.logger.error(f"Error starting PTT recording: {e}")
    
    def stop_ptt_recording(self):
        """Stop push-to-talk recording"""
        try:
            if hasattr(self.audio_recorder, 'stop_recording'):
                self.audio_recorder.stop_recording()
                self.logger.info("PTT recording stopped")
            else:
                self.logger.warning("Audio recorder not available")
        except Exception as e:
            self.logger.error(f"Error stopping PTT recording: {e}")
    
    def update_hotkeys(self):
        """Update hotkeys based on current configuration"""
        try:
            # Stop current monitoring
            self.stop_monitoring()
            
            # Setup new hotkeys
            self.setup_default_hotkeys()
            
            # Restart monitoring
            self.start_monitoring()
            
            self.logger.info("Hotkeys updated successfully")
            
        except Exception as e:
            self.logger.error(f"Error updating hotkeys: {e}")
    
    def add_hotkey(self, hotkey_str: str, callback: Callable, mode: str = 'action'):
        """Add a new hotkey"""
        try:
            self.hotkeys[hotkey_str] = {
                'callback': callback,
                'mode': mode
            }
            
            # Restart monitoring to include new hotkey
            self.start_monitoring()
            
            self.logger.info(f"Added hotkey: {hotkey_str}")
            
        except Exception as e:
            self.logger.error(f"Error adding hotkey {hotkey_str}: {e}")
    
    def remove_hotkey(self, hotkey_str: str):
        """Remove a hotkey"""
        try:
            if hotkey_str in self.hotkeys:
                del self.hotkeys[hotkey_str]
                
                # Restart monitoring to remove hotkey
                self.start_monitoring()
                
                self.logger.info(f"Removed hotkey: {hotkey_str}")
            else:
                self.logger.warning(f"Hotkey {hotkey_str} not found")
                
        except Exception as e:
            self.logger.error(f"Error removing hotkey {hotkey_str}: {e}")
    
    def get_active_hotkeys(self) -> Dict[str, dict]:
        """Get list of active hotkeys"""
        return self.hotkeys.copy()
    
    def is_hotkey_available(self, hotkey_str: str) -> bool:
        """Check if a hotkey is available (not already in use)"""
        return hotkey_str not in self.hotkeys
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.stop_monitoring()
            self.logger.info("Hotkey manager cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


class HotkeyRecorder:
    """Helper class to record hotkey combinations"""
    
    def __init__(self):
        self.recording = False
        self.recorded_keys = []
        self.listener = None
        self.logger = setup_logger(__name__)
    
    def start_recording(self, callback):
        """Start recording hotkey combination"""
        self.recording = True
        self.recorded_keys = []
        self.callback = callback
        
        try:
            self.listener = Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release
            )
            self.listener.start()
            self.logger.info("Hotkey recording started")
        except Exception as e:
            self.logger.error(f"Error starting hotkey recording: {e}")
    
    def stop_recording(self):
        """Stop recording hotkey combination"""
        self.recording = False
        
        try:
            if self.listener:
                self.listener.stop()
                self.listener = None
            
            # Process recorded keys
            if self.recorded_keys:
                hotkey_str = self.keys_to_hotkey_string(self.recorded_keys)
                self.callback(hotkey_str)
                self.logger.info(f"Recorded hotkey: {hotkey_str}")
            
        except Exception as e:
            self.logger.error(f"Error stopping hotkey recording: {e}")
    
    def on_key_press(self, key):
        """Handle key press during recording"""
        if self.recording:
            key_str = self.key_to_string(key)
            if key_str not in self.recorded_keys:
                self.recorded_keys.append(key_str)
    
    def on_key_release(self, key):
        """Handle key release during recording"""
        if self.recording:
            # Stop recording after first key combination
            self.stop_recording()
    
    def key_to_string(self, key):
        """Convert key object to string representation"""
        try:
            if hasattr(key, 'name'):
                return key.name
            elif hasattr(key, 'char') and key.char:
                return key.char
            else:
                return str(key)
        except:
            return str(key)
    
    def keys_to_hotkey_string(self, keys):
        """Convert list of keys to hotkey string"""
        # Sort keys to ensure consistent ordering
        special_keys = ['ctrl', 'alt', 'shift', 'cmd', 'super']
        sorted_keys = []
        
        # Add special keys first
        for key in keys:
            if key.lower() in special_keys:
                sorted_keys.append(key)
        
        # Add regular keys
        for key in keys:
            if key.lower() not in special_keys:
                sorted_keys.append(key)
        
        return '+'.join(sorted_keys)


def create_hotkey_manager(config, audio_recorder):
    """Create and return a hotkey manager instance"""
    return HotkeyManager(config, audio_recorder) 