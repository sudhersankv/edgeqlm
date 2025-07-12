"""
Audio Recorder Module
Handles system audio recording, transcription, and summarization
"""
import json
import os
import time
import threading
import wave
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

import pyaudio
import requests

import config
from src.utils import setup_logger, sanitize_filename, format_size

logger = setup_logger(__name__)

# Try to import Whisper
try:
    import whisper
    WHISPER_AVAILABLE = True
    logger.info("OpenAI Whisper is available")
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("OpenAI Whisper not available. Install with: pip install openai-whisper")

# Alternative: try faster-whisper
if not WHISPER_AVAILABLE:
    try:
        from faster_whisper import WhisperModel
        FASTER_WHISPER_AVAILABLE = True
        logger.info("Faster-Whisper is available")
    except ImportError:
        FASTER_WHISPER_AVAILABLE = False
        logger.warning("Faster-Whisper not available. Install with: pip install faster-whisper")


class AudioRecording:
    """Represents a single audio recording with metadata"""
    
    def __init__(self, filename: str, title: str = None):
        self.filename = filename
        self.title = title or f"Recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.timestamp = datetime.now()
        self.duration = 0.0
        self.file_size = 0
        self.transcription = None
        self.summary = None
        self.status = "recorded"  # recorded, transcribing, transcribed, summarized, error
        self.file_path = config.AUDIO_DIR / filename
        self.error_message = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert recording to dictionary for serialization"""
        return {
            'filename': self.filename,
            'title': self.title,
            'timestamp': self.timestamp.isoformat(),
            'duration': self.duration,
            'file_size': self.file_size,
            'transcription': self.transcription,
            'summary': self.summary,
            'status': self.status,
            'error_message': self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioRecording':
        """Create recording from dictionary"""
        recording = cls(data['filename'], data['title'])
        recording.timestamp = datetime.fromisoformat(data['timestamp'])
        recording.duration = data.get('duration', 0.0)
        recording.file_size = data.get('file_size', 0)
        recording.transcription = data.get('transcription')
        recording.summary = data.get('summary')
        recording.status = data.get('status', 'recorded')
        recording.error_message = data.get('error_message')
        return recording
    
    def update_file_info(self):
        """Update file size and duration information"""
        if self.file_path.exists():
            self.file_size = self.file_path.stat().st_size
            
            # Get duration from wave file
            try:
                with wave.open(str(self.file_path), 'rb') as wav_file:
                    frames = wav_file.getnframes()
                    rate = wav_file.getframerate()
                    self.duration = frames / float(rate)
            except Exception as e:
                logger.error(f"Error reading audio file duration: {e}")
                self.duration = 0.0


class AudioRecorder:
    """Handles audio recording and management"""
    
    def __init__(self):
        self.recordings: List[AudioRecording] = []
        self.current_recording: Optional[AudioRecording] = None
        self.is_recording = False
        self.recording_thread = None
        self.audio_stream = None
        self.pyaudio_instance = None
        self.metadata_file = config.AUDIO_DIR / "recordings_metadata.json"
        
        # Initialize Whisper model
        self.whisper_model = None
        self.faster_whisper_model = None
        self._initialize_whisper()
        
        # Load existing recordings
        self.load_recordings()
    
    def _initialize_whisper(self):
        """Initialize Whisper model for transcription"""
        try:
            if WHISPER_AVAILABLE:
                logger.info(f"Loading OpenAI Whisper model: {config.WHISPER_MODEL}")
                self.whisper_model = whisper.load_model(
                    config.WHISPER_MODEL,
                    device=config.WHISPER_DEVICE
                )
                logger.info("OpenAI Whisper model loaded successfully")
            elif FASTER_WHISPER_AVAILABLE:
                logger.info(f"Loading Faster-Whisper model: {config.WHISPER_MODEL}")
                self.faster_whisper_model = WhisperModel(
                    config.WHISPER_MODEL,
                    device=config.WHISPER_DEVICE
                )
                logger.info("Faster-Whisper model loaded successfully")
            else:
                logger.warning("No Whisper implementation available - transcription will use placeholder")
        except Exception as e:
            logger.error(f"Failed to initialize Whisper model: {e}")
            self.whisper_model = None
            self.faster_whisper_model = None
    
    def start_recording(self, title: str = None) -> bool:
        """Start recording audio"""
        if self.is_recording:
            logger.warning("Recording already in progress")
            return False
        
        try:
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"recording_{timestamp}.wav"
            
            # Create recording object
            self.current_recording = AudioRecording(filename, title)
            
            # Initialize PyAudio
            self.pyaudio_instance = pyaudio.PyAudio()
            
            # Open audio stream
            self.audio_stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=config.AUDIO_CHANNELS,
                rate=config.AUDIO_SAMPLE_RATE,
                input=True,
                frames_per_buffer=config.AUDIO_CHUNK_SIZE
            )
            
            # Start recording in separate thread
            self.is_recording = True
            self.recording_thread = threading.Thread(target=self._record_audio, daemon=True)
            self.recording_thread.start()
            
            logger.info(f"Started recording: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.cleanup_recording()
            return False
    
    def stop_recording(self) -> Optional[AudioRecording]:
        """Stop recording and return the recording object"""
        if not self.is_recording:
            logger.warning("No recording in progress")
            return None
        
        try:
            self.is_recording = False
            
            # Wait for recording thread to finish
            if self.recording_thread:
                self.recording_thread.join(timeout=5)
            
            # Cleanup audio resources
            self.cleanup_recording()
            
            if self.current_recording:
                # Update file information
                self.current_recording.update_file_info()
                
                # Add to recordings list
                self.recordings.append(self.current_recording)
                
                # Clean up old recordings
                self.cleanup_old_recordings()
                
                # Save metadata
                self.save_recordings()
                
                logger.info(f"Stopped recording: {self.current_recording.filename} "
                           f"({format_size(self.current_recording.file_size)}, "
                           f"{self.current_recording.duration:.1f}s)")
                
                recording = self.current_recording
                self.current_recording = None
                return recording
                
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            self.cleanup_recording()
        
        return None
    
    def _record_audio(self):
        """Internal method to record audio data"""
        frames = []
        
        try:
            while self.is_recording:
                data = self.audio_stream.read(config.AUDIO_CHUNK_SIZE)
                frames.append(data)
            
            # Save audio data to file
            if frames and self.current_recording:
                with wave.open(str(self.current_recording.file_path), 'wb') as wav_file:
                    wav_file.setnchannels(config.AUDIO_CHANNELS)
                    wav_file.setsampwidth(self.pyaudio_instance.get_sample_size(pyaudio.paInt16))
                    wav_file.setframerate(config.AUDIO_SAMPLE_RATE)
                    wav_file.writeframes(b''.join(frames))
                    
        except Exception as e:
            logger.error(f"Error during audio recording: {e}")
    
    def cleanup_recording(self):
        """Clean up audio resources"""
        try:
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = None
            
            if self.pyaudio_instance:
                self.pyaudio_instance.terminate()
                self.pyaudio_instance = None
                
        except Exception as e:
            logger.error(f"Error cleaning up recording resources: {e}")
    
    def cleanup_old_recordings(self):
        """Remove old recordings to keep only the latest N files"""
        if len(self.recordings) <= config.AUDIO_MAX_FILES:
            return
        
        # Sort by timestamp
        self.recordings.sort(key=lambda x: x.timestamp)
        
        # Remove oldest recordings
        recordings_to_remove = self.recordings[:-config.AUDIO_MAX_FILES]
        
        for recording in recordings_to_remove:
            try:
                # Delete file
                if recording.file_path.exists():
                    recording.file_path.unlink()
                    logger.info(f"Deleted old recording: {recording.filename}")
                
                # Remove from list
                self.recordings.remove(recording)
                
            except Exception as e:
                logger.error(f"Error deleting old recording {recording.filename}: {e}")
    
    def transcribe_recording(self, recording: AudioRecording) -> bool:
        """Transcribe an audio recording using Whisper"""
        if not recording.file_path.exists():
            logger.error(f"Audio file not found: {recording.filename}")
            recording.status = "error"
            recording.error_message = "Audio file not found"
            return False
        
        try:
            recording.status = "transcribing"
            self.save_recordings()
            
            # Use Whisper for transcription
            transcription = self._transcribe_with_whisper(recording.file_path)
            
            if transcription:
                recording.transcription = transcription
                recording.status = "transcribed"
                recording.error_message = None
                self.save_recordings()
                
                logger.info(f"Transcribed recording: {recording.filename}")
                return True
            else:
                recording.status = "error"
                recording.error_message = "Transcription failed"
                self.save_recordings()
                return False
                
        except Exception as e:
            logger.error(f"Error transcribing recording {recording.filename}: {e}")
            recording.status = "error"
            recording.error_message = str(e)
            self.save_recordings()
            return False
    
    def _transcribe_with_whisper(self, audio_file: Path) -> Optional[str]:
        """Transcribe audio using Whisper"""
        try:
            if self.whisper_model:
                # Use OpenAI Whisper
                logger.info(f"Transcribing {audio_file.name} with OpenAI Whisper")
                
                result = self.whisper_model.transcribe(
                    str(audio_file),
                    language=config.WHISPER_LANGUAGE,
                    temperature=config.WHISPER_TEMPERATURE
                )
                
                return result.get("text", "").strip()
                
            elif self.faster_whisper_model:
                # Use Faster-Whisper
                logger.info(f"Transcribing {audio_file.name} with Faster-Whisper")
                
                segments, info = self.faster_whisper_model.transcribe(
                    str(audio_file),
                    language=config.WHISPER_LANGUAGE,
                    temperature=config.WHISPER_TEMPERATURE
                )
                
                # Combine all segments
                text_segments = []
                for segment in segments:
                    text_segments.append(segment.text)
                
                return " ".join(text_segments).strip()
                
            else:
                # Fallback to placeholder
                logger.warning(f"No Whisper model available, using placeholder for {audio_file.name}")
                
                # Return placeholder transcription
                return f"[Placeholder transcription for {audio_file.name}]\n" \
                       f"Duration: {self.current_recording.duration:.1f}s\n" \
                       f"To enable real transcription, install Whisper:\n" \
                       f"pip install openai-whisper\n" \
                       f"or pip install faster-whisper"
                       
        except Exception as e:
            logger.error(f"Error in Whisper transcription: {e}")
            return None
    
    def summarize_recording(self, recording: AudioRecording) -> bool:
        """Summarize a transcribed recording using LLM"""
        if not recording.transcription:
            logger.error(f"No transcription available for {recording.filename}")
            return False
        
        try:
            # Use Ollama to summarize the transcription
            summary = self._summarize_with_ollama(recording.transcription, recording.title)
            
            if summary:
                recording.summary = summary
                recording.status = "summarized"
                self.save_recordings()
                
                logger.info(f"Summarized recording: {recording.filename}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error summarizing recording {recording.filename}: {e}")
            return False
    
    def _summarize_with_ollama(self, transcription: str, title: str = None) -> Optional[str]:
        """Summarize transcription using Ollama"""
        try:
            prompt = f"""Please summarize the following transcription of a meeting or audio recording.

