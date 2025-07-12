"""
Utility functions for edge-qlm
"""
import logging
import re
from logging.handlers import RotatingFileHandler
from typing import List, Optional

import config


def setup_logger(name: str) -> logging.Logger:
    """Set up a logger with file and console handlers"""
    logger = logging.getLogger(name)
    
    if logger.handlers:
        # Logger already configured
        return logger
    
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Create formatters
    formatter = logging.Formatter(config.LOG_FORMAT)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=config.LOG_MAX_SIZE,
        backupCount=config.LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def detect_content_type(content: str) -> str:
    """Detect the type of content based on patterns"""
    if not content or not content.strip():
        return "empty"
    
    content_lower = content.lower()
    
    # Check each pattern type
    for content_type, patterns in config.CONTENT_TYPE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                return content_type
    
    return "text"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters"""
    # Remove invalid characters for Windows filenames
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip('. ')
    
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed"
    
    return filename


def format_size(size_bytes: int) -> str:
    """Format byte size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"


def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """Extract key words from text for labeling"""
    if not text:
        return []
    
    # Common words to exclude
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
        'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
        'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
    }
    
    # Extract words (alphanumeric, length >= 3)
    words = re.findall(r'\b[a-zA-Z0-9]{3,}\b', text.lower())
    
    # Count word frequencies
    word_counts = {}
    for word in words:
        if word not in stop_words:
            word_counts[word] = word_counts.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words[:max_keywords]]


def is_system_idle() -> bool:
    """Check if system is idle (no user input for a while)"""
    try:
        import psutil
        import time
        
        # Get CPU usage over a short period
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Consider system idle if CPU usage is low
        return cpu_percent < 10
        
    except ImportError:
        # Fallback: assume not idle if psutil not available
        return False
    except Exception:
        # On error, assume not idle
        return False


def get_system_info() -> dict:
    """Get basic system information"""
    try:
        import psutil
        import platform
        
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_usage': psutil.disk_usage('/').percent if platform.system() != 'Windows' else psutil.disk_usage('C:').percent
        }
    except Exception as e:
        return {'error': str(e)}


def validate_json(text: str) -> bool:
    """Validate if text is valid JSON"""
    try:
        import json
        json.loads(text)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def escape_markdown(text: str) -> str:
    """Escape markdown special characters"""
    special_chars = ['*', '_', '`', '[', ']', '(', ')', '#', '+', '-', '.', '!', '|', '\\']
    for char in special_chars:
        text = text.replace(char, '\\' + char)
    return text 