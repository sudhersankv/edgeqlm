"""
Setup script for Edge-QLM MVP
"""
import os
import sys
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def check_ollama():
    """Check if Ollama is available"""
    try:
        import subprocess
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is available")
            models = result.stdout.strip().split('\n')[1:]  # Skip header
            if models and models[0].strip():
                print(f"   Available models: {len(models)}")
                for model in models[:3]:  # Show first 3 models
                    print(f"   - {model.split()[0]}")
            else:
                print("   ⚠️  No models found. Run 'ollama pull codellama:7b'")
            return True
        else:
            print("❌ Ollama not found or not running")
            return False
    except FileNotFoundError:
        print("❌ Ollama not found. Please install from https://ollama.ai")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print("❌ Failed to install dependencies")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_whisper_installation():
    """Check if Whisper is installed and working"""
    print("\n🎙️  Checking Whisper installation...")
    
    try:
        import whisper
        print("✅ OpenAI Whisper is available")
        
        # Try to load a small model to verify it works
        try:
            model = whisper.load_model("base")
            print("   ✅ Whisper model loaded successfully")
            print(f"   📊 Model: base (good balance of speed/accuracy)")
            return True
        except Exception as e:
            print(f"   ⚠️  Whisper installed but model loading failed: {e}")
            return False
            
    except ImportError:
        print("⚠️  OpenAI Whisper not found")
        
        # Check for faster-whisper
        try:
            from faster_whisper import WhisperModel
            print("✅ Faster-Whisper is available (alternative)")
            return True
        except ImportError:
            print("❌ No Whisper implementation found")
            print("\n📋 To enable audio transcription, install one of:")
            print("   Option 1 (Recommended): pip install openai-whisper")
            print("   Option 2 (Faster):      pip install faster-whisper")
            print("\n🔧 Whisper Models (balance of speed vs accuracy):")
            print("   • tiny   - Fastest, lowest accuracy")
            print("   • base   - Good balance (recommended)")
            print("   • small  - Better accuracy, slower")
            print("   • medium - High accuracy, much slower")
            print("   • large  - Best accuracy, very slow")
            print("\n⚙️  CPU Auto-Processing:")
            print("   • Transcription runs automatically when CPU < 15%")
            print("   • You can adjust CPU_THRESHOLD in config.py")
            print("   • Force processing anytime via GUI menu")
            return False

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    try:
        import config
        # The config module will create directories automatically
        print("✅ Directories created")
        return True
    except Exception as e:
        print(f"❌ Error creating directories: {e}")
        return False

def setup_qlm_global():
    """Setup qlm command globally"""
    project_root = Path(__file__).parent.absolute()
    
    if sys.platform == "win32":
        return setup_qlm_windows(project_root)
    else:
        return setup_qlm_unix(project_root)

def setup_qlm_windows(project_root):
    """Setup qlm for Windows"""
    print("\n🔧 Setting up qlm command for Windows...")
    
    # Option 1: Try WindowsApps directory (no admin required)
    user_path = Path(os.environ['USERPROFILE']) / "AppData/Local/Microsoft/WindowsApps"
    
    if user_path.exists():
        try:
            batch_file = user_path / "qlm.bat"
            batch_content = f'@echo off\npython "{project_root / "qlm.py"}" %*'
            
            with open(batch_file, 'w') as f:
                f.write(batch_content)
            
            print(f"✅ qlm command installed to {batch_file}")
            print("   You can now use 'qlm' directly in any PowerShell/Command Prompt")
            return True
            
        except PermissionError:
            print("⚠️ Permission denied for WindowsApps directory")
    
    # Option 2: Manual instructions
    print("\n📋 Manual setup options:")
    print("1. 🎯 Recommended - Run the PowerShell installer:")
    print("   PowerShell -ExecutionPolicy Bypass -File install_qlm_global.ps1")
    print()
    print("2. 📁 Add project directory to PATH:")
    print(f"   Add {project_root} to your Windows PATH environment variable")
    print()
    print("3. 🔗 Copy the batch file:")
    print(f"   Copy qlm.bat to a directory in your PATH")
    print()
    print("4. 💻 PowerShell profile method:")
    print("   Add this to your PowerShell profile:")
    print(f'   function qlm {{ python "{project_root / "qlm.py"}" @args }}')
    
    return True

