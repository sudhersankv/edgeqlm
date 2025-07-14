# Edge-QLM - Simple & Powerful CLI Assistant

A lightweight productivity tool for developers that combines clipboard management, audio recording, and AI-powered command generation in a simple, magical CLI experience.

## ✨ What Makes It Special

- **🎯 Simple CLI**: Just type `qlm "what you want"` and get executable commands
- **🧠 Context-Aware**: Uses your PowerShell history for smarter suggestions
- **📋 Always-On Clipboard**: Never lose anything you copy again
- **🎤 Voice Notes**: Quick audio recording with automatic transcription
- **⚡ Lightweight**: Modern PyQt6 GUI that stays out of your way
- **🔒 Local AI**: Uses Ollama - your data never leaves your machine

## Quick Start

1. **Install Ollama** (required for command generation):
   ```bash
   # Download from https://ollama.com and install
   ollama pull codellama:7b
   ```

2. **Install Edge-QLM**:
   ```bash
   git clone <repository-url>
   cd edge-qlm
   pip install -r requirements.txt
   ```

3. **Start using**:
   ```bash
   # Launch GUI
   qlm gui

   # Generate commands
   qlm "install nodejs using winget"
   qlm "git commit all changes with message fix bug"
   
   # With context (uses PowerShell history)
   qlm -c "run tests for current project"
   
   # Quick actions
   qlm r                    # Start recording
   qlm clip-10             # Show last 10 clipboard items
   ```

## Core Features

### 🤖 AI Command Generation
- **Simple**: `qlm "create new react app"`
- **Context-aware**: `qlm -c "commit changes"` (uses your recent commands)
- **Windows-focused**: Optimized for PowerShell, winget, git, docker, etc.
- **Smart output**: Commands wrapped in `$$command$$` and auto-copied

### 📋 Clipboard Management
- **Always running**: Saves everything you copy automatically
- **Smart categorization**: Code, JSON, errors, logs, configs
- **Powerful search**: Find anything you've copied, ever
- **Large capacity**: Stores up to 10,000 entries
- **CLI access**: `qlm clip-15` shows last 15 items in terminal

### 🎤 Audio Recording & Transcription
- **Hotkey recording**: F9 to start, F10 to stop (configurable)
- **CLI recording**: `qlm r` for quick voice notes
- **Auto-transcription**: Uses Whisper locally when CPU < 30%
- **On-demand**: Transcribe specific recordings from GUI
- **Smart processing**: Only processes when system is idle

### 🎯 Modern GUI
- **Clean interface**: Dark theme, tabbed design
- **Model management**: Install/switch Ollama models easily
- **Settings**: Adjust CPU thresholds, hotkeys, etc.
- **System tray**: Always accessible, never in your way
- **Launch from CLI**: `qlm gui` opens the interface

## Installation

### Prerequisites
- **Python 3.8+**
- **Ollama** (for AI features)
- **Windows 10/11** (optimized for Windows, but works on other platforms)

### Step-by-Step Setup

1. **Install Ollama**:
   ```bash
   # Download from https://ollama.com
   # After installation:
   ollama pull codellama:7b
   ollama serve  # Start the service
   ```

2. **Clone and Install**:
   ```bash
   git clone <repository-url>
   cd edge-qlm
   pip install -r requirements.txt
   ```

3. **Optional - Global CLI**:
   ```powershell
   # Windows PowerShell (run as administrator)
   PowerShell -ExecutionPolicy Bypass -File install_qlm_global.ps1
   ```

4. **Test Installation**:
   ```bash
   python test_simple.py
   qlm --test  # Test Ollama connection
   ```

## Usage Examples

### Command Generation
```bash
# Development
qlm "create dockerfile for node app"
qlm "find all typescript files modified today"
qlm -c "run build and deploy to staging"

# Git operations
qlm "create new branch called feature/login"
qlm -c "merge main and push changes"

# System administration
qlm "install docker desktop using winget"
qlm "restart windows service called MyService"
qlm "check disk space on all drives"

# File operations
qlm "copy all json files to backup folder"
qlm "find files larger than 100MB"
```

### Quick Actions
```bash
qlm gui          # Launch GUI
qlm r            # Start recording
qlm clip-15      # Show last 15 clipboard items
qlm --test       # Test Ollama connection
```

### Context-Aware Generation
```bash
# The -c flag uses your recent PowerShell history for context
qlm -c "commit these changes"           # Knows what files you've been working on
qlm -c "run the tests"                  # Understands your project structure
qlm -c "deploy to production"           # Uses context from recent commands
```

## Configuration

Edit `config.py` to customize:

```python
# Ollama Settings
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "codellama:7b"

# Clipboard Settings
CLIPBOARD_MAX_ENTRIES = 10000
CLIPBOARD_MONITOR_INTERVAL = 1.0

# Audio Settings
WHISPER_MODEL = "base"  # tiny, base, small, medium, large
CPU_THRESHOLD = 30      # Auto-transcribe when CPU < 30%

# UI Settings
UI_WINDOW_WIDTH = 1000
UI_WINDOW_HEIGHT = 700
```

## Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
qlm --test

# Start Ollama service
ollama serve

# Check available models
ollama list

# Install a model
ollama pull codellama:7b
```

### Common Issues
1. **"Ollama connection failed"**: Run `ollama serve` in a terminal
2. **GUI won't start**: Install PyQt6: `pip install PyQt6`
3. **Audio not working**: Check microphone permissions
4. **CLI not found**: Run the global installer or use `python qlm.py`

## Architecture

- **Lightweight**: Minimal dependencies, fast startup
- **Modular**: Clean separation of CLI, GUI, and core features
- **Local-first**: All AI processing happens on your machine
- **Background-friendly**: Smart CPU usage, idle-time processing

## Why Edge-QLM?

- **🚀 Instant**: Commands generated in seconds
- **🧠 Smart**: Context-aware suggestions
- **🔒 Private**: Your data stays on your machine
- **⚡ Fast**: Lightweight, responsive interface
- **🎯 Focused**: Does a few things really well

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

---

**Made for developers who want their tools to just work.** 🚀 