"""
Configuration file for edge-qlm MVP
"""
import os
from pathlib import Path

# Base directories
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
AUDIO_DIR = DATA_DIR / "audio"
CLIPBOARD_DIR = DATA_DIR / "clipboard"

# Create directories if they don't exist
for dir_path in [DATA_DIR, LOGS_DIR, AUDIO_DIR, CLIPBOARD_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "codellama:7b"  # Default coding model
OLLAMA_TIMEOUT = 30  # seconds

# Clipboard Configuration
CLIPBOARD_LOG_FILE = CLIPBOARD_DIR / "clipboard_history.json"
CLIPBOARD_MAX_ENTRIES = 10000  # Maximum entries to keep
CLIPBOARD_CLEANUP_THRESHOLD = 12000  # Start cleanup when this many entries
CLIPBOARD_MONITOR_INTERVAL = 1.0  # seconds

# Audio Configuration
AUDIO_MAX_FILES = 10  # Keep only last 10 recordings
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
AUDIO_FORMAT = "wav"
AUDIO_CHUNK_SIZE = 1024

# Whisper Configuration
WHISPER_MODEL = "base"  # tiny, base, small, medium, large
WHISPER_DEVICE = "cpu"  # cpu, cuda
WHISPER_LANGUAGE = None  # None for auto-detect, or specify like "en"
WHISPER_TEMPERATURE = 0.0  # 0.0 for deterministic, higher for more creative
TRANSCRIPTION_MODEL = "whisper"  # Can be changed to other models

# Command Generator Configuration
QLM_SESSION_TIMEOUT = 3600  # Session timeout in seconds (1 hour)
QLM_CONTEXT_MAX_ENTRIES = 50  # Maximum context entries per session
QLM_TEMPLATES_DIR = PROJECT_ROOT / "templates"

# UI Configuration
UI_WINDOW_WIDTH = 800
UI_WINDOW_HEIGHT = 600
UI_SEARCH_DEBOUNCE = 300  # milliseconds
UI_MAX_DISPLAY_ENTRIES = 100

# Background Processing Configuration
IDLE_THRESHOLD = 300  # seconds of inactivity before considering idle
IDLE_CHECK_INTERVAL = 60  # seconds between idle checks
PROCESSING_BATCH_SIZE = 10  # Number of items to process at once
CPU_THRESHOLD = 15  # CPU usage threshold (%) for auto-processing
CPU_CHECK_DURATION = 5  # seconds to average CPU usage over

# Content Type Detection Patterns
CONTENT_TYPE_PATTERNS = {
    "code": [r"^(function|class|def|import|#include|package|interface)", r"[{};]", r"^\s*(if|for|while|switch)"],
    "json": [r"^\s*[\[{]", r":\s*[\[\{\"'\d]", r"^\s*[\}\]]"],
    "error": [r"error", r"exception", r"traceback", r"failed", r"fatal"],
    "log": [r"^\d{4}-\d{2}-\d{2}", r"INFO|DEBUG|WARN|ERROR", r"^\[\d{2}:\d{2}:\d{2}\]"],
    "config": [r"^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=", r"^\s*\[[^\]]+\]", r"\.ini$|\.conf$|\.cfg$"],
    "command": [r"^\s*[a-zA-Z_][a-zA-Z0-9_-]*\s+", r"^\s*\$", r"--[a-zA-Z-]+"],
    "url": [r"https?://", r"www\.", r"\.com|\.org|\.net"],
    "file_path": [r"^[a-zA-Z]:\\", r"^/[a-zA-Z]", r"\.[\w]{2,4}$"]
}

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOGS_DIR / "edge_qlm.log"
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# System Configuration
SYSTEM_TRAY_ENABLED = True
AUTO_START_ENABLED = True
MINIMIZE_TO_TRAY = True 