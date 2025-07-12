"""
Background Processor Module
Handles idle-time processing for summarization and labeling
"""
import time
import threading
from datetime import datetime
from typing import Optional, List

import requests
import psutil

import config
from src.utils import setup_logger, extract_keywords
from src.clipboard_manager import ClipboardManager
from src.audio_recorder import AudioRecorder

logger = setup_logger(__name__)


class BackgroundProcessor:
    """Handles background processing during idle time"""
    
    def __init__(self, clipboard_manager: ClipboardManager, audio_recorder: AudioRecorder):
        self.clipboard_manager = clipboard_manager
        self.audio_recorder = audio_recorder
        self.running = False
        self.processor_thread = None
        self.last_activity_time = datetime.now()
        self.processing_active = False
        self.cpu_readings = []
        
    def start(self):
        """Start the background processor"""
        if self.running:
            logger.warning("Background processor already running")
            return
            
        self.running = True
        self.processor_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.processor_thread.start()
        logger.info("Background processor started")
        
    def stop(self):
        """Stop the background processor"""
        self.running = False
        if self.processor_thread:
            self.processor_thread.join(timeout=5)
        logger.info("Background processor stopped")
        
    def _process_loop(self):
        """Main processing loop"""
        while self.running:
            try:
                # Check if system is idle and CPU usage is low
                if self._is_system_ready_for_processing():
                    if not self.processing_active:
                        logger.info("System ready for processing (CPU < 15%, idle detected)")
                        self.processing_active = True
                    
                    # Process clipboard entries
                    self._process_clipboard_entries()
                    
                    # Process audio recordings
                    self._process_audio_recordings()
                    
                else:
                    if self.processing_active:
                        logger.info("System busy detected, pausing background processing")
                        self.processing_active = False
                    
                    self.last_activity_time = datetime.now()
                
                # Sleep between checks
                time.sleep(config.IDLE_CHECK_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in background processing loop: {e}")
                time.sleep(config.IDLE_CHECK_INTERVAL)
                
    def _is_system_ready_for_processing(self) -> bool:
        """Check if system is ready for processing (low CPU usage and idle)"""
        try:
            # Get current CPU usage
            current_cpu = psutil.cpu_percent(interval=1)
            
            # Keep a rolling average of CPU readings
            self.cpu_readings.append(current_cpu)
            if len(self.cpu_readings) > config.CPU_CHECK_DURATION:
                self.cpu_readings.pop(0)
            
            # Calculate average CPU usage
            avg_cpu = sum(self.cpu_readings) / len(self.cpu_readings)
            
            # Check if CPU is below threshold
            cpu_ok = avg_cpu < config.CPU_THRESHOLD
            
            # Check if enough time has passed since last activity
            idle_duration = (datetime.now() - self.last_activity_time).total_seconds()
            idle_ok = idle_duration >= config.IDLE_THRESHOLD
            
            if not cpu_ok:
                self.last_activity_time = datetime.now()  # Reset idle timer on high CPU
            
            return cpu_ok and idle_ok
            
        except Exception as e:
            logger.error(f"Error checking system status: {e}")
            return False
        
    def _process_clipboard_entries(self):
        """Process clipboard entries that need summarization"""
        try:
            # Get entries that need processing
            entries_to_process = self.clipboard_manager.get_entries_for_processing()
            
            if not entries_to_process:
                return
                
            logger.info(f"Processing {len(entries_to_process)} clipboard entries")
            
            # Process entries in batches
            for entry in entries_to_process[:config.PROCESSING_BATCH_SIZE]:
                if not self.running or not self._is_system_ready_for_processing():
                    break
                
                try:
                    # Generate summary
                    summary = self._generate_summary(entry.content, entry.content_type)
                    
                    # Extract keywords/labels
                    labels = extract_keywords(entry.content)
                    
                    # Update entry
                    self.clipboard_manager.update_entry_summary(entry, summary, labels)
                    
                    logger.info(f"Processed clipboard entry: {entry.content_type}")
                    
                    # Small delay to avoid overwhelming the system
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing clipboard entry: {e}")
                    
        except Exception as e:
            logger.error(f"Error in clipboard processing: {e}")
            
    def _process_audio_recordings(self):
        """Process audio recordings that need transcription/summarization"""
        try:
            # Get recordings that need processing
            recordings_to_process = self.audio_recorder.get_recordings_for_processing()
            
            if not recordings_to_process:
                return
                
            logger.info(f"Processing {len(recordings_to_process)} audio recordings")
            
            for recording in recordings_to_process:
                if not self.running or not self._is_system_ready_for_processing():
                    break
                
                try:
                    # Check CPU usage before heavy operations
                    current_cpu = psutil.cpu_percent(interval=1)
                    if current_cpu > config.CPU_THRESHOLD:
                        logger.info(f"CPU usage too high ({current_cpu:.1f}%), skipping audio processing")
                        break
                    
                    # Transcribe if needed
                    if recording.status == "recorded":
                        logger.info(f"Transcribing recording: {recording.filename}")
                        self.audio_recorder.transcribe_recording(recording)
                        
                        # Check if we should continue
                        if not self._is_system_ready_for_processing():
                            break
                    
                    # Summarize if transcribed
                    if recording.status == "transcribed":
                        logger.info(f"Summarizing recording: {recording.filename}")
                        self.audio_recorder.summarize_recording(recording)
                    
                    logger.info(f"Processed audio recording: {recording.filename}")
                    
                    # Longer delay for audio processing
                    time.sleep(5)
                    
                except Exception as e:
                    logger.error(f"Error processing audio recording {recording.filename}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in audio processing: {e}")
            
    def _generate_summary(self, content: str, content_type: str) -> Optional[str]:
        """Generate a summary for clipboard content using Ollama"""
        try:
            # Skip summarization for short content
            if len(content) < 200:
                return None
                
            prompt = self._build_summary_prompt(content, content_type)
            
            url = f"{config.OLLAMA_BASE_URL}/api/generate"
            
            payload = {
                "model": config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "max_tokens": 200
                }
            }
            
            response = requests.post(url, json=payload, timeout=config.OLLAMA_TIMEOUT)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None
            
    def _build_summary_prompt(self, content: str, content_type: str) -> str:
        """Build a prompt for summarizing clipboard content"""
        prompts = {
            "code": f"""Summarize this code snippet in 1-2 sentences:

{content}

Focus on what the code does, its main purpose, and any key functions or classes.""",
            
            "json": f"""Summarize this JSON data in 1-2 sentences:

{content}

Focus on the data structure, main fields, and purpose.""",
            
            "error": f"""Summarize this error message in 1-2 sentences:

{content}

Focus on the error type, cause, and potential solution.""",
            
            "log": f"""Summarize this log output in 1-2 sentences:

{content}

Focus on the main events, any errors, and overall status.""",
            
            "config": f"""Summarize this configuration in 1-2 sentences:

{content}

Focus on what is being configured and key settings."""
        }
        
        return prompts.get(content_type, f"""Summarize this text in 1-2 sentences:

{content}

Focus on the main topic and key information.""")
        
    def force_process_clipboard(self):
        """Force process clipboard entries regardless of idle state"""
        try:
            logger.info("Force processing clipboard entries")
            self._process_clipboard_entries()
        except Exception as e:
            logger.error(f"Error in force clipboard processing: {e}")
            
    def force_process_audio(self):
        """Force process audio recordings regardless of idle state"""
        try:
            logger.info("Force processing audio recordings")
            self._process_audio_recordings()
        except Exception as e:
            logger.error(f"Error in force audio processing: {e}")
            
    def get_status(self) -> dict:
        """Get current processor status"""
        try:
            current_cpu = psutil.cpu_percent(interval=0.1)
            avg_cpu = sum(self.cpu_readings) / len(self.cpu_readings) if self.cpu_readings else 0
        except:
            current_cpu = 0
            avg_cpu = 0
            
        return {
            'running': self.running,
            'processing_active': self.processing_active,
            'last_activity_time': self.last_activity_time.isoformat(),
            'system_ready': self._is_system_ready_for_processing() if self.running else False,
            'current_cpu_usage': current_cpu,
            'avg_cpu_usage': avg_cpu,
            'cpu_threshold': config.CPU_THRESHOLD,
            'pending_clipboard_entries': len(self.clipboard_manager.get_entries_for_processing()),
            'pending_audio_recordings': len(self.audio_recorder.get_recordings_for_processing())
        } 