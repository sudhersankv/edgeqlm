# Edge-QLM MVP

A productivity tool for semiconductor and software engineers that helps manage clipboard history, generate commands, and record/transcribe audio meetings.

## Features

- **Clipboard History Management**: Automatic clipboard monitoring with timestamped entries and content type detection
- **Command Generation (qlm CLI)**: Generate bash, git, and EDA commands using local LLM with session context support
- **Audio Recording & Transcription**: Record meetings and system audio with automatic transcription and summarization
- **Background Processing**: Idle-time processing for summarization and content labeling
- **Simple GUI**: Easy-to-use interface for browsing and managing clipboard history

## Prerequisites

- Python 3.8+
- Ollama installed and running (for command generation)
- A coding-focused model in Ollama (e.g., `codellama:7b`)
- **Optional**: Whisper for audio transcription (see installation options below)

### Installing Ollama

1. Download and install Ollama from [ollama.ai](https://ollama.ai)
2. Pull a coding model:
   ```bash
   ollama pull codellama:7b
   ```
3. Start Ollama (it typically runs as a service)

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd edge-qlm
   ```

2. Run the automated setup:
   ```bash
   python setup.py
   ```
   This will:
   - Install Python dependencies
   - Create necessary directories
   - Attempt to set up the global `qlm` command
   - Validate your environment
   - Check for Whisper installation

## Audio Transcription Setup (Optional)

For real audio transcription (instead of placeholders), install Whisper:

### 🎯 **Option 1: Quick Install (Recommended)**
```bash
# Install OpenAI Whisper (original)
pip install openai-whisper
```

### ⚡ **Option 2: Faster Performance**
```bash
# Install Faster-Whisper (4x faster, same accuracy)
pip install faster-whisper
```

### 🎙️ **Option 3: Interactive Installer**
```bash
# Use the interactive installer
python install_whisper.py
```

### Whisper Model Options

| Model  | Size    | Speed       | Accuracy | Best For |
|--------|---------|-------------|----------|----------|
| tiny   | ~39 MB  | ~32x realtime | ⭐⭐☆☆☆ | Quick demos |
| base   | ~74 MB  | ~16x realtime | ⭐⭐⭐☆☆ | **Recommended** |
| small  | ~244 MB | ~6x realtime  | ⭐⭐⭐⭐☆ | Best balance |
| medium | ~769 MB | ~2x realtime  | ⭐⭐⭐⭐⭐ | High accuracy |
| large  | ~1550 MB| ~1x realtime  | ⭐⭐⭐⭐⭐ | Best accuracy |

### 🔧 CPU Auto-Processing

**Audio transcription runs automatically when CPU usage < 15%**

- Configure the threshold in `config.py`:
  ```python
  CPU_THRESHOLD = 15  # Adjust this value (5-50%)
  ```
- Force processing anytime via GUI Tools menu
- Monitor CPU usage in System Status window

## Setting Up Global `qlm` Command

After installation, you can make `qlm` available globally in your shell:

### 🪟 Windows (PowerShell/Command Prompt)

**Option 1: Automated installer (Recommended)**
```powershell
PowerShell -ExecutionPolicy Bypass -File install_qlm_global.ps1
```

**Option 2: Manual WindowsApps method**
1. Copy `qlm.bat` to your WindowsApps directory:
   ```powershell
   copy qlm.bat "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\"
   ```

**Option 3: Add to PATH**
1. Add the project directory to your Windows PATH environment variable
2. Use `qlm.bat` directly

**Option 4: PowerShell profile**
1. Open your PowerShell profile: `notepad $PROFILE`
2. Add this line:
   ```powershell
   function qlm { python "C:\path\to\edge-qlm\qlm.py" @args }
   ```

### 🐧 Linux/macOS

**Option 1: Symlink (Recommended)**
```bash
ln -s "$(pwd)/qlm.py" ~/.local/bin/qlm
chmod +x ~/.local/bin/qlm
# Ensure ~/.local/bin is in your PATH
```

**Option 2: Shell alias**
```bash
echo 'alias qlm="python /path/to/edge-qlm/qlm.py"' >> ~/.bashrc
source ~/.bashrc
```

**Option 3: Add to PATH**
```bash
export PATH="/path/to/edge-qlm:$PATH"
```

## Usage

### Starting the GUI Application

```bash
python main.py
```

This will start the main GUI application with:
- Clipboard history monitoring
- Background processing
- Audio recording capabilities
- System tray integration (if enabled)

### Using the qlm Command Generator

#### Basic Usage (No Context)
```bash
qlm compile verilog testbench tb_axi
# Output: vcs -full64 -sverilog -debug_all -l compile.log tb_axi.sv
```

#### With Session Context
```bash
qlm -c compile verilog for chiplet2
qlm -c run regression for uart flow with coverage
```

#### Managing Sessions
```bash
# List active sessions
qlm --list-sessions

# End current session
qlm --end-session

# Use specific session ID
qlm -c --session-id my_project generate makefile
```

### Example Command Generation

```bash
# EDA Commands
qlm compile verilog testbench tb_axi
# Output: vcs -full64 -sverilog -debug_all -l compile.log tb_axi.sv

# Git Commands
qlm git commit all changes with message "fix timing issue"
# Output: git add . && git commit -m "fix timing issue"

# Complex workflows with context
qlm -c run regression for uart flow with coverage analysis
# Output: qual_regression run --flow=uart --coverage=all --log-level=debug

# Bash/PowerShell commands
qlm find all verilog files in src directory
# Output: find src -name "*.v" -o -name "*.sv"

# EDA tool commands
qlm synthesize design with timing constraints
# Output: dc_shell-t -f synth_script.tcl -output_log_file synth.log
```

### GUI Features

**Clipboard History Tab:**
- View all clipboard entries with timestamps
- Search by content or filter by type (code, JSON, error, etc.)
- Copy entries back to clipboard
- Delete unwanted entries
- Process entries for summarization

**Audio Recording:**
- Start/stop recording via Audio menu
- **Automatic transcription when CPU < 15%**
- Summarization of transcribed content
- Automatic cleanup (keeps only last 10 recordings)
- View recordings and details in Audio window

**System Status:**
- View clipboard and audio statistics
- Monitor background processing status
- **Real-time CPU usage monitoring**
- Force processing controls

## Configuration

The main configuration is in `config.py`. Key settings include:

```python
# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "codellama:7b"

# Whisper Configuration
WHISPER_MODEL = "base"  # tiny, base, small, medium, large
WHISPER_DEVICE = "cpu"  # cpu, cuda
WHISPER_LANGUAGE = None  # None for auto-detect, or "en", "es", etc.

# Clipboard Configuration
CLIPBOARD_MAX_ENTRIES = 10000
CLIPBOARD_MONITOR_INTERVAL = 1.0  # seconds

# Audio Configuration
AUDIO_MAX_FILES = 10
AUDIO_SAMPLE_RATE = 16000

# Background Processing
IDLE_THRESHOLD = 300  # seconds
CPU_THRESHOLD = 15  # CPU usage % for auto-processing
PROCESSING_BATCH_SIZE = 10
```

## Data Storage

The application stores data in the following directories:
- `data/clipboard/` - Clipboard history JSON files
- `data/audio/` - Audio recordings and metadata
- `logs/` - Application logs

## Architecture

The MVP consists of several modular components:

- **ClipboardManager** (`src/clipboard_manager.py`): Handles clipboard monitoring and storage
- **CommandGenerator** (`src/command_generator.py`): Generates commands using Ollama
- **AudioRecorder** (`src/audio_recorder.py`): Manages audio recording and Whisper transcription
- **BackgroundProcessor** (`src/background_processor.py`): Handles CPU-aware idle-time processing
- **UI** (`src/ui.py`): Simple tkinter-based GUI

## Troubleshooting

### Common Issues

1. **`qlm` command not found**
   - Ensure you ran the setup: `python setup.py`
   - Try the manual installation methods above
   - Restart your terminal/PowerShell
   - Check that Python is in your PATH

2. **Audio transcription not working**
   - Install Whisper: `pip install openai-whisper`
   - Check model loading in logs
   - Verify microphone permissions
   - Try different Whisper model in config.py

3. **CPU usage too high for auto-processing**
   - Lower `CPU_THRESHOLD` in config.py (default: 15%)
   - Force processing via GUI Tools menu
   - Check System Status for CPU monitoring

4. **Ollama Connection Error**
   - Ensure Ollama is running: `ollama serve`
   - Check if the model is available: `ollama list`
   - Verify the base URL in config.py

5. **Clipboard Monitoring Not Working**
   - Check clipboard permissions
   - Ensure PyClip is properly installed
   - Try running with elevated permissions

### Performance Tips

- **CPU Threshold**: Adjust `CPU_THRESHOLD` (5-50%) based on your system
- **Whisper Model**: Use `tiny` or `base` for faster processing, `small`+ for accuracy
- **Processing Batch**: Reduce `PROCESSING_BATCH_SIZE` if system becomes slow
- **Memory**: Use `faster-whisper` for lower memory usage

## Development

### Project Structure
```
edge-qlm/
├── config.py                    # Configuration settings
├── main.py                      # Main application entry point
├── qlm.py                       # CLI command script
├── qlm.bat                      # Windows batch file
├── install_qlm_global.ps1       # PowerShell installer
├── install_whisper.py           # Whisper installer script
├── setup.py                     # Setup and validation script
├── requirements.txt             # Python dependencies
├── src/
│   ├── __init__.py
│   ├── clipboard_manager.py
│   ├── command_generator.py
│   ├── audio_recorder.py
│   ├── background_processor.py
│   ├── ui.py
│   └── utils.py
├── data/                        # Data storage (created at runtime)
├── logs/                        # Application logs (created at runtime)
└── README.md
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Roadmap

### Near-term improvements:
- GPU acceleration for Whisper
- Enhanced content type detection
- Better error handling and recovery
- System tray integration
- Hotkey support

### Future enhancements:
- Sensitive data detection
- Team collaboration features
- Voice-activated commands
- Cross-platform packaging
- Plugin system

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs in the `logs/` directory
3. Open an issue on the project repository

---

**Note**: This is an MVP (Minimum Viable Product) implementation. Audio transcription uses real Whisper when installed, with automatic CPU-aware processing. 