#!/usr/bin/env python3
"""
QLM Command Line Interface
Simple wrapper script to run the command generator
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run the command generator
from src.command_generator_improved import main

if __name__ == "__main__":
    main() 