Title: {title or 'Audio Recording'}

Transcription:
{transcription}

Provide a concise summary including:
1. Key topics discussed
2. Important decisions made
3. Action items (if any)
4. Main participants/speakers mentioned

Format the summary in a clear, structured way."""

            url = f"{config.OLLAMA_BASE_URL}/api/generate"
            
            payload = {
                "model": config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "max_tokens": 500
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
            logger.error(f"Error summarizing with Ollama: {e}")
            return None
    
    def get_recordings(self) -> List[AudioRecording]:
        """Get all recordings"""
        return self.recordings.copy()
    
    def get_recording_by_filename(self, filename: str) -> Optional[AudioRecording]:
        """Get a specific recording by filename"""
        for recording in self.recordings:
            if recording.filename == filename:
                return recording
        return None
    
    def delete_recording(self, recording: AudioRecording) -> bool:
        """Delete a recording"""
        try:
            # Delete file
            if recording.file_path.exists():
                recording.file_path.unlink()
            
            # Remove from list
            if recording in self.recordings:
                self.recordings.remove(recording)
            
            # Save metadata
            self.save_recordings()
            
            logger.info(f"Deleted recording: {recording.filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting recording {recording.filename}: {e}")
            return False
    
    def get_recordings_for_processing(self) -> List[AudioRecording]:
        """Get recordings that need transcription or summarization"""
        return [
            recording for recording in self.recordings
            if recording.status in ["recorded", "transcribed"]
        ]
    
    def save_recordings(self):
        """Save recordings metadata to file"""
        try:
            data = {
                'recordings': [recording.to_dict() for recording in self.recordings]
            }
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save recordings metadata: {e}")
    
    def load_recordings(self):
        """Load recordings metadata from file"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.recordings = [
                    AudioRecording.from_dict(recording_data)
                    for recording_data in data.get('recordings', [])
                ]
                
                logger.info(f"Loaded {len(self.recordings)} audio recordings")
                
        except Exception as e:
            logger.error(f"Failed to load recordings metadata: {e}")
            self.recordings = []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get recording statistics"""
        total_recordings = len(self.recordings)
        total_duration = sum(recording.duration for recording in self.recordings)
        total_size = sum(recording.file_size for recording in self.recordings)
        
        status_counts = {}
        for recording in self.recordings:
            status_counts[recording.status] = status_counts.get(recording.status, 0) + 1
        
        return {
            'total_recordings': total_recordings,
            'total_duration': total_duration,
            'total_size': total_size,
            'status_counts': status_counts,
            'max_files': config.AUDIO_MAX_FILES,
            'whisper_available': WHISPER_AVAILABLE or FASTER_WHISPER_AVAILABLE,
            'whisper_model': config.WHISPER_MODEL
        } 