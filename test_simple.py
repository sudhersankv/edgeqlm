#!/usr/bin/env python3
"""
Simple test script for Edge-QLM Simple
"""

import sys
import os
import traceback

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        # Test config
        import config
        print(f"✓ Config loaded: {config.APP_NAME} v{config.APP_VERSION}")
        
        # Test utils
        from src.utils import setup_logger, get_system_info
        print("✓ Utils module imported")
        
        # Test clipboard manager
        from src.clipboard_manager import ClipboardManager
        print("✓ Clipboard manager imported")
        
        # Test audio recorder
        from src.audio_recorder import AudioRecorder
        print("✓ Audio recorder imported")
        
        # Test simple UI
        from src.ui_simple import create_simple_ui
        print("✓ Simple UI imported")
        
        # Test improved command generator
        from src.command_generator_improved import WindowsCommandGenerator
        print("✓ Improved command generator imported")
        
        return True
        
    except Exception as e:
        print(f"✗ Import error: {e}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality"""
    print("\nTesting basic functionality...")
    
    try:
        # Test clipboard manager
        from src.clipboard_manager import ClipboardManager
        clipboard = ClipboardManager()
        print("✓ Clipboard manager created")
        
        # Test audio recorder
        from src.audio_recorder import AudioRecorder
        audio = AudioRecorder()
        print("✓ Audio recorder created")
        
        # Test command generator
        from src.command_generator_improved import WindowsCommandGenerator
        cmd_gen = WindowsCommandGenerator()
        print("✓ Command generator created")
        
        # Test system info
        from src.utils import get_system_info
        system_info = get_system_info()
        print(f"✓ System info: {system_info}")
        
        return True
        
    except Exception as e:
        print(f"✗ Functionality test error: {e}")
        traceback.print_exc()
        return False

def test_config_access():
    """Test configuration access"""
    print("\nTesting configuration access...")
    
    try:
        import config
        
        # Test app settings
        print(f"✓ App Name: {config.APP_NAME}")
        print(f"✓ App Version: {config.APP_VERSION}")
        print(f"✓ App Description: {config.APP_DESCRIPTION}")
        
        # Test clipboard settings
        print(f"✓ Max Clipboard Entries: {config.MAX_CLIPBOARD_ENTRIES}")
        print(f"✓ Clipboard Check Interval: {config.CLIPBOARD_CHECK_INTERVAL}")
        
        # Test audio settings
        print(f"✓ Audio Sample Rate: {config.AUDIO_SAMPLE_RATE}")
        print(f"✓ Whisper Model: {config.WHISPER_MODEL}")
        
        # Test hotkey settings
        print(f"✓ Record Hotkey: {config.RECORD_HOTKEY}")
        print(f"✓ Stop Hotkey: {config.STOP_HOTKEY}")
        
        # Test CLI settings
        print(f"✓ CLI Context Chars: {config.CLI_CONTEXT_CHARS}")
        print(f"✓ CLI Auto Copy: {config.CLI_AUTO_COPY}")
        
        return True
        
    except Exception as e:
        print(f"✗ Config access error: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=== Edge-QLM Simple Test Suite ===\n")
    
    tests = [
        test_imports,
        test_config_access,
        test_basic_functionality
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✓ {test.__name__} PASSED")
            else:
                failed += 1
                print(f"✗ {test.__name__} FAILED")
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} FAILED: {e}")
        
        print()
    
    print(f"=== Test Results ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 