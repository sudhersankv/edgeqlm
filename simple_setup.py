#!/usr/bin/env python3
"""
Simple Setup Script for Edge-QLM
No complicated GUI - just gets the job done
"""

import os
import sys
import subprocess
import platform

def print_header():
    """Print simple header"""
    print("=" * 60)
    print("Edge-QLM Setup")
    print("=" * 60)

def check_python():
    """Check Python version"""
    print("Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current:", sys.version)
        return False
    print("✅ Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def install_requirements():
    """Install Python requirements"""
    print("\nInstalling Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ Python dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Failed to install dependencies:")
        print(e.stderr)
        return False

def check_ollama():
    """Check if Ollama is available"""
    print("\nChecking Ollama...")
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed")
            return True
        else:
            print("❌ Ollama not found")
            return False
    except FileNotFoundError:
        print("❌ Ollama not found")
        return False

def install_ollama_guide():
    """Guide user to install Ollama"""
    print("\n📋 To install Ollama:")
    print("1. Go to https://ollama.com")
    print("2. Download and install for your platform")
    print("3. Run: ollama pull codellama:7b")
    print("4. Run this setup again")

def check_whisper():
    """Check Whisper installation"""
    print("\nChecking Whisper...")
    try:
        import whisper
        print("✅ OpenAI Whisper installed")
        return True
    except ImportError:
        try:
            import faster_whisper
            print("✅ Faster-Whisper installed")
            return True
        except ImportError:
            print("❌ Whisper not found")
            return False

def install_whisper():
    """Install Whisper"""
    print("\nWhich Whisper would you like?")
    print("1. OpenAI Whisper (original)")
    print("2. Faster-Whisper (recommended)")
    print("3. Skip")
    
    choice = input("Choose (1/2/3): ").strip()
    
    if choice == "1":
        package = "openai-whisper"
    elif choice == "2":  
        package = "faster-whisper"
    else:
        print("⏭️ Skipping Whisper installation")
        return True
    
    try:
        print(f"Installing {package}...")
        subprocess.run([sys.executable, "-m", "pip", "install", package], 
                      check=True, capture_output=True, text=True)
        print(f"✅ {package} installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}")
        print(e.stderr)
        return False

def setup_directories():
    """Create necessary directories"""
    print("\nCreating directories...")
    dirs = ["data", "logs", "data/audio", "data/clipboard"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print("✅ Directories created")

def test_run():
    """Test if the application can start"""
    print("\nTesting application...")
    try:
        # Just try importing main components
        import config
        from src.utils import setup_logger
        from src.clipboard_manager import ClipboardManager
        from src.command_generator import CommandGenerator
        print("✅ All modules can be imported")
        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Main setup function"""
    print_header()
    
    # Check Python
    if not check_python():
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Setup directories  
    setup_directories()
    
    # Check Ollama
    if not check_ollama():
        install_ollama_guide()
    
    # Check/Install Whisper
    if not check_whisper():
        install_whisper()
    
    # Test run
    if not test_run():
        print("\n❌ Setup incomplete. Check errors above.")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("\nTo run Edge-QLM:")
    print("  python main.py")
    print("\nTo use CLI:")
    print("  python qlm.py 'your command here'")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 