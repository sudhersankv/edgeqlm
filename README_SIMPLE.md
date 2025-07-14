# Edge-QLM Simple

> A clean, always-on engineering assistant for Windows that actually works.

## What It Does

- **Always-on Clipboard History**: Automatically saves and categorizes everything you copy
- **Voice Recording**: Quick voice notes with automatic transcription
- **Smart CLI**: Context-aware command generation with PowerShell history integration
- **Clean Interface**: Simple, focused UI without bloat

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python main.py
   ```

3. **Use the CLI**:
   ```bash
   # Basic usage
   qlm install nodejs using winget
   
   # With context from PowerShell history
   qlm -c git commit all changes with message bug fix
   
   # Test connection
   qlm --test
   ```

## Key Features

### 📋 Clipboard Management
- **Always Running**: Saves everything you copy, always
- **Smart Search**: Find anything you've copied, ever
- **Auto-Categorization**: Code, errors, logs, configs, etc.
- **Large Capacity**: Stores up to 5000 clipboard entries

### 🎤 Voice Recording
- **Hotkey Recording**: F9 to start, F10 to stop
- **Auto-Transcription**: Automatic speech-to-text
- **Quick Notes**: Save transcriptions as clipboard entries
- **Local Processing**: Uses Whisper locally (no cloud)

### 💻 Smart CLI
- **Context-Aware**: Reads your PowerShell history for better commands
- **Windows-Focused**: Optimized for Windows development workflows
- **Clean Output**: Only commands, no explanations or fluff
- **Auto-Copy**: Generated commands automatically copied to clipboard

### 🎯 Clean Interface
- **Two Main Tabs**: Clipboard and Audio - that's it
- **System Tray**: Always accessible, never in your way
- **Dark Theme**: Easy on the eyes
- **Responsive**: Fast and lightweight

## Configuration

Edit `config.py` to customize:

```python
# Clipboard settings
MAX_CLIPBOARD_ENTRIES = 5000  # How many entries to keep
CLIPBOARD_CHECK_INTERVAL = 1  # How often to check (seconds)

# Audio settings
RECORD_HOTKEY = "F9"  # Key to start recording
STOP_HOTKEY = "F10"   # Key to stop recording
WHISPER_MODEL = "base"  # Whisper model size

# CLI settings
CLI_CONTEXT_CHARS = 1000  # PowerShell history chars to use
CLI_AUTO_COPY = True      # Auto-copy generated commands
```

## Why This Version?

The original Edge-QLM became too complex. This simplified version:

- ❌ Removes unnecessary complexity
- ❌ Removes background processing overhead  
- ❌ Removes command generation from UI
- ✅ Focuses on core functionality
- ✅ Always-on clipboard monitoring
- ✅ Better CLI with PowerShell integration
- ✅ Reliable, simple, fast

## Requirements

- **Windows 10/11**: Optimized for Windows development
- **Python 3.8+**: Modern Python required
- **Ollama**: For CLI command generation
- **PowerShell**: For context-aware commands

## Troubleshooting

### Common Issues

1. **Import Errors**: Run `python test_simple.py` to check setup
2. **Audio Issues**: Check microphone permissions
3. **CLI Not Working**: Ensure Ollama is running (`qlm --test`)
4. **Clipboard Not Saving**: Check write permissions in data folder

### Test Your Installation

```bash
python test_simple.py
```

## CLI Examples

```bash
# Development tasks
qlm create new react app called myapp
qlm -c run tests for current project
qlm find all typescript files modified today

# Git operations
qlm -c add all changes and commit with message "fix bug"
qlm create new branch called feature/login
qlm merge main into current branch

# System administration
qlm install docker desktop using winget
qlm check disk space on C drive
qlm restart windows service called "MyService"

# File operations
qlm copy all json files to backup folder
qlm find files larger than 100MB in current directory
qlm compress folder called "old_projects" to zip
```

## Philosophy

> "I want a brilliantly executed simple tool, not a simply executed brilliant tool"

This version prioritizes:
- **Reliability** over features
- **Simplicity** over complexity  
- **Performance** over polish
- **Usability** over configurability

Built for engineers who want tools that work, not toys that impress.

---

*Clean. Simple. Always working.* 