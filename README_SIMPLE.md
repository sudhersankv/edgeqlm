# Edge-QLM Simple

> A clean, always-on engineering assistant that actually works.

## What It Does

- **🤖 Smart CLI**: Type `qlm "what you want"` → get executable commands
- **📋 Always-On Clipboard**: Saves everything you copy, searchable forever
- **🎤 Voice Notes**: F9 to record, auto-transcription with Whisper
- **⚡ Modern GUI**: Dark theme, system tray, model management

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start Ollama (required for AI features)
ollama serve
ollama pull codellama:7b

# Launch GUI
python main.py
# OR
qlm gui

# Use CLI
qlm "install nodejs using winget"
qlm -c "commit all changes"  # Uses PowerShell history for context
qlm r                        # Start recording
qlm clip-10                  # Show last 10 clipboard items
```

## Key Features

### 🤖 AI Command Generation
- **Context-aware**: Reads your PowerShell history for better commands
- **Windows-focused**: Optimized for PowerShell, winget, git, docker
- **Smart output**: Commands in `$$command$$` format, auto-copied
- **Local AI**: Uses Ollama - your data stays private

### 📋 Clipboard Management
- **Always running**: Saves everything automatically
- **Smart search**: Find anything you've copied, ever
- **Auto-categorization**: Code, errors, logs, configs, etc.
- **Large capacity**: Stores up to 10,000 entries
- **CLI access**: `qlm clip-N` shows entries in terminal

### 🎤 Audio Recording
- **Hotkey recording**: F9 to start, F10 to stop
- **CLI recording**: `qlm r` for quick voice notes
- **Auto-transcription**: Uses Whisper when CPU < 30%
- **Local processing**: No cloud, no privacy concerns

### 🎯 Clean Interface
- **Modern PyQt6 UI**: Dark theme, responsive design
- **Model management**: Install/switch Ollama models easily
- **System tray**: Always accessible, never in your way
- **Settings**: Adjust CPU thresholds, hotkeys, etc.

## Installation

### Prerequisites
- **Python 3.8+**
- **Ollama** (download from https://ollama.com)
- **Windows 10/11** (optimized for Windows)

### Setup
1. **Install Ollama and model**:
   ```bash
   ollama pull codellama:7b
   ollama serve
   ```

2. **Install Edge-QLM**:
   ```bash
   git clone <repository>
   cd edge-qlm
   pip install -r requirements.txt
   ```

3. **Test**:
   ```bash
   python test_simple.py
   qlm --test
   ```

## Configuration

Edit `config.py`:

```python
# Clipboard settings
CLIPBOARD_MAX_ENTRIES = 10000
CLIPBOARD_MONITOR_INTERVAL = 1.0

# Audio settings
WHISPER_MODEL = "base"  # tiny, base, small, medium
CPU_THRESHOLD = 30      # Auto-transcribe when CPU < 30%

# Ollama settings
OLLAMA_MODEL = "codellama:7b"
OLLAMA_BASE_URL = "http://localhost:11434"
```

## CLI Examples

```bash
# Development
qlm "create new react app called myapp"
qlm "find all typescript files modified today"
qlm -c "run tests for current project"

# Git operations
qlm "create new branch called feature/login"
qlm -c "add all changes and commit with message bug fix"

# System administration
qlm "install docker desktop using winget"
qlm "check disk space on C drive"
qlm "restart windows service MyService"

# Quick actions
qlm gui          # Launch GUI
qlm r            # Start recording
qlm clip-15      # Show last 15 clipboard items
qlm --test       # Test Ollama connection
```

## Why This Version?

- ✅ **Simple**: Does a few things really well
- ✅ **Fast**: Lightweight, responsive
- ✅ **Smart**: Context-aware command generation
- ✅ **Private**: All processing happens locally
- ✅ **Reliable**: Modern PyQt6 interface, stable core

## Troubleshooting

### Common Issues
1. **"Ollama connection failed"**: Run `ollama serve`
2. **GUI won't start**: Install PyQt6: `pip install PyQt6`
3. **Audio not working**: Check microphone permissions
4. **CLI not found**: Use `python qlm.py` or run installer

### Test Commands
```bash
python test_simple.py    # Test all imports
qlm --test              # Test Ollama connection
python main.py          # Launch GUI
```

---

**Built for developers who want their tools to just work.** 🚀 