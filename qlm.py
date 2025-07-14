#!/usr/bin/env python3
"""
QLM Command Line Interface
Simple wrapper script to run the command generator
"""
import sys
from pathlib import Path
import config
from filelock import FileLock, Timeout

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run the command generator
from src.command_generator_improved import main

if __name__ == "__main__":
    LOCK_FILE = config.DATA_DIR / "qlm_cli.lock"
    lock = FileLock(str(LOCK_FILE))
    try:
        lock.acquire(timeout=0)
    except Timeout:
        print("Another qlm CLI instance is already running. Exiting.")
        sys.exit(0)
    try:
        main()
    finally:
        if lock.is_locked:
            lock.release() 