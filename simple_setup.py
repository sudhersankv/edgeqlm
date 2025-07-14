#!/usr/bin/env python3
"""
Simple Setup Script for Edge-QLM
Streamlined installation and validation
"""
import subprocess
import sys
import os
from pathlib import Path

def print_header():
    print("🚀 Edge-QLM Simple Setup")
    print("=" * 40)
    print("A clean, always-on engineering assistant")
    print("=" * 40)

def check_python():
    """Check Python version"""
    print("\n📋 Checking Python...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        print(f"   Current: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True

def install_requirements():
    """Install Python requirements"""
    print("\n📦 Installing requirements...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Requirements installed")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Failed to install requirements")
        print(f"   Error: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")
    dirs = ["data", "data/clipboard", "data/audio", "logs"]
    for dir_name in dirs:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
    print("✅ Directories created")

def check_ollama():
    """Check if Ollama is available"""
    print("\n🤖 Checking Ollama...")
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed")
            
            # Check if a model is available
            try:
                models_result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
                if "codellama" in models_result.stdout or "llama" in models_result.stdout:
                    print("✅ AI model available")
                    return True
                else:
                    print("⚠️  No models found")
                    install_ollama_model()
                    return True
            except:
                print("⚠️  Could not check models")
                return True
        else:
            print("❌ Ollama not found")
            return False
    except FileNotFoundError:
        print("❌ Ollama not found")
        return False

def install_ollama_model():
    """Guide user to install Ollama model"""
    print("\n📋 Installing recommended model...")
    try:
        subprocess.run(["ollama", "pull", "codellama:7b"], check=True)
        print("✅ Model installed")
    except:
        print("⚠️  Manual model installation needed:")
        print("   Run: ollama pull codellama:7b")

def install_ollama_guide():
    """Guide user to install Ollama"""
    print("\n📋 To install Ollama:")
    print("1. Go to https://ollama.com")
    print("2. Download and install for your platform")
    print("3. Run: ollama pull codellama:7b")
    print("4. Run: ollama serve")
    print("5. Run this setup again")

def check_whisper():
    """Check if Whisper is available"""
    print("\n🎤 Checking Whisper...")
    try:
        import whisper
        print("✅ OpenAI Whisper available")
        return True
    except ImportError:
        try:
            import faster_whisper
            print("✅ Faster-Whisper available")
            return True
        except ImportError:
            print("⚠️  Whisper not found (audio transcription disabled)")
            return False

def install_whisper():
    """Install Whisper"""
    print("\n📦 Installing Whisper...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "openai-whisper"], 
                      check=True, capture_output=True)
        print("✅ Whisper installed")
    except:
        print("⚠️  Whisper installation failed (optional feature)")

def test_run():
    """Test basic functionality"""
    print("\n🧪 Testing installation...")
    try:
        # Test imports
        sys.path.insert(0, str(Path.cwd()))
        import config
        from src.utils import setup_logger
        from src.clipboard_manager import ClipboardManager
        from src.audio_recorder import AudioRecorder
        
        print("✅ Core modules imported successfully")
        
        # Test PyQt6
        try:
            from PyQt6.QtWidgets import QApplication
            print("✅ PyQt6 available")
        except ImportError:
            print("⚠️  PyQt6 not available (GUI disabled)")
        
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
    print("\nQuick Start:")
    print("  python main.py          # Launch GUI")
    print("  python qlm.py --test    # Test CLI")
    print("  python qlm.py gui       # Launch GUI from CLI")
    print("\nNext steps:")
    print("  1. Start Ollama: ollama serve")
    print("  2. Test connection: python qlm.py --test")
    print("  3. Generate commands: python qlm.py 'install nodejs'")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 