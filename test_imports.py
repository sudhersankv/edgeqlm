#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

import sys
import os

def test_imports():
    """Test all module imports"""
    print("Testing imports...")
    
    try:
        # Test basic imports
        print("1. Testing basic imports...")
        import config
        print("   ✓ config imported successfully")
        
        # Test src module imports
        print("2. Testing src module imports...")
        from src.utils import setup_logger
        print("   ✓ setup_logger imported successfully")
        
        from src.clipboard_manager import ClipboardManager
        print("   ✓ ClipboardManager imported successfully")
        
        from src.command_generator import CommandGenerator
        print("   ✓ CommandGenerator imported successfully")
        
        from src.audio_recorder import AudioRecorder
        print("   ✓ AudioRecorder imported successfully")
        
        from src.background_processor import BackgroundProcessor
        print("   ✓ BackgroundProcessor imported successfully")
        
        # Test new UI imports
        print("3. Testing new UI imports...")
        try:
            from src.ui_modern import create_ui
            print("   ✓ ui_modern imported successfully")
        except ImportError as e:
            print(f"   ✗ ui_modern import failed: {e}")
            return False
        
        try:
            from src.hotkey_manager import HotkeyManager
            print("   ✓ hotkey_manager imported successfully")
        except ImportError as e:
            print(f"   ✗ hotkey_manager import failed: {e}")
            return False
        
        # Test PyQt6 imports
        print("4. Testing PyQt6 imports...")
        try:
            from PyQt6.QtWidgets import QApplication
            print("   ✓ PyQt6 imported successfully")
        except ImportError as e:
            print(f"   ✗ PyQt6 import failed: {e}")
            print("   Install with: pip install PyQt6")
            print("   Note: PyQt6-tools is NOT required")
            return False
        
        # Test hotkey library imports (optional)
        print("5. Testing hotkey library imports...")
        pynput_ok = True
        keyboard_ok = True
        
        try:
            import pynput
            print("   ✓ pynput imported successfully")
        except ImportError as e:
            print(f"   ✗ pynput import failed: {e}")
            print("   Install with: pip install pynput")
            pynput_ok = False
        
        try:
            import keyboard
            print("   ✓ keyboard imported successfully")
        except ImportError as e:
            print(f"   ✗ keyboard import failed: {e}")
            print("   Install with: pip install keyboard")
            keyboard_ok = False
        
        if not pynput_ok or not keyboard_ok:
            print("   Note: Hotkey functionality will be disabled without these libraries")
        
        print("\nAll imports successful! ✓")
        return True
        
    except Exception as e:
        print(f"Import test failed: {e}")
        return False

def test_logger():
    """Test logger functionality"""
    print("\nTesting logger...")
    try:
        from src.utils import setup_logger
        logger = setup_logger("test")
        logger.info("Test log message")
        print("   ✓ Logger working correctly")
        return True
    except Exception as e:
        print(f"   ✗ Logger test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Edge-QLM Import Test")
    print("=" * 50)
    
    success = True
    success &= test_imports()
    success &= test_logger()
    
    if success:
        print("\n" + "=" * 50)
        print("✓ All tests passed! The application should run correctly.")
        print("You can now run: python main.py")
    else:
        print("\n" + "=" * 50)
        print("✗ Some tests failed. Please install missing dependencies.")
        print("Run: pip install -r requirements.txt")
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 