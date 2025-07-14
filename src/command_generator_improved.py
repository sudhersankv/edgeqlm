"""
Improved Command Generator
Windows-focused CLI with PowerShell history integration
"""
import json
import os
import sys
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests

import config
from src.utils import setup_logger
import time
import subprocess
from src.audio_recorder import AudioRecorder
import json
from pathlib import Path
import config
import pyperclip

logger = setup_logger(__name__)


class WindowsCommandGenerator:
    """Improved command generator for Windows with PowerShell history"""
    
    def __init__(self):
        self.powershell_history_path = self._get_powershell_history_path()
        self.context_cache = {}
        self.last_context_update = None
        
    def _get_powershell_history_path(self) -> Optional[Path]:
        """Get PowerShell history file path"""
        try:
            # PowerShell 5.x history
            ps_history_path = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "PowerShell" / "PSReadLine" / "ConsoleHost_history.txt"
            if ps_history_path.exists():
                return ps_history_path
            
            # PowerShell 7+ history
            ps7_history_path = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "PowerShell" / "PSReadLine" / "ConsoleHost_history.txt"
            if ps7_history_path.exists():
                return ps7_history_path
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting PowerShell history path: {e}")
            return None
    
    def get_recent_powershell_commands(self, max_chars: int = 1000) -> str:
        """Get recent PowerShell commands for context"""
        try:
            if not self.powershell_history_path or not self.powershell_history_path.exists():
                return ""
            
            # Read the last part of the history file
            with open(self.powershell_history_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Read last 2000 characters to get recent commands
                f.seek(0, 2)  # Go to end
                file_size = f.tell()
                if file_size > 2000:
                    f.seek(file_size - 2000)
                else:
                    f.seek(0)
                
                content = f.read()
                
                # Clean up and filter commands
                lines = content.split('\n')
                
                # Filter out noise and get meaningful commands
                filtered_lines = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#') and len(line) > 3:
                        # Remove sensitive information
                        if not any(keyword in line.lower() for keyword in ['password', 'token', 'key', 'secret']):
                            filtered_lines.append(line)
                
                # Get last few commands within character limit
                recent_commands = []
                char_count = 0
                
                for line in reversed(filtered_lines):
                    if char_count + len(line) + 1 <= max_chars:
                        recent_commands.append(line)
                        char_count += len(line) + 1
                    else:
                        break
                
                recent_commands.reverse()
                return '\n'.join(recent_commands)
                
        except Exception as e:
            logger.error(f"Error reading PowerShell history: {e}")
            return ""
    
    def get_current_context(self) -> Dict[str, Any]:
        """Get current system context"""
        try:
            context = {
                'working_directory': os.getcwd(),
                'platform': 'Windows',
                'shell': 'PowerShell',
                'user': os.environ.get('USERNAME', 'user'),
                'computer': os.environ.get('COMPUTERNAME', 'local'),
                'recent_commands': self.get_recent_powershell_commands(),
                'timestamp': datetime.now().isoformat()
            }
            
            # Add directory contents (just names, not full listing)
            try:
                items = os.listdir('.')
                context['directory_contents'] = [item for item in items[:20]]  # Limit to 20 items
            except:
                context['directory_contents'] = []
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting current context: {e}")
            return {}
    
    def generate_command(self, prompt: str, use_context: bool = False) -> str:
        """Generate a command based on the prompt"""
        try:
            # Build system prompt for Windows commands
            system_prompt = self._build_system_prompt(use_context)
            
            # Build user prompt
            user_prompt = self._build_user_prompt(prompt, use_context)
            
            # Call Ollama
            response = self._call_ollama(system_prompt, user_prompt)
            
            if response:
                return self._clean_command_response(response)
            else:
                return "# Error: Failed to generate command - check logs for details"
                
        except Exception as e:
            logger.error(f"Error generating command: {e}")
            return f"# Error: {str(e)}"
    
    def _build_system_prompt(self, use_context: bool) -> str:
        """Build system prompt for Windows commands"""
        return """You are a Windows command-line expert. Generate ONLY executable commands.

CRITICAL RULES:
1. Output ONLY the command(s) - no explanations, comments, or extra text
2. Use Windows/PowerShell commands primarily
3. For multi-step operations, separate commands with newlines
4. Use appropriate Windows paths (backslashes)
5. Include necessary parameters and flags
6. Common tools: PowerShell, CMD, Git, Docker, Python, Node.js, VS Code, etc.

FOCUS AREAS:
- File operations (copy, move, delete, search)
- Git operations (clone, push, pull, commit, branch)
- Development tasks (build, test, deploy)
- System administration (services, processes, registry)
- Network operations (ping, curl, ssh)
- Package management (winget, choco, pip, npm)

OUTPUT FORMAT: Raw commands only, one per line if multiple steps."""
    
    def _build_user_prompt(self, prompt: str, use_context: bool) -> str:
        """Build user prompt with context if requested"""
        if use_context:
            context = self.get_current_context()
            context_str = f"""
CURRENT CONTEXT:
Directory: {context.get('working_directory', 'unknown')}
User: {context.get('user', 'unknown')}
Computer: {context.get('computer', 'unknown')}

RECENT COMMANDS:
{context.get('recent_commands', 'None')}

DIRECTORY CONTENTS:
{', '.join(context.get('directory_contents', []))}

USER REQUEST: {prompt}"""
            return context_str
        else:
            return f"USER REQUEST: {prompt}"
    
    def _call_ollama(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Call Ollama API"""
        try:
            url = f"{config.OLLAMA_BASE_URL}/api/generate"
            
            # Combine prompts
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            payload = {
                "model": config.OLLAMA_MODEL,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Lower temperature for more consistent commands
                    "top_p": 0.8,
                    "max_tokens": 300,   # Shorter responses for commands
                    "stop": ["#", "```", "Note:", "Explanation:"]  # Stop on explanations
                }
            }
            
            response = requests.post(
                url,
                json=payload,
                timeout=config.OLLAMA_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                error_msg = f"Ollama API error: {response.status_code}"
                if response.status_code == 404:
                    error_msg += " - Model '{config.OLLAMA_MODEL}' not found. Run 'ollama pull {config.OLLAMA_MODEL}'"
                logger.error(error_msg)
                return None
        except requests.ConnectionError:
            error_msg = "Failed to connect to Ollama. Is Ollama running? Try starting it with 'ollama serve' in a terminal. If not installed, download from ollama.com."
            logger.error(error_msg)
            return None
        except requests.Timeout:
            logger.error("Ollama request timed out")
            return None
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return None
    
    def _clean_command_response(self, response: str) -> str:
        """Clean and format command response"""
        if not response:
            return "# Error: Empty response"
        
        # Remove explanations and comments
        lines = response.split('\n')
        command_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#') or line.startswith('//'):
                continue
            
            # Skip explanatory text
            if any(word in line.lower() for word in ['explanation:', 'note:', 'here', 'this will', 'the command']):
                continue
            
            # Remove common prefixes
            for prefix in ['$ ', '> ', 'PS> ', 'C:\\>', 'Command: ', 'command: ']:
                if line.startswith(prefix):
                    line = line[len(prefix):].strip()
            
            # Remove markdown code blocks
            if line.startswith('```') or line.endswith('```'):
                continue
            
            if line:
                command_lines.append(line)
        
        # Join commands
        result = '\n'.join(command_lines)
        
        # If no valid commands found, return original response
        if not result.strip():
            return response.strip()
        
        return result
    
    def test_connection(self) -> bool:
        """Test Ollama connection"""
        try:
            url = f"{config.OLLAMA_BASE_URL}/api/tags"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False


def main():
    """Main CLI function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='QLM - Windows Command Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  qlm install nodejs using winget
  qlm -c git commit all changes with message bug fix
  qlm create new folder called test and cd into it
  qlm find all python files in current directory
  qlm start docker container for postgresql
        """
    )
    
    parser.add_argument('prompt', nargs='*', help='Command generation prompt')
    parser.add_argument('-c', '--context', action='store_true', 
                       help='Use PowerShell history and current context')
    parser.add_argument('--test', action='store_true',
                       help='Test connection to Ollama')
    parser.add_argument('--no-copy', action='store_true',
                       help='Don\'t copy result to clipboard')
    parser.add_argument('--record', '-r', action='store_true', help='Start audio recording')
    parser.add_argument('--gui', action='store_true', help='Launch GUI application')
    parser.add_argument('--clip', type=int, nargs='?', const=10, help='Display last N clipboard entries (default: 10)')
    
    args = parser.parse_args()
    
    generator = WindowsCommandGenerator()
    
    # Test connection
    if args.test:
        if generator.test_connection():
            print("✓ Ollama connection successful")
        else:
            print("✗ Ollama connection failed")
        return

    # Handle positional shortcuts
    if args.prompt and len(args.prompt) == 1:
        prompt_str = args.prompt[0]
        if prompt_str == 'gui':
            args.gui = True
        elif prompt_str == 'r':
            args.record = True
        elif prompt_str.startswith('clip-'):
            try:
                args.clip = int(prompt_str[5:])
            except ValueError:
                pass

    # Launch GUI
    if args.gui:
        project_root = Path(__file__).parent.parent
        subprocess.Popen(['python', str(project_root / 'main.py')])
        print("Launching GUI...")
        return

    # Start recording
    if args.record:
        audio_recorder = AudioRecorder()
        audio_recorder.start_recording()
        print("Recording started. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            audio_recorder.stop_recording()
            print("Recording stopped.")
        return

    # Display clipboard
    if args.clip is not None:
        n = args.clip
        try:
            with open(config.CLIPBOARD_LOG_FILE, 'r') as f:
                entries = json.load(f)
            entries = sorted(entries, key=lambda x: x.get('timestamp', ''), reverse=True)[:n]
            print(f"Last {len(entries)} clipboard entries:")
            for i, entry in enumerate(entries, 1):
                ts = entry.get('timestamp', '')[:19]
                content = entry.get('content', '')[:100].replace('\n', ' ').strip()
                print(f"{i}. [{ts}] {content}...")
        except Exception as e:
            print(f"Error loading clipboard: {e}")
        return
    
    # Generate command
    if not args.prompt:
        parser.print_help()
        return
    
    prompt = ' '.join(args.prompt)
    
    # Show context info if requested
    if args.context:
        print(f"Using context from PowerShell history...")
    
    # Generate command
    command = generator.generate_command(prompt, use_context=args.context)
    
    # Copy to clipboard
    if not args.no_copy:
        try:
            pyperclip.copy(command)
            print("Generated command (copied to clipboard):")
        except Exception:
            print("Generated command (copy failed):")
    else:
        print("Generated command:")
    
    # Output the command
    print(f"$${command}$$")


if __name__ == "__main__":
    main() 