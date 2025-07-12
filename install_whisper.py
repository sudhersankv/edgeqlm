#!/usr/bin/env python3
"""
Whisper Installation Script for Edge-QLM
Choose between different Whisper implementations
"""
import sys
import subprocess
import argparse

def install_openai_whisper():
    """Install OpenAI Whisper (original)"""
    print("🎙️  Installing OpenAI Whisper...")
    print("📊 Features:")
    print("   • Original implementation")
    print("   • Good accuracy")
    print("   • Moderate speed")
    print("   • Easy to use")
    print()
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', 'openai-whisper'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ OpenAI Whisper installed successfully!")
            test_whisper_installation()
            return True
        else:
            print("❌ Installation failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error installing OpenAI Whisper: {e}")
        return False

def install_faster_whisper():
    """Install Faster-Whisper (optimized)"""
    print("⚡ Installing Faster-Whisper...")
    print("📊 Features:")
    print("   • 4x faster than original")
    print("   • Lower memory usage")
    print("   • Same accuracy")
    print("   • Better for batch processing")
    print()
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', 'faster-whisper'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Faster-Whisper installed successfully!")
            test_faster_whisper_installation()
            return True
        else:
            print("❌ Installation failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error installing Faster-Whisper: {e}")
        return False

def test_whisper_installation():
    """Test OpenAI Whisper installation"""
    try:
        import whisper
        model = whisper.load_model("base")
        print("   ✅ Whisper model loaded successfully")
        print("   📝 Model: base (good balance)")
        return True
    except Exception as e:
        print(f"   ⚠️  Model loading failed: {e}")
        return False

def test_faster_whisper_installation():
    """Test Faster-Whisper installation"""
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("base")
        print("   ✅ Faster-Whisper model loaded successfully")
        print("   📝 Model: base (good balance)")
        return True
    except Exception as e:
        print(f"   ⚠️  Model loading failed: {e}")
        return False

def show_model_info():
    """Show information about Whisper models"""
    print("\n🔧 Whisper Model Options:")
    print("=" * 40)
    print("📊 Model Size vs Speed vs Accuracy:")
    print()
    
    models = [
        ("tiny", "~39 MB", "~32x realtime", "⭐⭐☆☆☆"),
        ("base", "~74 MB", "~16x realtime", "⭐⭐⭐☆☆"),
        ("small", "~244 MB", "~6x realtime", "⭐⭐⭐⭐☆"),
        ("medium", "~769 MB", "~2x realtime", "⭐⭐⭐⭐⭐"),
        ("large", "~1550 MB", "~1x realtime", "⭐⭐⭐⭐⭐"),
    ]
    
    print(f"{'Model':<8} {'Size':<12} {'Speed':<16} {'Accuracy'}")
    print("-" * 50)
    for model, size, speed, accuracy in models:
        print(f"{model:<8} {size:<12} {speed:<16} {accuracy}")
    
    print()
    print("💡 Recommendations:")
    print("   • tiny/base: For real-time applications")
    print("   • small: Best balance for most users")
    print("   • medium/large: For high-accuracy needs")
    print()
    print("⚙️  CPU Auto-Processing in Edge-QLM:")
    print("   • Runs when CPU usage < 15%")
    print("   • Configure via CPU_THRESHOLD in config.py")
    print("   • Change model via WHISPER_MODEL in config.py")

def main():
    parser = argparse.ArgumentParser(
        description="Install Whisper for Edge-QLM audio transcription",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python install_whisper.py --openai        # Install OpenAI Whisper
  python install_whisper.py --faster        # Install Faster-Whisper
  python install_whisper.py --info          # Show model information
        """
    )
    
    parser.add_argument('--openai', action='store_true', 
                       help='Install OpenAI Whisper (original)')
    parser.add_argument('--faster', action='store_true', 
                       help='Install Faster-Whisper (optimized)')
    parser.add_argument('--info', action='store_true', 
                       help='Show model information')
    
    args = parser.parse_args()
    
    print("🎙️  Whisper Installation for Edge-QLM")
    print("=" * 40)
    
    if args.info:
        show_model_info()
        return
    
    if args.openai:
        success = install_openai_whisper()
    elif args.faster:
        success = install_faster_whisper()
    else:
        # Interactive mode
        print("\nChoose Whisper implementation:")
        print("1. 🎯 OpenAI Whisper (recommended for beginners)")
        print("2. ⚡ Faster-Whisper (recommended for performance)")
        print("3. 📊 Show model information")
        print("4. ❌ Exit")
        
        while True:
            try:
                choice = input("\nEnter choice (1-4): ").strip()
                
                if choice == "1":
                    success = install_openai_whisper()
                    break
                elif choice == "2":
                    success = install_faster_whisper()
                    break
                elif choice == "3":
                    show_model_info()
                    continue
                elif choice == "4":
                    print("Installation cancelled")
                    return
                else:
                    print("Invalid choice. Please enter 1, 2, 3, or 4.")
                    
            except KeyboardInterrupt:
                print("\nInstallation cancelled")
                return
    
    if 'success' in locals() and success:
        print("\n🎉 Installation completed!")
        print("\n📝 Next steps:")
        print("1. Run 'python main.py' to start Edge-QLM GUI")
        print("2. Use Audio menu to start recording")
        print("3. Recordings auto-transcribe when CPU < 15%")
        print("4. Edit config.py to change model or CPU threshold")

if __name__ == "__main__":
    main() 