def setup_qlm_unix(project_root):
    """Setup qlm for Unix/Linux/macOS"""
    print("\n🔧 Setting up qlm command for Unix/Linux...")
    
    # Make qlm.py executable
    qlm_path = project_root / "qlm.py"
    try:
        os.chmod(qlm_path, 0o755)
        print(f"✅ Made {qlm_path} executable")
    except Exception as e:
        print(f"⚠️ Could not make qlm.py executable: {e}")
    
    # Try to create symlink in common locations
    possible_paths = [
        Path.home() / ".local/bin",
        Path("/usr/local/bin"),
        Path("/opt/local/bin")
    ]
    
    for bin_path in possible_paths:
        if bin_path.exists() and os.access(bin_path, os.W_OK):
            try:
                symlink_path = bin_path / "qlm"
                if symlink_path.exists():
                    symlink_path.unlink()
                symlink_path.symlink_to(qlm_path)
                print(f"✅ Created symlink: {symlink_path} -> {qlm_path}")
                return True
            except Exception as e:
                print(f"⚠️ Could not create symlink in {bin_path}: {e}")
    
    # Manual instructions
    print("\n📋 Manual setup options:")
    print("1. 🔗 Create symlink (recommended):")
    print(f"   ln -s {qlm_path} ~/.local/bin/qlm")
    print("   # Make sure ~/.local/bin is in your PATH")
    print()
    print("2. 📝 Add alias to shell profile:")
    print(f'   echo \'alias qlm="python {qlm_path}"\' >> ~/.bashrc')
    print("   source ~/.bashrc")
    print()
    print("3. 📁 Add to PATH:")
    print(f"   export PATH=\"{project_root}:$PATH\"")
    
    return True

def verify_installation():
    """Verify the installation works"""
    print("\n🧪 Testing installation...")
    try:
        import subprocess
        result = subprocess.run(['python', 'qlm.py', '--help'], 
                              capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode == 0:
            print("✅ qlm.py works correctly")
            return True
        else:
            print("❌ qlm.py test failed")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error testing qlm.py: {e}")
        return False

def show_usage_examples():
    """Show usage examples"""
    print("\n🚀 Usage Examples:")
    print("="*50)
    print()
    print("📋 GUI Application:")
    print("   python main.py")
    print()
    print("🤖 qlm Command Generator:")
    print("   qlm compile verilog testbench tb_axi")
    print("   qlm -c run regression for uart flow with coverage")
    print("   qlm git commit all changes with message 'fix bug'")
    print("   qlm --list-sessions")
    print()
    print("🎙️  Audio Processing:")
    print("   • Start GUI and use Audio menu")
    print("   • Recordings auto-transcribe when CPU < 15%")
    print("   • Force processing via Tools menu")
    print()
    print("⚙️  Configuration:")
    print("   • Edit config.py to customize settings")
    print("   • Change WHISPER_MODEL for speed/accuracy balance")
    print("   • Adjust CPU_THRESHOLD for auto-processing")

def main():
    """Main setup function"""
    print("🚀 Edge-QLM MVP Setup")
    print("=" * 50)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Check Ollama
    if not check_ollama():
        success = False
    
    # Install dependencies
    if success and not install_dependencies():
        success = False
    
    # Check Whisper installation
    whisper_ok = check_whisper_installation()
    
    # Create directories
    if success and not create_directories():
        success = False
    
    # Verify basic installation
    if success and not verify_installation():
        success = False
    
    # Setup global qlm command
    if success:
        setup_qlm_global()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Setup completed successfully!")
        
        if whisper_ok:
            print("🎙️  Audio transcription ready!")
        else:
            print("⚠️  Audio transcription will use placeholder until Whisper is installed")
        
        show_usage_examples()
        
    else:
        print("❌ Setup encountered errors. Please check the messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 